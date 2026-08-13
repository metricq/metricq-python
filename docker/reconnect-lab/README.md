# Reconnect lab

A throwaway MetricQ instance for exercising `metricq-python`'s reconnect
handling (`aio_pika.connect_robust` + `ConnectionWatchdog` in
[`metricq/agent.py`](../../metricq/agent.py) and
[`metricq/connection_watchdog.py`](../../metricq/connection_watchdog.py))
against real connection drops, broker restarts and cluster failover.

Two stacks are provided:

- `docker-compose.singlenode.yml` — manager, couchdb, a single RabbitMQ
  broker, and a source+sink pair built from *this* checkout of
  `metricq-python`.
- `docker-compose.cluster.yml` — the same, but with a 3-node RabbitMQ
  cluster instead of a single broker.

Both use `rabbitmq:3-management-alpine`. RabbitMQ 4's management-plugin/
queue-type defaults broke `metricq-manager`'s setup, so this pins to the
3.x series — don't bump this without checking that upstream `metricq`
project has fixed that first.

The source/sink containers run `examples/metricq_source.py` /
`examples/metricq_sink.py` /
[`examples/metricq_durable_sink.py`](../../examples/metricq_durable_sink.py)
from this repo via an **editable install**, so whatever's checked out
locally is what gets tested — rebuild (`docker compose build`) after
changing client code.

`sink-py-durable-dummy` uses `metricq.DurableSink` instead of `metricq.Sink`.
Despite the name, **`DurableSink` does not make the data queue survive
being fully unsubscribed** — in testing, killing either sink for a while and
restarting it lost exactly the same backlog for both; a fresh `sink.subscribe`
RPC gets a fresh queue either way. What `DurableSink` actually buys you is a
*fixed* :term:`Token` (no random UUID suffix) and a `sink.register` RPC
handshake, i.e. a persistent, manageable identity (visible in the wizard,
holds a config document) across restarts — not message durability. Don't
reach for it expecting at-least-once delivery across an outage.

## Quick start

```sh
cd docker/reconnect-lab
docker compose -f docker-compose.singlenode.yml up --build
```

Watch the source/sink logs (`-v DEBUG` is already baked into their
commands):

```sh
./chaos.sh -f docker-compose.singlenode.yml logs source-py-dummy
./chaos.sh -f docker-compose.singlenode.yml logs sink-py-dummy
./chaos.sh -f docker-compose.singlenode.yml logs sink-py-durable-dummy
```

RabbitMQ's management UI is at http://localhost:15672 (admin/admin), CouchDB
at http://localhost:5984/_utils.

For the cluster variant, same idea:

```sh
docker compose -f docker-compose.cluster.yml up --build
```

Management UIs are at :15672 / :15673 / :15674 for node0/1/2 respectively.
Clients connect to the shared `rabbitmq-server` DNS alias, which all three
nodes share on the compose network — Docker's embedded DNS round-robins
across whichever nodes currently have that alias, so a robust reconnect
after a node dies will typically land on a survivor.

## Simulating drops with `chaos.sh`

`chaos.sh` wraps `docker compose`/`docker network`/`rabbitmqctl` primitives
for the failure modes that actually differ in how a client observes them:

| Command | What happens | What the client sees |
|---|---|---|
| `stop <svc>` | graceful container stop | clean AMQP `connection.close`, immediate reconnect |
| `kill <svc>` | `SIGKILL` | TCP just dies, no FIN — client only notices via missed heartbeats |
| `restart <svc>` | stop+start | clean close, brief outage |
| `blip <svc> [s=5]` | stop, wait, start | short full outage |
| `flap <svc> [n=5] [interval=3]` | kill/start loop | repeated abrupt drops — good for checking reconnect backoff doesn't spiral |
| `pause <svc>` / `unpause <svc>` | `SIGSTOP`/`SIGCONT` | TCP stays open but silent — pure heartbeat-timeout path |
| `partition <svc>` / `heal <svc>` | detach/reattach the container's network interface | hardest case: no FIN/RST at all, client hangs until its own timeout |
| `app-stop <node>` / `app-start <node>` (cluster only) | `rabbitmqctl stop_app`/`start_app` | node leaves/rejoins the cluster logically, container & Erlang VM keep running |

Examples:

```sh
# single node: kill the broker for 10s, watch clients recover
./chaos.sh -f docker-compose.singlenode.yml blip rabbitmq-server 10

# cluster: take node1 out of the cluster (not the container) and back in
./chaos.sh -f docker-compose.cluster.yml app-stop rabbitmq-server-node1
./chaos.sh -f docker-compose.cluster.yml app-start rabbitmq-server-node1

# cluster: hard network partition of node0 (the one clients likely connected
# to first), confirm failover to node1/node2
./chaos.sh -f docker-compose.cluster.yml partition rabbitmq-server-node0
./chaos.sh -f docker-compose.cluster.yml logs source-py-dummy
./chaos.sh -f docker-compose.cluster.yml heal rabbitmq-server-node0

# flap the broker to stress-test reconnect backoff
./chaos.sh -f docker-compose.singlenode.yml flap rabbitmq-server 8 2
```

`partition`/`heal` state (which network + aliases a container had) is kept
in `.chaos-state/` next to this README; it's gitignored scratch state, feel
free to delete it.

## Running the predefined scenario set

