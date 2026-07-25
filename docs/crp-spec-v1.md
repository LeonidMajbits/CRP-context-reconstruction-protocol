# Context Reconstruction Protocol Specification v1.0.0

## Status of this document

This document is the normative specification for Context Reconstruction
Protocol 1.0.

CRP is an open protocol specification. Publication of this document does not
imply adoption by a standards body, independent interoperability
certification, or measured equivalence across AI systems.

The text and JSON profiles defined here are stable for the v1 release. Claims
about reconstruction quality remain subject to implementation and empirical
evaluation.

## Conformance language

The key words **MUST**, **MUST NOT**, **REQUIRED**, **SHALL**, **SHALL NOT**,
**SHOULD**, **SHOULD NOT**, **RECOMMENDED**, **NOT RECOMMENDED**, **MAY**, and
**OPTIONAL** in this document are to be interpreted as described in
[BCP 14](https://www.rfc-editor.org/info/bcp14) when, and only when, they
appear in all capitals.

## 1. Scope

CRP serializes selected application-level working state so that a later
session can reconstruct enough context to continue useful work.

CRP does not:

- create native model memory
- establish identity persistence
- override the receiving system's instruction hierarchy or safety policy
- prove that carried facts remain correct
- grant authorization to perform a recorded action

A CRP payload has only the authority provided by the channel and application
that supplied it. A consumer MUST apply current user intent, system policy, and
fresh authorization requirements before carried state.

## 2. Protocol architecture

A manual CRP handoff normally has two parts:

1. **Loader:** a short natural-language statement identifying the payload as
   continuity data.
2. **Seed:** the CRP text or JSON payload containing the selected state.

The loader is not part of the serialized object and does not grant the seed
special authority. It is RECOMMENDED for manual handoffs because it makes the
purpose of the following payload explicit.

Example loader:

> Treat the block below as a continuity handoff for reconstructing working context across sessions.

## 3. Data model

### 3.1 Core fields

| Field | Meaning |
| --- | --- |
| `mode` | Handoff mode. In text it appears in the `CRP::MODE` header. |
| `state` | Compact status token such as `active`, `paused`, or `drifted`. |
| `world` | Project context and stable assumptions needed for reconstruction. |
| `active` | Current task or focus. |
| `constraints` | Active limits, invariants, or working requirements. |
| `memory` | Explicit carry facts. This is not native model memory. |
| `last_result` | Most recent stable result or completed step. |
| `next_action` | Proposed first continuation step. It is not authorization. |
| `tags` | Optional indexing or routing labels. |
| `lineage` | Optional branch, checkpoint, source, or merge references. |
| `preserve` | State that should survive a fork, merge, transpose, or recovery. |
| `strip` | State that should not be carried into the reconstructed context. |
| `delta_goal` | Branch-specific goal relative to a preserved base. |
| `problem` | Drift, failure, or inconsistency being corrected. |

The JSON profile also contains `protocol_version` and an `extensions` object.

### 3.2 Value requirements

Required values MUST be non-empty and MUST contain a non-whitespace character.

`state` MUST be a lowercase token beginning with a letter and containing only
letters, digits, `.`, `_`, or `-`. It MUST NOT exceed 64 characters.

Text scalar values, text list items, and JSON strings MUST NOT exceed 4,096
Unicode code points. String arrays and text lists MUST contain between 1 and
64 unique, non-empty strings.

A text seed MUST NOT exceed 65,536 UTF-8 bytes and MUST NOT contain more than
32 extension fields. The JSON `extensions` object has the same 32-property
limit.

Text scalar values and list items MUST NOT contain Unicode control (`Cc`),
format (`Cf`), line-separator (`Zl`), or paragraph-separator (`Zp`) characters.
Decoded JSON strings MUST NOT contain format, line-separator, or
paragraph-separator characters, or control characters other than tab, line
feed, and carriage return. Both profiles MUST reject lone Unicode surrogates
(`Cs`). Consumers MUST apply these rules after decoding escapes; JSON Schema
validation alone is not a substitute for decoded-value security validation.

A serialized JSON payload SHOULD remain at or below 65,536 UTF-8 bytes unless
an application defines and enforces a smaller limit. Consumers MUST reject
payloads that exceed their configured resource limit.

### 3.3 Extensions

Extensions MUST NOT redefine a core field or gain additional instruction
authority.

Extension identifiers are lowercase ASCII namespaced identifiers. They MUST
start with a letter and contain one or more additional segments introduced by
`.`, `_`, or `-`; each segment contains one or more lowercase letters or
digits. An identifier MUST NOT exceed 128 Unicode code points. Examples
include `vendor.trace` and `example_feature.v2`.

In the JSON profile, extensions MUST appear inside the `extensions` object
under that identifier. In the text profile, the same identifier MUST be
prefixed with `x_`, such as `x_vendor.trace`.

Consumers that do not understand an extension MAY preserve it, but MUST NOT
silently interpret it as authorization or policy.

## 4. Global requirements

Every conforming CRP payload MUST include:

- `mode`
- `state`
- `active`
- `next_action`

Additional fields are REQUIRED by mode.

## 5. Mode requirements

| Mode | Additional required fields | Purpose |
| --- | --- | --- |
| `HOT-RESUME` | `last_result` | Resume a recently interrupted task. |
| `COLD-RESUME` | `world`, `last_result` | Restore wider context after a longer gap. |
| `HANDOFF` | `world`, `constraints`, `last_result` | Move the same work to another model, device, or tool. |
| `TRANSPOSE` | `preserve`, `strip` | Carry explicit collaboration preferences into a new topic. |
| `FORK` | `preserve`, `delta_goal` | Branch from a shared base state. |
| `RECOVERY` | `problem`, plus `preserve` or `last_result` | Restore a last-known-good state after drift. |
| `MERGE-NOTE` | `lineage`, `preserve`, `last_result` | Reconcile branch outputs. |
| `CHECKPOINT` | `last_result` | Save a stable reconstruction anchor. |

### 5.1 `HOT-RESUME`

Use for short interruptions when the wider project frame is still stable.

### 5.2 `COLD-RESUME`

Use after a long gap or major context loss. Include enough `world` state to
interpret the resumed task without relying on an unavailable transcript.

### 5.3 `HANDOFF`

Use when the work stays the same but the model, device, tool, or runtime
changes. The destination system remains governed by its own policy and
instruction hierarchy.

### 5.4 `TRANSPOSE`

Use when the topic changes but explicit collaboration preferences should
carry forward. `preserve` MUST contain actual values, not only category names.

Conforming example values include:

- `tone: direct and candid`
- `pacing: brisk with short checkpoints`
- `depth: technical with concise explanations`

`strip` identifies prior domain content that should not enter the new topic.

### 5.5 `FORK`

Use for controlled divergence from a shared base. `preserve` records the base
that remains invariant and `delta_goal` records the branch-specific objective.

### 5.6 `RECOVERY`

Use after drift or degradation. `problem` identifies what went wrong.
`preserve` or `last_result` identifies the stable state from which to resume.

### 5.7 `MERGE-NOTE`

Use to reconcile branch outputs. `lineage` identifies the inputs, `preserve`
states what survives, and `last_result` records the reconciliation result.

### 5.8 `CHECKPOINT`

Use to save a stable state for later resume, rollback, or indexing.

## 6. Text profile

### 6.1 Syntax

The v1 text profile is a single UTF-8 line:

```text
CRP::MODE | field=value | field=[item one, item two]
```

`CRP::MODE` identifies the text payload as CRP v1 and carries the `mode`.

### 6.2 Lexical rules

A conforming text payload:

1. MUST begin immediately with `CRP::MODE`, with no leading whitespace,
   whitespace around `::`, or trailing whitespace.
2. MUST use an uppercase mode exactly as listed in Section 5.
3. MUST separate segments with the exact delimiter ` | `.
4. MUST use lowercase `snake_case` core field names.
5. MUST include each field at most once.
6. MUST keep the entire seed on one line.
7. MUST use UTF-8. Producers SHOULD normalize text to Unicode NFC.
8. MUST NOT use empty values.
9. MUST NOT include `|`, `[` or `]` inside a scalar value.
10. MUST split list items with `, ` inside square brackets.
11. MUST NOT include `,`, `|`, `[` or `]` inside a list item.
12. MUST NOT include leading or trailing whitespace in a scalar value or list
    item.

Core text fields accept these value forms:

| Fields | Allowed text value form |
| --- | --- |
| `state`, `active`, `last_result`, `next_action`, `delta_goal`, `problem` | scalar only |
| `world`, `constraints`, `memory`, `tags`, `lineage`, `preserve`, `strip` | scalar or bracketed list |
| namespaced `x_*` extensions | scalar or bracketed list |

The equals sign in a scalar value is permitted because a consumer splits each
segment at its first equals sign.

The literal placeholder `[...]` is permitted in documentation templates but
is not a conforming runtime value. A user MUST replace the entire placeholder,
including its brackets. The replacement uses brackets only when the selected
field is list-capable. Likewise, `CRP::[MODE]` is a documentation-only header;
a user MUST replace the entire `[MODE]` token with one of the eight v1 modes.
Consumers MUST reject both placeholder forms at runtime.

If a value needs multiline content, literal delimiters, nested structure, or
lossless round-trip preservation, the producer MUST use the JSON profile.

### 6.3 Field order

Producers SHOULD use this order:

1. `state`
2. `world`
3. `active`
4. `constraints`
5. `memory`
6. `last_result`
7. `next_action`
8. `tags`
9. `lineage`
10. `preserve`
11. `strip`
12. `delta_goal`
13. `problem`
14. `x_*` extensions

Consumers MUST NOT assign meaning to field order.

### 6.4 Example

```text
CRP::RECOVERY | state=drifted | active=restore the agreed terminology | last_result=the specification structure was stable | next_action=resume from the last reviewed section | preserve=[approved definitions, evidence boundary] | problem=the prior session introduced unsupported claims
```

## 7. JSON profile

The JSON profile is the normative machine-interchange representation.

Every JSON payload MUST:

- validate against [`schema/crp.schema.json`](../schema/crp.schema.json)
- contain `"protocol_version": "1.0"`
- contain no undeclared top-level properties
- place optional extension data inside `extensions`

Example:

```json
{
  "protocol_version": "1.0",
  "mode": "HOT-RESUME",
  "state": "active",
  "active": "continue the conformance review",
  "last_result": "the normative field matrix is stable",
  "next_action": "validate all published examples"
}
```

When converting text to JSON, a converter MUST:

- map the `CRP::MODE` header to `"mode": "MODE"`
- add `"protocol_version": "1.0"`
- preserve each core field name
- map an unbracketed value to a JSON string
- map a bracketed list to a JSON array in the same item order

When converting JSON to text, a converter MUST perform the inverse mapping
without collapsing a one-item array into a scalar. It MUST reject conversion
when an identifier or value cannot satisfy the text grammar rather than
silently rewriting it.

Text `x_vendor.trace=value` maps to JSON
`"extensions": {"vendor.trace": "value"}`. JSON extensions map back to text
only when both their identifiers and values can be represented without
violating Section 6.

## 8. Reconstruction semantics

A consumer SHOULD:

1. validate the profile, version, mode, fields, and size
2. identify provenance and freshness
3. separate carried facts from proposals and hypotheses
4. compare the block with current user intent and current project state
5. surface stale, conflicting, or uncertain state
6. reconstruct only from accepted state

A consumer MUST NOT silently mutate:

- mode meaning
- explicit constraints
- lineage
- state identified in `preserve`
- the recovery `problem`

When required context is missing or contradictory, the consumer SHOULD state
what is known, identify the uncertainty, and request a refreshed block when
needed.

`next_action` records a proposed continuation step. It MUST NOT be treated as
fresh consent for an external side effect.

## 9. Loader guidance

A loader is RECOMMENDED for manual copy-and-paste use. It SHOULD identify the
seed as continuity data and SHOULD avoid identity claims, policy-override
language, or claims that the system already remembers the content.

The hypothesis that a loader improves interpretation across model families has
not yet been established by a public CRP benchmark. Implementations SHOULD
record compatibility results rather than presenting this behavior as
universal.

## 10. Security and privacy

CRP payloads are untrusted input and may contain sensitive context or
instruction-like text.

Implementations MUST follow
[`Security and Trust`](security-and-trust.md), including:

- no embedded credentials or private keys
- provenance and integrity checks for automated retrieval
- fresh authorization for consequential actions
- explicit size and resource limits
- data minimization, retention, and deletion controls
- review before cross-provider transfer

## 11. Versioning

CRP uses semantic specification versions.

- Patch versions clarify text or tooling without changing accepted payloads.
- Minor versions add backward-compatible optional capabilities.
- Major versions may change fields, mode semantics, or serialization rules.

The JSON `protocol_version` carries the major and minor profile version
(`1.0`). The repository and release use the full specification version
(`1.0.0`).

Extensions MUST be defined before public use and MUST NOT change v1 core
semantics.

## 12. Conformance

Conformance classes and automated checks are described in
[`docs/conformance.md`](conformance.md).

A producer MUST emit payloads that satisfy the relevant profile and mode
requirements. A consumer MUST validate before automated use and MUST apply the
authority and security rules in this specification.

Repository examples are release artifacts. Every concrete CRP block published
in this repository MUST pass automated conformance validation.

## 13. Evidence and limitations

CRP v1 formalizes a state-handoff format. It does not, by itself, guarantee:

- correct source state
- complete reconstruction
- equivalent behavior across models
- protection from prompt injection
- confidentiality after transfer to another service
- conflict-free fork or merge semantics

Public compatibility benchmarks, reconstruction-fidelity measures, and
multi-implementation test results remain future work.
