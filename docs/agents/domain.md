# Domain docs

## Layout

This is a single-context repository:

- CONTEXT.md at the root: domain vocabulary and model.
- docs/adr/: architectural decision records.

## Before exploring

Read CONTEXT.md and ADRs relevant to the area being explored.
If they do not exist, proceed silently without proposing placeholders.
The domain-modeling skill creates them when terms or decisions
are resolved.

Use existing project documentation as the authority for current
behavior and decisions. Keep temporary plans in project-local
working areas.

## Vocabulary

Use domain terms as defined in CONTEXT.md in issues, proposals,
hypotheses, and tests. If a needed concept is missing, check existing
project terminology before noting a gap for domain-modeling.

## ADR conflicts

Explicitly identify any proposal that contradicts an existing ADR,
including the ADR reference and the reason for reconsidering it.
