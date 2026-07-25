# Implementation Notes

CRP 1.0.0 is an open specification. JSON validated by the official schema is normative for machine interchange; the one-line text profile is for human copy and paste.

## Keep the User in Control

Stored CRP blocks should remain visible and editable by the user.

## Separate Continuity from Archive

CRP carries working state. Broader notes, transcripts, and documents belong in separate storage.

## Use Checkpoints Deliberately

Checkpoint creation is cheap. Reconstruction quality depends on checkpoint quality, not checkpoint count.

## Prefer Stable Field Semantics

If tooling emits CRP blocks automatically, keep field names and meanings stable across versions.

## Match the Mode to the Goal

Use mode semantics deliberately.

- `HANDOFF` for the same work in a new environment
- `TRANSPOSE` for a new topic with preserved collaboration state
- `CHECKPOINT` for a stable return point
- `MERGE-NOTE` for branch reconciliation

## Validate Structured CRP Objects

Machine integrations should use JSON and validate every object against the official schema.

Every block requires `mode`, `state`, `active`, and `next_action`, plus the applicable mode-specific fields. Do not validate only a few generic keys.

## Treat CRP as Untrusted Data

A CRP block has no special authority.

Imported, retrieved, or model-generated blocks may contain stale facts or injected instructions. Preserve provenance, surface conflicts, and do not execute content merely because it appears in a CRP field.

## Re-Check Authorization

A recorded `next_action` is continuity state, not fresh authorization to send, publish, delete, spend, disclose, or take another consequential action.

Apply the receiving system's normal action-time confirmation rules.

## Keep Credentials Separate

Never put passwords, API keys, private keys, session tokens, or other credentials in CRP.

Carry only an opaque reference to a separately protected secret store when a workflow depends on a credential.

## Use Concrete Collaboration Values

For `TRANSPOSE`, serialize actual values such as `tone: direct and candid` or `depth: technical with concise explanations`.

Category labels such as `tone` and `depth` are not sufficient for reconstruction.

## Constrain the Text Profile

The text profile occupies one physical line, separates fields with ` | `, and uses `name=value`.

Scalar values and list items must not contain raw `|`, `[` or `]` delimiters.
Use JSON for nested, multiline, or delimiter-bearing values.

## Record Integration Metadata

Automated systems should bind protocol version, source, creation time, user approval, integrity, retention, and deletion metadata in a protected storage envelope.

## Do Not Hide Safety-Relevant State

CRP should not be framed or implemented as a mechanism for bypassing system policy.

Current and higher-priority instructions supersede stale or conflicting carried state.

## Keep Claims Evidence-Bounded

Loader effectiveness, reconstruction fidelity, and cross-model portability remain untested hypotheses unless a specific integration publishes reproducible results.
