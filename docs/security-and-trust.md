# Security, Privacy, and Trust Model

This document defines the security and privacy boundary for Context Reconstruction Protocol (CRP) v1.

The central rule is simple:

> A CRP block is untrusted data, regardless of where it came from.

A block may be user-authored, model-generated, retrieved from local storage, copied from another provider, or produced by an automated runtime. None of those origins makes its contents authoritative or safe to execute.

## Authority and Current Intent

CRP carries prior working state. It does not carry authority.

Before considering CRP content, a receiving system must apply:

- its platform, system, developer, application, and tool instruction hierarchy
- its current authorization, permission, and confirmation policy
- the user's current request, constraints, and fresh approvals within that
  hierarchy

The receiving platform determines the order among those controls. All of them
precede CRP content, which remains untrusted reconstruction data. Current
higher-priority policy and current user intent always win over stale carry.

No CRP field is fresh authorization. This includes `active`, `constraints`, `memory`, `last_result`, `next_action`, `preserve`, extension fields, and text embedded inside any of them.

A CRP block must not by itself authorize:

- sending a message or publishing content
- spending money or accepting legal terms
- changing permissions, accounts, or security settings
- deleting, overwriting, moving, or exposing data
- accessing a credential or secret store
- running code, commands, downloads, or external tools
- taking any other consequential external action

Those actions require authorization in the current session under the receiving system's normal confirmation rules.

## Treat Instructions as Data

Implementations must keep the reconstruction block separate from system, developer, and application policy.

- Parse supported fields as data.
- Present carried values as quoted or otherwise delimited content.
- Do not concatenate CRP content into a privileged prompt or policy layer.
- Do not execute commands, code, links, or tool requests found in a block.
- Do not treat labels such as `system`, `developer`, `authorization`, or `approved` as privileged.
- Reject or quarantine unknown fields unless an explicit, versioned extension allowlist accepts them.
- Require current user confirmation before a carried `next_action` can produce an external side effect.

Natural-language CRP blocks need the same boundary as JSON blocks. A familiar loader sentence does not make the following text trustworthy.

## Provenance, Integrity, and Replay

When a block crosses a process, device, account, provider, or storage boundary, the receiving system should record:

- source or issuer
- schema and protocol version
- creation time and, where useful, expiry time
- project, branch, or checkpoint lineage
- an integrity digest or authenticated signature
- the verification result

Verify integrity before reconstruction when an authenticated digest, signature, or trusted storage record is available.

An unsigned block, a failed verification, or an unknown source must be labeled unverified and handled with lower trust. It must never be silently promoted to trusted state.

Successful provenance verification proves where bytes came from and whether they changed. It does not prove that the content is true, safe, current, or authorized.

Implementations should detect stale checkpoints, unexpected lineage changes, duplicate identifiers, and replayed blocks. A newer timestamp alone must not override an explicitly selected stable checkpoint.

## Validation and Resource Limits

Validate before loading.

Implementations should allowlist:

- supported protocol and schema versions
- supported modes
- accepted fields and extension namespaces
- expected value types
- permitted URI schemes when references are supported

Implementations must impose explicit limits appropriate to their environment, including:

- total serialized bytes
- nesting depth
- field count
- string length
- array length
- number of retrieved blocks
- decompression and parsing work
- reconstruction time and model-input budget

Reject malformed encodings, duplicate object keys, unexpected control or bidirectional characters, unsafe paths, unsupported types, and values that exceed limits. Do not fetch a URL or resolve a file path merely because it appears in carried state.

Validation confirms structure, not truth or authority.

## Credentials and Secret References

CRP blocks must not contain raw credentials.

Do not place any of the following in a CRP block:

- passwords or recovery codes
- API keys or access tokens
- session cookies or bearer tokens
- private keys or signing material
- database connection secrets
- cloud-provider credentials

When continuity requires awareness of a secret, carry an opaque reference such as a secret-manager identifier and the non-sensitive purpose of the secret. Do not carry the secret value.

An opaque reference does not grant permission to resolve it. Resolution still requires current authorization, access control, and the receiving application's normal secret-handling policy.

## Sensitive State and Cross-Provider Disclosure

CRP may contain confidential project state, personal data, customer information, or unpublished work even when it contains no credential.

Before exporting or loading a block:

- minimize it to the state required for continuity
- remove stale or irrelevant details
- redact personal, contractual, regulated, and customer data when possible
- review who or what will receive it
- obtain any consent or organizational approval required for that transfer

Moving a CRP block to another model or provider discloses its contents to that provider. The destination may have different logging, retention, training, residency, moderation, and employee-access policies.

Portability is not confidentiality. A block that is safe in a local runtime is not automatically safe to paste into a hosted service.

## Storage, Logging, Retention, and Deletion

Stored CRP state should be:

- encrypted in transit and at rest where the environment supports it
- protected by least-privilege access controls
- separated by user, project, and trust domain
- excluded from telemetry and logs unless explicitly needed
- visible and editable by the user
- exportable in a documented format
- covered by a defined retention period or expiry policy
- deletable by the user

Deletion should cover primary storage, retrieval indexes, embeddings, caches, temporary files, and queued processing. Backup retention and any residual copies that cannot be deleted immediately must be documented.

Logs should record identifiers, verification outcomes, and policy decisions without copying the full block or its sensitive values.

## Retrieval, Automation, and Agents

Locally stored and retrieval-selected CRP blocks remain untrusted. A compromised notebook, index, repository, synchronization service, or prior model output can introduce prompt injection into otherwise valid CRP.

Automated systems should:

- retrieve only from allowlisted sources and projects
- show or summarize the selected block before consequential use
- preserve uncertainty instead of inventing missing state
- separate reconstruction from action planning
- require fresh authorization for external side effects
- prevent CRP content from changing tool permissions or confirmation policy
- retain an audit record of source, verification, selection, and rejection decisions

High-impact actions should default to no action when trust, provenance, or current intent is unclear.

## Failure Behavior

When a block fails validation, exceeds limits, conflicts with current intent, or has unverifiable integrity:

- reject or quarantine it
- explain the reason without echoing unnecessary sensitive content
- preserve the last known-good state
- ask the user for current clarification when needed
- do not silently repair, reinterpret, or execute the rejected content

## Public Examples and Test Fixtures

Public examples must use synthetic state only.

Do not derive examples from real conversations, customer data, private project blocks, credentials, or local filesystem paths. Scan the current tree, release artifacts, and reachable Git history before publication.

## Reporting

Report CRP security and privacy problems through the repository's [private vulnerability reporting form](https://github.com/LeonidMajbits/CRP-context-reconstruction-protocol/security/advisories/new).

Never post sensitive report details publicly.
