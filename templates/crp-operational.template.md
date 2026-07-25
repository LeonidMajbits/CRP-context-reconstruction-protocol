# CRP Operational Template

Loader:

> Use the block below as structured reconstruction data so the work can continue without rebuilding the project context from scratch.

Before use, replace the entire `[MODE]` token and every entire `[...]` token,
including their brackets. Reintroduce brackets only when supplying a
list-capable field as a list.

Seed:

```text
CRP::[MODE] | state=[...] | world=[...] | active=[...] | constraints=[...] | memory=[...] | last_result=[...] | next_action=[...] | tags=[...]
```

Use this for normal working sessions where both project frame and immediate next step matter.

Replace `[MODE]` and add every mode-specific required field. Do not assume this generic field set validates for every mode.

The one-line text profile is for human copy and paste. Machine interchange must use schema-validated JSON.
