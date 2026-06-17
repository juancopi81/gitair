# Session Core

This document explains the current Gitair session core: the Milestone 1
priming-to-jam tracer bullet, the Milestone 2 manual companion steering
contract, and the Milestone 3 gesture event boundary.

The goal is still not to build real audio, webcam input, live visuals, or a
real music model integration yet. The goal is to keep the main Gitair
abstraction explicit enough that the project owner can explain it before
delegating broader work to agents.

## Layout

The current layout is intentionally small:

- `gitair/core/`: the core session logic and data models.
- `gitair/companions/`: companion implementations. For now, this only includes
  a fake companion.
- `gitair/gestures/`: source-neutral gesture events, fake gesture sources, and
  gesture-to-control mapping.
- `gitair/demos/`: executable demos that assemble the components together.
- `tests/`: focused tests for the current behavior.

More folders should only be added when the project earns them through working
demos.

## Session

A `Session` is a bounded Gitair run.

It follows this workflow:

1. A `Session` starts in `PRIMING_PASS`.
2. During the priming pass, the guitarist plays first.
3. The session receives a `PhraseContext`.
4. `PhraseContext` represents musical context such as chords, tempo, style, and
   prompt summary.
5. The user applies `BRING_COMPANION_IN`.
6. If the session is in `PRIMING_PASS`, that action requires phrase context,
   moves the session into `JAM_PASS`, and creates active companion state.
7. While in `JAM_PASS`, the user can silence, reintroduce, or adjust the
   companion.
8. A companion receives a `SessionSnapshot` and responds from it.

In short:

```text
Session starts
  -> PRIMING_PASS
  -> receives PhraseContext
  -> receives BRING_COMPANION_IN
  -> moves to JAM_PASS
  -> creates CompanionState(active, intensity 3)
  -> FakeCompanion responds from SessionSnapshot
```

Invalid session operations fail with explicit errors instead of silently doing
nothing. The deliberate exception is intensity clamping: asking for more
intensity at `5` or less intensity at `1` is valid steering at a boundary.

Current invalid operations include:

- bringing the companion in without phrase context
- bringing the companion in again while it is already active
- silencing the companion before `JAM_PASS`
- silencing the companion when it is already silent
- changing intensity before `JAM_PASS`
- asking the companion to respond before `JAM_PASS`
- asking the companion to respond without phrase context
- asking the companion to respond without companion state

The current custom errors are intentionally small:

- `InvalidSessionTransition` for invalid session state changes
- `UnsupportedControlAction` for unsupported session actions
- `CompanionNotReady` for companion responses requested from an invalid snapshot

## Core Concepts

### `PhraseContext`

`PhraseContext` represents what Gitair currently knows about the phrase.

For now, it is provided to the dry run manually, but later it may come from:

- manual input
- chord recognition
- phrase priming
- audio analysis
- embedding models
- prompt generation

Current fields include:

- chords
- tempo
- style description
- prompt summary

### `ControlAction`

`ControlAction` represents an instruction applied to the session.

The current actions are:

- `BRING_COMPANION_IN`
- `SILENCE_COMPANION`
- `INCREASE_INTENSITY`
- `DECREASE_INTENSITY`

`BRING_COMPANION_IN` is musician-facing language. During `PRIMING_PASS`, it
starts the jam by bringing the companion into the performance. During
`JAM_PASS`, it can bring a silent companion back using the existing phrase
context.

There is no compatibility action for the old implementation-shaped phase-start
name. The repo is early, so the public vocabulary has moved to the
musician-facing action.

### `CompanionState`

`CompanionState` is the small session-owned target state for the companion.

It includes:

- `status`: `active` or `silent`
- `intensity`: an integer target from `1` to `5`

When the companion first enters, the default state is:

```text
status = active
intensity = 3
```

`SILENCE_COMPANION` changes status to `silent` without replacing
`PhraseContext`. `BRING_COMPANION_IN` changes a silent companion back to
`active`.

