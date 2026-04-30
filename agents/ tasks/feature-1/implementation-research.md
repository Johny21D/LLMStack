# Implementation Research — Smart Daily Digest

## Feature Summary

This document supports the feature brief in `feature-1.md`. The Smart Daily Digest
sends each enrolled student a once-daily summary of everything they need to complete
across all their Canvas courses: due assignments, unread announcements, upcoming quizzes,
and incomplete discussions. The goal is to replace the noisy per-event notification
stream with a single, actionable morning message so students never miss a deadline.

---

## 1. Design Considerations

### User Flows

**Student (primary consumer)**
1. Student checks email or Canvas in the morning.
2. They receive one digest — email and/or in-app bell notification — listing:
   - Items due today (hard deadline)
   - Items due in the next 3 days (upcoming)
   - Unread announcements posted since last digest
   - Incomplete graded discussions
3. Each item is a deep link back to the relevant Canvas page.
4. Student can opt out or adjust delivery time in their Notification Preferences.

**Instructor (passive)**
- No action required. Digest is generated from existing course data.
- Instructors are out of scope for receiving digests (they have different needs).

**Admin**
- Can enable/disable the digest feature institution-wide via a Feature Flag.
- Can set the default delivery time (e.g. 7:00 AM local time).

### Data Crossing Boundaries

| Data | Source | Destination | Notes |
|------|--------|-------------|-------|
| Assignment due dates | `assignments` table | Digest job | Filtered by `due_at`, enrollment |
| Submission status | `submissions` table | Digest job | Exclude already-submitted work |
| Announcement posts | `discussion_topics` | Digest job | `is_announcement = true`, unread |
| Discussion completion | `discussion_entries` | Digest job | Student has not posted |
| User notification prefs | `notification_policies` | Digest job | Opt-out check |
| Digest email | Mailer / SMTP | Student inbox | Uses existing Canvas mailer stack |
| In-app notification | `delayed_messages` / `stream_items` | Student bell | Uses existing notification pipeline |

### Interaction with Existing Canvas Concepts

- **Enrollments** — digest is scoped to active student enrollments only. Concluded courses are excluded.
- **Assignments** — uses the existing `Assignment` model. Respects overrides (differentiated assignments, section overrides) via `AssignmentOverrideApplicator`.
- **Notification Preferences** — Canvas already has a `NotificationPolicy` model with frequency options (`immediately`, `daily`, `weekly`, `never`). The digest adds a new notification type `digest_daily` that plugs into this system.
- **Feature Flags** — guarded behind a Canvas `FeatureFlag` so institutions can opt in.
- **Time Zones** — delivery time must respect the student's Canvas time zone setting, not server time.

### UX Risks and Tradeoffs

| Risk | Mitigation |
|------|------------|
| Digest arrives after deadline has passed | Deliver by 7 AM student local time; show "due today" vs "due soon" clearly |
| Overwhelming list for students in many courses | Cap at 10 items per digest; link to full to-do list |
| Students ignore it like other emails | Subject line includes count: "3 things due today in Canvas" |
| Duplicate with existing per-event notifications | Encourage opt-out of per-event; digest is additive by default |
| FERPA — grade data in email | Do NOT include scores or grade-sensitive info in digest body |

### Lab 4 Project Plan Tracking (GitHub Projects)

The MCP integration in Lab 4 should track:

- **Milestones**: Schema migration done · Background job runs · Email renders · Feature flag wired · Notification prefs wired · Acceptance tests pass
- **Tasks**: Create `DailyDigestJob` · Create `DailyDigestMailer` · Add `notification_type` record · Wire `NotificationPolicy` opt-out · Build React opt-in toggle in Notification Preferences UI · Write RSpec unit tests · Write integration test
- **Dependencies**: Feature flag must exist before UI toggle; DB migration before job
- **Definition of Done**: Job runs daily on schedule, email delivers correct items per student, opt-out works, no PII/grades leak into email body, accessibility audit passes on email template

---

## 2. Functional Requirements

### In Scope

**FR-1** — The system shall generate one digest per enrolled student per day, no more than once per 24-hour window.

**FR-2** — Given a student is enrolled in at least one active course, when the scheduled digest job runs, then the student receives a notification listing all assignments due within the next 72 hours that have not been submitted.

**FR-3** — Given an assignment has a student-specific due date override, when the digest is generated, then the override date (not the base due date) is used for that student.

**FR-4** — Given a student has already submitted an assignment, when the digest is generated, then that assignment is excluded from the digest.

**FR-5** — Given an announcement was posted in a student's course since the last digest was delivered, when the digest is generated, then that announcement title and course name are included.

**FR-6** — Given a student has not posted a reply to a graded discussion, when the digest is generated, then that discussion is listed as incomplete.

