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
