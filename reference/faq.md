# FAQ

## Does CRP create memory?

No. CRP reconstructs working state from explicit carried context.

## Is CRP an adopted public standard?

No. CRP 1.0.0 is an open specification. Adoption, interoperability, and reconstruction quality should be evaluated with published evidence.

## Is CRP a system prompt?

No. A system prompt derives higher priority from its role in the receiving platform. CRP is application-level continuity data with no special authority.

CRP can contain user-level requested actions and constraints, but it cannot override current or higher-priority instructions.

## Does CRP depend on one model?

No. It is designed to be portable, though reconstruction quality varies by system.

CRP 1.0.0 has not yet established cross-model fidelity through controlled comparative testing.

## Can CRP be used manually?

Yes. Manual copy-paste use is the baseline workflow.

## Can CRP be used across unrelated topics?

Yes. `TRANSPOSE` can carry productive collaboration state into a fresh topic while stripping irrelevant prior domain context.

## Can CRP be integrated into software?

Yes. Private runtimes can use CRP for checkpoints, reconstruction, cross-model carry, and archive-linked continuity.

Machine integrations should use normative JSON, validate it against the official schema, preserve provenance, and treat every block as untrusted data.

## Should CRP carry secrets?

No. Never embed passwords, API keys, private keys, session tokens, or other credentials.

If a workflow depends on a credential, carry only an opaque reference to a separately protected secret store.

## Does `next_action` authorize an action?

No. It records the next requested operation as continuity state.

The receiving system must compare it with the user's current request and apply normal authorization or confirmation before any consequential external action.

## Does a loader guarantee better compatibility?

No. A plain loader may reduce ambiguity, but CRP 1.0.0 has not yet validated that hypothesis across model families.

## Which representation should software use?

Use JSON validated by the official schema.

The one-line text profile is intended for direct human copy and paste and deliberately excludes raw delimiter characters, nested data, and multiline values.