**FR-7** — Given a student sets their notification preference for `digest_daily` to `never`, when the digest job runs, then no digest is sent to that student.

**FR-8** — The system shall deliver the digest via email and as a Canvas in-app notification, using the student's preferred delivery channel as set in Notification Preferences.

**FR-9** — Each item in the digest shall include a direct hyperlink to the relevant Canvas page (assignment, announcement, discussion).

**FR-10** — The digest shall be delivered by the configured delivery time (default 7:00 AM) in the student's local time zone.

**FR-11** — An admin shall be able to enable or disable the digest feature institution-wide via a Canvas Feature Flag without a code deploy.

### Out of Scope

- Instructor or TA digests
- Digests for concluded or unpublished courses
- Grade or score information in the digest body
- Real-time or on-demand digest triggering (daily scheduled only)
- Mobile push notifications (email + in-app only in v1)
- Custom digest frequency (weekly, etc.) — daily only in v1
- External calendar integration (Google Calendar, iCal)

---

## 3. Non-Functional Requirements

### Performance

- The daily digest job must process all students at an institution within a 2-hour window to ensure delivery before students wake up.
- Per-student query time must not exceed 500 ms; batch processing with `find_each` to avoid loading all users into memory.
- Job must be idempotent — re-running after a failure must not send duplicate digests.

### Security and Privacy (FERPA)

- No grade data, score, or grading comments may appear in the digest.
- Email body contains only: item title, course name, due date, and a link.
- Links must use Canvas's existing authenticated deep-link pattern (no tokenless public URLs).
- Digest emails must not be logged in a way that exposes student data to non-authorized parties.
- Opt-out must be honored within the same job run — no race condition where a student opts out and still receives that day's digest.

### Accessibility

- Email template must meet WCAG 2.1 AA: sufficient color contrast, semantic HTML, alt text on any images/icons.
- In-app notification must be reachable via keyboard navigation (existing Canvas bell component handles this).
- Due dates must be written in plain language ("Today, April 29" not "2026-04-29T00:00:00Z").

### Observability

- Log each digest job run: start time, number of students processed, number of emails queued, errors.
- Track a metric `digest.delivered` per institution for monitoring.
- Failed deliveries (SMTP bounce, missing email) must be logged with student ID (not email) for privacy-safe debugging.

### Reliability

- Digest job failure for one student must not abort the entire batch (rescue per-student errors).
- If SMTP is unavailable, retry up to 3 times via the existing Canvas delayed job retry mechanism.
- If job misses its schedule window (e.g. server downtime), skip that day rather than sending late (a late digest is worse than no digest).

### Compatibility

- Must work with Canvas's existing Delayed Jobs infrastructure (`delayed_job` gem).
- Must not break existing per-event notification delivery.
- Must respect multi-tenancy — institutions using Canvas Data / subaccounts must only see their own students' data.
- Compatible with both self-hosted and Instructure-hosted Canvas deployments.

---

## 4. Codebase Analysis Using the analyze-repo Agent

### How to Run the Agent (Step-by-Step Instructions)

Follow these steps exactly to reproduce this analysis against your local Canvas LMS clone.
All commands run from the root of the course repo (`LLMStack/`). Your Canvas fork must
be cloned locally (e.g. at `~/canvas-lms`).

**Step 1 — Build the index (run this in your terminal, NOT inside the LLM)**
```bash
python agents/scripts/build_index.py ~/canvas-lms
```
This writes two files into the Canvas repo:
- `.analysis/manifest.json` — directory tree, file counts, line counts, language breakdown, entry points
- `.analysis/symbol_map.json` — every class and function mapped to its file

Check that both files exist before continuing. If the script errors, confirm that
`~/canvas-lms` is a valid git repo with at least one committed file.

**Step 2 — Read manifest.json**
Open `.analysis/manifest.json` in your editor or paste it into the LLM chat.
Identify the top 5 directories by line count and all listed entry points.
Do NOT open any Canvas source file yet — the manifest is enough to plan next steps.

**Step 3 — Summarize folders (run in your terminal)**
```bash
python agents/scripts/summarize_folders.py ~/canvas-lms
```
This writes `.analysis/folder_summaries.json`. Read it to understand each top-level
directory's purpose. This is the primary architectural source — read it once and do
not re-read it.

**Step 4 — Run targeted symbol lookups (run in your terminal)**
For each symbol relevant to your feature, run:
```bash
python agents/scripts/query_index.py ~/canvas-lms --symbol NotificationPolicy
python agents/scripts/query_index.py ~/canvas-lms --symbol DelayedMessage
python agents/scripts/query_index.py ~/canvas-lms --symbol AssignmentOverrideApplicator
python agents/scripts/query_index.py ~/canvas-lms --symbol DiscussionTopic
```
Each command returns the file path(s) where that symbol is defined. Paste the output
into the LLM chat alongside your question. Do not open the source files directly.

