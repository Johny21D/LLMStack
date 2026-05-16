---
agent: canvas-reminder-bot
last_verified: 2026-05-16
verified_against:
  - repo: Canvas-Reminder- (private)
  - workflow: .github/workflows/reminder.yml @ commit c8c528d
  - last successful run:#39 (2026-05-15 21:25 MT)
  - script: canvas_reminder.py @ commit c8c528d
  - model: claude-haiku-4-5-20251001
re_ground_on:
  - any edit to NOTIFY_THRESHOLDS, THRESHOLD_TO_TIER, TIER_INFO, or CRITICAL_TIERS
  - any merge to main on Canvas-Reminder-
  - any edit to canvas_reminder.py or its workflow YAML
  - rotation of ANTHROPIC_API_KEY, CANVAS_ACCESS_TOKEN, or the ntfy topic
  - any change to state.json schema
  -  ">7 days idle since last_verified"
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
- Workflow: `.github/workflows/<FILL_IN>.yml.`
- State: `state.json` (committed back to the repo by the bot to deduplicate
  notifications across runs)

## Trigger

- Cron schedule: `0 */6 * * *` — every 6 hours, on the hour (UTC)
- Manual: `workflow_dispatch` enabled
  
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
5. Assign urgency tier from hours-until-due. Crossing any threshold in
   `NOTIFY_THRESHOLDS = [72, 48, 36, 24, 18, 12, 9, 6, 3, 1]` triggers a
   notification at the corresponding tier:

   | Tier        | Emoji | Triggers at (hours-until-due) | ntfy priority | Label                     |
   |-------------|-------|-------------------------------|---------------|---------------------------|
   | `radar`     | 🟢    | 72                            | low           | ON THE RADAR              |
   | `heads_up`  | 🟡    | 48, 36                        | default       | HEADS UP                  |
   | `tomorrow`  | 🟠    | 24, 18                        | high          | DUE TOMORROW              |
   | `urgent`    | 🔴    | 12, 9, 6                      | urgent        | URGENT — DUE SOON         |
   | `panic`     | 🚨    | 3                             | urgent        | PANIC — DROP EVERYTHING   |
   | `last_call` | 💀    | 1                             | urgent        | LAST CALL — <1HR LEFT     |

   Tiers in `CRITICAL_TIERS = {"last_call", "panic", "urgent"}` bypass
   quiet hours. All tier mappings live in `canvas_reminder.py` under
   `THRESHOLD_TO_TIER` and `TIER_INFO` — this table is a mirror that the
   `last_verified` header governs.
6. Push to ntfy with priority matching the highest tier in the batch.
7. Update `state.json`, commit with `[skip ci]`.

## Known drift risks (why this spec has a `last_verified` header)

- The tier table in section 5 mirrors `NOTIFY_THRESHOLDS`, `THRESHOLD_TO_TIER`,
  `TIER_INFO`, and `CRITICAL_TIERS` in `canvas_reminder.py`. Any code edit to
  those four constants will silently invalidate this spec.
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
