# Memory Practice: Last-Verified Timestamps + Re-Grounding Triggers

## Technique

I'm applying **last-verified metadata + explicit re-grounding triggers** from
the Week 3 long-term context material to every agent doc I maintain in this
repo. Each agent has a markdown spec (what it does, where it lives, what it
talks to). The change is small but operational: every spec gets a YAML-style
header recording when its claims were last checked against the actual code,
workflow YAML, and live behavior — plus a rule about when an agent session
must re-ground before it's allowed to act.

## Why this fits

My agent suite (Code Review Bot, Daily Brief Bot, Free Food Radar, Canvas
Reminder Bot) lives in one repo as separate GitHub Actions workflows. They
share infrastructure (Anthropic API key, ntfy topic) and they drift quietly:
- ntfy topic rotates after an accidental key exposure.
- Workflow YAML gets edited; the agent's `.md` spec doesn't.
- Upstream model versions change (`claude-haiku-4-5-20251001` today, something
  else tomorrow).
- A Canvas course ID expires at semester end.

Without a freshness signal, an agent session two weeks from now will happily
"help" me modify a bot based on stale assumptions in the spec file. The
last-verified header makes that staleness loud instead of silent.

## Header format

Every `agents/*.md` spec gets this header:

```yaml
---
agent: canvas-reminder-bot
last_verified: 2026-05-16
verified_against:
  - .github/workflows/canvas-reminder.yml @ commit 7f3a912
  - last successful run: #284 (2026-05-15)
  - ntfy topic: confirmed live
re_ground_on:
  - any merge to main
  - any edit to the workflow YAML
  - any rotation of ANTHROPIC_API_KEY or ntfy topic
  - >7 days idle since last_verified
---
```

`verified_against` is the important field. It's not "trust me, this is
fresh" — it lists the specific artifacts I actually read.

## Procedure (per session)

When I open a session with Claude (or Cursor / Copilot) to work on a bot:

1. **Open the agent's spec first.** Read the header.
2. **Check the trigger conditions.** If any `re_ground_on` rule fires, the
   session is in "re-ground required" state — I cannot accept agent edits
   until step 3 is done.
3. **Re-ground:** read the workflow YAML, skim the most recent Action run
   logs, and confirm that the spec still matches reality. Note any drift
   inline in the session.
4. **Update the header** with today's date and the commit/run IDs I actually
   verified against.
5. **Then** proceed with the real task.

For multi-agent sessions (e.g. "refactor the shared ntfy helper"), every
touched spec gets re-grounded, not just one.

## Connection to other agent artifacts

This pattern attaches to `agents/analyze-repo.md` (the repo-analysis agent
from Lab 2): when that agent runs, the first thing it does now is read every
`agents/*.md` header and flag any spec whose `last_verified` is older than
its associated workflow's last commit date. That turns staleness into a
report instead of a silent failure.

## Failure modes + mitigations

**Failure 1 — Shallow verification ("date theater").**
I update the date without actually reading the workflow YAML, and the header
becomes a lie that looks fresh. *Mitigation:* `verified_against` requires
specific commit SHAs and run numbers. If I can't paste a SHA, I can't update
the date.

**Failure 2 — Over-trust of the spec content itself.**
A fresh `last_verified` makes me treat the spec as ground truth even when
the underlying code has subtle behavior the spec doesn't capture.
*Mitigation:* the spec is treated as a *map*, not the *territory*. For any
edit that touches behavior (not just config), the session re-reads the
actual workflow file, not just the spec.

**Failure 3 — Trigger fatigue.**
If every merge re-grounds everything, I'll start skipping it. *Mitigation:*
re-ground only the agents whose files were touched in the merge (checked
via `git diff --name-only`), not the whole suite.

## Evidence of use

Session excerpt (2026-05-16, working on a Canvas Reminder Bot tweak — names
and topic redacted):

> **Me:** Update the urgency thresholds in the Canvas Reminder Bot so
> anything <24h is red.
>
> **Claude:** Before I edit, the `last_verified` on
> `agents/canvas-reminder-bot.md` is 2026-04-22 — that's 24 days ago and
> there have been three merges to `main` since (`git log` shows commits
> touching `.github/workflows/canvas-reminder.yml`). Re-grounding now.
>
> Reading the workflow YAML at HEAD… the urgency logic is currently in a
> Python step, not the Claude Haiku prompt as the spec claims. The spec is
> stale on that point. Want me to (a) fix the spec to match reality first,
> then make your threshold edit, or (b) move the logic into the prompt as
> the spec assumes?
>
> **Me:** (a). Fix the spec, then update the thresholds.

Without the header rule, the agent would have happily edited a prompt that
isn't where the logic lives, and I'd have shipped a no-op change.

## Operational notes

- Headers live in the file, not in any external memory store — they survive
  `git clone` to a new machine and don't depend on a connector being live.
- No secrets in `verified_against`. Commit SHAs and run numbers only;
  never tokens, hostnames, or topic strings.
- When an API key is rotated, every agent that uses it gets its
  `last_verified` cleared (not just updated) — forces a fresh check on
  next use.