**Step 5 — Open entry point files only if needed**
Only open a file if ALL three conditions are true:
- It is listed as an entry point in `manifest.json`
- It is under 300 lines
- You have not already read it this session

**Step 6 — Write findings**
Document hypotheses, concrete findings, and open questions based only on what the
scripts returned. Stay under 40% of model context (≈64k tokens for Claude Sonnet).

---

### Agent Session Notes (Selected Output)

```
# Step 1 output summary
total_files: 14,203
total_lines: ~1.8M
language_breakdown: {.rb: 62%, .js/.jsx: 28%, .scss: 5%, other: 5%}
top directories by line count:
  app/         ~620k lines
  gems/        ~280k lines
  spec/        ~510k lines
  ui/          ~190k lines (React)
  db/          ~40k lines

entry_points identified: config/routes.rb, app/jobs/, Gemfile

# Step 4 — symbol lookups
query_index.py --symbol NotificationPolicy
  → app/models/notification_policy.rb
  → app/controllers/notification_preferences_controller.rb

query_index.py --symbol DelayedMessage
  → app/models/delayed_message.rb

query_index.py --symbol AssignmentOverrideApplicator
  → lib/assignment_override_applicator.rb

query_index.py --symbol DiscussionTopic
  → app/models/discussion_topic.rb
```

### Hypotheses: Where Changes Will Land

| Area | Path (hypothesized) | Reason |
|------|--------------------|----|
| Background job | `app/jobs/daily_digest_job.rb` (new) | Canvas uses `app/jobs/` for scheduled work |
| Mailer | `app/mailers/daily_digest_mailer.rb` (new) | Existing mailers live in `app/mailers/` |
| Email template | `app/views/daily_digest_mailer/` (new) | ERB email views follow this pattern |
| Notification type | `db/migrate/` + `app/models/notification.rb` | New notification type record needed |
| Notification policy | `app/models/notification_policy.rb` | Opt-out hooks into existing model |
| Feature flag | `config/feature_flags/` | Canvas feature flag definitions |
| React UI (prefs) | `ui/features/notification_preferences/` | Existing notification prefs React bundle |
| Routes | `config/routes.rb` | Only if a new API endpoint is needed for prefs |
| DB migration | `db/migrate/` | `daily_digest_sent_at` column or new `digest_deliveries` table |

### Concrete Findings

**Existing notification pipeline:**
Canvas already has `DelayedMessage` (batched notifications) and `NotificationPolicy`
(per-user frequency settings). The `Notification` model has types like
`'Submission Comment'`, `'Assignment Due Date'`, etc. Adding `'Daily Digest'` as a new
type follows this exact pattern and hooks into the existing opt-out UI automatically.

**Background job pattern:**
Canvas uses `delayed_job` with job classes in `app/jobs/`. Existing jobs like
`GradebookExporterJob` show the pattern: a class with a `perform` method, enqueued with
`delay(run_at: next_7am)`. The digest job will follow this pattern and re-enqueue itself
after each run.

**Assignment override applicator:**
`lib/assignment_override_applicator.rb` already contains
`assignment_overridden_for(assignment, student)` — the correct method to call to get
the student-specific due date. FR-3 (overrides respected) is largely already solved
by this existing utility.

**Submission check:**
`Submission` model has a `workflow_state` column. States `'submitted'`, `'graded'`
indicate completion. The query
`Submission.where(user: student, workflow_state: ['submitted', 'graded'])` is the
correct exclusion filter for FR-4.

**Discussion completion:**
`DiscussionEntry.where(discussion_topic: topic, user: student).exists?` is the pattern
Canvas uses to check student participation, visible in existing gradebook logic.

### Open Questions

- **OQ-1 (spike needed):** Does Canvas's existing `NotificationPolicy` daily batching conflict with a new `digest_daily` type, or do they coexist independently? Need to trace `delayed_messages` flush logic.
- **OQ-2 (stakeholder):** Should the digest respect "quiet hours" set by the student, or always deliver at 7 AM institution time?
- **OQ-3 (spike needed):** What is the correct way to schedule a recurring daily job in Canvas's delayed_job setup — cron-style via `config/initializers/` or a self-re-enqueuing job?
- **OQ-4 (stakeholder):** Should to-do items from Canvas's native To Do list (Pages marked as to-do, etc.) be included, or only assignments and discussions?
- **OQ-5 (spike needed):** How does Canvas handle time zone resolution for students — is it stored on the `User` model or the `Enrollment`?

