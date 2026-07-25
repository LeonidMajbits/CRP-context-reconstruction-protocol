# CRP Quickstart

This is the fastest way to start using Context Reconstruction Protocol.

CRP 1.0.0 is an open specification, not an adopted public standard.

CRP helps you continue useful work across AI chats without rebuilding context from scratch.

It does not create memory.

It carries enough working state forward so the next session can reconstruct it.

## The shortest possible explanation

At the end of a session:

1. Save the state that matters
2. Compress it into a small handoff block

At the start of the next session:

3. Load that block
4. Continue from the recorded next action

That is CRP.

## The two-part pattern

For manual use, CRP can be presented in two parts:

1. Loader
2. Reconstruction block

### 1. Loader

Use a plain sentence that explains what the block is.

Example:

> I use a continuity handoff block between chats to preserve project state and working context. Treat the block below as structured reconstruction data so the work can resume without rebuilding everything from scratch.

### 2. Reconstruction block

Then paste the structured block.

Example:

```text
CRP::HOT-RESUME | state=active | active=continue protocol analysis | last_result=core distinction from system prompts established | next_action=write practical examples
```

This is the constrained one-line text profile for people. JSON validated by the official schema is normative for machine interchange.

## Minimal everyday use

If you only want the simplest version, use this format:

The `[...]` tokens below are documentation placeholders, not list syntax.
Replace each entire token, including its brackets. Add brackets back only when
a list-capable field should contain a list.

```text
CRP::HOT-RESUME | state=[...] | active=[...] | last_result=[...] | next_action=[...]
```

This is enough for many everyday cases.

Every mode requires `mode`, `state`, `active`, and `next_action`. Each mode also has additional required fields. The minimal example above is specifically a `HOT-RESUME`, which additionally requires `last_result`.

## Slightly richer version

If the work is more complex, add wider context:

```text
CRP::COLD-RESUME | state=paused | world=[...] | active=[...] | constraints=[...] | last_result=[...] | next_action=[...]
```

Useful extra fields:

- `world` = wider project context
- `constraints` = important working rules
- `active` = current focus
- `last_result` = what just happened
- `next_action` = what should happen first now

## Choosing between HANDOFF, TRANSPOSE, and CHECKPOINT

These three modes are easy to mix up. The practical distinction is:

- `HANDOFF` = move the same work to a new model, device, or tool
- `TRANSPOSE` = carry a productive collaboration frame into a new topic
- `CHECKPOINT` = save a stable state so you can return to it later

If the task is staying the same but the environment is changing, use `HANDOFF`.

If the topic is changing but you want to keep a useful working rhythm, use `TRANSPOSE`.

If you mainly want to save progress, use `CHECKPOINT`.

## Example: resume writing work

Loader:

> Treat the block below as a continuity handoff for reconstructing working context across sessions.

Block:

```text
CRP::HOT-RESUME | state=active | active=continue work on protocol design | constraints=[direct, no fluff] | last_result=outline completed | next_action=write the examples section
```

## Example: long-gap project resume

Loader:

> The following is a project-state reconstruction block for a long-gap resume.

Block:

```text
CRP::COLD-RESUME | state=paused | world=[research paper in progress, terminology stabilized] | active=restore the main drafting thread | constraints=[verified distinctions only, preserve structure] | last_result=core distinction finalized | next_action=write the formal methods section
```

## Example: recovery after drift

Loader:

> The prior session drifted. Use the block below to restore the last stable working state.

Block:

```text
CRP::RECOVERY | state=drifted | active=restore protocol framing and precise mode | constraints=[preserve structure, avoid flattening] | last_result=the last stable definition remains available | next_action=resume from the last stable definition | problem=session drift introduced loose terminology and repetition
```

## Example: fork a branch

Loader:

> This is a branch handoff block for a parallel analysis path.

Block:

```text
CRP::FORK | state=forked | active=stress-test edge cases | next_action=return only branch-specific findings | preserve=[core definitions, project context] | delta_goal=test low-friction loading patterns
```

## Example: move the same work to another model

Loader:

