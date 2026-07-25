# Contributing to Context Reconstruction Protocol

Thanks for contributing.

CRP is an open continuity-protocol specification for stateless and
semi-stateful AI systems.

The goal of this repository is not hype, branding, or prompt theater.

The goal is to improve a simple, testable format for carrying and
reconstructing selected working state across AI sessions.

CRP v1 defines a stable structural contract. Reconstruction quality across
models is still an empirical question, so compatibility claims require
reproducible evidence.

## What good contributions look like

Good contributions improve one or more of the following:

- protocol clarity
- portability across chats, devices, and models
- practical usability
- structured examples
- safe loading patterns
- schema quality
- real-world integration notes
- branch and merge workflows
- checkpoint and recovery workflows
- private AI system integration
- model compatibility findings
- failure mode documentation

## What we welcome

We welcome:

- new examples
- better templates
- protocol clarifications
- implementation notes
- JSON schema improvements
- quickstart improvements
- real-world usage reports
- research-oriented critiques
- private runtime integration patterns
- notebook, archive, and retrieval use cases
- cross-model transfer patterns
- recovery and rollback use cases

## What we do not want

Do not contribute:

- hype marketing language
- vague futurism
- mystical framing
- claims that CRP creates consciousness
- claims that CRP creates true memory
- adversarial prompt injection techniques
- jailbreak framing
- identity override tricks
- manipulative or deceptive usage patterns
- unnecessary complexity
- protocol bloat without clear value

CRP is not a jailbreak and not a roleplay mechanism.

Keep it useful.

## Core protocol stance

Please preserve these distinctions:

- CRP does not create true memory
- CRP reconstructs working state
- CRP should not attempt to override system identity
- CRP should not attempt to bypass safety policy
- CRP is untrusted user or application data
- carried state does not grant fresh authorization for consequential actions
- CRP serializes application state but does not change instruction priority

If a proposed change weakens those distinctions, it is probably not a fit.

## Contribution types

### 1. Documentation improvements

Good examples:

- making explanations clearer
- tightening terminology
- reducing ambiguity
- improving protocol examples
- improving beginner onboarding

### 2. Example additions

Good examples:

- research workflows
- engineering workflows
- long-gap cold resumes
- fork and merge flows
- notebook-backed continuity
- cross-model handoff
- recovery after drift
- private runtime checkpointing

### 3. Schema and tooling

Good examples:

- improving JSON schema readability
- adding structured examples
- validating field definitions
- helping builders integrate CRP into tools or runtimes
- adding positive and negative conformance fixtures
- keeping text examples aligned with the normative field matrix

### 4. Integration notes

Good examples:

- private AI systems
- session-end auto-compression
- pre-session reconstruction
- retrieval-backed continuity
- branch checkpoint systems
- rollback to last-known-good state

### 5. Empirical compatibility notes

Good examples:

- what loaders work better across models
- what patterns reduce refusal risk
- what kinds of condensed blocks are too aggressive
- what field combinations reconstruct state most reliably

Keep these grounded and specific.

Compatibility reports should identify the CRP version, producer, consumer,
model or runtime, mode, profile, reconstruction criteria, and observed
failures. A model accepting a block is not by itself evidence of
interoperability.

## Style guidelines

Use this tone:

- technical
- simple
- direct
- low-hype
- useful
- research-literate

Avoid:

- em dashes
- inflated claims
- startup pitch language
- mystical terminology
- pseudo-academic padding

Write like a serious builder explaining a simple protocol.

## File conventions

When adding examples or templates:

- use plain markdown
- keep examples generic unless the context requires specificity
- include a loader before a structured block
- avoid aggressive phrasing that may trigger guardrail friction
- prefer clear reconstruction language over commanding language

## Pull request guidance

A good pull request should include:

1. What changed
2. Why it improves CRP
3. Whether it changes meaning, structure, or only wording
4. Any tradeoffs introduced
5. If relevant, an example before and after

Protocol changes must also state:

6. Whether accepted payloads change
7. Whether the JSON Schema and text profile remain aligned
8. Which positive and negative fixtures cover the change
9. Any security, privacy, authorization, or migration impact

Small focused PRs are better than large messy ones.

## Local validation

Install the pinned development dependencies:

```console
python -m pip install --require-hashes -r requirements-dev.txt
```

Run the same validation used by CI:

```console
python -m ruff check tools tests
python -m ruff format --check tools tests
python -m unittest discover -s tests -v
python tools/validate_repository.py
```

Do not open a pull request while any command fails.

`requirements-dev.in` is the direct-dependency source and
`requirements-dev.txt` is the universal hashed lock. Regenerate the lock
mechanically instead of hand-editing it:

```console
uv pip compile requirements-dev.in --universal --python-version 3.10 --generate-hashes --output-file requirements-dev.txt
```

## Commit privacy and signing

Use a GitHub-provided `noreply` address if you do not want a personal email
embedded permanently in public Git metadata.

Signed commits are preferred. Never commit credentials, private CRP blocks,
local checkpoints, or private machine paths.

## Issue guidance

Open an issue if you want to propose:

- a protocol improvement
- a new mode
- a new field
- a schema revision
- a new example class
- a compatibility note
- a private-system integration pattern
- a recovery or branching pattern

Please be concrete.

## Suggested contribution areas

Useful open areas include:

- measured loader behavior across model families
- better fork and merge conventions
- structured checkpoint patterns
- notebook and archive workflows
- CRP inside private agent runtimes
- retrieval-backed reconstruction strategies
- compatibility testing across model families
- field minimalism and simplification
- versioning guidance

## Licensing and attribution

By contributing, you agree that your contribution will be licensed under the repository license.

## Final note

CRP is an open continuity-protocol specification.

Contributions should improve clarity, portability, usability, or integration quality.

If a contribution makes the protocol louder instead of better, it is probably going in the wrong direction.