---

## 5. Testing and Verification Plan

### What Will Be Tested

1. **Digest content accuracy** — correct items appear for each student based on enrollment, due dates, and submission status.
2. **Exclusion logic** — submitted assignments, concluded courses, and opted-out students are correctly excluded.
3. **Delivery mechanics** — email and in-app notification both fire; links resolve correctly.
4. **Idempotency** — re-running the job does not send duplicate digests.
5. **Feature flag gating** — disabling the flag stops the job entirely.
6. **FERPA compliance** — no grade or score data appears anywhere in the email.

### How It Will Be Tested

#### Unit-Level Tests (RSpec, isolated)

| Unit Under Test | What to Assert |
|-----------------|---------------|
| `DailyDigestJob#items_for_student` | Returns correct assignments due in next 72h; excludes submitted work; respects overrides |
| `DailyDigestJob#items_for_student` | Returns empty array for student with no upcoming work |
| `DailyDigestJob#should_send?` | Returns false when student notification pref is `never` |
| `DailyDigestJob#should_send?` | Returns false if digest already sent within 24h |
| `DailyDigestMailer#digest_email` | Email subject contains item count |
| `DailyDigestMailer#digest_email` | Email body contains deep links for each item |
| `DailyDigestMailer#digest_email` | Email body contains NO grade or score data |
| Assignment override logic | Student with override gets override date, not base date |

#### Integration Tests

| Integration | How |
|-------------|-----|
| Job → DB (assignments, submissions, enrollments) | RSpec with `factory_bot` fixtures; test with real PG in CI |
| Job → Mailer → SMTP | Use ActionMailer test delivery mode; assert `ActionMailer::Base.deliveries` |
| Notification type → `notification_policies` opt-out | Create a `NotificationPolicy` with `frequency: 'never'`; assert no email queued |
| Feature flag → job gating | Assert job exits early when flag disabled |
| Re-enqueue (job schedules next run) | Assert `DelayedJob` queue contains next run after `perform` |

#### Manual / Exploratory Checks (requires running Canvas instance)

- **Role check:** Log in as a student → verify digest arrives. Log in as instructor → verify no digest.
- **Opt-out flow:** Go to Notification Preferences → set Daily Digest to Never → confirm no email next run.
- **Time zone edge case:** Set student time zone to UTC-8, server to UTC → confirm delivery at correct local time.
- **Concluded course:** Conclude a course → confirm assignments from it do not appear in digest.
- **Differentiated assignment:** Create assignment with override for specific student → confirm digest shows override date.
- **Already submitted:** Submit an assignment → run digest job → confirm submitted item is absent.
- **Empty digest:** Student with no upcoming work → confirm no email is sent (no empty digest spam).
- **Regression:** Confirm existing per-event notifications still fire normally after feature is enabled.

### Success vs. Failure Criteria (mapped to Functional Requirements)

| FR | What Success Looks Like | What Failure Looks Like | Test Type |
|----|------------------------|------------------------|-----------|
| FR-1 | Job logs show exactly one digest per student per 24h | Student receives 2+ emails in one day | Integration |
| FR-2 | Email lists all unsubmitted assignments due ≤72h | Missing items or items from wrong course appear | Unit + Integration |
| FR-3 | Override due date shown, not base due date | Base date shown for student with override | Unit + Manual |
| FR-4 | Submitted assignment absent from digest | Already-submitted work appears in email | Unit + Integration |
| FR-5 | New announcement appears; old one does not | Stale announcements repeat across digests | Unit + Integration |
| FR-6 | Unposted graded discussion appears; posted one does not | Completed discussions listed as incomplete | Unit + Manual |
| FR-7 | Opted-out student receives zero emails | Email arrives despite `never` preference | Manual |
| FR-8 | Both email and in-app notification appear | One channel missing entirely | Manual |
| FR-9 | Each link opens the correct Canvas page | Links 404 or route to wrong item | Manual |
| FR-10 | Email arrives before 7 AM student local time | Email arrives late or at server time | Manual (staging) |
| FR-11 | Disabling flag stops all digest sending | Job fires even when flag is off | Integration + Manual |

### Areas Where Automation Is Impractical

- **Email rendering across clients** (Gmail, Outlook, Apple Mail) — visual regression is not automatable in CI. Mitigation: use a known-good HTML email template from Canvas's existing mailer; manual spot-check on 3 clients before launch.
- **Exact delivery time** — testing real cron timing in CI is flaky. Mitigation: unit test the time calculation logic; manually verify in staging environment.
- **FERPA audit** — no automated tool catches all cases. Mitigation: pre-launch checklist reviewed by a second developer confirming no grade data in email body, logs, or URLs.
