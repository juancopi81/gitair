# Gitair Milestones

This file records the current implementation slices. It should stay lightweight and change as the project learns what feels musical.

## Milestone 1 — Core interaction dry run

### Purpose

Prove the core Gitair interaction before adding real audio, webcam gestures, live visuals, or a specific music model.

The first slice should make the domain language executable: a `Session` moves from `Priming Pass` to `Jam Pass`, carries `Phrase Context`, accepts `Control Action`s, and lets a fake `Companion` respond to session state.

### Expected behavior

1. A user starts a session.
2. The session begins in the priming pass.
3. The user enters simple phrase context manually, such as chords, tempo, style, or bar count.
4. The user triggers a control action to start the jam pass.
5. The session moves into the jam pass.
6. A fake companion produces a visible response based on the phrase context and current session state.

### User-owned decisions

The project owner should understand and approve these before agents expand the code:

- the `Session` state model
- the canonical `Control Action` vocabulary
- the shape of `Phrase Context`
- the boundary between `Companion` and a future model adapter
- what counts as success for the milestone

### Delegable work

Agents can safely implement narrow pieces once the owner-owned decisions above are clear:

- data classes or typed models
- a fake companion adapter
- a CLI or tiny demo runner
- focused tests for priming-to-jam transitions
- simple serialization or display helpers

### Out of scope

- real-time guitar audio processing
- webcam gesture detection
- MRT2 or other live model integration
- polished UI or live visualizer
- automatic chord recognition
- permanent audio recording

### Validation

Milestone 1 is done when tests prove the priming-to-jam transition and a local demo shows the fake companion responding to manually entered phrase context.

Standard checks:

```bash
uv run pytest
uv run python -m gitair.demos.dry_run_session --chords "E7,G5,A" --tempo-bpm 120 --auto-demo-steering
```

## Milestone 2 — Manual companion steering

### Purpose

Define the first musician-facing control vocabulary for steering the companion during a session, before adding webcam gesture detection or a real companion backend.

Milestone 2 should keep input sources manual and explicit. The goal is to decide what the performer can ask the companion to do, how the session and companion state change, and how the fake companion reveals those changes.

### Expected behavior

1. A user starts with the existing priming-to-jam dry run.
2. The user applies `BRING_COMPANION_IN` as the musician-facing action that brings the companion into the performance.
3. If the session is in the priming pass, `BRING_COMPANION_IN` moves the session into the jam pass and activates the companion.
4. If the session is already in the jam pass and the companion is silent, `BRING_COMPANION_IN` activates the companion again using the existing phrase context.
5. The user can apply `SILENCE_COMPANION` while in the jam pass to make the companion silent without losing the phrase context.
6. The user can apply `INCREASE_INTENSITY` and `DECREASE_INTENSITY` while in the jam pass to adjust companion prominence.
7. The fake companion response reflects companion state clearly enough for the owner to inspect.

### First control actions

- `BRING_COMPANION_IN`
- `SILENCE_COMPANION`
- `INCREASE_INTENSITY`
- `DECREASE_INTENSITY`

The old implementation-shaped phase-start action from Milestone 1 is replaced by `BRING_COMPANION_IN` because the musician's cue is to bring the companion into the performance. The repo is still early, so no internal compatibility action or public alias is needed.

### First companion state

The first `Companion State` shape is:

- `status`: `active` or `silent`
- `intensity`: integer from `1` to `5`
- default when the companion first enters: `status=active`, `intensity=3`

`SILENCE_COMPANION` changes `status` to `silent` without replacing `Phrase Context`.
`BRING_COMPANION_IN` changes `status` to `active`.
`INCREASE_INTENSITY` and `DECREASE_INTENSITY` adjust `intensity` by one step and clamp at `1` and `5`.

For Milestone 2, `intensity` is a discrete target level in the session contract.
Smooth crescendos or decrescendos are companion rendering behavior and can be added later without changing the first state shape.

### User-owned decisions

The project owner should understand and approve these before agents expand the code:

- the first musician-facing `Control Action` vocabulary
- the shape of `Companion State`: active or silent, intensity `1` to `5`, default `3`
- replacing the old phase-start action with `BRING_COMPANION_IN` instead of keeping compatibility aliases
- how smooth intensity transitions should be expressed later
- which invalid steering operations should raise explicit errors

### Delegable work

Agents can safely implement narrow pieces once the owner-owned decisions above are clear:

- update the control action enum and session state model
- add a small companion state object or field
- update the manual CLI to accept the new actions
- update fake companion output
- add focused tests for state transitions and invalid steering operations
- refresh owner-facing docs

### Out of scope

- real webcam or gesture detection
- choosing physical gesture mappings
- real-time guitar audio processing
- MRT2 or other live model integration
- automatic chord recognition
- live visual interface work

### Validation

Milestone 2 is done when tests prove manual companion steering and the local dry run demonstrates bringing the companion in, silencing it, bringing it back, and changing intensity without replacing the existing phrase context.
