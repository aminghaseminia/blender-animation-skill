#!/usr/bin/env bash
# Install the Blender Animation Skills pack into an agent's skills directory.
#
# Usage:
#   ./install.sh                         # auto-detect target
#   ./install.sh --target DIR            # install every skill into DIR
#   ./install.sh --target DIR blender-animation motion-design
#   ./install.sh --list                  # show bundled skills and target
#   ./install.sh --force                 # overwrite existing skill folders
#
# Notes:
#   - Skills are installed as sibling directories; motion-studio references
#     the others by relative path, so install the full pack unless you have a reason.
#   - Existing folders are skipped unless --force is given.

set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILLS_DIR="$ROOT/skills"
TARGET=""
FORCE=0
SELECTED=()

usage() {
  sed -n '2,18p' "$0" | sed 's/^# \{0,1\}//'
  echo
  echo "Available skills:"
  list_skills | sed 's/^/  - /'
}

list_skills() {
  for d in "$SKILLS_DIR"/*/; do
    [ -f "$d/SKILL.md" ] && basename "$d"
  done
}

detect_target() {
  local candidates=(
    "$HOME/.config/opencode/skills"
    "$HOME/.claude/skills"
    "$HOME/.agents/skills"
  )
  # Prefer an agent config that already exists.
  for c in "${candidates[@]}"; do
    if [ -d "$(dirname "$c")" ]; then
      echo "$c"
      return
    fi
  done
  echo "$HOME/.agents/skills"
}

while [ $# -gt 0 ]; do
  case "$1" in
    --target|-t) TARGET="${2:?missing directory}"; shift 2 ;;
    --force|-f) FORCE=1; shift ;;
    --list|-l) echo "source: $SKILLS_DIR"; echo "target: ${TARGET:-$(detect_target)}"; echo; list_skills; exit 0 ;;
    --help|-h) usage; exit 0 ;;
    -*) echo "unknown option: $1" >&2; usage; exit 1 ;;
    *) SELECTED+=("$1"); shift ;;
  esac
done

TARGET="${TARGET:-$(detect_target)}"
mkdir -p "$TARGET"

if [ ${#SELECTED[@]} -eq 0 ]; then
  while IFS= read -r s; do SELECTED+=("$s"); done < <(list_skills)
fi

echo "Installing ${#SELECTED[@]} skill(s) into $TARGET"
INSTALLED=0
SKIPPED=0

for name in "${SELECTED[@]}"; do
  src="$SKILLS_DIR/$name"
  if [ ! -f "$src/SKILL.md" ]; then
    echo "  ! unknown skill: $name" >&2
    SKIPPED=$((SKIPPED + 1))
    continue
  fi

  dest="$TARGET/$name"
  if [ -e "$dest" ] && [ "$FORCE" -ne 1 ]; then
    echo "  = exists, skipped: $name (use --force to replace)"
    SKIPPED=$((SKIPPED + 1))
    continue
  fi

  rm -rf "$dest"
  cp -R "$src" "$dest"
  # make helper scripts executable
  find "$dest" -type f \( -name '*.sh' -o -name '*.py' \) -exec chmod +x {} + 2>/dev/null || true
  echo "  + $name"
  INSTALLED=$((INSTALLED + 1))
done

echo
echo "Done: $INSTALLED installed, $SKIPPED skipped."
echo "Restart your agent (or start a new session), then try:"
echo '  "Use blender-animation. Create a 6-second turntable of a glossy abstract shape."'
if [ "$SKIPPED" -gt 0 ]; then
  echo
  echo "Existing skills were left untouched. Re-run with --force to replace them."
fi
