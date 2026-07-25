# CRP Minimal Template

Loader:

> Treat the block below as a continuity handoff for reconstructing working context across sessions.

Before use, replace the entire `[MODE]` token and every entire `[...]` token,
including their brackets. Reintroduce brackets only when supplying a
list-capable field as a list.

Seed:

```text
CRP::[MODE] | state=[...] | active=[...] | last_result=[...] | next_action=[...]
```

Use this when you need the smallest workable handoff.

This skeleton is a `HOT-RESUME`-shaped starting point. Replace `[MODE]` and add every field required by the selected mode; all modes require `state`, `active`, and `next_action`.

The one-line text profile is for human copy and paste. Machine interchange must use schema-validated JSON.
