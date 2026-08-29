# JediKit `v0.1.0-alpha.2` gate — 2026-08-29

Status: **release gate passed; pinned GitHub install pending**.

- Runtime source commit: `b3688ff6e4aafa573a1bf65995cc9b0bae7c5ca2`
- Runtime tree SHA-256: `5a125a8a5ab811be848f8c3aeb68e5bef021545cafc4f75fafa2716808e55623`
- Release ZIP: `dist/jedikit-v0.1.0-alpha.2.zip`
- Release ZIP SHA-256: `9d636fa8c5938ce273e7aa51cca0993c2d63444377242af4ff540a222bbf2d12`

## Compatibility fix

`packages/jedikit/mcp.json` was removed. Hermes 0.20.6 assigned those
declarations new namespaced server names but did not carry `auth: oauth`, so
they duplicated the two endpoints without inheriting existing OAuth sessions.
The Hermes package now registers only two skills; provider access remains in
the working host-level `singularity` and `habitify` connections.

The release gate now fails if `packages/jedikit/mcp.json` returns. Root
`.mcp.json` remains part of the Codex/Claude plugin contract.

## Verification

| Check                              | Result                                                             |
| ---------------------------------- | ------------------------------------------------------------------ |
| Baseline / green behavior evidence | 33/33 / 33/33                                                      |
| Codex 0.151.0 local plugin smoke   | both qualified skills loaded; 0 tool calls                         |
| Hermes 0.20.6 project-plugin smoke | two skills; zero portable MCP; no diagnostics                      |
| Host-level Singularity MCP         | OAuth connected; 48 tools discovered                               |
| Host-level Habitify MCP            | OAuth connected; 12 tools discovered                               |
| Hermes doctor                      | passed on source and extracted ZIP                                 |
| Codex plugin validator             | passed on source and extracted ZIP                                 |
| ZIP contents                       | one root `.mcp.json`; no Hermes `mcp.json`; byte comparison passed |
| Procoder check                     | 0 blocking, unformatted, unchecked, or out-of-scope findings       |

Codex evidence is retained under `/tmp/jedikit-alpha2-codex.X9JNyp`; Hermes
evidence is retained under `/tmp/jedikit-alpha2-hermes.PCUTWr`. Neither smoke
called a provider tool, read account data, performed a write, or delivered an
external message.

## Release gate output

```text
cases: 33 valid
harness: ok
baseline evidence current: 33/33
green evidence current: 33/33
runtime tree sha256: 5a125a8a5ab811be848f8c3aeb68e5bef021545cafc4f75fafa2716808e55623
current provider smoke: 2/2
release gate: passed
```

The installed `alpha.1` plugin has not been changed by these pre-publication
checks. The report will be finalized after a pinned GitHub installation of the
published candidate.
