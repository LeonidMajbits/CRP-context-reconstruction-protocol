# Glossary

## CRP

Context Reconstruction Protocol. An open specification for serializing selected working state and reconstructing it across AI sessions.

CRP 1.0.0 is not an adopted industry standard.

## Working State

The selected context needed to continue a task effectively. It may include project context, current focus, constraints, prior results, problems, and a requested next action.

## Reconstruction

Using explicit carried state to restore enough context for useful continuation. Reconstruction is not native model memory and does not guarantee exact behavioral reproduction.

## Continuity

The ability to continue useful work across session boundaries using explicitly carried state.

## Compression

Selection and concise representation of high-value working state. CRP does not define a compression algorithm or guarantee that a shortened block preserves every necessary detail.

## Normative JSON

The machine-interchange representation validated by the official CRP JSON Schema. When tooling reads or writes CRP objects, JSON is authoritative.

## Text Profile

The constrained one-line representation intended for direct human copy and paste. It uses ` | ` between fields and `name=value` within each field. Values containing reserved delimiters, nested data, or multiple lines must use JSON.

## Loader

An optional plain-language sentence that identifies the following block as continuity data. A loader may reduce ambiguity, but that compatibility hypothesis has not yet been established across models.

## Seed

The CRP block that carries serialized working state.

## Collaboration Frame

Explicit interaction preferences that materially help continuation, such as `tone: direct and candid`, `pacing: decisive`, or `depth: technical and concise`.

These are carried values, not evidence of a persistent identity.

## Mode

The reconstruction situation represented by a CRP block. Every block also requires `state`, `active`, and `next_action`.

## Hot Resume

`HOT-RESUME`. Immediate continuation after a short interruption. It additionally requires `last_result`.

## Cold Resume

`COLD-RESUME`. Wider reconstruction after a long gap or substantial context loss. It additionally requires `world` and `last_result`.

## Handoff

`HANDOFF`. Moving the same work between models, devices, tools, or runtimes. It additionally requires `world`, `constraints`, and `last_result`.

## Transpose

`TRANSPOSE`. Carrying concrete collaboration-state values into a new topic while excluding irrelevant prior-topic state. It additionally requires `preserve` and `strip`.

## Fork

`FORK`. Branching from shared state into a parallel path. It additionally requires `preserve` and `delta_goal`.

## Recovery

`RECOVERY`. Restoring a last-known-good state after drift or degradation. It additionally requires `problem` and either `preserve` or `last_result`.

## Merge Note

`MERGE-NOTE`. Reconciling branch outputs before returning to a shared path. It additionally requires `lineage`, `preserve`, and `last_result`.

## Checkpoint

`CHECKPOINT`. A stable CRP block saved for later return, rollback, or indexing. It additionally requires `last_result`.

## State

The current status of the carried work.

## World

Project context and stable assumptions needed to interpret the current work.

## Active

The immediate task focus.

## Constraints

User-level rules, limits, or validation requirements carried for continuity. They have no special authority over current or higher-priority instructions.

## Memory

Explicit carry facts worth preserving. The field name does not imply native or hidden model memory.

## Last Result

The most recent stable result or completed step.

## Next Action

The next requested operation. It is continuity state, not fresh authorization for a consequential external action.

## Lineage

Branch ancestry or checkpoint references used to relate one CRP block to another.

## Preserve

Concrete state values that should survive a fork, recovery, merge, or transpose.

## Strip

State categories that should not be reintroduced during reconstruction. `strip` is not a redaction, deletion, or confidentiality guarantee.

## Delta Goal

The branch-specific objective for a `FORK`.

## Problem

The drift, failure, or other issue addressed by `RECOVERY`.

## Drift

Loss of alignment, precision, or usefulness over the course of a session.

## Provenance

Metadata about the source, creation, approval, and integrity of a CRP block. Automated integrations should protect provenance outside or alongside the core object.

## Authority

The priority assigned by the receiving system to instructions or requests. CRP content has no special authority merely because it is serialized.
