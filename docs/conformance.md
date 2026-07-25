# CRP v1 Conformance

This document defines the conformance surfaces for CRP 1.0.

The normative requirements remain in
[`crp-spec-v1.md`](crp-spec-v1.md). This document explains how an
implementation demonstrates them.

## Conformance classes

### Text producer

A conforming text producer:

- emits one-line `CRP::MODE` payloads
- follows the v1 delimiter and value rules
- includes the global and mode-specific required fields
- emits only core fields or correctly namespaced `x_*` extension fields
- enforces value and payload-size limits
- rejects runtime placeholders and unsafe decoded control or format characters

### Text consumer

A conforming text consumer:

- rejects malformed, duplicate, empty, oversized, or unknown core fields
- validates all mode-specific requirements
- treats `x_` fields as untrusted extension data
- does not infer authorization from carried values
- directs values outside the text profile to the JSON profile

### JSON producer

A conforming JSON producer emits an object that validates against
[`schema/crp.schema.json`](../schema/crp.schema.json), including
`"protocol_version": "1.0"`, and satisfies the decoded-string and resource
requirements in Section 3.2 of the specification. Generic JSON Schema
validation establishes structural conformance but does not replace that
semantic security pass.

### JSON consumer

A conforming JSON consumer:

- validates the complete object before use
- applies decoded-string hygiene after JSON escape processing
- rejects unknown top-level fields
- applies configured resource limits before model ingestion
- treats `extensions` as untrusted data
- applies current policy, user intent, and fresh authorization requirements

## Repository validation

The repository validator checks:

- JSON Schema meta-schema validity
- positive and negative mode fixtures
- every standalone concrete CRP text block in repository Markdown
- internal Markdown links and balanced code fences
- JSON, YAML, and SVG syntax
- UTF-8 and unsafe Unicode control characters
- personal-email, local-path, and hidden-comment leakage
- version agreement across release-facing files

Run:

```console
python -m pip install --require-hashes -r requirements-dev.txt
python -m ruff check tools tests
python -m ruff format --check tools tests
python -m unittest discover -s tests -v
python tools/validate_repository.py
```

CI runs the same checks on Windows and Linux.

## What conformance does not prove

Conformance proves structural compatibility with the CRP v1 contract. It does
not prove:

- that carried state is true or current
- reconstruction quality on a particular model
- safety of an importing application
- confidentiality after provider transfer
- semantic equivalence between implementations

Those properties require application-level controls and empirical evaluation.

## Reporting results

Compatibility reports should record:

- CRP specification version
- producer and consumer versions
- model or runtime identifier
- mode and profile used
- whether structural validation passed
- task-specific reconstruction criteria
- observed failures, mutations, or missing state

Do not report a system as CRP-compatible solely because it accepted a block.
