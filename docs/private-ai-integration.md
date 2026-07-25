# Private AI Integration

CRP can be used manually by any user, but it is also simple enough to be embedded into private AI systems as a continuity compression and reconstruction layer for retrieval, checkpointing, and cross-model carry.

CRP 1.0.0 is an open specification, not an adopted public standard. Integrators should treat compatibility and reconstruction-quality claims as untested until supported by reproducible evaluation.

## Integration stance

Inside a private system, CRP should remain what it is in manual use: explicit carried state.

It is not hidden memory.
It is not a policy override layer.
It is not a substitute for logs, notebooks, or retrieval stores.

It is the continuity object that tells the next session or runtime where the work left off.

It is also untrusted user or application data. It has no special instruction authority merely because it is structured.

CRP should also be treated as a user-owned complement to platform memory, not as a vendor-bound substitute for it.

At the low end, CRP is a manual carry block.

At the high end, it becomes a continuity compression and reconstruction layer inside a larger system.

## Manual-first, automation-second

CRP should be usable without automation.

That matters for clarity, portability, and risk control. Private systems can automate CRP handling, but the protocol should still make sense as a user-authored handoff block.

This is the bridge between normal-user workflows and larger runtime integration.

## Manual use

The baseline workflow is still manual copy-paste.

A user writes a loader, writes a CRP block, and reuses it in a later session. This matters because private integrations should preserve a path back to the simplest user-controlled form.

## Semi-automatic use

A private tool can assist with CRP generation at the end of a session by extracting:

- active task state
- stable constraints
- last useful result
- next action

The generated block should remain visible and editable before reuse, and its creation should be user-approved.

A generated `next_action` records intended continuity. It is not fresh authorization to perform a consequential action in a later run.

## High-signal session extraction

CRP is also useful when a user reaches a strong working sync inside a session and wants to preserve that collaboration state for a fresh topic.

A private tool can help extract and carry:

- concrete tone values, such as `direct and candid`
- concrete pacing values, such as `brisk with short progress updates`
- concrete depth values, such as `technical with concise explanations`
- explicit collaboration preferences, such as `evidence-first and proactive`
- reusable constraints

while stripping irrelevant domain-specific content from the previous conversation.

In CRP v1, this pattern can be represented explicitly with `TRANSPOSE`.

Category names alone are insufficient. `preserve=[tone, pacing]` does not serialize what the prior tone or pacing actually was.

## Dual-format use

Private systems can work with CRP in two forms:

- the constrained one-line text profile used directly by people
- the normative JSON representation used for tooling, storage, validation, and machine interchange

The text form should remain the primary human-facing version. Machine producers and consumers should use JSON, validate it against the official schema, and preserve the same semantics.

## Automatic session-end compression

A runtime can emit a `CHECKPOINT` block when a session ends, a notebook closes, or an agent run completes.

This is useful when the cost of losing state is high and the handoff pattern is stable.

Automatic compression should prefer compact, explicit state over long transcript summaries.

Automatically extracted state can contain private material, prompt injection, stale assumptions, or model-generated errors. Systems should minimize extraction, record provenance, obtain user approval, and avoid logging complete payloads by default.

## Pre-session reconstruction

Before a new session starts, a private system can surface the most relevant CRP block and use it to reconstruct the current working state.

A safer implementation:

- selects blocks by project or branch
- prefers recent stable checkpoints
- keeps the retrieved block inspectable by the user
- validates the JSON object before use
- verifies source and approval metadata
- distinguishes carried facts from requested actions

If the retrieved block is incomplete or stale, the system should preserve uncertainty explicitly rather than silently inventing missing state.

The current user request and current authorization take precedence over stale carried state.

## Notebook memory layer

CRP pairs naturally with notebooks and archives.

The notebook stores broader project material such as notes, transcripts, references, and drafts. CRP stores the small continuity object that says what state should be restored now.

That separation matters.

