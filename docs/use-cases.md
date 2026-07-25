# Use Cases

CRP is useful anywhere continuity matters more than one-shot output quality.

These are intended use cases for the CRP 1.0.0 open specification. They are not claims of measured compatibility or guaranteed reconstruction fidelity.

## Cross-session continuity

Resume a project in a new chat without rebuilding the full working context.

## Cross-device handoff

Move work between phone, desktop, and laptop while preserving the current task state.

## Cross-model transfer

Carry active context from one model or tool to another when the runtime changes.

The goal is to preserve the work, not to force the destination model to imitate the previous one.

CRP transfers project state, constraints, prior decisions, and next-step continuity while allowing the receiving model to operate in its own native style.

It can also carry collaboration-frame traits such as tone, pacing, or depth when those traits are explicitly preserved and remain useful to the work.

Cross-model fidelity has not yet been established through controlled CRP testing. Treat it as an evaluation target, not a performance guarantee.

## Cross-scope continuity

Carry a productive collaboration state into a fresh topic without dragging the full prior transcript into the new chat.

This is useful when a session has reached a strong working sync and the user wants to preserve:

- a concrete tone, such as `direct and candid`
- a concrete pacing preference, such as `brisk with short progress updates`
- a concrete depth preference, such as `technical with concise explanations`
- an explicit collaboration style, such as `evidence-first and proactive`
- relevant constraints

while stripping irrelevant domain baggage from the previous topic.

In CRP v1, this pattern is represented by `TRANSPOSE`.

This should be understood as carrying productive collaboration state, not as a claim of stable identity.

The values must be serialized explicitly. Category labels such as `tone` or `depth` cannot reconstruct a prior collaboration frame by themselves.

## Project continuity

Preserve prior decisions, constraints, and next-step state across longer projects that span many sessions.

## Forked branches

Preserve a shared base state while exploring alternate approaches in parallel.

## Recovery after drift

Restore the last stable working state after a session becomes noisy, repetitive, or misaligned.

## Checkpointing

Save stable CRP blocks at useful milestones so the work can be resumed or rolled back later.

## Research workflows

Carry distinctions, partial conclusions, and next-step state across long-running investigations.

## Notebook and archive continuity

Use CRP as the small continuity object while notebooks or archives store broader supporting material.

## Private AI integration

Use CRP as a continuity layer for compression, reconstruction, checkpointing, retrieval, and cross-model carry inside private systems.

Machine integrations should use normative JSON, validate it against the official schema, preserve provenance, and treat every block as untrusted data.

A recorded next action is not fresh authorization for a consequential external action, and CRP blocks should never contain credentials.