`run-scenarios.sh` runs a fixed battery of the above through `chaos.sh` and
reports whether source/sink data flow recovered within a scenario-specific
timeout -- a repeatable smoke test rather than a substitute for manually
digging into a specific failure mode. Requires the stack to already be up
and happily exchanging `test.py.dummy` data.

```sh
docker compose -f docker-compose.singlenode.yml up -d --build
./run-scenarios.sh                       # everything applicable
./run-scenarios.sh blip kill              # just a subset
./run-scenarios.sh -f docker-compose.cluster.yml
```

Known: `node_partition_heal` (cluster only) can legitimately never recover
within any timeout -- that's not a runner bug, see the next section.

## Findings: queues, cluster nodes, and network partitions

Classic RabbitMQ queues (what `metricq-manager` declares by default -- no
mirroring/quorum policy is set up in this cluster) live on exactly one node:
whichever node the *declaring* connection happened to be on. Since a sink's
management connection and data connection are independent AMQP connections
that each resolve the shared `rabbitmq-server` DNS alias on their own, they
can (and did, in testing) land on different nodes -- e.g. management on
node2, data (and therefore the data queue) on node0. That's not a problem by
itself: any node in the cluster transparently proxies AMQP operations to
whichever node actually owns a queue, as long as that node is up.

The interesting case is what happens when the node owning the queue dies
while the client was connected to it too (the common case, since a *fresh*
subscribe always creates the queue on the connecting node) and is reachable
by other nodes. Tested via `app-stop` on the node a client's data connection
was on (see `chaos.sh`'s cluster example above): the client's data
connection dies with a clean `CONNECTION_FORCED` close, `aio_pika`
reconnects (DNS lands it on a survivor within its `reconnect_interval`), the
sink resubscribes, and the manager hands back a *fresh* queue on the
surviving node -- recovered in ~5s, no special handling needed.

A **hard network partition** (`chaos.sh partition <rabbitmq-node>` on the
node itself, not just a client) is a much rougher edge, and is worth
testing explicitly if you're debugging reconnect robustness:

- The affected connection doesn't get a FIN/RST -- it just goes silent.
  In testing this took **several minutes** (well beyond one AMQP heartbeat
  interval) before the client noticed anything at all, vs. ~5s for a clean
  stop/kill/`app-stop`. If you're debugging "why didn't it reconnect yet",
  check how long it's actually been -- a partition is not a blip.
- When `_resubscribe()` finally ran, its `sink.subscribe` RPC publish came
  back as a `Basic.Nack` (`aiormq.exceptions.DeliveryError`). Before the fix
  below, that surfaced as an *unhandled exception* rather than being
  retried: `sink-py-dummy` sat fully stuck -- process alive, no data, no
  further resubscribe attempt -- until its container's
  `restart: unless-stopped` eventually cycled it (losing its subscription
  state and, for a plain `Sink`, its identity). `sink-py-durable-dummy`
  happened to recover once the partition healed, but only because its next
  scheduled retry (the underlying connection's own `reconnect_interval`)
  happened to land after the heal, not because the failed resubscribe was
  itself retried.

  **Fixed** in `Sink._resubscribe`
  ([`metricq/sink.py`](../../metricq/sink.py)): a failed `sink.subscribe`
  RPC (or the queue declare/consume after it) is now retried on a short
  delay (`Sink._resubscribe_retry_delay`, default 5s) instead of being
  logged as terminal. See `tests/test_sink.py` for the regression tests
  (retry-until-success, and that a genuine reconnect/cancellation still
  aborts the retry loop cleanly instead of being swallowed).

Reproduce with:

```sh
./chaos.sh -f docker-compose.cluster.yml partition rabbitmq-server-node0
# watch: nothing happens for a while (this is the slow part -- a partition
# is not a blip), then a Nack, then repeated "Resubscribing failed ...,
# retrying in 5 second(s)..." warnings instead of a stall
./chaos.sh -f docker-compose.cluster.yml logs sink-py-dummy
./chaos.sh -f docker-compose.cluster.yml logs sink-py-durable-dummy
./chaos.sh -f docker-compose.cluster.yml heal rabbitmq-server-node0
```

**Still open, and NOT fixed by the above:** `run-scenarios.sh`'s
`node_partition_heal` reproduced this on its own during testing (no special
setup): the sink's *management* connection was on node1, its *data*
connection (and therefore its data queue) on node0. Partitioning node0
killed the queue -- confirmed gone cluster-wide via
`GET /api/queues` -- while the data connection itself never dropped (both
connections kept heartbeating throughout, never closed, never reconnected).
The source kept happily `send()`-ing the whole time. The sink just silently
stopped receiving data, forever, with zero log output indicating anything
was wrong. This is the `Basic.Cancel`-swallowed-by-aiormq gap: unlike the
Nack case above, nothing ever closes or throws, so there's no reconnect
event to hook a retry onto with the current client/channel/queue APIs (see
the design discussion this session -- confirmed unfixed as of aio-pika
10.0.1, not just the `~9.0` pinned here). Only a manual restart of the sink
process clears it (`./chaos.sh -f docker-compose.cluster.yml restart
sink-py-dummy`). A watchdog that tracks time-since-last-message and forces a
reconnect after some threshold is the only viable mitigation given aio_pika
provides no hook for this -- not yet implemented.

## Cleaning up

```sh
docker compose -f docker-compose.singlenode.yml down -v
docker compose -f docker-compose.cluster.yml down -v
```
