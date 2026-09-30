#!/usr/bin/env bash
# Student helper pack installer (folder name: student-pack; markers keep "starter pack"). Students never run this by hand: they paste one
# line into Claude Code and Claude runs it. Works in macOS bash 3.2 and Git Bash
# on Windows (the shell Claude Code uses there). Needs only bash, curl, grep, awk.
# Never touches settings.json. Safe to run again.
# Everything is inside main() so a cut-off download never runs half a script.

main() {
  set -u
  local PACK_BASE="${PACK_BASE:-https://raw.githubusercontent.com/Coach-Foundation/claude-code-best-practices/student-v1/student-pack}"
  local HOME_DIR="$HOME"
  # Claude Code on Windows reads %USERPROFILE%\.claude, which can differ from Git Bash's HOME
  if [ -n "${USERPROFILE:-}" ] && command -v cygpath >/dev/null 2>&1; then
    HOME_DIR="$(cygpath -u "$USERPROFILE")"
  fi
  local CLAUDE_DIR="$HOME_DIR/.claude"
  local CLAUDE_MD="$CLAUDE_DIR/CLAUDE.md"
  local START='<!-- >>> starter pack >>> -->'
  local END='<!-- <<< starter pack <<< -->'
  local WRITE_FAIL="Nothing more was installed: I could not save files in $CLAUDE_DIR. Copy this message and ask Claude for help."

  fail() { echo "$1"; exit 1; }

  # The hackathon rules block tells Claude to write only inside the project folder,
  # so the student must run the hackathon page's "Set up Claude Code with your own account" step first.
  if [ -f "$CLAUDE_MD" ] && grep -qF '<!-- >>> hackathon rules >>> -->' "$CLAUDE_MD"; then
    fail "Please do the step \"Set up Claude Code with your own account\" first. Then paste the helper pack line again."
  fi

  # A start marker without its end marker means the student edited the block: touch nothing.
  if [ -f "$CLAUDE_MD" ] && grep -qF "$START" "$CLAUDE_MD" && ! grep -qF "$END" "$CLAUDE_MD"; then
    fail "Nothing was installed: the helper pack lines in ~/.claude/CLAUDE.md were changed. Ask Claude to delete them, then paste the helper pack line again."
  fi

  command -v curl >/dev/null 2>&1 || fail "Nothing was installed: the curl command is missing on this computer."

  # Global (not local): the EXIT trap runs after main() returns
  STARTER_TMP="$(mktemp -d 2>/dev/null)" || STARTER_TMP=""
  [ -n "$STARTER_TMP" ] || { STARTER_TMP="$CLAUDE_DIR/.starter-pack-tmp"; mkdir -p "$STARTER_TMP" || fail "$WRITE_FAIL"; }
  trap 'rm -rf "$STARTER_TMP"' EXIT
  local tmp="$STARTER_TMP"

  # Download everything first, so a network error changes nothing.
  local f
  for f in skills/handoff/SKILL.md skills/grill-me/SKILL.md claude-md-lines.md; do
    mkdir -p "$tmp/$(dirname "$f")" || fail "$WRITE_FAIL"
    curl -fsSL "$PACK_BASE/$f" -o "$tmp/$f"
    case $? in
      0) ;;
      22) fail "Nothing was installed: the pack address was not found." ;;
      *) fail "Nothing was installed: could not download the pack. Check your internet and try again." ;;
    esac
    grep -qE 'starter[- ]pack' "$tmp/$f" || fail "Nothing was installed: the downloaded file looks wrong ($f)."
  done

  local skipped="" s dest
  for s in handoff grill-me; do
    dest="$CLAUDE_DIR/skills/$s/SKILL.md"
    # Keep a skill the student made themselves; only replace our own copy.
    if [ -e "$dest" ] && ! grep -qF "starter-pack" "$dest"; then
      skipped="$skipped $s"
      continue
    fi
    mkdir -p "$CLAUDE_DIR/skills/$s" && cp "$tmp/skills/$s/SKILL.md" "$dest" || fail "$WRITE_FAIL"
  done

  if [ -f "$CLAUDE_MD" ] && grep -qF "$START" "$CLAUDE_MD"; then
    # Already there (older or same version): replace only the lines between the markers.
    awk -v s="$START" -v e="$END" -v f="$tmp/claude-md-lines.md" '
      { t=$0; sub(/\r$/, "", t) }
      t==s { while ((getline l < f) > 0) print l; skip=1; next }
      t==e { skip=0; next }
      !skip { print }
    ' "$CLAUDE_MD" > "$CLAUDE_MD.tmp" && mv "$CLAUDE_MD.tmp" "$CLAUDE_MD" || fail "$WRITE_FAIL"
  else
    # First install: add the lines at the end, keeping everything already there.
    mkdir -p "$CLAUDE_DIR" || fail "$WRITE_FAIL"
    [ -e "$CLAUDE_MD" ] && [ ! -f "$CLAUDE_MD" ] && fail "$WRITE_FAIL"
    if [ -s "$CLAUDE_MD" ]; then
      { [ -z "$(tail -c1 "$CLAUDE_MD")" ] || echo ""; echo ""; } >> "$CLAUDE_MD" || fail "$WRITE_FAIL"
    fi
    cat "$tmp/claude-md-lines.md" >> "$CLAUDE_MD" || fail "$WRITE_FAIL"
  fi

  local msg="Done. Helper pack installed."
  [ -n "$skipped" ] && msg="$msg You already had your own:$skipped, so I kept yours."
  echo "$msg Close Claude Code and open it again. Then type: grill me"
}

main "$@"
