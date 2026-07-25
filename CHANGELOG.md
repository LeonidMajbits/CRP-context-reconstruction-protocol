# Changelog

All notable changes to CRP are documented here. The project follows
[Semantic Versioning](https://semver.org/) for the specification and its
machine-readable artifacts.

## [Unreleased]

No unreleased changes.

## [1.0.0] - 2026-07-24

### Added

- normative CRP v1 text and JSON profiles
- explicit protocol versioning and mode-specific conformance rules
- security and trust guidance for untrusted continuity data
- automated validation for the schema, examples, links, and public boundary
- contributor templates, citation metadata, and release-ready repository policy

### Changed

- positioned CRP as an open specification rather than an adopted standard
- made empirical and interoperability limits explicit
- tightened the JSON extension model and rejected empty required values
- aligned every published example and template with the normative contract

### Security

- prohibited embedding raw credentials in CRP blocks
- clarified that carried state never grants fresh authorization for consequential actions
- added provenance, size, retention, and cross-provider disclosure guidance

[Unreleased]: https://github.com/LeonidMajbits/CRP-context-reconstruction-protocol/compare/v1.0.0...HEAD
[1.0.0]: https://github.com/LeonidMajbits/CRP-context-reconstruction-protocol/releases/tag/v1.0.0
