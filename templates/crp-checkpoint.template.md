# CRP Checkpoint Template

Loader:

> Treat the block below as a stable continuity checkpoint for later reconstruction.

Before use, replace every entire `[...]` token, including its brackets.
Reintroduce brackets only when supplying a list-capable field as a list.

Seed:

```text
CRP::CHECKPOINT | state=stable | world=[...] | active=[...] | constraints=[...] | last_result=[...] | next_action=[...] | tags=[...]
```

Use this when the current state is reliable enough to save as a future return point.
