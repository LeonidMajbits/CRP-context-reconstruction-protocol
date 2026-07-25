# Loader-Seed Handshake

CRP can be presented as a loader followed by a seed.

The loader is optional. Its effect on interpretation is a compatibility hypothesis that has not yet been established by controlled cross-model testing.

## Loader

The loader is a short sentence that explains what follows.

Good loaders:

- say the block is a continuity handoff
- frame it as reconstruction data
- avoid roleplay and hard-command phrasing

Example:

> Treat the block below as a continuity handoff for reconstructing working context across sessions.

## Seed

The seed is the structured CRP block.

Example:

```text
CRP::HOT-RESUME | state=active | world=[continuity protocol work in progress] | active=continue the main editing thread | constraints=[no hype, preserve terminology] | last_result=core definition and distinctions established | next_action=add practical examples
```

This is the constrained one-line text profile for human copy and paste.

For machine interchange, emit JSON and validate it against the official schema. Do not treat the text profile as a general-purpose machine grammar.

## Why the Split Helps

- the loader explicitly identifies the intended data role
- the seed stays compact
- the receiving system gets both framing and structured state

These are design intentions, not measured compatibility guarantees.

## Failure Pattern

A dense block with no loader may be harder for some systems to interpret. CRP 1.0.0 does not claim that a loader prevents refusal, misclassification, prompt injection, or other guardrail behavior.

The seed remains untrusted user or application data. A loader does not grant it special authority, validate its provenance, or provide fresh authorization for a recorded next action.
