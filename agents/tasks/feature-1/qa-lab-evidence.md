# QA Lab Evidence — feature-1

Traceability for Lab 4.1: each closed work item maps to **work item → tests run → pass
(or justified skip)**, per the procedure in `agents/quality-assurance.md`.

---

## Item 1 — Add secret-redaction helper for safe logging

- **Work item:** Add a `redact_secrets()` utility so prompts/responses logged by
  LLMStack never contain raw API keys or tokens.
  — [LINK to your GitHub Project item / issue, e.g. `#NN`]
- **Branch:** `feature/redact-secrets-NN`  *(replace NN with the issue number)*
- **Classification:** Behavior change → tests required.
- **Code added:**
  - `llmstack/common/utils/redact.py` — new module: `redact_secrets(text)` masks
    Anthropic / OpenAI / GitHub / AWS key formats; `contains_secret(text)` detects them.
- **Tests added:**
  - `llmstack/common/tests/test_redact.py` — 9 tests (AAA style), covering each key
    format, multiple secrets in one string, clean text left unchanged, non-string input,
    and the `contains_secret` true/false cases.
- **Command run:** `python -m pytest -q llmstack/common/tests/test_redact.py`
- **Outcome:** PASS — `9 passed in 0.02s`
- **PR / commit:** [LINK to your PR or commit]

---

## Summary table (instructor skim)

| # | Work item | Behavior change? | Tests | Command | Result |
|---|-----------|------------------|-------|---------|--------|
| 1 | Secret-redaction helper for safe logging | Yes | `llmstack/common/tests/test_redact.py` (9 tests) | `python -m pytest -q llmstack/common/tests/test_redact.py` | PASS — 9 passed |
