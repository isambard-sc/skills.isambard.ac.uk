#!/usr/bin/env bash
# Weekly docs -> skills sync, run locally (by hand, cron or launchd).
#
#  1. Refreshes snapshots/ (snapshot_docs.py) in a temporary worktree of
#     origin/main, so your own checkout is never touched.
#  2. If no cited docs page changed, stops there.
#  3. Otherwise commits the refreshed snapshots and runs Claude Code headless
#     to apply Workflow B of .github/agents/update-skills-from-docs.md to the
#     affected skills, one commit per skill.
#  4. Pushes a docs-sync/<date> branch and opens a draft PR containing the
#     snapshot diff, the skill updates and Claude's summary. Never merges.
#
# Needs: git, gh (logged in), claude (logged in), and python3 with PyYAML or uv.
#
# Usage, from anywhere in a skills.isambard.ac.uk checkout:
#   .github/workflows/scripts/docs_sync.sh            # full run
#   .github/workflows/scripts/docs_sync.sh --dry-run  # snapshot report only
#
# DOCS_SYNC_BASE=origin/<branch> runs against another branch (for testing);
# the PR still targets main.
#
# Example crontab entry (Mondays 09:00):
#   0 9 * * 1 /path/to/skills.isambard.ac.uk/.github/workflows/scripts/docs_sync.sh >> "$HOME/docs-sync.log" 2>&1

set -euo pipefail

dry_run=false
[ "${1:-}" = "--dry-run" ] && dry_run=true

repo=$(git -C "$(dirname "$0")" rev-parse --show-toplevel)
date=$(date +%Y-%m-%d)
branch="docs-sync/$date"
tmp=$(mktemp -d)
work="$tmp/skills"

cleanup() {
  git -C "$repo" worktree remove --force "$work" 2>/dev/null || true
  git -C "$repo" branch -D "$branch" >/dev/null 2>&1 || true
  rm -rf "$tmp"
}
trap cleanup EXIT

if python3 -c "import yaml" 2>/dev/null; then
  py="python3"
else
  py="uv run --quiet --no-project --with pyyaml python"
fi

base=${DOCS_SYNC_BASE:-origin/main}
git -C "$repo" fetch --quiet origin
if git -C "$repo" ls-remote --exit-code --heads origin "$branch" >/dev/null; then
  echo "$branch already exists on origin; nothing to do."
  exit 0
fi
git -C "$repo" worktree add --quiet -b "$branch" "$work" "$base"
cd "$work"

$py .github/workflows/scripts/snapshot_docs.py --report "$tmp/report.md"

if [ -z "$(git status --porcelain -- snapshots)" ]; then
  echo "No docs changes; nothing to do."
  exit 0
fi
if $dry_run; then
  git add --intent-to-add snapshots
  git diff --stat -- snapshots
  exit 0
fi

git add snapshots
git commit --quiet -m "chore(snapshots): refresh docs snapshots ($date)"

prompt=$(cat <<EOF
The snapshots of docs.isambard.ac.uk pages in snapshots/ have just been
refreshed. The last commit (git show HEAD) is exactly what changed in the docs
since the skills were last checked. This is the refresh report:

$(cat "$tmp/report.md")

For each skill citing a changed page, follow Workflow B in
.github/agents/update-skills-from-docs.md, using the snapshot diff as the record
of what changed in place of fetching the pages. Change only what the diff makes
necessary; prose rewording needs no update. For a page listed as new, compare
the skills citing it against the whole snapshot. Removed snapshots need no
action. Follow AGENTS.md, run its validation commands (use \`$py\` for
python3) and fix any failures.

Commit each skill's update separately, with a message like
"fix(<skill>): sync with docs change to <page>". Do not edit snapshots/, push,
or open pull requests.

Finish with a Markdown summary for the pull request description and nothing
else: for each changed page, what changed in the docs, and for each affected
skill, what you changed or why no change was needed.
EOF
)

claude -p "$prompt" \
  --max-turns 80 \
  --allowedTools \
    "Read" "Edit" "Write" "Glob" "Grep" \
    "Bash(git show *)" "Bash(git diff *)" "Bash(git log *)" "Bash(git status *)" \
    "Bash(git add *)" "Bash(git commit *)" \
    "Bash($py .github/workflows/scripts/*)" \
    "WebFetch(domain:docs.isambard.ac.uk)" \
  > "$tmp/summary.md"

{
  cat "$tmp/report.md"
  echo
  echo "## Skill updates"
  echo
  cat "$tmp/summary.md"
  echo
  echo "---"
  echo "Opened by \`.github/workflows/scripts/docs_sync.sh\`. Review the snapshot"
  echo "diff against the skill changes before merging; merging records the new"
  echo "snapshots as the baseline."
  echo
  echo "🤖 Generated with [Claude Code](https://claude.com/claude-code)"
} > "$tmp/body.md"

git push --quiet --set-upstream origin "$branch"
gh pr create --draft --base main --head "$branch" \
  --title "chore: sync skills with docs changes ($date)" \
  --body-file "$tmp/body.md"
