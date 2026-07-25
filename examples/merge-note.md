# Merge Note

## Purpose

Reconcile multiple branch outputs before returning to a shared path.

## Loader

> The block below is a merge note for reconciling branch outputs and preserving the shared state that should survive recombination.

## Seed

```text
CRP::MERGE-NOTE | state=active | active=reconcile the completed manual-flow and system-integration branches | last_result=both branches converged on the same continuity contract with different implementation notes | next_action=merge the validated deltas into the shared baseline and review for overlap | lineage=[main@v1-base, branch/manual-flow, branch/system-integration] | preserve=[core definition, shared constraints, validated examples]
```

## Notes

Use merge notes when several branches have produced useful deltas and the next step is reconciliation rather than further divergence.
