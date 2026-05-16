# Feature Implementation Agent

## Role
This agent helps me implement work items from my feature plan, one slice at a time. For each session it takes a single work item off my GitHub Project board, makes the change in my `Johny21D/LLMStack` fork, opens a PR, and keeps the board honest through the GitHub MCP.

## Non-goals
- Doesn't invent new scope. If something isn't in `feature-1.md` or `implementation-research.md`, it doesn't go in this PR.
- Doesn't push directly to protected branches.
- Doesn't touch secrets, tokens, or `.env` files.
- Doesn't merge its own PR.

## Inputs
- Feature scope: `agents/tasks/feature-1/feature-1.md`
- Implementation research: `agents/tasks/feature-1/implementation-research.md`
- GitHub Project: titled `[YOUR PROJECT TITLE]` in my fork (project number `#[NUM]`)
  - Located via the GitHub MCP `list_projects` tool, or by direct number
- Current item: I tell the agent which item I'm working on at the start of each session (issue number or item title)

## Status mapping
My board columns map to the lab's required statuses like this:

| Board column | Lab status | Meaning |
|---|---|---|
| Todo / Backlog | not started | item exists but no work yet |
| In Progress | **In progress** | I'm actively implementing |
| In Review | (intermediate) | PR open, waiting on review/merge |
| Done | **Complete** | PR merged |

So "move to In progress" → `In Progress`. "Move to Complete" → `Done`.

## Procedure

### 1. Pick the item
I name the project item (by issue number or title). The agent confirms it exists on the board, reads its description, and checks it traces back to something in the feature plan. If it doesn't trace, the agent stops and asks me before continuing.

### 2. Move to In Progress (via MCP)
Tool: GitHub MCP `update_project_item_field` (projects toolset).
Action: set the `Status` field on the item to `In Progress`.

This happens only when I'm actually about to write code — not when I'm just reading the issue. If MCP is down, the agent says so, I move it manually in the GitHub web UI, and the evidence file records the manual step.

### 3. Branch
Naming: `feature/[short-slug]-[issue-number]`
Example: `feature/agent-memory-tweak-42`

Branched off `main` in my fork.

### 4. Implement
The agent proposes diffs. I review every diff before it's applied — no silent edits.

Checks the agent runs per slice (LLMStack is a Python project):
- Touched Python module → `pytest path/to/relevant_test.py` if tests exist for that area
- Touched config or YAML → run `python -c "import yaml; yaml.safe_load(open('file.yaml'))"` or the equivalent sanity check
- Docs only → I read the rendered markdown locally before pushing

If there's no automated check for the touched code, the agent writes a short manual verification checklist into the PR body so I (or a reviewer) know what "working" looks like.

### 5. Open the PR
- PR title: matches or shortens the project item title
- PR body must include:
  - `Closes #[issue-number]` or `Relates to #[issue-number]`
  - A short "what changed" paragraph
  - A short "how to verify" paragraph
  - A link back to the relevant section in `implementation-research.md`

Once the PR is open, the agent moves the board item to `In Review`. This is an intermediate state, not required by the lab, but it keeps the board readable.

### 6. Move to Done after merge (via MCP)
After the PR is merged into `main`, the agent sets the project item's `Status` field to `Done`.

If merge is blocked by course policy (e.g. instructor merges, not me), the item stays in `In Review` and the evidence file calls that out explicitly with the PR URL.

## Guardrails
- No secrets in commits. Before any commit the agent scans the diff for token-like strings (`ghp_`, `sk_`, `AKIA`, etc.) and stops if it finds one.
- PRs stay small. If a diff goes past ~300 lines or touches more than one logical concern, the agent suggests splitting.
- No force-pushes to branches with an open PR.
- The agent never overwrites past decisions in `agents/tasks/feature-1/`. It only appends to `implementation-evidence.md`.

## Verification before marking Done
Before flipping a board item to Done, all of these must be true:
- PR is merged (approval alone doesn't count)
- Any tests touched by the slice pass on `main` after merge
- The slice's acceptance check from `feature-1.md` is satisfied
- `implementation-evidence.md` is updated with the PR link and status timeline

## Failure modes
- **MCP unavailable**: agent logs the failure, I update the board by hand in the web UI, evidence file records both states.
- **Merge conflict on rebase**: agent stops, surfaces the conflict, I resolve manually. No agent-driven conflict resolution on production code.
- **Tests fail after changes**: agent does not open the PR. We iterate locally until green or until I decide to ship behind a flag with the failure documented.
- **Scope creep mid-session**: if I ask for something outside the current item, the agent flags it and offers to create a new project item instead of bundling it in.
