# Context Reconstruction Protocol

## Design Note for the CRP 1.0.0 Open Specification

### Version 1.0

**Status:** Public, non-peer-reviewed technical design note

**Specification version:** 1.0.0

**Author:** Leonid Majbits

## Abstract

Context Reconstruction Protocol, or CRP, is an open specification for carrying selected working state between AI sessions.

CRP serializes project context, current work, constraints, prior results, and the next requested action so a receiving session can reconstruct enough state to continue. It does not create model memory, prove identity persistence, or gain authority over the receiving system.

CRP has two representations:

- JSON validated by the official JSON Schema is normative for machine interchange.
- A constrained one-line text profile is provided for direct human copy and paste.

This note explains the design. The normative contract is defined by the versioned specification and schema.

## 1. Publication and Evidence Status

CRP 1.0.0 is an open specification, not an adopted industry standard.

This document has not been peer reviewed. It does not claim controlled evidence for model compatibility, loader effectiveness, reconstruction fidelity, or cross-model performance.

The current evidence status is:

- the JSON representation is mechanically testable against the published schema;
- the examples demonstrate intended semantics;
- manual continuity is a design use case, not a measured performance guarantee;
- improved interpretation from a loader sentence is a hypothesis that still requires comparative testing;
- cross-model and cross-provider reconstruction fidelity has not yet been established empirically.

Compatibility or effectiveness claims should remain explicitly provisional until reproducible evaluations are published.

## 2. Problem

AI work often spans more than one chat, model, device, or runtime. Useful state can be lost when the active context is no longer available.

The practical state worth carrying may include:

- project context;
- current task focus;
- constraints and invariants;
- prior decisions or stable results;
- unresolved problems;
- the next requested action;
- explicit collaboration preferences when they materially help continuation.

CRP represents that selected state in a portable object. It does not preserve the full transcript by default.

## 3. Definition

CRP is an application-level state serialization and reconstruction specification.

It performs three conceptual operations:

1. **Selection:** choose the state necessary for continuation.
2. **Serialization:** represent that state in a CRP object or one-line human profile.
3. **Reconstruction:** present the carried state to a receiving session without treating it as hidden memory or higher-authority policy.

Reconstruction is successful only to the extent that the selected state is accurate, current, sufficiently detailed, and interpreted correctly.

## 4. Authority and Trust

CRP data has no special instruction priority.

A CRP block is untrusted user or application data. Its content remains subordinate to:

1. applicable law and platform policy;
2. the receiving system's higher-priority instructions;
3. the user's current request and current authorization;
4. the carried state.

Fields such as `constraints` and `next_action` may contain requested behavior, but their presence in CRP does not convert them into system-level instructions.

A recorded `next_action` is historical continuity state. It is not fresh authorization to:

- send a message;
- publish or deploy;
- delete or overwrite data;
- spend money;
- expose private information;
- perform another consequential external action.

Before taking such an action, the receiving system must apply its normal authorization and confirmation rules.

Automated integrations should validate provenance, separate trusted metadata from untrusted content, and avoid executing retrieved text merely because it appears inside a CRP object.

## 5. Representations

### 5.1 Normative JSON representation

JSON is normative for machine interchange.

Machine producers and consumers should:

