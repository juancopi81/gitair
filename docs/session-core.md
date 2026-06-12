# Session Core

This document briefly explains the code introduced for [issue 1](https://github.com/juancopi81/gitair/issues/1).

The goal of this first slice is not to build real audio, webcam input, live visuals, or a real music model integration yet. The goal is to make the first Gitair core path explicit enough that I can explain it from memory before delegating broader work to agents.

## Layout

This first slice introduces the initial project layout:

- `gitair/`: the main Python package.
- `gitair/core/`: the core session logic and data models.
- `gitair/companions/`: companion implementations. For now, this only includes a fake companion.
- `gitair/demos/`: small executable demos that assemble the components together.
- `tests/`: focused tests for the current Gitair behavior.

The layout is intentionally small. More folders should only be added when the project earns them through working demos.

## Session

A `Session` is the core object of this first Gitair slice.

Right now, it is very simple and follows this workflow:

1. A `Session` starts in `PRIMING_PASS` by default.
2. During the priming pass, the guitarist plays first.
3. At some point, the session receives a `PhraseContext`.
4. The `PhraseContext` represents musical context from the priming pass, such as chords, tempo, style, and prompt summary.
5. Once the session has phrase context, it can receive a `ControlAction`.
6. Right now, the only supported control action is `START_JAM_PASS`.
7. `START_JAM_PASS` moves the session from `PRIMING_PASS` to `JAM_PASS`.
8. A companion receives a `SessionSnapshot` and responds from it.

In short:

```text
Session starts
  → PRIMING_PASS
  → receives PhraseContext
  → receives START_JAM_PASS
  → moves to JAM_PASS
  → FakeCompanion responds from SessionSnapshot
```

## Core concepts

### `PhraseContext`

`PhraseContext` represents what Gitair currently knows about the phrase.

For now, it is hard-coded in the dry run, but later it may come from:

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

For now, the only action is:

```text
START_JAM_PASS
```

Later, this vocabulary may grow to include actions such as:

- stop jam
- companion on/off
- increase intensity
- decrease intensity
- capture phrase
- reset session

### `SessionSnapshot`

`SessionSnapshot` is a serializable view of the current session state.

It currently includes:

- the current session phase
- the current phrase context, if one has been received

The snapshot is what other parts of the system can read without directly controlling the session.

### `FakeCompanion`

`FakeCompanion` proves the companion boundary.

It does not generate audio and does not talk to a real music model. It simply receives a `SessionSnapshot` and returns a fake response based on the current phase and phrase context.

This makes the future integration point clearer:

```text
FakeCompanion today
MRT2Companion later
Other companions later
```

## Dry run

The dry run demonstrates the first executable Gitair core path without real audio, webcam input, visuals, or a specific music model.

The dry run should show:

1. the initial session snapshot
2. a phrase context being received
3. a control action starting the jam pass
4. the updated session snapshot
5. a fake companion response

This proves the first tracer bullet:

```text
Priming Pass → Phrase Context → Control Action → Jam Pass → Companion Response
```

## What this slice intentionally does not include

This first slice does not include:

- real guitar audio
- webcam input
- gesture detection
- live visuals
- MRT2 integration
- chord recognition
- phrase analysis
- browser UI
- module loading

Those belong to later milestones.

For now, the important thing is that the core session model is small, understandable, and executable.

## Why this matters

This slice establishes the first shared vocabulary for Gitair:

- `Session`
- `PhraseContext`
- `ControlAction`
- `SessionSnapshot`
- `Companion`
- `PRIMING_PASS`
- `JAM_PASS`

Before adding agents, models, gestures, visuals, or real audio, I want to understand this core flow clearly.

The first goal is not technical completeness.

The first goal is ownership of the main abstraction.
