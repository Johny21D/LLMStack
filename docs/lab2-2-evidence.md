# Lab 2.2 — Project Creation Agent: Evidence of Successful Run

## Run metadata

| Field | Value |
|-------|-------|
| Date | 2026-05-15 |
| MCP host | Claude Code v2.1.141 |
| GitHub MCP server | `api.githubcopilot.com/mcp/` — 86 tools exposed |
| Target repo | `Johny21D/LLMStack` |
| Agent spec | `agents/project-creation.md` |

> **Note on tooling gaps:** The hosted GitHub MCP server (`api.githubcopilot.com/mcp/`) does not expose milestone-creation or Project v2 creation/management tools. Milestones M1–M5 and the Project v2 board were therefore created via `Invoke-RestMethod` (GitHub REST API v3 and GraphQL v4) directly in the Claude Code session. All issue creation, label creation, and issue updates used the MCP `issue_write` tool. Issues were additionally disabled on the fork at run time and were enabled via a `PATCH /repos/{owner}/{repo}` call before issue creation proceeded.

---

## Project

**URL:** https://github.com/users/Johny21D/projects/2
**Title:** Feature 1 — Daily Assignment Digest
**Project node ID:** `PVT_kwHOC6VgYM4BX0PF`

---

## Milestones

| # | Title | URL |
|---|-------|-----|
| 1 | M1: Design & spike confirmed | https://github.com/Johny21D/LLMStack/milestone/1 |
| 2 | M2: Backend job + notification type behind feature flag | https://github.com/Johny21D/LLMStack/milestone/2 |
| 3 | M3: Notification preference UI surfaced | https://github.com/Johny21D/LLMStack/milestone/3 |
| 4 | M4: Internal beta | https://github.com/Johny21D/LLMStack/milestone/4 |
| 5 | M5: GA behind flag | https://github.com/Johny21D/LLMStack/milestone/5 |

---

## Functional Requirement → Issue Traceability

Every in-scope functional requirement from `agents/tasks/feature-1/implementation-research.md §2.1` maps to at least one issue. No requirement is untracked.

| FR | Requirement | Covering issue(s) |
|----|-------------|-------------------|
| FR-1 | At most one digest per student per calendar day | #7 (Scheduled job — idempotency guard) |
| FR-2 | Only assignments from courses with an active student enrollment | #5 (Recipient query), #2 (Spike: enrollment scopes) |
| FR-3 | Exclude unpublished, concluded, soft-deleted, or hidden courses | #5 (Recipient query) |
| FR-4 | Exclude submitted, unpublished, or student-hidden assignments | #6 (Digest service) |
| FR-5 | Digest contains total count + per-course breakdown | #6 (Digest service), #8 (Message templates) |
| FR-6 | No digest when student has zero outstanding assignments | #7 (Scheduled job skip guard), #6 (Digest service empty result) |
| FR-7 | Delivery routed through Canvas notification framework | #4 (Register notification type), #7 (Scheduled job dispatch) |
| FR-8 | Students can suppress digest via notification preference | #11 (Preference UI seam story) |
| FR-9 | Account-level feature flag, off by default | #4 (Register notification type + feature flag) |
| FR-10 | Digest text localized via Canvas i18n (`I18n.t`) | #8 (Message templates with i18n) |

---

## All Created Artifacts

### Labels (17)

Created via MCP `label_write` on `Johny21D/LLMStack`:

`feature-1` · `type:story` · `type:task` · `type:test` · `type:spike` · `phase:1` · `phase:2` · `phase:3` · `phase:4` · `phase:5` · `subsystem:models` · `subsystem:services` · `subsystem:messages` · `subsystem:lib` · `subsystem:config` · `subsystem:ui` · `subsystem:spec`

### Milestones (5)

Created via `Invoke-RestMethod POST /repos/Johny21D/LLMStack/milestones`:

| Number | Title | Created via |
|--------|-------|-------------|
| 1 | M1: Design & spike confirmed | Invoke-RestMethod |
| 2 | M2: Backend job + notification type behind feature flag | Invoke-RestMethod |
| 3 | M3: Notification preference UI surfaced | Invoke-RestMethod |
| 4 | M4: Internal beta | Invoke-RestMethod |
| 5 | M5: GA behind flag | Invoke-RestMethod |

### Project v2 Board

Created via `Invoke-RestMethod POST /graphql` (`createProjectV2` mutation):

- **Title:** Feature 1 — Daily Assignment Digest
- **URL:** https://github.com/users/Johny21D/projects/2
- **Node ID:** `PVT_kwHOC6VgYM4BX0PF`
- All 16 issues added via `addProjectV2ItemById` GraphQL mutation.

### Issues (16)

Created via MCP `issue_write`, dependencies wired via MCP `issue_write` update. All issues assigned to `Johny21D`, all added to the project board.

