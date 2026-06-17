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

## Milestone 3 — Gesture event boundary

### Purpose

Prove the boundary between physical gestures and session control before adding real webcam detection.

Milestone 3 should make this path executable:

```text
Gesture Event -> Control Action -> Session
```

The goal is not to recognize real head or hand movement yet. The goal is to define the source-neutral event that a gesture module can emit and the mapper that turns that event into the existing musician-facing control actions.

### Expected behavior

1. A user starts with the existing priming-to-jam dry run.
2. A fake or manual gesture source emits a `Gesture Event`.
3. Gitair maps the gesture event to a `Control Action`.
4. The session applies that control action using the existing Milestone 2 behavior.
5. The dry run shows both the recognized gesture event and the resulting companion state.

### First gesture mapping

Milestone 3 uses a tiny hard-coded default mapping:

- `HEAD_RIGHT` -> `BRING_COMPANION_IN`
- `HEAD_LEFT` -> `SILENCE_COMPANION`
- `NOD_UP` -> `INCREASE_INTENSITY`
- `NOD_DOWN` -> `DECREASE_INTENSITY`

Configurable gesture mapping is out of scope for this milestone. A later setup screen can let the user choose enabled gestures, mappings, sensitivity, and thresholds.

### First gesture event shape

The first `Gesture Event` shape is:

- `gesture_type`: one of `HEAD_RIGHT`, `HEAD_LEFT`, `NOD_UP`, or `NOD_DOWN`
- `confidence`: optional float, default `1.0`

For Milestone 3, confidence should be visible in the dry run but should not change behavior. Real thresholds, stability windows, timestamps, durations, raw coordinates, and camera frames are out of scope.

### Boundary with Session

`Session` should not know about gestures. Milestone 3 should keep the boundary outside the session core:

```text
Gesture Source -> Gesture Event -> Gesture Mapper -> Control Action -> Session
```

This keeps gesture input, keyboard input, MIDI input, and future UI controls able to share the same `Control Action` contract.

### Demo source

Milestone 3 should start with a scripted fake gesture source, not webcam input or interactive gesture entry.

The default scripted gesture sequence should be:

```text
HEAD_RIGHT -> HEAD_LEFT -> HEAD_RIGHT -> NOD_UP -> NOD_DOWN
```

This keeps the demo deterministic, testable, and runnable without camera hardware.

Example command shape:

```bash
uv run python -m gitair.demos.gesture_dry_run --gestures "HEAD_RIGHT,HEAD_LEFT,HEAD_RIGHT,NOD_UP,NOD_DOWN"
```

### Invalid gesture events

Milestone 3 should use explicit custom errors for unsupported or unmapped gesture events. These errors should follow the existing `GitairError` pattern instead of using generic `ValueError`s or silently ignoring invalid gesture events.

Raw noisy movement is out of scope for this milestone. Once something is represented as a `Gesture Event`, it should either map to a `Control Action` or fail clearly.

### Validation

Milestone 3 is done when one deterministic command shows the full path:

```text
scripted gesture event -> mapped control action -> session state change -> visible companion state
```

Focused tests should cover:

- the `Gesture Event` shape
- the default gesture mapping
- unsupported or unmapped gesture errors
- the fact that `Session` remains gesture-agnostic

The dry run should show each scripted gesture event, the mapped control action, and the resulting companion state. Webcam input, camera dependencies, thresholds, and real gesture detection are out of scope.