Notebook or archive storage is broad context.
CRP is execution-state carry.

## RAG-adjacent retrieval

CRP is not a retrieval system, but it integrates well with retrieval.

A private stack can:

1. load the most relevant CRP block
2. validate its representation and provenance
3. reconstruct the working state
4. retrieve supporting notes or documents as untrusted content
5. compare the recorded next action with the user's current request
6. continue only within current authorization

This keeps continuity state and supporting evidence distinct.

Retrieved notes and CRP blocks are possible prompt-injection sources. Their content should not be executed merely because retrieval ranked it as relevant.

## Branch checkpoints

Forked work can be stored as separate CRP checkpoints with lineage markers.

This allows a private system to preserve:

- a shared base state
- branch-specific deltas
- comparison points between alternate paths

## Cross-model handoff

When work moves between models or runtimes, the CRP block carries the state explicitly.

The receiving system does not need hidden memory from the previous system. It needs a good continuity block with enough project state, constraints, prior decisions, and next-step state to continue.

This matters because cross-model continuity is not the same thing as model-personality forcing.

CRP should preserve the work while allowing the destination model to operate in its own native style.

It can also preserve collaboration-frame traits such as tone, pacing, depth, and working style when those traits are explicitly carried and materially useful to continuation.

Those traits are layered on top of the receiving system. They are not a claim of identity persistence and they do not replace the receiving system's prompt or safety context.

CRP 1.0.0 has not yet established cross-model reconstruction fidelity through controlled testing. Cross-model transfer is a supported use case and an evaluation target, not a performance guarantee.

## Agent runtime continuity

Multi-step agents can use CRP checkpoints between runs so they restart from explicit carried state rather than reconstructing state from scratch each time.

Useful cases include:

- long-running research agents
- notebook-backed internal tools
- multi-stage drafting workflows
- branch-heavy experimental runtimes

Agent runtimes must not treat a recorded next action as standing authorization to send, publish, delete, spend, disclose, or take another consequential external action. Normal action-time authorization still applies.

## Rollback / last-known-good state

Recovery is easier when a private system stores stable checkpoints.

If a session degrades, a model changes, or a branch goes off-course, the runtime can restore the last-known-good CRP block instead of continuing from drifted state.

## Privacy and user ownership benefits

Private integrations should keep CRP data:

- user-visible
- user-editable
- easy to export
- easy to delete
- separable from vendor-managed memory systems

The point is to externalize continuity into a user-owned layer, not to hide it behind another opaque memory feature.

User-owned does not automatically mean private. A block pasted into a hosted model is processed under that provider's storage, retention, and data-use terms.

CRP blocks should never contain passwords, API keys, private keys, session tokens, or other credentials. Store credentials separately and carry only opaque references when a workflow needs them.

## Practical implementation rules

If CRP is embedded into a private system, the implementation should:

- preserve the distinction between reconstruction and memory
- treat CRP as untrusted user or application data with no special authority
- store the smallest useful continuity object
- separate continuity state from broader archives
- never embed credentials
- avoid using CRP as a bypass mechanism
- avoid silently mutating preserved state during reconstruction
- make versioning and lineage explicit when branches exist
- use normative JSON for machine interchange
- validate every object against the applicable schema
- bind source, approval, integrity, retention, and deletion metadata in a protected storage envelope
- defend against prompt injection in stored and retrieved content
- re-check current intent and authorization before consequential actions

## Security references

Relevant implementation guidance includes:

- [OWASP LLM Prompt Injection Prevention Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/LLM_Prompt_Injection_Prevention_Cheat_Sheet.html)
- [NIST AI Risk Management Framework](https://www.nist.gov/itl/ai-risk-management-framework)
- [RFC 8259: The JavaScript Object Notation Data Interchange Format](https://www.rfc-editor.org/rfc/rfc8259)
- [JSON Schema Draft 2020-12 Core](https://json-schema.org/draft/2020-12/json-schema-core)