`INCREASE_INTENSITY` and `DECREASE_INTENSITY` adjust the target by one step and
clamp at `1` and `5`. Smooth crescendos and decrescendos are intentionally out
of scope for this slice; a future companion or audio adapter can render a smooth
transition toward the discrete target.

### `SessionSnapshot`

`SessionSnapshot` is a serializable view of the current session state.

It currently includes:

- the current session phase
- the current phrase context, if one has been received
- the current companion state, if the companion has entered the jam

The snapshot is what other parts of the system can read without directly
controlling the session.

### `FakeCompanion`

`FakeCompanion` proves the companion boundary.

It does not generate audio and does not talk to a real music model. It receives
a `SessionSnapshot` and returns a fake response based on phase, phrase context,
and companion state.

This keeps the future integration point clear:

```text
FakeCompanion today
MRT2Companion later
Other companions later
```

## Gesture Boundary

Gestures stay outside the session core. The current Milestone 3 path is:

```text
Gesture Source
  -> Gesture Event
  -> Gesture Mapper
  -> Control Action
  -> Session
```

`GestureEvent` is source-neutral. It contains:

- `gesture_type`: `HEAD_RIGHT`, `HEAD_LEFT`, `NOD_UP`, or `NOD_DOWN`
- `confidence`: a visible confidence value, defaulting to `1.0`

The default hard-coded mapping is:

- `HEAD_RIGHT` -> `BRING_COMPANION_IN`
- `HEAD_LEFT` -> `SILENCE_COMPANION`
- `NOD_UP` -> `INCREASE_INTENSITY`
- `NOD_DOWN` -> `DECREASE_INTENSITY`

Unsupported or unmapped gesture events fail with custom Gitair errors. Webcam
input, camera dependencies, thresholds, real gesture detection, configurable
mapping, and UI controls are intentionally out of scope for this slice.

## Dry Run

The dry run demonstrates the current executable Gitair core path without real
audio, webcam input, visuals, or a specific music model.

The manually steerable dry run shows:

1. the initial session snapshot
2. a phrase context being received
3. `BRING_COMPANION_IN` entering the jam pass
4. `SILENCE_COMPANION` making the companion silent
5. `BRING_COMPANION_IN` bringing the same companion context back
6. intensity actions changing the discrete target
7. fake companion responses from each resulting snapshot

This proves the current tracer bullet:

```text
Priming Pass
  -> Phrase Context
  -> Control Action
  -> Jam Pass
  -> Companion State
  -> Companion Response
```

Run it with your own phrase context:

```bash
uv run python -m gitair.demos.dry_run_session --chords "Dm7,G7,Cmaj7" --tempo-bpm 96 --style-description "quiet bossa nova" --prompt-summary "soft syncopated guitar phrase"
```

The command waits for Enter before each default steering action. For a
non-interactive check, add `--auto-demo-steering`.

The gesture dry run demonstrates the source-neutral gesture boundary:

```bash
uv run python -m gitair.demos.gesture_dry_run --gestures "HEAD_RIGHT,HEAD_LEFT,HEAD_RIGHT,NOD_UP,NOD_DOWN"
```

It prints each scripted gesture event, the mapped control action, and the
resulting companion state.

## What This Slice Intentionally Does Not Include

This slice does not include:

- real guitar audio
- webcam input
- real gesture detection
- live visuals
- MRT2 integration
- chord recognition
- phrase analysis
- browser UI
- module loading
- smooth intensity fades

Those belong to later milestones.

For now, the important thing is that the core session model is small,
understandable, and executable.

## Why This Matters

This slice keeps the shared vocabulary concrete:

- `Session`
- `PhraseContext`
- `ControlAction`
- `CompanionState`
- `SessionSnapshot`
- `Companion`
- `GestureEvent`
- `PRIMING_PASS`
- `JAM_PASS`

Before adding agents, models, gestures, visuals, or real audio, the project
owner should understand this core flow clearly.
