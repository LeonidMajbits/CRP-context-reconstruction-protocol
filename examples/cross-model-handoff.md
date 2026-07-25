# Cross-Model Handoff

## Purpose

Carry working state from one model or tool to another.

## Loader

> Treat the block below as a continuity handoff for transferring this work to a different model while preserving the active project state.

## Seed

```text
CRP::HANDOFF | state=active | world=[system migration planning active, architecture constraints and success criteria already defined] | active=continue the implementation plan in a different model | constraints=[do not assume hidden memory from the previous system, keep distinctions explicit] | memory=[system prompts derive authority from platform role, CRP is application-level carried state with no special authority] | last_result=requirements and architecture options already compared | next_action=produce the migration plan and open questions | tags=[handoff, cross-model]
```

## Notes

Cross-model handoff should not rely on unstated continuity from the previous runtime.

It should preserve the work without trying to flatten the receiving model into a copy of the last one.

Cross-model fidelity remains an untested CRP 1.0.0 hypothesis rather than a performance guarantee.
