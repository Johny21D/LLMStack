# QA Lab Evidence — feature-1

Traceability for Lab 4.1: each closed work item maps to **work item → tests run → pass
(or justified skip)**. Filled in by the QA agent / human reviewer per the procedure in
`agents/quality-assurance.md`.

> Replace the bracketed `[...]` placeholders with your real values before submitting.
> Keep the example structure; add one block per work item you close in this lab.

---

## Item 1 — [behavior-changing item: e.g. "Add JSON export for entries (#12)"]

- **Work item:** [Project item title] — [link to issue/PR, e.g. `#12` / PR `#15`]
- **Branch:** `[feature/12-export-json]`
- **Classification:** Behavior change → tests required.
- **Tests added/updated:**
  - `tests/test_[module].py::test_[exports_valid_json]` — new
  - `tests/test_[module].py::test_[handles_empty_input]` — new
- **Command run:** `pytest -q tests/test_[module].py` then `pytest -q`
- **Outcome:** PASS — [paste the pytest summary line, e.g. `7 passed in 0.31s`]
- **PR / commit:** [link]

---

## Item 2 — [docs/config-only item, if you close one]

- **Work item:** [title] — [link]
- **Branch:** `[branch]`
- **Classification:** [Docs only / config only / tooling with no test hook] → **no automated test required.**
- **Rationale (1–2 sentences):** [e.g. "This change only updates the README usage
  section and adds no executable behavior, so no pytest coverage is applicable."]
- **PR / commit:** [link]

---

## Summary table (instructor skim)

| # | Work item | Behavior change? | Tests | Command | Result |
|---|-----------|------------------|-------|---------|--------|
| 1 | [#12 export JSON] | Yes | `test_[module].py` (2 new) | `pytest -q` | PASS — [N passed] |
| 2 | [#13 README update] | No | — | — | Justified skip (docs only) |
