# CRP Fork Template

Loader:

> The block below is a branch handoff. Preserve the shared base state and continue only the fork-specific path.

Before use, replace every entire `[...]` token, including its brackets.
Reintroduce brackets only when supplying a list-capable field as a list.

Seed:

```text
CRP::FORK | state=forked | world=[...] | active=[...] | last_result=[...] | next_action=[...] | lineage=[...] | preserve=[...] | delta_goal=[...]
```

Use this when branching work into parallel paths.
