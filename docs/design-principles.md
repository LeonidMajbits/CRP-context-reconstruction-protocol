# Design Principles

CRP is intentionally simple. CRP 1.0.0 is an open specification, not an adopted public standard. These principles define what the protocol is trying to preserve and what it is trying to avoid.

## 1. User ownership

The carried state should be visible, editable, portable, and not dependent on a vendor-managed memory feature.

## 2. Reconstruction over memory claims

CRP reconstructs working state.

It does not claim true memory, identity persistence, or hidden continuity inside the model.

That working state can still include collaboration-frame traits such as tone, pacing, depth, and related personality-like interaction qualities when they are explicitly carried and materially useful.

## 3. Manual-first, automation-second

CRP should be understandable and usable by a person without requiring automation.

Tooling can extend the protocol, but the manual human-readable form remains the primary direct-use surface.

For machine interchange, however, JSON validated by the official schema is normative. The one-line text profile is a constrained human format, not a substitute machine grammar.

## 4. Minimal sufficient state

Carry enough state to resume useful work.

Do not carry the full transcript by default.

## 5. Explicit working state

A good CRP block makes the important state legible:

- current focus
- relevant project context
- active constraints
- collaboration frame when it matters to continuation
- last stable result
- next action

The block should carry concrete values rather than category labels. For example, `tone: direct and candid` is reconstructable; the word `tone` by itself is not.

## 6. Guardrail-aware framing

Use a short loader that explains the handoff clearly.

Avoid theatrical phrasing, role framing, override language, and command-heavy loading patterns.

A loader may reduce ambiguity, but that is an untested compatibility hypothesis rather than a guaranteed guardrail outcome.

## 7. Stable distinctions

Keep critical distinctions explicit, especially:

- reconstruction vs memory
- instruction vs serialized context
- facts vs assumptions
- continuity state vs broader archive material

## 8. Dual-format portability

CRP should survive movement across chats, devices, tools, and models with minimal adaptation.

The protocol should remain usable both as:

- a constrained one-line text profile for people
- normative JSON for machine interchange

## 9. User-owned complement to platform memory

CRP should complement platform-managed memory or session systems without depending on them.

The carried state should stay portable and inspectable even when a vendor memory layer exists.

## 10. Safety-compatible integration

CRP should not attempt to override system identity or safety policy.

Integrations should protect user data and keep stored continuity inspectable.

The protocol should stay small enough for direct manual use while remaining structured enough for system-level embedding.

## 11. No special authority

A CRP block is untrusted user or application data.

Carried constraints and next actions do not outrank the receiving system's instructions or the user's current request. A recorded next action is continuity state, not fresh authorization for a consequential external action.

## 12. Credentials stay outside CRP

CRP blocks should never contain passwords, API keys, private keys, session tokens, or other credentials.

When a workflow needs a credential, carry only an opaque reference to a separately protected secret store.

## 13. Evidence before compatibility claims

Cross-model fidelity, loader effectiveness, and reconstruction quality vary by implementation and have not yet been established by controlled CRP evaluations.

Public claims should distinguish design goals, hypotheses, observed test results, and independently reproduced evidence.
