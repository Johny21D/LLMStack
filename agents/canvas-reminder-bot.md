---
agent: canvas-reminder-bot
last_verified: TODO_FILL_DATE_AFTER_VERIFY
verified_against:
  - repo: Canvas-Reminder- (private)
  - workflow: .github/workflows/<FILENAME>.yml @ commit <SHA>
  - last successful run: #<RUN_NUMBER>
  - script: canvas_reminder.py @ commit <SHA>
  - model: claude-haiku-4-5-20251001
re_ground_on:
  - any merge to main on Canvas-Reminder-
  - any edit to canvas_reminder.py or its workflow YAML
  - rotation of ANTHROPIC_API_KEY, CANVAS_ACCESS_TOKEN, or the ntfy topic
  - any change to state.json schema
  - >7 days idle since last_verified
---

# Canvas Reminder Bot

## What it does

Pulls upcoming assignments from Canvas, asks Claude Haiku to estimate time
required and suggest a "start tonight" recommendation, and pushes a grouped
notification to my phone and laptop via ntfy. Runs on a cron schedule from
GitHub Actions — free tier.

## Where it lives

- Repo: `Canvas-Reminder-` (private)
- Script: `canvas_reminder.py`
- Workflow: `.github/workflows/<FILL_IN>.yml`
- State: `state.json` (committed back to the repo by the bot to deduplicate
  notifications across runs)

## Trigger

- Cron schedule: `<FILL_IN_FROM_WORKFLOW>` (e.g. every 6h per README)
- Manual: workflow_dispatch enabled / disabled — `<CONFIRM>`

## Inputs / secrets (names only, never values)

- `ANTHROPIC_API_KEY` — repo secret
- `CANVAS_ACCESS_TOKEN` — repo secret
- `CANVAS_BASE_URL` — repo secret or env (BYU-I instance)
- `NTFY_TOPIC` — repo secret (treat as confidential — topic IS the auth)

## Behavior contract

1. Fetch assignments due in the next 48h from Canvas API.
2. Compare against `state.json` to skip ones already notified at the
   current urgency tier.
3. Group by course.
4. Call Claude Haiku once per batch with assignment titles + due times to
   get a time estimate and "start tonight" suggestion.
5. Assign urgency tier and color:
   - Tier 1 / <COLOR>: <THRESHOLD> — <FILL_IN>
   - Tier 2 / <COLOR>: <THRESHOLD> — <FILL_IN>
   - Tier 3 / <COLOR>: <THRESHOLD> — <FILL_IN>
6. Push to ntfy with priority matching the highest tier in the batch.
7. Update `state.json`, commit with `[skip ci]`.

## Known drift risks (why this spec has a `last_verified` header)

- The urgency thresholds in section 5 live in `canvas_reminder.py`, not in
  the spec — easy for them to drift apart.
- Model string is pinned in the workflow env; Anthropic releases occasionally
  obsolete it.
- Canvas course IDs roll over each semester. The bot uses "all active
  enrollments" rather than hardcoded IDs, but verify when a semester rolls.

## Connection to memory practice

This spec is the first concrete artifact governed by the rules in
`agents/memory-practice.md`. The YAML header above is the live application
of "last-verified timestamps + re-grounding triggers." If the header is
stale or `verified_against` SHAs don't match HEAD, any session touching
this agent must re-ground before acting.
