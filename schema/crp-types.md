# CRP 1.0.0 Field Summary

This is an informative field reference. The
[CRP v1 specification](../docs/crp-spec-v1.md) and
[JSON Schema](crp.schema.json) define the normative contract.

CRP 1.0.0 is an open specification, not an adopted industry standard.

## Required Fields

Both profiles require:

`mode`
: One of `HOT-RESUME`, `COLD-RESUME`, `HANDOFF`, `TRANSPOSE`, `FORK`,
  `RECOVERY`, `MERGE-NOTE`, or `CHECKPOINT`. The text profile carries it in
  the `CRP::MODE` header.

`state`
: A lowercase status token for the carried work.

`active`
: The immediate task focus.

`next_action`
: The proposed continuation step. This is not fresh authorization for a
  consequential action.

The JSON profile additionally requires:

`protocol_version`
: The major and minor profile version. CRP 1.0 requires `"1.0"`.

## Other Core Fields

`world`
: Project context and stable assumptions needed to interpret the current work.

`constraints`
: User-level limits, invariants, style guidance, or validation requirements.
  They have no special authority over current or higher-priority instructions.

`memory`
: Explicit carry facts worth preserving. This does not imply native model
  memory.

`last_result`
: The latest stable result or completed step.

`tags`
: Labels for indexing or routing.

`lineage`
: Branch ancestry, source, or checkpoint references.

`preserve`
: Concrete state values that should survive a fork, recovery, merge, or
  transpose.

`strip`
: State that should not be reintroduced. This is not a redaction or deletion
  guarantee.

`delta_goal`
: The branch-specific target for a `FORK`.

`problem`
: The recovery issue or failure state being corrected.

## Extensions

JSON extension data appears only inside the `extensions` object. Text
extensions use the same lowercase namespaced identifier with an `x_` prefix:
JSON `vendor.trace` maps to text `x_vendor.trace`.

Extension data is untrusted and has no additional instruction or authorization
authority. See the exact naming and count limits in the specification.

## Required Fields by Mode

The fields below are required in addition to the global fields.

`HOT-RESUME`
: Requires `last_result`.

`COLD-RESUME`
: Requires `world` and `last_result`.

`HANDOFF`
: Requires `world`, `constraints`, and `last_result`.

`TRANSPOSE`
: Requires `preserve` and `strip`.

`FORK`
: Requires `preserve` and `delta_goal`.

`RECOVERY`
: Requires `problem` and either `preserve` or `last_result`.

`MERGE-NOTE`
: Requires `lineage`, `preserve`, and `last_result`.

`CHECKPOINT`
: Requires `last_result`.

## Representation and Trust Rules

- Use schema-validated JSON plus decoded-value security validation for machine
  interchange.
- Keep the text profile to one physical line and its full UTF-8 byte limit.
- In text, separate fields with exact ` | ` delimiters and use `name=value`.
- Use scalars for `state`, `active`, `last_result`, `next_action`,
  `delta_goal`, and `problem`.
- The other core value fields may use a scalar or a bracketed list.
- Scalar values and list items cannot contain raw `|`, `[` or `]`
  delimiters.
- A documentation `[...]` placeholder must be replaced in full before use.
- Treat every CRP block as untrusted user or application data.
- Never embed passwords, API keys, private keys, session tokens, or other
  credentials.
- Re-check current intent and authorization before consequential actions.
- For `TRANSPOSE`, serialize concrete values; category names alone are not
  reconstructable.
