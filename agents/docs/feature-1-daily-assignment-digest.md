# Daily Assignment Digest — Feature documentation and rollout plan

> Feature flag: `daily_assignment_digest` (account-level)
> Status: behind flag, rolling out per the plan below
> Tracking issue: #15
> Source of truth: `agents/tasks/feature-1/feature-1.md`,
> `agents/tasks/feature-1/implementation-research.md`

## What this feature does

The Daily Assignment Digest sends each active student one notification per day
listing their outstanding assignments per enrolled course. It runs as a
scheduled job in the Canvas notification framework and respects the user's
existing notification preferences.

## When it runs

- Once per day per user, at a time anchored to the user's time zone.
- Recipients are limited to **active student enrollments only** — users with
  no current student enrollment receive no digest.
- Idempotent: if the job is retried within the same logical day for the same
  user, no duplicate notification rows are created.

## How to disable it

Three ways, in order of scope:

1. **Per user**: in Notifications preferences, toggle
   *Daily Assignment Digest* off.
2. **Per account / institution**: account admins toggle the
   `daily_assignment_digest` feature flag off in account settings.
3. **Globally (emergency rollback)**: flip the feature flag off at the
   site-admin level. Rollback is flag-flip only — no data migration required
   (per NFR-Rel-4).

## Known limitations

- **Stale data**: the digest reflects the assignment state at job-run time, not
  at the moment of delivery. Assignments submitted after the job runs but
  before the user reads the notification will still appear as outstanding
  until the next day's digest.
- **Time-zone caveat**: users without an explicit time-zone preference are
  bucketed into the account default. A user who travels across time zones may
  see the digest arrive at an unexpected local hour until they update their
  preference.

## Rollout plan

Staged rollout per NFR-Rel-3. Each gate has explicit go/no-go criteria; if any
fail, hold at the current gate and triage before advancing.

### Stage 1 — Internal account

- **Audience**: Anthropic / course-internal Canvas account only.
- **Duration**: minimum 7 days (matches the soak window in issue #14).
- **Go criteria for next gate**:
  - Zero duplicate-delivery incidents over the 7-day soak.
  - Job run-duration stays within the budget set in the research doc.
  - All unit and integration tests (issues #9, #10, #12) green on `main`.
  - Manual QA checklist (#13) signed off — roles matrix, time-zone behavior,
    preference toggles all behave as documented above.

### Stage 2 — Pilot institution

- **Audience**: one volunteer pilot institution, opted in by their admin.
- **Duration**: minimum 14 days.
- **Go criteria for next gate**:
  - No P0/P1 incidents attributable to the digest job.
  - Opt-out rate at the user level is within the threshold set in
    `implementation-research.md`.
  - Pilot admin sign-off in writing.

### Stage 3 — GA behind flag

- **Audience**: all accounts, flag defaulted off; admins opt in per account.
- **Tracking**: issue #16.
- **Rollback**: flag-flip only.

## Cross-references

- Feature scope: [`agents/tasks/feature-1/feature-1.md`](../agents/tasks/feature-1/feature-1.md)
- Implementation research: [`agents/tasks/feature-1/implementation-research.md`](../agents/tasks/feature-1/implementation-research.md)
- Implementation agent: [`agents/Feature implementation.md`](../agents/Feature%20implementation.md)
