# JediKit `v0.1.0-alpha.1` gate — 2026-08-29

Status: **release gate passed**.

- Runtime source commit: `290141c753196ad563356e14785663ecc6dd38a7`
- Runtime tree SHA-256: `9ec62367ddf0d33f1d368c1528e1cec937193e969e2626646d4711cd3b202340`
- Release ZIP: `dist/jedikit-v0.1.0-alpha.1.zip`
- Release ZIP SHA-256: `0048af50baf7d1d8d90a5640814f881a85ec527f4f7377088e099824173ee260`

## Behavior evidence

| Phase    | Result |
| -------- | -----: |
| Baseline |  33/33 |
| Green    |  33/33 |

The original 26-case files remain preserved as `baseline-2026-08-09.jsonl` and
`green-2026-08-09.jsonl`. The current release gate validates all 33 case
digests, the fake MCP harness and full-runtime host-smoke freshness.

## Current runtime smoke

| Host   | Result                              | Evidence root                      |
| ------ | ----------------------------------- | ---------------------------------- |
| Codex  | passed, installed plugin skills     | `/tmp/jedikit-codex-alpha.ZhgOnN`  |
| Hermes | passed, pinned GitHub plugin skills | `/tmp/jedikit-hermes-alpha.3dgyI2` |
| Claude | runtime unverified                  | structural validation only         |

Codex CLI `0.151.0` installed `jedikit@jedikit-alpha-290141c` through a real
local marketplace and loaded both qualified child skills in a fresh ephemeral,
read-only session. The response reproduced the task intents/read-back boundary,
the native undo/read-back gate for a direct habit status log and the Off Mode
fallback. No MCP tool, user file or real account data was read; the temporary
Codex plugin and marketplace registrations were removed, while all logs remain.

Hermes Agent `0.20.6` installed and enabled the package in one command from
`ibelyasov/singularity-jedi-skill/packages/jedikit`, pinned to the exact runtime
commit. Its install security scan returned `SAFE`; installed-tree scan returned
`Allowed (clean scan)`. Both namespaced child skills loaded successfully through
`skills_list`/`skill_view`, and both portable MCP definitions registered.

### Hermes OAuth limitation

Hermes `0.20.6` translates Portable Agent Plugin HTTP entries using only
`type`, `url` and `headers`; it does not propagate native `auth: oauth`.
`hermes mcp login` also enumerates only host-level `mcp_servers`. The two
namespaced plugin MCP connections therefore failed authentication without
reading provider data. Existing working host-level `singularity` and `habitify`
connections were retained and were not used by the smoke. Token files were not
copied and the security scan was not disabled.

## Final verification

| Stage                     | Result                                 |   Duration |
| ------------------------- | -------------------------------------- | ---------: |
| Ruff check/format         | passed                                 |     0.06 s |
| Fake MCP + eval harness   | passed                                 |     0.24 s |
| Release gate              | `2/2`; passed                          |     0.10 s |
| Four skill validators     | passed                                 |     0.25 s |
| Codex plugin validator    | passed                                 |     0.11 s |
| Hermes package doctor     | passed                                 |     0.25 s |
| Installed Hermes smoke    | `SAFE`; two skills; two MCP registered |     0.53 s |
| ZIP checksum/byte compare | passed                                 |     0.13 s |
| Git diff check            | passed                                 |     0.04 s |
| Procoder check            | 0 blocking/unformatted/unchecked       |     5.03 s |
| **Total**                 | **passed**                             | **7.12 s** |

Full readable output:
`/tmp/jedikit-alpha-final-gate.h6NBNe/validation-2.log` (SHA-256
`6be0620c87c16720d2c576e7877aa28c8f7d8381a1647b3f135876d9ac7911af`).
The first formatting-failed run is preserved as `validation.log`. Final ZIP
extraction used for byte comparison is preserved at
`/tmp/jedikit-alpha-final-archive.jFmPNX`; earlier archive candidates are under
`/tmp/jedikit-alpha-package.UsWyPj`.

## Release gate output

```text
cases: 33 valid
harness: ok
baseline evidence current: 33/33
green evidence current: 33/33
runtime tree sha256: 9ec62367ddf0d33f1d368c1528e1cec937193e969e2626646d4711cd3b202340
current provider smoke: 2/2
release gate: passed
```

Passing this gate does not itself create a tag or GitHub release. Claude runtime
and plugin-provided Hermes OAuth remain explicitly unverified/blocked as stated
above.
