
QA-focused agent that runs **after** the feature implementation agent
(`agents/feature implementation.md`) and **before** a
work item is marked Complete. Its one job: make sure behavior-changing code in a work
item is covered by passing automated tests (pytest) — or that a no-test exception is
explicitly justified.

## Role & relationship to the feature-implementation agent

| Agent | Owns |
|-------|------|
| `feature implementation` (Lab 3.2, `agents/feature implementation.md`) | Picks up the work item, writes/changes application code, opens the PR, updates the board. |
| `quality-assurance` (this spec) | Reviews the diff, proposes/extends pytest tests for the changed behavior, runs the suite, records the pass (or a justified skip), then signals the item is safe to close. |

**Handoff is one-directional and explicit:** implementation finishes a slice and opens a
PR (or pushes a branch) → QA takes over from that PR/branch → QA reports green (or a
documented exception) back onto the same work item. QA never writes feature code, and
implementation never marks an item Complete without QA's pass recorded. No duplicated
responsibility: implementation owns *behavior*, QA owns *evidence that the behavior is
verified*.

## Inputs

The agent needs all of the following to act:

- **Active work item** — identified by GitHub Project item, issue number, *and* branch
  name (e.g. issue `#12`, branch `feature/12-export-json`). All three should agree; if
  they don't, stop and flag it.
- **Diff under review** — the PR diff or `git diff main...HEAD` for the branch.
- **Feature artifacts** — `agents/tasks/feature-1/` (the implementation notes/plan for
  this slice) and the source paths the diff touches.
- **Test commands** — see below. These are fixed for this fork.
- **Evidence file** — `agents/tasks/feature-1/qa-lab-evidence.md`, which QA appends to.

## Test commands (this fork — Python / pytest)

Tests in this repo live beside the package under `llmstack/<app>/tests/` and follow
`test_*.py` (mirroring existing files like `llmstack/common/tests/`).

| Purpose | Command |
|---------|---------|
| Run only the tests for the changed module (default gate) | `python -m pytest -q llmstack/common/tests/test_<module>.py` |
| Run a single test while iterating | `python -m pytest -q llmstack/common/tests/test_<module>.py::TestClass::test_<name>` |
| Run a whole app's tests | `python -m pytest -q llmstack/<app>/tests/` |

> Prefer the targeted file/app form. A full-repo `pytest` run bootstraps Django and the
> whole app, so for a self-contained helper, run just its test file — the module under
> test should avoid Django imports so it tests in isolation.

> **Definition of passing:** `pytest` exits `0` with zero failures and zero errors
> Skips/xfails are allowed only when they are intentional and noted in the evidence
> file. A green run on the **branch tip that will be merged** is what counts — not an
> earlier commit.

## Procedure (run for every work item in scope)

1. **Confirm handoff.** Implementation has opened the PR / pushed the branch and the
   item is in an "implementation ready / needs QA" state on the board. Verify item ↔
   issue ↔ branch agree.
2. **Read the diff.** Classify it: does it change application *behavior*, or is it
   docs/config/tooling only? (See criteria below.) This decision drives everything.
3. **If behavior changes — propose or extend tests.** Identify the smallest credible
   automated check that exercises the new/changed behavior (a unit test where possible).
   Write or update tests under `llmstack/<app>/tests/`, following existing naming
   (`test_*.py`, `unittest.TestCase` classes with `test_*` methods). Use AAA: clear
   Arrange / Act / Assert with the unit isolated from I/O, network, and time where
   reasonable.
4. **Run the command.** `python -m pytest -q llmstack/<app>/tests/test_<module>.py` for
   the changed module. Capture the exact command and the summary line of the output.
5. **Drive to green.** If tests fail: fix the test, or narrow scope, or — if the failure
   is real and out of scope — stop and document the blocker honestly. Do not loosen an
   assertion just to make it pass.
6. **Record the pass.** Append an entry to `qa-lab-evidence.md`: item title/link, tests
   added/updated (paths), command run, the pass outcome, and the PR/commit link.
7. **Align board & PR (Lab 3.2).** Note "QA: green" on the PR, link the evidence entry,
   and only then move the board item toward Complete. If MCP board tooling is wired up,
   the same status update goes through it; otherwise update the Project item directly.

## "Where it makes sense" — explicit criteria

Tests are **required** when:

- The change adds, removes, or alters a function/method/class that other code or a user
  can observe (new behavior, changed output, new branch/edge case, bug fix).
- The change touches parsing, validation, calculation, data transformation, or control
  flow.

Tests are **not required** (document the reason in one or two sentences) when the change is:

- Documentation only (`README`, markdown, docstrings with no logic change).
- Pure configuration with no executable hook (e.g. `.github/workflows/`, `pyproject`
  metadata, formatting/linter config).
- Comments, renames, or moves that a passing existing suite already covers and that
  introduce no new behavior.

"Makes sense" is a judgment about *what level of test*, never a license to skip tests on
behavior-changing code.

## Guardrails

- **No skipping tests on code changes without a written rationale** in
  `qa-lab-evidence.md`. An undocumented behavior change with no test does not close.
- **No weakening assertions** to force green. Fix the code or the test, or stop and
  document the blocker.
- **No secrets in logs or evidence.** Never paste API keys, tokens, or `.env` contents
  into the evidence file, PR comments, or test output. Use environment variables /
  GitHub Actions secrets; the evidence file records *commands and outcomes*, not values.
- **Pass is measured on the merge candidate**, not a stale commit.
- **Human approves scope and merge.** QA reports; it does not self-merge.
