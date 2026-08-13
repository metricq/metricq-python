#!/usr/bin/env bash
#
# Runs a predefined set of chaos.sh scenarios against an already-running
# reconnect-lab stack and reports whether source/sink data flow recovered
# within a scenario-appropriate timeout. A smoke test for reconnect
# robustness, not a substitute for manually digging into a specific failure
# mode (see README.md for that).
#
# Usage:
#   ./run-scenarios.sh [-f <compose-file>] [scenario...]
#
# With no scenario names, runs everything applicable to the given compose
# file (broker scenarios always; cluster-node scenarios only against
# docker-compose.cluster.yml). Pass one or more names to run a subset.
#
# Requires the stack to already be up (docker compose ... up -d --build) and
# source-py-dummy/sink-py-dummy (and sink-py-durable-dummy, if present) to be
# happily exchanging test.py.dummy data already -- this only measures how
# long it takes to *recover* from each disruption, it doesn't set the stack
# up for you.
#
# Exit code is non-zero if any scenario failed to recover in time.

set -uo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
COMPOSE_FILE="docker-compose.singlenode.yml"

while [[ "${1:-}" == "-f" ]]; do
  COMPOSE_FILE="$2"
  shift 2
done

CHAOS="$SCRIPT_DIR/chaos.sh"

chaos() {
  "$CHAOS" -f "$COMPOSE_FILE" "$@"
}

compose() {
  docker compose -f "$SCRIPT_DIR/$COMPOSE_FILE" "$@"
}

# Sink services to watch for recovery. sink-py-durable-dummy only exists if
# the compose file declares it; check rather than hardcode.
sink_services() {
  compose config --services 2>/dev/null | grep -E '^sink-py-(dummy|durable-dummy)$'
}

is_cluster() {
  compose config --services 2>/dev/null | grep -qx "rabbitmq-server-node0"
}

now_marker() {
  # RFC3339 with an explicit "Z" -- without it, docker interprets the
  # (already UTC) timestamp as local time, silently shifting the window.
  date -u +%Y-%m-%dT%H:%M:%SZ
}

# Poll every service in sink_services() for a fresh "test.py.dummy:" log line
# after $marker, up to $timeout seconds. Echoes elapsed seconds on success,
# returns 1 on timeout.
wait_for_recovery() {
  local marker="$1" timeout="$2"
  local start elapsed services svc all_recovered
  start="$(date +%s)"
  services=$(sink_services)

  while true; do
    all_recovered=true
    for svc in $services; do
      # Capture into a variable rather than piping straight into `grep -q`:
      # grep -q exits on the first match while `compose logs` is still
      # writing, the resulting SIGPIPE makes `compose logs` exit non-zero,
      # and with `pipefail` that flips this whole check to "not recovered"
      # even though the match was right there.
      svc_logs="$(compose logs --since "$marker" "$svc" 2>&1)"
      if ! grep -q "test\.py\.dummy:" <<<"$svc_logs"; then
        all_recovered=false
        break
      fi
    done
    elapsed=$(($(date +%s) - start))
    if $all_recovered; then
      echo "$elapsed"
      return 0
    fi
    if ((elapsed >= timeout)); then
      return 1
    fi
    sleep 2
  done
}

RESULTS_NAMES=()
RESULTS_STATUS=()
RESULTS_TIME=()

run_scenario() {
  local name="$1" timeout="$2"
  shift 2
  local marker elapsed

  echo
  echo "=== $name ==="
  marker="$(now_marker)"

  # Remaining args are the disruption itself, e.g. "blip rabbitmq-server 8".
  "$@"

  echo "Waiting up to ${timeout}s for data flow to recover..."
  if elapsed="$(wait_for_recovery "$marker" "$timeout")"; then
    echo "PASS: recovered in ${elapsed}s"
    RESULTS_NAMES+=("$name")
    RESULTS_STATUS+=("PASS")
    RESULTS_TIME+=("${elapsed}s")
  else
    echo "FAIL: no recovery within ${timeout}s"
    RESULTS_NAMES+=("$name")
    RESULTS_STATUS+=("FAIL")
    RESULTS_TIME+=(">${timeout}s")
  fi
}

scenario_blip() {
  run_scenario "blip" 60 chaos blip rabbitmq-server 8
}

