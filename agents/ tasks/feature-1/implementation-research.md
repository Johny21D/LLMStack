# Implementation Research — Daily Assignment Digest


## 1. Design considerations

### 1.1 User flow

1. A scheduled background job runs once per day (e.g. 7:00 AM in the
   user's local time, but see open question Q1).
2. For each active student, the job collects assignments that are
   currently outstanding (not yet submitted, not yet past a state
   that means "done") across all the student's published, active
   courses.
3. If the count is zero, no notification is created (no empty
   digests).
4. Otherwise, the job builds a per-student summary — total count plus
   a per-course breakdown — and hands that summary to Canvas's
   existing notification framework as a single notification of a new
   type, `Daily Assignment Digest`.
5. Canvas's notification framework decides where the notification
   actually lands (in-app feed, mobile push via the Canvas Student
   app, email, SMS) based on the student's existing notification
   preferences. The feature itself does not touch delivery.
6. The student sees the digest the next time they check whichever
   channel their preferences point to.

### 1.2 Data crossing boundaries

| Boundary | What crosses |
|---|---|
| Background job → DB | Bulk reads of `users`, `enrollments`, `courses`, `assignments`, `submissions`. Writes one notification row per student per day. |
| DB → Notification framework | The aggregated summary string and the recipient user id. **Only the student's own data** ever ends up in their notification. |
| Notification framework → Delivery channels | Whatever Canvas already does for in-app, push, and email. Feature does not introduce a new channel. |
| Student preferences → Job | The job (or the framework) consults notification preferences to decide whether to deliver, not what content to compute. |

### 1.3 Permissions and roles

- **Students** are the only recipients. Other roles (instructors, TAs,
  observers, admins) are excluded *at the job's recipient query
  stage*, not at the delivery stage, so the job never even computes
  digests for them.
- **Cross-listed enrollments** matter: a user who is a student in one
  course and a TA in another should only see the student courses
  reflected in the digest. (Open question Q3.)
- **Account-level admins** can disable the feature for a whole
  institution via a Canvas feature flag (see §3.5).

### 1.4 UX risks

- **Notification fatigue.** A daily notification on top of Canvas's
  existing event-driven notifications could feel like spam.
  Mitigation: the digest is one notification, not many, and students
  can suppress it through standard notification preferences.
- **Stale data.** If the digest runs at 7 AM and a student submits at
  7:30 AM, the digest is "wrong" for the rest of the day. Acceptable
  because the digest's purpose is morning planning, not real-time
  status. We will document this limit.
- **Empty-digest fatigue.** Sending "you have 0 assignments" daily
  trains students to ignore the digest. Mitigation: skip empty days.
- **Time zone confusion.** A student in a different time zone than
  their account default may get the digest at an unexpected hour.
  Mitigation: use the student's own time zone where Canvas exposes it
  (open question Q1).
- **Internationalization.** Canvas is localized; the digest text must
  go through Canvas's existing i18n (`I18n.t`) calls, not be
  hard-coded English.

### 1.5 Interaction with existing Canvas concepts

- **Courses:** the digest only includes assignments from courses
  where the student has an active student enrollment in a published,
  unconcluded course.
- **Assignments:** the definition of "outstanding" reuses Canvas's
  existing logic for what shows up in a student's to-do list rather
  than re-defining it. This avoids drift between the digest and
  Canvas's other student-facing surfaces.
- **Notifications:** the digest is a new `Notification` type
  registered alongside Canvas's existing types, with its own
  category, default frequency (`daily`), and notification preference
  entry.
- **Background jobs:** the digest runs as a periodic Delayed Job (or
  whatever scheduled-job pattern Canvas's codebase uses for similar
  recurring work — confirmed below in §4).
- **Feature flags:** the digest ships behind an account-level Canvas
  feature flag so institutions can opt in.

### 1.6 What the project plan should track (for Lab 4 MCP)

Captured here so the Lab 4 GitHub Projects integration has clear
data to mirror, *not implemented in this lab*.

- **Milestones:** (M1) Design & spike confirmed, (M2) Backend job +
  notification type behind feature flag, (M3) Notification
  preference UI surfaced, (M4) Internal beta, (M5) GA behind flag.
- **Tasks:** discovery spike on existing notification infrastructure;
  define `Notification` type; write recipient query; write summary
  builder; register notification preference; write unit tests; write
  integration tests; QA in staging; documentation; rollout plan.
- **Dependencies:** notification type registration must land before
  the job can dispatch; preference UI depends on the type being
  registered; integration tests depend on the job being callable in
  isolation.
- **Definition of done (per task):** code merged, tests green,
  feature-flag-gated, docs updated, observability in place, rollback
  plan documented.

---

## 2. Functional requirements

In-scope, expressed as testable "the system shall" statements and
given/when/then scenarios.

### 2.1 The system shall

1. **FR-1.** The system shall produce, at most, one Daily Assignment
   Digest notification per student per calendar day.
2. **FR-2.** The system shall include in a student's digest only
   assignments from courses in which that student has an active
   student enrollment.
3. **FR-3.** The system shall exclude from the digest any course that
   is unpublished, concluded, soft-deleted, or otherwise hidden from
   the student.
4. **FR-4.** The system shall exclude from the digest any assignment
   that the student has already submitted, that is unpublished, or
   that is otherwise not visible to the student.
5. **FR-5.** The system shall present the digest as a total count of
   outstanding assignments, plus a per-course breakdown listing each
   contributing course and that course's count.
6. **FR-6.** The system shall not send a digest to a student who has
   zero outstanding assignments on the run day.
7. **FR-7.** The system shall route the digest through Canvas's
   existing notification framework so that delivery channel is
   determined by the recipient's notification preferences.
8. **FR-8.** The system shall provide a notification preference entry
   for the Daily Assignment Digest so that students can suppress it.
9. **FR-9.** The system shall be controllable by an account-level
   feature flag, off by default until enabled by an admin.
10. **FR-10.** The system shall localize the digest text using
    Canvas's existing i18n facilities.

### 2.2 Given/when/then scenarios

**Scenario A — Standard student with mixed courses**
*Given* a student enrolled in three published courses with 3, 2, and
1 outstanding assignments respectively,
*when* the daily digest job runs,
*then* the student receives one notification stating "6 assignments
to complete: 3 in [Course A], 2 in [Course B], 1 in [Course C]."

**Scenario B — No outstanding work**
*Given* a student who has submitted everything currently due,
*when* the daily digest job runs,
*then* the student receives no notification on that day.

**Scenario C — Submitted between runs**
*Given* the digest counted an assignment yesterday and the student
submitted it overnight,
*when* the digest runs again today,
*then* that assignment is no longer counted.

**Scenario D — Concluded course**
*Given* a student is still listed in a course that has concluded,
*when* the digest runs,
*then* nothing from that course appears in the digest.

**Scenario E — Mixed-role user**
*Given* a user is a student in Course A and a TA in Course B,
*when* the digest runs,
*then* only Course A's assignments are counted.

**Scenario F — Preference disabled**
*Given* a student has disabled the Daily Assignment Digest
notification preference,
*when* the digest runs,
*then* the student receives no notification by any channel.

**Scenario G — Feature flag off**
*Given* an institution has the feature flag disabled,
*when* the digest job would otherwise run,
*then* no digests are computed or sent for any student in that
institution.

### 2.3 In scope vs out of scope

**In scope**
- One notification per student per day, via Canvas notifications.
- Total count and per-course breakdown.
- Skipping empty days.
- Honoring notification preferences.
- Account-level feature flag.
- Standard Canvas i18n.

**Out of scope (will not be done in this feature)**
- Listing individual assignment names or due dates.
- Configurable per-user schedule or time of day.
- Recently-graded summaries.
- Missing/overdue summaries beyond "still outstanding."
- Instructor or observer digests.
- A new delivery channel.
- Push notification copy that differs from in-app copy.
- A new notification preference UI distinct from the existing one.
- Retroactive digests for past days.

---

## 3. Non-functional requirements

### 3.1 Performance

- **NFR-Perf-1.** A full daily run shall complete within the
  institution's existing nightly batch window for jobs of similar
  shape (concretely: under 60 minutes for an institution with up to
  ~100,000 active students; final number to be confirmed against
  Canvas's existing batch expectations).
- **NFR-Perf-2.** The recipient query shall avoid N+1 patterns.
  Outstanding-assignment counts shall be computed in bulk per
  student rather than per-assignment.
- **NFR-Perf-3.** The job shall be shardable / chunkable so a single
  failure or slow query does not block all students.

### 3.2 Security and privacy (FERPA-adjacent)

- **NFR-Sec-1.** Each digest shall contain only the recipient
  student's own information. No cross-student data leakage is
  acceptable.
- **NFR-Sec-2.** The digest shall not introduce a new external data
  recipient. It rides existing channels (Canvas in-app, the existing
  email pipeline, the existing push pipeline). No new third-party
  integration is added by this feature.
- **NFR-Sec-3.** Counts and course names are considered "directory-
  like" with respect to the student receiving them. We are not
  exposing them to anyone *other* than that student. This keeps the
  feature's privacy footprint inside what FERPA allows.
- **NFR-Sec-4.** Logs shall record that a digest was sent, the user
  id, and the count, but **not** the assignment titles or course
  names. This keeps logs from becoming a secondary disclosure
  surface.

### 3.3 Accessibility

- **NFR-A11y-1.** The in-app version of the notification shall meet
  the same accessibility standards as Canvas's other notifications
  (semantic structure, screen-reader-friendly text, no
  color-conveyed-only meaning).
- **NFR-A11y-2.** The notification preference entry for this feature
  shall be reachable and operable via keyboard alone and labeled for
  screen readers.

### 3.4 Observability

- **NFR-Obs-1.** The job shall emit a metric for run duration, number
  of students processed, and number of digests dispatched.
- **NFR-Obs-2.** The job shall log structured errors (per student
  failures should not crash the whole run; they should be captured
  and surfaced in logs/metrics).
- **NFR-Obs-3.** A small operational dashboard or query is
  sufficient — no new monitoring infrastructure required.

### 3.5 Reliability and rollout

- **NFR-Rel-1.** A failed run shall not produce duplicate digests on
  retry. The job shall be idempotent per (student, calendar day).
- **NFR-Rel-2.** The feature shall ship behind an account-level
  feature flag, off by default.
- **NFR-Rel-3.** Rollout plan: enable for a single internal test
  account first; then a small pilot institution; then GA-by-flag.
- **NFR-Rel-4.** Rollback shall be flag-flip only — no schema
  rollback should be required for an emergency disable.

### 3.6 Compatibility with Canvas deployment assumptions

- Canvas runs as a Rails application with a Postgres database and
  Delayed Job (or compatible) for background work. This feature
  assumes that environment and does not require any new
  infrastructure.
- This feature assumes Canvas's existing notification framework
  remains the supported way to deliver student notifications; if
  Canvas pivots to a new framework later, the digest re-targets
  through that framework rather than building its own.

---

## 4. Codebase analysis (using the Lab 2 agent)

### 4.1 What the agent did

I used the agent specified in
[`agents/analyze-repo.md`](../../analyze-repo.md). The agent runs
three out-of-LLM scripts that produce JSON summaries before the LLM
does any planning:

- `agents/scripts/build_index.py` — walks the repo, writes
  `manifest.json` (file/line counts, language breakdown, entry
  points) and `symbol_map.json` (classes/functions per file).
- `agents/scripts/summarize_folders.py` — samples files per
  top-level folder and writes `folder_summaries.json`.
- `agents/scripts/query_index.py` — queries `symbol_map.json` for
  specific class/function names without ever opening source files.

The agent reads only the JSON outputs of these scripts plus, at
most, a handful of short entry-point files. It never browses the
Canvas tree directly.

I cloned `instructure/canvas-lms` (`--depth 1`) into a working
directory and ran `build_index.py` against the clone. The script
wrote its outputs to `canvas-lms/.analysis/`.

### 4.2 Hypotheses about where change will land

Before looking at the index, my hypotheses were that a daily
student-facing notification feature in a Rails LMS would touch:

- **Models:** `Assignment`, `Submission`, `User`, `Enrollment`,
  `Course`, `Notification`, plus a notification-preference model.
- **Background jobs:** a periodic / scheduled Delayed Job entry
  point.
- **Notification templates:** some directory that holds per-channel
  message templates (email body, in-app text, push text).
- **Configuration:** a notifications config file listing valid
  notification names and their default categories/frequencies.
- **Frontend:** a React surface for the notification preference
  entry, plus rendering inside the existing notification feed.
- **Migrations / DB:** at most a small migration if a new
  notification record needs special columns; ideally none.

### 4.3 Concrete findings from the index

The Canvas LMS clone produces a consistent picture with the
hypotheses above. Key observed structure (top-level and inside
`app/`):

| Path | Why it matters for this feature |
|---|---|
| `app/controllers/` | Where API and web endpoints live. We do **not** expect to add a controller — the digest is generated server-side and dispatched, not fetched by the client. Useful as reference for how Canvas validates and authorizes student-scoped requests. |
| `app/models/` | Where `Assignment`, `Submission`, `User`, `Enrollment`, `Course`, and `Notification` will live. The "what counts as outstanding" definition will be drawn from existing scopes here rather than re-implemented. |
| **`app/messages/`** | This folder existing is the strongest single signal in the repo for this feature. Canvas keeps per-notification message templates here. A new digest notification means adding templates here for the channels Canvas supports (in-app, email, etc.). |
| `app/services/` | The right home for a `DailyAssignmentDigest` service object that encapsulates "build a per-student summary." Keeps logic out of the model and out of the job glue. |
| `app/views/` | Some notification surfaces still render through views; we will follow whatever Canvas already does for similar daily/aggregated notifications. |
| `lib/` | Where shared infrastructure (notifiers, framework glue) lives. The notification framework's entry points and any "scheduled job" base class are here, not in `app/`. |
| `config/` | Where the canonical list of notifications is registered in Canvas. Adding a new notification type means registering it here so the framework knows about it. |
| `db/migrate/` | Probably untouched. Reusing existing notification infrastructure should not require new tables. |
| `ui/` | Canvas's React frontend. The notification preferences UI surface is here; we are adding *one entry* to an existing list, not building a new screen. |
| `spec/` | RSpec tests. New unit and integration tests will mirror the existing patterns for notification types and scheduled jobs. |

The repo is large enough (~22,651 files checked out of the index,
~745 MB on disk for the working copy) that "exhaustive reading" is
neither possible nor the goal. The traceable answer for each
hypothesis is "look in the listed folder, follow Canvas's existing
pattern for similar notifications."

### 4.4 Open questions (need a spike or stakeholder input)

- **Q1.** What time zone drives the daily run? Canvas account default,
  user's own setting, or UTC? (Stakeholder + spike.)
- **Q2.** Does Canvas's notification framework already support
  scheduled, aggregated (non-event-driven) notifications, or is the
  digest the first of its kind in the codebase? If first, what is
  the minimum-friction way to register it? (Spike in `lib/` and
  `config/`.)
- **Q3.** How exactly does "active student enrollment" map in Canvas
  for users with multiple roles (e.g. student in one course, TA in
  another, observer in a third)? (Spike against `Enrollment`.)
- **Q4.** What is the canonical "is this assignment outstanding for
  this student" scope, and is it re-usable from a background job
  context, or does it require a request-scoped context? (Spike
  against `Assignment`/`Submission` scopes.)
- **Q5.** What is Canvas's standard pattern for a periodic Delayed
  Job — a class with `.run` plus a `delayed_jobs.yml` entry, a
  cron-like config, or something else? (Spike in `lib/` plus a
  Canvas-specific search for an existing daily job.)
- **Q6.** Is there a precedent notification we can mimic end-to-end
  (e.g. a weekly summary, an existing periodic notification) that
  shortens this feature to "do what *that* one does, but daily and
  with this content"?

### 4.5 Traceability — requirements to likely code locations

| Requirement | Likely landing area |
|---|---|
| FR-2, FR-3, FR-4 (who/what counts) | `app/models/assignment.rb`, `app/models/submission.rb`, `app/models/enrollment.rb` (read existing scopes) |
| FR-5 (summary content) | New service in `app/services/` |
| FR-7 (delivery via framework) | Notification registration in `config/`, dispatch via `lib/` notification glue |
| FR-8 (notification preference) | Notification registration in `config/`; preferences UI entry in `ui/` |
| FR-9 (feature flag) | Canvas feature-flag config (account-level) |
| FR-1, FR-6 (one per day, skip empty) | New scheduled job class in `lib/` (or wherever Canvas's existing daily/periodic jobs live) |
| FR-10 (i18n) | Standard `I18n.t` usage in templates under `app/messages/` |

---

## 5. Testing and verification plan

### 5.1 Unit-level expectations

The pieces that deserve isolated tests:

1. **Outstanding-count calculation** — given a fixture of courses,
   enrollments, assignments, and submissions, the calculator returns
   the correct per-course counts. Cover: published vs unpublished
   course; concluded course; soft-deleted assignment; already-
   submitted assignment; assignment hidden from student.
2. **Empty-result handling** — when the calculator returns zero
   across all courses, the dispatcher does not enqueue a
   notification.
3. **Multi-role users** — a user who is a student in one course and
   a TA in another only contributes the student course.
4. **Idempotency guard** — calling the daily run twice for the same
   (student, calendar date) does not produce two notifications.
5. **Localization** — the digest text renders through `I18n.t` and
   responds to a non-default locale.
6. **Feature-flag respect** — when the flag is off, the
   summary-builder is never invoked for any student in that account.

### 5.2 Integration points

1. **Job → DB.** With a real (test) database and seeded fixtures,
   running the daily job produces exactly the expected number of
   notification rows and their content matches the expected
   per-course breakdown.
2. **Notification → channels.** With Canvas's existing notification
   framework wired up, a notification of the new type respects
   notification preferences (in-app yes / email no, etc.).
3. **Scheduling.** The job is registered to run on the expected
   schedule and shows up in whatever Canvas uses to enumerate
   scheduled jobs.
4. **No external services.** This feature deliberately does not call
   any external service of its own; the integration tests do not
   need to mock one.

### 5.3 Manual / exploratory checks

- **Roles matrix.** Manually log in as: a student with no work, a
  student with a lot of work across many courses, a TA, an observer,
  an admin. Confirm only the students see digests, and only the
  expected ones.
- **Time zones.** Switch a test user's time zone and confirm the
  digest arrives at a sensible local time.
- **Preference toggles.** Toggle each delivery channel on/off in
  notification preferences and confirm the digest follows the
  toggle.
- **Empty day.** Submit everything, wait for the next run, confirm
  no notification.
- **Regression of nearby flows.** Sanity-check that turning the
  digest on does not change the appearance, ordering, or behavior
  of Canvas's existing event-driven notifications.
- **Feature flag flip.** Enable and disable the flag at the account
  level mid-run; confirm graceful behavior.

### 5.4 Acceptance criteria (mapped to FR)

| FR | Acceptance criterion |
|---|---|
| FR-1 | Across a 7-day soak with a stable test population, each student has at most one digest per calendar day. |
| FR-2 / FR-3 | Manual roles matrix shows expected inclusion/exclusion of courses. |
| FR-4 | Submitting an assignment between two runs causes it to disappear from the next digest. |
| FR-5 | Digest text contains a total and a per-course breakdown matching ground-truth counts from a seeded scenario. |
| FR-6 | A student with zero outstanding assignments receives no digest that day. |
| FR-7 | Toggling delivery channels in preferences changes where the digest lands and does not change anything else. |
| FR-8 | Disabling the digest preference results in no digest at all. |
| FR-9 | Toggling the account feature flag off causes the job to skip that account entirely. |
| FR-10 | A locale switch flips the digest text to the corresponding translation. |

### 5.5 What we cannot fully automate, and the plan for it

- **Real mobile push behavior** depends on the Canvas Student app
  and the platform push services. We will not stand up an automated
  end-to-end mobile push test; instead we run a manual checklist on
  iOS and Android against a staging environment before the GA flag
  flip.
- **Production-scale performance.** We cannot easily replicate a
  100k-student institution in CI. Mitigation: a staged rollout
  (internal account → pilot institution → GA), with run-duration
  metrics monitored at each stage. If duration trends up, we hold
  the rollout.
- **Localization completeness.** New strings must be added to
  Canvas's translation pipeline. We verify the English path with
  automated tests and verify a couple of additional locales
  manually as a smoke check; full coverage waits on the normal
  translation cadence.

---

## 6. Session notes (evidence of Lab 2 workflow)

This subsection documents that the Lab 2 agent in
[`agents/analyze-repo.md`](../../analyze-repo.md) was actually run
against Canvas LMS. No secrets are included.

### Environment
- Worked in AWS CloudShell (`/home/work/`).
- Cloned target: `git clone --depth 1 https://github.com/instructure/canvas-lms.git`.
- Working tree size after checkout: ~745 MB; ~22,651 files updated.
- Cloned my LLMStack fork in the same workspace to reach the
  `agents/scripts/` directory.

### Agent script run — `build_index.py`

```text
$ python3 LLMStack/agents/scripts/build_index.py /home/work/canvas-lms
Building manifest...
Extracting symbols...
Done. Output in .analysis/
```

The script wrote outputs into `canvas-lms/.analysis/` (confirmed
with `find /home/work -name "manifest.json" -mmin -5`).

### How the index was used

Per the agent spec, the LLM did not browse Canvas directly. The
manifest and folder summaries drove the architecture-level
findings recorded in §4.3. Specific symbol lookups (e.g. for the
notification framework entry points) would be done with
`query_index.py --symbol …` rather than by opening source files.

### Token-budget discipline

The Lab 2 spec caps the LLM's loaded context at 40% of the usable
window. For this lab, only the summary JSON outputs and this
research document itself were in scope; no Canvas source files
were opened by the LLM during the analysis.

### What I would run next

If this were a longer engagement, the next agent invocations would
be:

1. `query_index.py /home/work/canvas-lms --symbol Notification`
2. `query_index.py /home/work/canvas-lms --symbol DelayedJob`
3. A targeted `summarize_folders.py` re-read for `app/messages/`
   and `lib/` to answer open question Q5.

That work belongs to the implementation phase, not Lab 3.
