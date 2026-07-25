# CRP Merge Note Template

Loader:

> The block below is a merge note for reconciling branch outputs and preserving the state that should survive recombination.

Before use, replace every entire `[...]` token, including its brackets.
Reintroduce brackets only when supplying a list-capable field as a list.

Seed:

```text
CRP::MERGE-NOTE | state=active | active=[...] | last_result=[...] | next_action=[...] | lineage=[...] | preserve=[...]
```

Use this when multiple branches need to be reconciled before returning to a shared path.