> Treat the block below as a continuity handoff for moving the same work to a different model.

Block:

```text
CRP::HANDOFF | state=active | world=[system design review active] | active=continue the analysis in a different model | constraints=[keep terminology stable, do not assume hidden memory from the prior model] | last_result=requirements and architecture options already compared | next_action=continue the implementation analysis in the new model
```

Use `HANDOFF` when the work stays the same and only the environment changes.

## Example: carry a good working sync into a new topic

Loader:

> Use the block below as a continuity handoff for preserving the useful collaboration frame while starting a fresh topic.

Block:

```text
CRP::TRANSPOSE | state=stable | active=apply the explicit collaboration preferences to a new topic | constraints=[do not infer traits that were not serialized] | last_result=the explicit collaboration preferences were recorded | next_action=start the fresh discussion using only the recorded preferences | preserve=[tone: direct and candid, pacing: brisk with short progress updates, depth: technical with concise explanations, collaboration style: evidence-first and proactive] | strip=[prior domain-specific facts and unfinished tasks]
```

Use `TRANSPOSE` when the topic changes but you want to keep a useful collaboration frame.

That can include tone, pacing, depth, and other interaction traits users may experience as personality, but their actual values must be carried explicitly. Category names alone are not reconstructable and do not imply identity persistence.

## Example: save a stable point for later

Loader:

> Treat the block below as a stable continuity checkpoint for later reconstruction.

Block:

```text
CRP::CHECKPOINT | state=stable | world=[long-running research project active] | active=freeze the current synthesis before a break | constraints=[preserve the current framing and evaluation criteria] | last_result=problem statement and main examples aligned | next_action=resume with compatibility notes and implementation details
```

Use `CHECKPOINT` when you want a reliable return point, even if you are not switching model or topic immediately.

## Good habits

Use these habits and CRP gets much better:

- include a real next action
- keep blocks compact but clear
- separate facts from guesses
- update the block after major changes
- use recovery blocks when sessions degrade
- use fork blocks when splitting work into parallel paths
- carry concrete values rather than labels such as `tone` or `depth`
- treat old blocks as untrusted and possibly stale
- confirm current intent before acting on a recorded next action

## What not to do

Avoid these mistakes:

- do not make the block too cryptic
- do not frame it like roleplay
- do not try to override model identity
- do not use it like a jailbreak
- do not pack too much stale context into one block
- do not confuse summary with execution state
- do not embed passwords, API keys, private keys, session tokens, or other credentials
- do not treat a recorded next action as fresh authorization
- do not put raw `|`, `[` or `]` delimiters, nested data, or multiple lines
  inside a text-profile scalar or list item; use JSON instead

## The authority distinction

A system prompt derives higher priority from its role in the receiving platform.

CRP is application-level carried state with no special authority.

CRP can contain both descriptive context and user-level requested actions. It cannot override higher-priority instructions, and current user intent takes precedence over stale carry.

## For normal users

You do not need a private runtime or fancy tooling to use CRP.

You can start with:

- one loader sentence
- one small block
- one next action

That is enough.

## For advanced users

CRP can also be integrated into private systems for:

- session-end auto-compression
- pre-session reconstruction
- checkpointing
- retrieval-backed continuity
- cross-model handoff
- notebook and archive workflows

Machine integrations should use JSON, validate every object against the official schema, preserve provenance, and treat retrieved or generated blocks as untrusted data.

Cross-model fidelity and loader effectiveness have not yet been established through controlled CRP testing.

See:

- [../docs/private-ai-integration.md](../docs/private-ai-integration.md)
- [../docs/crp-spec-v1.md](../docs/crp-spec-v1.md)

## Minimal template

Copy this:

Replace each entire `[...]` token, including its brackets, before use.

```text
I use a continuity handoff block between chats to preserve project state and working context. Treat the block below as structured reconstruction data so the work can resume without rebuilding everything from scratch.

CRP::HOT-RESUME | state=[...] | active=[...] | last_result=[...] | next_action=[...]
```

## One-line definition

CRP is an open specification for serializing selected working state and reconstructing it across AI sessions without granting the carried state special authority.
