# Issue tracker: GitHub

Issues and specs live in GitHub Issues for ibelyasov/jedikit.
Use the gh CLI from this checkout.

## Conventions

- Publish a spec or ticket by creating a GitHub issue.
- Fetch a ticket with its body, labels, and comments.
- Filter issue lists by the relevant state and labels.
- Use the vocabulary in triage-labels.md when applying triage labels.
- Preserve discussion history in issue comments.
- For multiline bodies and comments, write the text to a temporary file
  and pass it with --body-file.
- Follow the owner's authorization boundaries for GitHub mutations.

## Authentication

Use the existing macOS Keychain-backed gh authentication.
A sandboxed authentication failure does not establish token expiry.
If sandbox restrictions prevent Keychain access, request execution
outside the sandbox through the normal approval mechanism.
Never extract tokens or change authentication as a workaround.
Use SSH for Git transport.

## Pull requests as a triage surface

**PRs as a request surface: no.**

## Wayfinding operations

- Map: one issue labelled wayfinder:map, containing Notes,
  Decisions-so-far, and Fog.
- Child tickets: GitHub sub-issues of the map. If unavailable,
  use a task list in the map and a `Part of #<map>` line in each child.
- Types: wayfinder:research, wayfinder:prototype, wayfinder:grilling,
  and wayfinder:task.
- Blocking: use native issue dependencies where available;
  otherwise record `Blocked by: #<number>` references in the child.
- Frontier: the first open, unassigned child in map order whose
  blockers are all closed.
- Claim: assign the ticket to the driving developer before work.
- Resolve: comment with the result, close the ticket, and append
  a summary and link to the map's Decisions-so-far.