- emit valid JSON as defined by [RFC 8259](https://www.rfc-editor.org/rfc/rfc8259);
- validate objects against the versioned CRP JSON Schema;
- reject objects that fail required-field or mode-specific validation;
- preserve string and array meanings during storage and transfer;
- treat unknown or extension content as untrusted data;
- include the required `protocol_version` field and preserve it in any storage envelope.

The schema uses JSON Schema Draft 2020-12.

### 5.2 Human-readable text profile

The text profile is a one-line format intended for direct human use:

```text
CRP::HOT-RESUME | state=active | active=continue protocol review | last_result=core terminology approved | next_action=review the remaining examples
```

For CRP 1.0.0:

- the block occupies one physical line;
- fields are separated by ` | `;
- each field uses `name=value`;
- list-like values use square brackets and comma-separated items;
- field names and mode values are case-sensitive;
- scalar values and list items must not contain raw `|`, `[` or `]`
  delimiter characters;
- duplicate fields are not permitted;
- values requiring delimiter characters, nested structure, or multiple lines must use JSON instead.

The text profile is human-readable and deliberately constrained. It is not the normative machine interchange format.

### 5.3 Loader

A loader is an optional plain-language sentence identifying the following block as continuity data.

Example:

> Treat the block below as a continuity handoff for reconstructing working context across sessions.

The hypothesis is that explicit framing may reduce ambiguity for some receiving systems. That hypothesis has not yet been validated across model families, so a loader must not be described as a guaranteed compatibility or safety mechanism.

## 6. Core Fields

Every CRP block requires:

- `mode`;
- `state`;
- `active`;
- `next_action`.

The core fields are:

`mode`
: The reconstruction situation.

`state`
: The current status of the carried work.

`world`
: Project context and stable assumptions needed to interpret the work.

`active`
: The immediate task focus.

`constraints`
: User-level rules, limits, or validation requirements that remain relevant.

`memory`
: Explicit carry facts. This name does not imply native model memory.

`last_result`
: The latest stable result or completed step.

`next_action`
: The next requested operation, subject to current authorization.

`tags`
: Optional indexing or routing labels.

`lineage`
: Branch, checkpoint, or ancestry references.

`preserve`
: Concrete state values that should survive a transition.

`strip`
: State categories that should not be reintroduced during reconstruction.

`delta_goal`
: The branch-specific objective for a fork.

`problem`
: The failure or drift condition addressed by recovery.

## 7. Modes and Required State

In addition to `mode`, `state`, `active`, and `next_action`, each mode has these requirements:

| Mode | Additional required fields |
| --- | --- |
| `HOT-RESUME` | `last_result` |
| `COLD-RESUME` | `world`, `last_result` |
| `HANDOFF` | `world`, `constraints`, `last_result` |
| `TRANSPOSE` | `preserve`, `strip` |
| `FORK` | `preserve`, `delta_goal` |
| `RECOVERY` | `problem`, plus either `preserve` or `last_result` |
| `MERGE-NOTE` | `lineage`, `preserve`, `last_result` |
| `CHECKPOINT` | `last_result` |

The JSON Schema is authoritative for machine validation.

## 8. Concrete Collaboration-State Values

CRP must serialize values, not merely name categories.

This is insufficient for a new session:

```text
preserve=[tone, pacing, depth]
```

It names dimensions but does not say what their values were.

A useful `TRANSPOSE` block records the actual collaboration state:

```text
CRP::TRANSPOSE | state=stable | active=begin the new topic with the recorded collaboration preferences | next_action=ask for the new topic and apply only the explicit preserved preferences | preserve=[tone: direct and candid, pacing: brisk with short progress updates, depth: technical with concise explanations, collaboration style: evidence-first and proactive] | strip=[prior domain-specific facts and unfinished tasks]
```

Descriptions should be specific enough to reconstruct without access to the prior transcript.

## 9. Reconstruction Rules

A receiving system should:

1. validate the representation when machine processing is involved;
2. identify the source and trust level of the block;
3. distinguish carried facts from requested actions;
4. compare carried state with the user's current request;
5. identify stale, conflicting, incomplete, or unverifiable values;
6. avoid inventing missing state;
7. reconstruct only the state necessary for the current task;
8. seek current authorization before consequential actions.

If current instructions conflict with a CRP block, the conflict should be surfaced rather than silently resolved in favor of stale state.

## 10. Security and Privacy

CRP can contain sensitive project or personal information.

Implementations should:

- never embed passwords, API keys, private keys, session tokens, or other credentials;
- use opaque references to a separate secret manager when a workflow depends on a credential;
- minimize collected state;
- obtain user approval before automatically saving extracted state;
- apply appropriate access control, encryption, retention, and deletion rules;
- avoid logging full CRP payloads by default;
- preserve provenance for retrieved or generated blocks;
- validate data before use;
- treat RAG documents, imported blocks, and model-generated checkpoints as possible prompt-injection sources;
- re-check authorization at action time.

The `strip` field is reconstruction guidance, not a redaction or deletion guarantee. Sensitive content should be removed before serialization.

Relevant implementation guidance includes the [OWASP LLM Prompt Injection Prevention Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/LLM_Prompt_Injection_Prevention_Cheat_Sheet.html) and the [NIST AI Risk Management Framework](https://www.nist.gov/itl/ai-risk-management-framework).

## 11. Limits

CRP does not guarantee:

- correct or complete source state;
- consistent interpretation across models;
- recovery of information that was not serialized;
- resistance to prompt injection without integration controls;
- authenticity without provenance controls;
- exact reproduction of tone or behavior;
- durable memory or identity continuity;
- safe execution of a recorded next action.

Text compression can remove necessary detail. Conversely, excessive carry can preserve stale assumptions, private material, or irrelevant context.

## 12. Evaluation Agenda

Claims about effectiveness should be tested with published methods and fixtures.

Useful evaluation dimensions include:

- required-field and round-trip conformance;
- reconstruction accuracy against a known source state;
- constraint retention;
- stale-state detection;
- resistance to injected instructions;
- privacy leakage;
- loader versus no-loader interpretation;
- cross-model variance;
- failure behavior for ambiguous or incomplete blocks.

Until such tests exist, compatibility statements remain hypotheses rather than established results.

## 13. Normative and Informative Sources

Normative CRP artifacts:

- [CRP Specification v1](crp-spec-v1.md)
- [CRP JSON Schema](../schema/crp.schema.json)
- [Security and trust model](security-and-trust.md)

Informative CRP references:

- [CRP field summary](../schema/crp-types.md)
- [Conformance guide](conformance.md)

External technical references:

- [RFC 8259: The JavaScript Object Notation Data Interchange Format](https://www.rfc-editor.org/rfc/rfc8259)
- [JSON Schema Draft 2020-12 Core](https://json-schema.org/draft/2020-12/json-schema-core)
- [OWASP LLM Prompt Injection Prevention Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/LLM_Prompt_Injection_Prevention_Cheat_Sheet.html)
- [NIST AI Risk Management Framework](https://www.nist.gov/itl/ai-risk-management-framework)

## 14. Acknowledgments

CRP was developed through iterative human-AI collaboration by Leonid Majbits with OpenAI's ChatGPT and Codex.

These systems assisted with concept exploration, drafting, critique, and refinement. Responsibility for the published specification remains with the author.

## 15. One-Line Definition

Context Reconstruction Protocol is an open specification for serializing selected working state and reconstructing it across AI sessions without granting the carried state special authority.
