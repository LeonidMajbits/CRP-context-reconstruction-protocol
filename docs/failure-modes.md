# Failure Modes

CRP is useful, but it is not automatic, authoritative, or self-correcting. These are the main ways reconstruction quality or integration safety can degrade.

## Over-condensation

If the block is too compressed, the next session may reconstruct the wrong state or miss an important constraint.

## Ambiguity drift

If field values are vague, different sessions may interpret them differently.

## Stale carry

Old state can become drag if it is preserved after the project has materially changed.

## Misclassification

Aggressive, theatrical, or overly dense loaders can make the handoff harder to interpret correctly.

The inverse claim is not guaranteed: a plain loader may reduce ambiguity, but its effect has not yet been established across models.

## False precision

A polished block can still encode weak assumptions. Compact formatting does not guarantee correctness.

## Summary-state confusion

A summary of what happened is not always enough to continue the work.

CRP should carry execution state, not only recap prose.

## Archive-state confusion

Large notes, transcripts, and reference material should not be collapsed into the continuity block without selection.

Keep broader archives and active continuity state separate.

## Model variance

Different systems reconstruct the same CRP block with different fidelity.

CRP 1.0.0 does not yet publish controlled cross-model compatibility results.

## Category-only carry

A block may name a dimension without serializing its value.

For example, `preserve=[tone, pacing]` does not tell a new session what the tone or pacing should be. Carry concrete descriptions instead.

## Delimiter ambiguity

Text-profile scalar values and list items cannot safely represent raw `|`,
`[` or `]` characters, nested data, or multiline values.

Use normative JSON whenever a value needs those forms.

## Prompt injection and untrusted retrieval

A CRP block is untrusted user or application data. Imported, retrieved, or model-generated blocks may contain instructions that were not authorized by the current user.

Validate the representation, preserve provenance, distinguish data from requested actions, and never execute content solely because it appears in a CRP field.

## Stale authorization

A recorded `next_action` may describe what a prior session intended to do, but it is not fresh authorization to send, publish, delete, spend, expose data, or perform another consequential action.

Apply current authorization and confirmation rules at action time.

## Secret and privacy leakage

Portable blocks can cross providers, devices, logs, and storage systems.

Never embed credentials. Minimize sensitive state, remove it before serialization when possible, and do not treat `strip` as a redaction or deletion mechanism.

## Provenance failure

Without trustworthy source metadata, a receiving system may not know whether a checkpoint is authentic, current, or user-approved.

Automated integrations should bind CRP content to provenance and retention metadata in a protected storage envelope.
