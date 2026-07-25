# System Prompts and CRP

System prompts and CRP describe different concerns, but “instruction” and “context” are not mutually exclusive content types.

The precise distinction is:

- a system prompt occupies a higher-priority instruction role defined by the receiving platform;
- a CRP block is application-level user or application data used to reconstruct selected working state.

CRP has no special authority merely because it is structured.

## System Prompt

A system prompt commonly supplies higher-priority instructions for a model session.

Depending on the platform, it may:

- define behavior and boundaries;
- establish policy or tool rules;
- shape tone or output requirements;
- be visible or hidden;
- be authored by a platform, application, developer, or local user.

System prompts are defined by their role in the receiving system's instruction hierarchy, not simply by whether their text looks like an instruction.

## CRP

Context Reconstruction Protocol serializes selected working state for later reconstruction.

A CRP block can carry:

- project context;
- current objective;
- prior results;
- user-level constraints;
- concrete collaboration preferences;
- unresolved problems;
- a requested next action.

Some of those fields are descriptive, while others contain user-level requested behavior. The entire block remains untrusted user or application data.

## Authority Rule

A CRP block cannot:

- replace or override a system prompt;
- bypass platform policy;
- gain higher instruction priority;
- prove that its contents are true or current;
- provide standing authorization for an external action.

A recorded `next_action` is historical continuity state. The receiving system must compare it with the user's current request and apply normal action-time authorization.

## Why the Distinction Matters

CRP addresses a continuity problem:

> What selected state should be carried so another session can understand where the work left off?

A system prompt addresses an instruction-hierarchy problem:

> What higher-priority rules govern this session?

The same message can contain both contextual facts and requested actions, so a slogan cannot replace the authority model.

A precise summary is:

> System prompts supply higher-priority session instructions. CRP supplies application-level carried state with no special authority.

## Personality and Collaboration State

CRP can carry concrete collaboration preferences, for example:

- `tone: direct and candid`;
- `pacing: brisk with short progress updates`;
- `depth: technical with concise explanations`;
- `collaboration style: evidence-first and proactive`.

These are explicit carried values. They do not demonstrate identity persistence, and they do not require the destination model to imitate another model exactly.

Category names alone are insufficient. `preserve=[tone, pacing]` does not tell a new session what the tone or pacing should be.

## Side-by-Side Example

### Higher-priority system instruction

```text
You are a concise research assistant. Prioritize technical accuracy and follow the application's tool-authorization policy.
```

### CRP state

```text
CRP::COLD-RESUME | state=paused | world=[research project on continuity architecture is active] | active=restore the main analysis thread | constraints=[use direct language, separate verified facts from hypotheses] | last_result=core terminology and distinctions stabilized | next_action=draft the evaluation plan
```

The CRP block describes project state and user-level requested continuation. It remains subordinate to current and higher-priority instructions.

## Can They Be Used Together?

Yes.

A receiving application can use its normal system instructions while accepting a CRP block as user or application data. The application should validate machine-readable CRP as JSON, preserve provenance, surface conflicts, and avoid executing a recorded action without current authorization.

## Evidence Status

CRP 1.0.0 is an open specification, not an adopted public standard.

Its cross-model reconstruction fidelity and loader behavior have not yet been established through controlled comparative testing. They should be presented as use cases and hypotheses rather than guarantees.

## Bottom Line

System prompts and CRP operate at different layers.

System prompts derive authority from their platform-defined role. CRP carries selected working state and derives no authority from its format.
