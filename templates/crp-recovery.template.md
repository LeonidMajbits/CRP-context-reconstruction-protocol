# CRP Recovery Template

Loader:

> The prior session drifted. Use the block below to restore the last stable working context.

Before use, replace every entire `[...]` token, including its brackets.
Reintroduce brackets only when supplying a list-capable field as a list.

Seed:

```text
CRP::RECOVERY | state=drifted | world=[...] | active=[...] | constraints=[...] | last_result=[...] | next_action=[...] | preserve=[...] | problem=[...]
```

Use this when you need to cut noise and return to a stable state.
