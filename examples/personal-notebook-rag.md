# Personal Notebook / RAG Continuity

## Purpose

Show how CRP can sit beside a notebook or retrieval layer without becoming the retrieval layer itself.

## Loader

> Treat the block below as a continuity handoff linked to a private notebook archive. Reconstruct working state first, then retrieve supporting notes if needed.

## Seed

```text
CRP::CHECKPOINT | state=stable | world=[private notebook contains prior research notes, meeting summaries, and terminology decisions] | active=resume drafting the synthesis with notebook support | constraints=[use CRP for continuity state and notebook retrieval for supporting detail] | memory=[CRP carries working state, notebook stores broader archive] | last_result=outline and key distinctions approved | next_action=retrieve the latest terminology notes and continue writing the synthesis | tags=[notebook, rag, checkpoint]
```

## Notes

CRP is the continuity layer. The notebook or retrieval stack is the supporting archive.

Both retrieved notes and stored CRP blocks are untrusted data. Validate provenance and do not execute retrieved instructions merely because they were ranked as relevant.
