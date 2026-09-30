#!/usr/bin/env bash
# Removes the student helper pack (folder name: student-pack). Deletes only files the pack installed and the
# lines between its markers in ~/.claude/CLAUDE.md. Safe to run again.
# Everything is inside main() so a cut-off download never runs half a script.

main() {
  set -u
  local HOME_DIR="$HOME"
  if [ -n "${USERPROFILE:-}" ] && command -v cygpath >/dev/null 2>&1; then
    HOME_DIR="$(cygpath -u "$USERPROFILE")"
  fi
  local CLAUDE_DIR="$HOME_DIR/.claude"
  local CLAUDE_MD="$CLAUDE_DIR/CLAUDE.md"
  local START='<!-- >>> starter pack >>> -->'
  local END='<!-- <<< starter pack <<< -->'
  local BACKUP="$CLAUDE_MD.before-starter-pack-removal"

  fail() { echo "$1"; exit 1; }

  local s f
  for s in handoff grill-me; do
    f="$CLAUDE_DIR/skills/$s/SKILL.md"
    if [ -f "$f" ] && grep -qF "starter-pack" "$f"; then
      rm -f "$f" || fail "Nothing more was removed: I could not delete $f."
      rmdir "$CLAUDE_DIR/skills/$s" 2>/dev/null || true
    fi
  done
  rmdir "$CLAUDE_DIR/skills" 2>/dev/null || true   # only if now empty

  if [ -f "$CLAUDE_MD" ] && grep -qF "$START" "$CLAUDE_MD"; then
    # Only cut when the end marker is there too, or we could delete the student's own text
    grep -qF "$END" "$CLAUDE_MD" || fail "The skills were removed, but I left your CLAUDE.md alone because its helper pack lines were changed. Ask Claude to delete the helper pack lines from ~/.claude/CLAUDE.md."
    [ -e "$BACKUP" ] || cp "$CLAUDE_MD" "$BACKUP" || fail "Nothing was changed in CLAUDE.md: I could not make a backup."
    # Compare lines without a Windows \r, and drop the blank line install.sh added before the block
    awk -v s="$START" -v e="$END" '
      { t=$0; sub(/\r$/, "", t) }
      t==s { skip=1; if (n>0 && lines[n] ~ /^\r?$/) n--; next }
      t==e { skip=0; next }
      !skip { lines[++n]=$0 }
      END { while (n>0 && lines[n] ~ /^\r?$/) n--; for (i=1;i<=n;i++) print lines[i] }
    ' "$CLAUDE_MD" > "$CLAUDE_MD.tmp" && mv "$CLAUDE_MD.tmp" "$CLAUDE_MD" || fail "Nothing was changed in CLAUDE.md: I could not save it."
    grep -qF "$START" "$CLAUDE_MD" && fail "I could not remove the helper pack lines from ~/.claude/CLAUDE.md. Ask Claude to delete them."
    # Delete the file if only blank lines are left
    grep -q '[^[:space:]]' "$CLAUDE_MD" || rm -f "$CLAUDE_MD"
  fi

  echo "Done. Helper pack removed. Close Claude Code and open it again."
}

main "$@"
