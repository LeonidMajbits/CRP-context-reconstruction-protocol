# Security Policy

## Scope

This policy covers the Context Reconstruction Protocol specification, schemas, examples, templates, diagrams, and integration guidance in this repository.

The protocol's security and privacy requirements are defined in [Security, Privacy, and Trust Model](docs/security-and-trust.md).

## Report a Vulnerability Privately

Use this repository's GitHub private vulnerability reporting form:

[Report a vulnerability privately](https://github.com/LeonidMajbits/CRP-context-reconstruction-protocol/security/advisories/new)

Never post sensitive report details in a public issue, discussion, pull request, commit, or comment. If the private form is unavailable, do not publish the details while seeking a private reporting channel.

Include:

- a concise description of the problem and its impact
- affected documents, schemas, examples, or integration patterns
- reproduction steps or a minimal proof of concept
- suggested mitigations, if known
- whether any credential, personal data, or private CRP state may have been exposed

Do not include live credentials, private keys, access tokens, or unnecessary personal data. Use redacted samples.

## What to Report

- unsafe handling of user continuity data
- prompt-injection or trust-boundary weaknesses in CRP loading
- examples that could grant authority from carried state
- tooling patterns that could leak, retain, or silently mutate CRP state
- schema or template behavior that creates avoidable privacy or resource-exhaustion risk
- provenance, integrity, replay, or cross-provider disclosure failures

## Coordinated Disclosure

Please allow reasonable time for triage and remediation before public disclosure. Publication should be coordinated through the private report so users can receive accurate mitigation guidance.
