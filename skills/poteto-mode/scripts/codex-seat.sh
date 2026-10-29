#!/usr/bin/env bash
# Run one Codex seat and print its final message, or a line starting CODEX_SEAT_LOST.
# Usage: codex-seat.sh <read-only|workspace-write> <dir> <effort|-> <prompt-file> <out-file>
# Run it with Bash run_in_background: true and timeout: 600000.
# CODEX_SEAT_TIMEOUT (seconds, default 540) caps the run; keep it under the Bash timeout.
set -uo pipefail

sandbox=$1 dir=$2 effort=$3 prompt=$4 out=$5
cap=${CODEX_SEAT_TIMEOUT:-540}
log="$out.log"
pid=""

lost() {
	echo "CODEX_SEAT_LOST: $1"
	[ -f "$log" ] && tail -5 "$log"
}

stop_codex() {
	[ -n "$pid" ] || return 0
	pkill -TERM -P "$pid" 2>/dev/null
	kill -TERM "$pid" 2>/dev/null
	for _ in 1 2 3 4 5; do kill -0 "$pid" 2>/dev/null || return 0; sleep 1; done
	pkill -KILL -P "$pid" 2>/dev/null
	kill -KILL "$pid" 2>/dev/null
}

trap 'stop_codex; lost "interrupted"; exit 0' INT TERM HUP

case "$sandbox" in
	read-only | workspace-write) ;;
	*) lost "sandbox must be read-only or workspace-write, got '$sandbox'"; exit 0 ;;
esac
command -v codex >/dev/null || { lost "codex CLI not installed"; exit 0; }

effort_args=()
[ "$effort" != "-" ] && effort_args=(-c "model_reasoning_effort=${effort/max/xhigh}")

rm -f "$out"
# Written this way because macOS bash 3.2 rejects an empty "${a[@]}" under set -u.
codex exec --skip-git-repo-check -s "$sandbox" -C "$dir" -o "$out" ${effort_args[@]+"${effort_args[@]}"} - <"$prompt" >"$log" 2>&1 &
pid=$!

# Codex writes -o once, at the end. It can linger after that, so stop on the file, not the exit.
waited=0
while [ ! -s "$out" ] && kill -0 "$pid" 2>/dev/null && [ "$waited" -lt "$cap" ]; do
	sleep 5
	waited=$((waited + 5))
done
[ -s "$out" ] && sleep 3
stop_codex

if [ -s "$out" ]; then
	cat "$out"
	echo
	rm -f "$log"
else
	lost "no output after ${waited}s"
fi
