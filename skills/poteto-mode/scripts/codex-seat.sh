#!/usr/bin/env bash
# Run one Codex seat and print its final message, or CODEX_SEAT_LOST.
# Usage: codex-seat.sh <read-only|workspace-write> <dir> <effort|-> <prompt-file> <out-file>
# Run it with Bash run_in_background: true. CODEX_SEAT_TIMEOUT (seconds, default 1500) caps the run.
set -uo pipefail

sandbox=$1 dir=$2 effort=$3 prompt=$4 out=$5
cap=${CODEX_SEAT_TIMEOUT:-1500}

if ! command -v codex >/dev/null; then
	echo "CODEX_SEAT_LOST: codex CLI not installed"
	exit 0
fi

effort_args=()
[ "$effort" != "-" ] && effort_args=(-c "model_reasoning_effort=${effort/max/xhigh}")

rm -f "$out"
log="$out.log"
codex exec -s "$sandbox" -C "$dir" -o "$out" "${effort_args[@]}" "$(cat "$prompt")" >"$log" 2>&1 &
pid=$!

# Codex writes -o once, at the end. It can linger after that, so stop on the file, not the exit.
waited=0
while [ ! -s "$out" ] && kill -0 "$pid" 2>/dev/null && [ "$waited" -lt "$cap" ]; do
	sleep 5
	waited=$((waited + 5))
done
[ -s "$out" ] && sleep 3
kill "$pid" 2>/dev/null

if [ -s "$out" ]; then
	cat "$out"; echo
else
	echo "CODEX_SEAT_LOST: no output after ${waited}s. Last log lines:"
	tail -5 "$log"
fi
