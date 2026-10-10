#!/usr/bin/env bash
# Re-port the latest upstream pstack into this checkout. Review `git diff` after.
set -euo pipefail

root="$(cd "$(dirname "$0")/.." && pwd)"
tmp="$(mktemp -d)"
trap 'rm -rf "$tmp"' EXIT

git clone -q --depth 1 --filter=blob:none --sparse https://github.com/cursor/plugins.git "$tmp/src"
git -C "$tmp/src" sparse-checkout set pstack
up="$tmp/src/pstack"

# Files this port owns outright.
keep=(skills/setup-pstack/SKILL.md skills/poteto-mode/references/claude-code-runtime.md skills/poteto-mode/scripts/codex-seat.sh)
for f in "${keep[@]}"; do cp "$root/$f" "$tmp/$(echo "$f" | tr / _)"; done

rsync -a --delete --exclude make-bot-ui "$up/skills/" "$root/skills/"
rsync -a --delete "$up/agents/" "$root/agents/"
rsync -a --delete "$up/docs/" "$root/docs/"

for f in "${keep[@]}"; do cp "$tmp/$(echo "$f" | tr / _)" "$root/$f"; done

python3 "$root/port/port.py" "$root"
python3 "$root/port/hand_edits.py" "$root"

echo "upstream version: $(python3 -c "import json;print(json.load(open('$up/.cursor-plugin/plugin.json'))['version'])")"
echo "Leftover Cursor references (review each):"
grep -rnE '\.cursor|[Cc]ursor|grok|`Task`' "$root/skills" "$root/agents" | grep -v '/scripts/\|claude-code-runtime' || true