| # | Title | Type | Phase | Milestone | Subsystem label(s) |
|---|-------|------|-------|-----------|-------------------|
| [#1](https://github.com/Johny21D/LLMStack/issues/1) | [Spike] Audit existing Canvas notification infrastructure | spike | 1 | M1 | `subsystem:lib`, `subsystem:config` |
| [#2](https://github.com/Johny21D/LLMStack/issues/2) | [Spike] Audit enrollment and assignment "outstanding" scopes | spike | 1 | M1 | `subsystem:models` |
| [#3](https://github.com/Johny21D/LLMStack/issues/3) | [Spike] Confirm time-zone handling strategy for daily digest run | spike | 1 | M1 | `subsystem:models` |
| [#4](https://github.com/Johny21D/LLMStack/issues/4) | [Story] Register DailyAssignmentDigest notification type and account-level feature flag | story | 2 | M2 | `subsystem:config`, `subsystem:lib` |
| [#5](https://github.com/Johny21D/LLMStack/issues/5) | [Story] Implement recipient query — active student enrollments only | story | 2 | M2 | `subsystem:models`, `subsystem:services` |
| [#6](https://github.com/Johny21D/LLMStack/issues/6) | [Story] Implement DailyAssignmentDigest service — outstanding-assignment count per course | story | 2 | M2 | `subsystem:models`, `subsystem:services` |
| [#7](https://github.com/Johny21D/LLMStack/issues/7) | [Story] Implement DailyAssignmentDigest scheduled job with idempotency guard | story | 2 | M2 | `subsystem:lib` |
| [#8](https://github.com/Johny21D/LLMStack/issues/8) | [Story] Add DailyAssignmentDigest message templates with i18n support | story | 2 | M2 | `subsystem:messages` |
| [#9](https://github.com/Johny21D/LLMStack/issues/9) | [Test] Unit tests for DailyAssignmentDigest service and job | test | 2 | M2 | `subsystem:spec` |
| [#10](https://github.com/Johny21D/LLMStack/issues/10) | [Test] Integration test: job produces correct notification rows in DB | test | 2 | M2 | `subsystem:spec` |
| [#11](https://github.com/Johny21D/LLMStack/issues/11) | [Story] Surface notification preference entry for Daily Assignment Digest | story | 3 | M3 | `subsystem:config`, `subsystem:ui` |
| [#12](https://github.com/Johny21D/LLMStack/issues/12) | [Test] Integration test: notification preference controls digest delivery | test | 3 | M3 | `subsystem:spec` |
| [#13](https://github.com/Johny21D/LLMStack/issues/13) | [Task] Execute manual QA checklist — roles matrix, time-zone, preference toggles | task | 4 | M4 | _(manual, no subsystem)_ |
| [#14](https://github.com/Johny21D/LLMStack/issues/14) | [Task] Monitor run-duration and idempotency across 7-day internal soak | task | 4 | M4 | _(observability, no subsystem)_ |
| [#15](https://github.com/Johny21D/LLMStack/issues/15) | [Task] Write feature documentation and rollout plan | task | 5 | M5 | _(docs, no subsystem)_ |
| [#16](https://github.com/Johny21D/LLMStack/issues/16) | [Task] Expand flag rollout to pilot institution and execute GA flag flip | task | 5 | M5 | _(ops, no subsystem)_ |

---

## Dependency Chain

Full graph encoded as `Blocked by` / `Blocks` references in each issue body.

```
#1 (Spike: notif infra) ──────────────────────┐
#2 (Spike: enrollment/assignment scopes) ──┐  │
#3 (Spike: time-zone) ────────────────────┐│  │
                                           ││  │
                                           ▼▼  ▼
#4 (Register notification type) ◄──────────────┘
#5 (Recipient query)            ◄──────────┘
#6 (Digest service)             ◄──────────┘
          │    │    │
          ▼    │    ▼
         #7 (Scheduled job) ◄──────────────────┘
          │
          ├──► #9  (Unit tests)              ◄── also blocked by #6, #8
          ├──► #10 (Integration: job → DB)
          ├──► #12 (Integration: preference) ◄── also blocked by #11
          ├──► #13 (Manual QA)               ◄── also blocked by #11
          └──► #14 (7-day soak)
                    │
                    ▼
               #8 (Message templates) ◄── blocked by #4, blocks #9
               #11 (Preference UI)    ◄── blocked by #4, blocks #12, #13
               #15 (Documentation)   ◄── blocked by #14
                    │
                    ▼
               #16 (GA rollout)       ◄── also blocked by #13, #15
```

**Critical path:** #1/#2/#3 → #4/#5/#6 → #7 → #14 → #15 → #16

---

## Lab 2 Integration Check

**Status: SATISFIED**

Every issue carries at least one `subsystem:*` label drawn from the brownfield analysis in `agents/analyze-repo.md §4.3`. The full set of touched subsystems is:

| Subsystem label | Sourced from analyze-repo.md | Issues |
|-----------------|------------------------------|--------|
| `subsystem:lib` | `lib/` — notification framework glue, scheduled-job base | #1, #4, #7 |
| `subsystem:config` | `config/` — notification type registry, feature flags | #1, #4, #8 (via #4), #11 |
| `subsystem:models` | `app/models/` — Assignment, Submission, Enrollment, Course | #2, #3, #5, #6 |
| `subsystem:services` | `app/services/` — DailyAssignmentDigest service object | #5, #6 |
| `subsystem:messages` | `app/messages/` — per-channel notification templates | #8 |
| `subsystem:ui` | `ui/` — React notification preferences surface | #11 |
| `subsystem:spec` | `spec/` — RSpec unit and integration tests | #9, #10, #12 |