scenario_kill() {
  # NOTE: docker (compose) kill counts as an intentional stop, same as
  # `stop` -- `restart: unless-stopped` only kicks in for a container that
  # crashes on its own, so it does NOT bring this back automatically. Start
  # it back up explicitly, same as flap does internally.
  run_scenario "kill" 60 bash -c "
    '$CHAOS' -f '$COMPOSE_FILE' kill rabbitmq-server
    sleep 2
    '$CHAOS' -f '$COMPOSE_FILE' start rabbitmq-server
  "
}

scenario_pause_unpause() {
  run_scenario "pause_unpause" 240 bash -c "
    '$CHAOS' -f '$COMPOSE_FILE' pause rabbitmq-server
    sleep 10
    '$CHAOS' -f '$COMPOSE_FILE' unpause rabbitmq-server
  "
}

scenario_flap() {
  run_scenario "flap" 60 chaos flap rabbitmq-server 3 2
}

scenario_partition_heal() {
  # Only held for a short observation window here -- see README.md for the
  # multi-minute detection-latency deep dive on a real hard partition.
  run_scenario "partition_heal" 60 bash -c "
    '$CHAOS' -f '$COMPOSE_FILE' partition rabbitmq-server
    sleep 15
    '$CHAOS' -f '$COMPOSE_FILE' heal rabbitmq-server
  "
}

scenario_app_stop_start() {
  run_scenario "app_stop_start" 30 bash -c "
    '$CHAOS' -f '$COMPOSE_FILE' app-stop rabbitmq-server-node0
    sleep 5
    '$CHAOS' -f '$COMPOSE_FILE' app-start rabbitmq-server-node0
  "
}

scenario_node_partition_heal() {
  # KNOWN to sometimes not recover at all within any timeout: if a sink's
  # data queue happened to live on the partitioned node while its own
  # connection survived on a different (healthy) one, RabbitMQ's Basic.Cancel
  # for the now-gone queue is silently swallowed by aio_pika/aiormq -- no
  # exception, no reconnect, nothing. The sink sits there with a perfectly
  # healthy, heartbeating connection and just never receives data again.
  # Only a manual restart of the sink clears it. See README.md ("queues,
  # cluster nodes, and network partitions") for the full writeup -- this
  # isn't a runner bug, it's the actual gap that section documents.
  run_scenario "node_partition_heal" 120 bash -c "
    '$CHAOS' -f '$COMPOSE_FILE' partition rabbitmq-server-node0
    sleep 15
    '$CHAOS' -f '$COMPOSE_FILE' heal rabbitmq-server-node0
  "
}

ALL_BROKER_SCENARIOS=(blip kill pause_unpause flap partition_heal)
ALL_CLUSTER_SCENARIOS=(app_stop_start node_partition_heal)

requested=("$@")
if [[ ${#requested[@]} -eq 0 ]]; then
  requested=("${ALL_BROKER_SCENARIOS[@]}")
  if is_cluster; then
    requested+=("${ALL_CLUSTER_SCENARIOS[@]}")
  fi
fi

for name in "${requested[@]}"; do
  case "$name" in
    blip) scenario_blip ;;
    kill) scenario_kill ;;
    pause_unpause) scenario_pause_unpause ;;
    flap) scenario_flap ;;
    partition_heal) scenario_partition_heal ;;
    app_stop_start)
      is_cluster || {
        echo "Skipping $name: not a cluster compose file" >&2
        continue
      }
      scenario_app_stop_start
      ;;
    node_partition_heal)
      is_cluster || {
        echo "Skipping $name: not a cluster compose file" >&2
        continue
      }
      scenario_node_partition_heal
      ;;
    *)
      echo "Unknown scenario: $name" >&2
      echo "Known: ${ALL_BROKER_SCENARIOS[*]} ${ALL_CLUSTER_SCENARIOS[*]}" >&2
      exit 1
      ;;
  esac
done

echo
echo "=== Summary ==="
failed=0
for i in "${!RESULTS_NAMES[@]}"; do
  printf '%-20s %-6s %s\n' "${RESULTS_NAMES[$i]}" "${RESULTS_STATUS[$i]}" "${RESULTS_TIME[$i]}"
  [[ "${RESULTS_STATUS[$i]}" == "FAIL" ]] && failed=1
done

exit "$failed"
