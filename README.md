# Context Reconstruction Protocol (CRP)

[![Validation](https://github.com/LeonidMajbits/CRP-context-reconstruction-protocol/actions/workflows/validation.yml/badge.svg)](https://github.com/LeonidMajbits/CRP-context-reconstruction-protocol/actions/workflows/validation.yml)
[![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

CRP is an open specification for serializing selected working state and
reconstructing it in a later AI session.

It does not create memory, preserve identity, or grant instructions special
authority. It carries an explicit, user-inspectable state object so work can
resume without replaying an entire transcript.

## Status

- Specification version: **1.0.0**
- Protocol profile: **CRP 1.0**
- License: **MIT**
- Stability: the v1 syntax and schema are defined and automatically validated
- Evidence boundary: cross-model reconstruction quality and loader effectiveness
  have not yet been established by a public benchmark

CRP is an open protocol specification. It is not an adopted industry standard,
and this repository does not claim independent interoperability certification.

## Minimal example

Loader:

> Treat the block below as a continuity handoff for reconstructing working context across sessions.

Seed:

```text
CRP::HOT-RESUME | state=active | active=continue protocol analysis | last_result=core terminology is stable | next_action=write the conformance examples
```

The loader explains the payload. The seed carries the state.

## What CRP carries

A CRP block can carry:

- project and world context
- the active task
- constraints and stable decisions
- the last reliable result
- the next proposed action
- branch, checkpoint, or recovery state
- explicit collaboration preferences when they materially aid reconstruction

The block should contain the smallest useful state, not a transcript archive.

## Two profiles

CRP v1 defines two representations:

1. **Text profile** for manual, human-readable handoffs.
2. **JSON profile** for validated storage and machine interchange.

The text profile is deliberately constrained. Values that require delimiters,
multiline content, or exact round-trip preservation belong in the JSON profile.

The JSON profile is defined by
[`schema/crp.schema.json`](schema/crp.schema.json).

## Modes

| Mode | Purpose |
| --- | --- |
| `HOT-RESUME` | Resume a recently interrupted task |
| `COLD-RESUME` | Restore wider context after a longer gap |
| `HANDOFF` | Move the same work across a model, device, or tool |
| `TRANSPOSE` | Carry explicit collaboration preferences into a new topic |
| `FORK` | Branch from a shared base state |
| `RECOVERY` | Restore a last-known-good state after drift |
| `MERGE-NOTE` | Reconcile branch results |
| `CHECKPOINT` | Save a stable reconstruction anchor |

Mode-specific required fields are normative. See the
[`v1 specification`](docs/crp-spec-v1.md#5-mode-requirements).

## Authority and trust boundary

A CRP block is user or application data. It is not a system message and has no
authority beyond the channel and application that supplied it.

Consumers must:

- treat imported or retrieved blocks as untrusted input
- apply current user intent and higher-priority policy before carried state
- require fresh authorization for sending, deleting, publishing, spending, or
  any other consequential action
- validate provenance, size, fields, and protocol version before automated use
- never embed passwords, API keys, private keys, or session tokens

See [`Security and Trust`](docs/security-and-trust.md) before building an
automatic loader or agent integration.

## What CRP is not

CRP is not:

- native model memory
- a system prompt
- a jailbreak or policy bypass
- roleplay scaffolding
- an identity-persistence mechanism
- evidence that carried facts remain correct
- authorization to execute a recorded action

The useful shorthand is:

> CRP serializes application state; the receiving system still controls instruction priority and policy.

## Why use it

CRP is intended for work that crosses:

- chat or session boundaries
- devices and tools
- model providers
- long project gaps
- forks, checkpoints, and recovery points
- private notebook or retrieval systems

It complements provider-managed memory without depending on it.

## Start here

- [Quickstart](reference/quickstart.md)
- [Normative v1 specification](docs/crp-spec-v1.md)
- [Security and trust model](docs/security-and-trust.md)
- [Conformance guide](docs/conformance.md)
- [JSON schema](schema/crp.schema.json)
- [Design paper](docs/crp-paper.md)
- [Private integration guidance](docs/private-ai-integration.md)

## Repository map

- `docs/`: specification, design rationale, limits, and integration guidance
- `examples/`: complete example handoffs
- `templates/`: copyable starting points
- `schema/`: the machine-readable JSON profile
- `reference/`: quickstart, FAQ, implementation notes, and roadmap
- `tests/` and `tools/`: conformance and public-boundary validation

## Validate the repository

Install the pinned validation dependencies:

```console
python -m pip install --require-hashes -r requirements-dev.txt
```

Run the checks:

```console
python -m unittest discover -s tests -v
python tools/validate_repository.py
```

CI repeats these checks on Windows and Linux with supported Python versions and
runs a full-history secret scan.

## Security and privacy

CRP blocks may contain sensitive project context even when they contain no
credentials. Review and minimize a block before moving it between providers or
publishing it.

Report repository vulnerabilities through
[GitHub private vulnerability reporting](https://github.com/LeonidMajbits/CRP-context-reconstruction-protocol/security/advisories/new).
Do not place sensitive report details in a public issue.

## Contributing

Contributions are welcome when they improve precision, portability, safety,
conformance, examples, or measured interoperability.

Read [CONTRIBUTING.md](CONTRIBUTING.md) before proposing a protocol change.

## Citation and license

Citation metadata is available in [CITATION.cff](CITATION.cff).

CRP was developed through iterative human-AI collaboration by Leonid Majbits
with OpenAI's ChatGPT and Codex. The published specification and its claims
remain the author's responsibility.

Licensed under the [MIT License](LICENSE).

## One-line definition

Context Reconstruction Protocol is a user-owned format for serializing selected
working state and reconstructing it across AI sessions.
