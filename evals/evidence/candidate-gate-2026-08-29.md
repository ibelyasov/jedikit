# Candidate gate — 2026-08-29

Status: **release gate passed; candidate remains unreleased**.

- Runtime tree SHA-256: `31f882c53052c897cde8aa29ab125c46f8c953d4d9e9ef54a4b16715e2479f62`
- Candidate ZIP SHA-256: `3c05c405b502ef12d1506e8a3fcde3ac298e168c211ac7012098b25bd2843307`
- Tag created: no
- Published: no
- Final local verification duration: 8.19 s

## Behavior evidence

Current maintainer-reviewed deterministic evidence:

| Phase    | Result |
| -------- | -----: |
| Baseline |  33/33 |
| Green    |  33/33 |

Rows `M4`, `M9`, `M10`, `M11`, `M12`, `R4`, `R9`, `R10`, `R11` and `S10` were recorded against current case digests and current fake ledgers. The original 26-case files remain preserved as:

- `evals/evidence/baseline-2026-08-09.jsonl` — SHA-256 `f0bfefba3cbfb03ebfb851a215239b676cc80a5de33eb37a81067aac3aaa8abb`;
- `evals/evidence/green-2026-08-09.jsonl` — SHA-256 `5c53b19d12dd68810fb911e134129009e64a151fd78eecdaeb26123d50106519`.

## Current-tree provider smoke

| Host   | Result              | Duration | Session/thread                         | Evidence root                        |
| ------ | ------------------- | -------: | -------------------------------------- | ------------------------------------ |
| Codex  | passed              |  56.98 s | `01a04d08-8f6a-7091-a422-29efb1167bf9` | `/tmp/jedikit-codex-current.uyU7el`  |
| Hermes | passed, local stage |  73.85 s | `20260829_132223_62b1d0`               | `/tmp/jedikit-hermes-current.wCN0oM` |
| Claude | runtime unverified  |        — | —                                      | structural validation only           |

Both verified hosts loaded the exact runtime tree above, read the required skill references and completed exactly three fake MCP reads: `task_list_today(timezone=Europe/Moscow)`, `task_list_overdue(timezone=Europe/Moscow)` and broad `task_list`. Their ledgers contain 0 writes. Real OAuth, real user data, external delivery and persistent schedules were not used.

Temporary Codex plugin/marketplace and Hermes MCP entries were removed. The Hermes staged skill was moved into its retained `/tmp` evidence root. Existing Hermes `singularity` and `habitify` MCP entries remained configured; user schedules were not changed. Failed/partial Codex attempts were retained next to the successful JSONL.

## Final verification

| Stage                                                | Result                                 | Duration |
| ---------------------------------------------------- | -------------------------------------- | -------: |
| `ruff check evals/fake_mcp.py evals/run.py`          | all checks passed                      |   0.04 s |
| `ruff format --check evals/fake_mcp.py evals/run.py` | 2 files already formatted              |   0.04 s |
| `python3 evals/fake_mcp.py --self-test`              | `fake_mcp: ok`                         |   0.08 s |
| `python3 evals/run.py validate`                      | `cases: 33 valid`                      |   0.07 s |
| `python3 evals/run.py self-test`                     | `harness: ok`                          |   0.09 s |
| baseline score                                       | `33/33 passed`                         |   0.08 s |
| green score                                          | `33/33 passed`                         |   0.09 s |
| `python3 evals/run.py release-gate`                  | `release gate: passed`                 |   0.13 s |
| skill quick validator                                | `Skill is valid!`                      |   0.34 s |
| plugin validator                                     | passed                                 |   0.08 s |
| candidate ZIP checksum                               | OK                                     |   0.04 s |
| six runtime files byte-match ZIP                     | passed                                 |   0.05 s |
| `git diff --check`                                   | passed                                 |   0.04 s |
| `procoder check`                                     | 0 blocking, 0 unformatted, 0 unchecked |   6.34 s |

Full readable output: `/tmp/jedikit-final-gate.qMIZUm/validation.log` (SHA-256 `96e0aa1a73a9cacf9534051690a786e74597ca8d450b110b3f624e7b1bbe43d6`). ZIP extraction used for byte comparison was preserved at `/tmp/jedikit-zip-verify.I00xSR`. The earlier invocation-error sweep was also preserved at `/tmp/jedikit-final-gate.HnF4B4`.

## Release gate output

```text
cases: 33 valid
harness: ok
baseline evidence current: 33/33
green evidence current: 33/33
runtime tree sha256: 31f882c53052c897cde8aa29ab125c46f8c953d4d9e9ef54a4b16715e2479f62
current provider smoke: 2/2
release gate: passed
```

Passing this gate does not create a version, tag or publication. Those remain separate decisions. Claude runtime also remains explicitly `unverified`.
