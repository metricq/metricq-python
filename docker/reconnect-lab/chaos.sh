#!/usr/bin/env bash
#
# Helper to simulate connection drops / reconnects against the reconnect-lab
# docker-compose stacks. See README.md for the full scenario walkthrough.
#
# Usage:
#   ./chaos.sh [-f <compose-file>] <command> [args...]
#
# Commands:
#   status                          Show container states
#   logs <service>                  Follow logs of one service
#   stop <service>                  Graceful stop (clean AMQP close, TCP FIN)
#   start <service>                 Start a stopped service back up
#   kill <service>                  SIGKILL (abrupt: no FIN/close-ok, client
#                                   only notices via missed heartbeats)
#   restart <service>                docker compose restart (stop+start)
#   blip <service> [seconds=5]      stop, wait, start -- a short outage
#   flap <service> [count=5] [interval=3]
#                                    kill/start in a loop -- flapping link
#   pause <service>                  Freeze the process (SIGSTOP): TCP stays
#                                   open but nothing is read/written, so the
#                                   peer only notices via heartbeat timeout
#   unpause <service>                Resume a paused service
#   partition <service>              Detach the container from the docker
#                                   network entirely (hard network partition,
#                                   no FIN/RST -- client hangs until its own
#                                   timeout fires)
#   heal <service>                   Reattach a partitioned container
#   app-stop <rabbitmq-service>      rabbitmqctl stop_app: node leaves the
#                                   cluster logically but keeps running
#                                   (cluster.yml only)
#   app-start <rabbitmq-service>     rabbitmqctl start_app: node rejoins
#
# Examples:
#   ./chaos.sh -f docker-compose.singlenode.yml blip rabbitmq-server 10
#   ./chaos.sh -f docker-compose.cluster.yml app-stop rabbitmq-server-node1
#   ./chaos.sh -f docker-compose.cluster.yml partition rabbitmq-server-node0

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
COMPOSE_FILE="docker-compose.singlenode.yml"
STATE_DIR="$SCRIPT_DIR/.chaos-state"

while [[ "${1:-}" == "-f" ]]; do
  COMPOSE_FILE="$2"
  shift 2
done

cmd="${1:-}"
[[ $# -gt 0 ]] && shift || true

compose() {
  docker compose -f "$SCRIPT_DIR/$COMPOSE_FILE" "$@"
}

container_id() {
  local service="$1"
  local cid
  cid="$(compose ps -q "$service")"
  if [[ -z "$cid" ]]; then
    echo "No running container for service '$service' (check 'status')" >&2
    exit 1
  fi
  echo "$cid"
}

usage() {
  sed -n '2,40p' "${BASH_SOURCE[0]}" | sed 's/^# \{0,1\}//'
  exit 1
}

case "$cmd" in
  status)
    compose ps
    ;;

  logs)
    compose logs -f --tail=100 "${1:?service name required}"
    ;;

  stop)
    service="${1:?service name required}"
    echo "Gracefully stopping $service..."
    compose stop "$service"
    ;;

  start)
    service="${1:?service name required}"
    echo "Starting $service..."
    compose start "$service"
    ;;

  kill)
    service="${1:?service name required}"
    echo "SIGKILLing $service (abrupt drop, no clean close)..."
    compose kill "$service"
    ;;

  restart)
    service="${1:?service name required}"
    echo "Restarting $service..."
    compose restart "$service"
    ;;

  blip)
    service="${1:?service name required}"
    seconds="${2:-5}"
    echo "Blip: stopping $service for ${seconds}s..."
    compose stop "$service"
    sleep "$seconds"
    compose start "$service"
    echo "$service back up."
    ;;

  flap)
    service="${1:?service name required}"
    count="${2:-5}"
    interval="${3:-3}"
    echo "Flapping $service: $count cycles, ${interval}s apart..."
    for ((i = 1; i <= count; i++)); do
      echo "  [$i/$count] kill"
      compose kill "$service"
      sleep "$interval"
      echo "  [$i/$count] start"
      compose start "$service"
      sleep "$interval"
    done
    ;;

  pause)
    service="${1:?service name required}"
    echo "Pausing $service (SIGSTOP, connection left dangling)..."
    compose pause "$service"
    ;;

  unpause)
    service="${1:?service name required}"
    echo "Unpausing $service..."
    compose unpause "$service"
    ;;

  partition)
    service="${1:?service name required}"
    cid="$(container_id "$service")"
    network="$(docker inspect "$cid" --format '{{range $k, $v := .NetworkSettings.Networks}}{{$k}}{{end}}')"
    aliases="$(docker inspect "$cid" --format '{{range $k, $v := .NetworkSettings.Networks}}{{range $v.Aliases}}{{.}} {{end}}{{end}}')"
    mkdir -p "$STATE_DIR"
    printf '%s\n%s\n' "$network" "$aliases" >"$STATE_DIR/$service.partition"
    echo "Partitioning $service off network '$network' (aliases: $aliases)..."
    docker network disconnect "$network" "$cid"
    echo "Partitioned. Run 'heal $service' to reconnect."
    ;;

  heal)
    service="${1:?service name required}"
    cid="$(container_id "$service")"
    state="$STATE_DIR/$service.partition"
    if [[ ! -f "$state" ]]; then
      echo "No recorded partition state for $service (did you run 'partition $service' first?)" >&2
      exit 1
    fi
    network="$(sed -n '1p' "$state")"
    aliases="$(sed -n '2p' "$state")"
    alias_args=()
    for a in $aliases; do
      alias_args+=(--alias "$a")
    done
    echo "Reattaching $service to network '$network' (aliases: ${aliases:-none})..."
    docker network connect "${alias_args[@]}" "$network" "$cid"
    rm -f "$state"
    echo "Healed."
    ;;

  app-stop)
    service="${1:?rabbitmq service name required}"
    echo "rabbitmqctl stop_app on $service (node leaves cluster, container keeps running)..."
    compose exec "$service" rabbitmqctl stop_app
    ;;

  app-start)
    service="${1:?rabbitmq service name required}"
    echo "rabbitmqctl start_app on $service (node rejoins cluster)..."
    compose exec "$service" rabbitmqctl start_app
    ;;

  *)
    usage
    ;;
esac
