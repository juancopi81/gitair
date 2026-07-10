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

## Milestone 4 — Webcam gesture source spike

### Purpose

Prove that a real camera-backed `Gesture Source` can emit the same source-neutral `Gesture Event` contract introduced in Milestone 3.

Milestone 4 should make this path executable:

```text
Webcam Gesture Source -> Gesture Event -> Gesture Mapper -> Control Action -> Session
```

The goal is not to refine musical gesture feel yet. The goal is to keep `Session` gesture-agnostic while replacing the scripted gesture source with a real input source.

### Expected behavior

1. A user starts a webcam-backed gesture dry run.
2. The webcam gesture source observes a limited first set of movements.
3. Gitair emits `Gesture Event`s using the existing event contract.
4. The existing gesture mapper turns those events into `Control Action`s.
5. The session applies those actions using the existing companion steering behavior.

### First source choice

Milestone 4 should use MediaPipe Face Landmarker for the first real gesture source. OpenCV can be used only as webcam frame plumbing if needed.

Hand gesture recognition is out of scope for this milestone. MediaPipe Gesture Recognizer or MediaPipe Hands may be useful later for hand or conductor-style cues, but Milestone 4 should focus on head movement.

### First recognized gestures

The first webcam-backed source only needs to emit:

- `HEAD_RIGHT`
- `HEAD_LEFT`

`NOD_UP` and `NOD_DOWN` remain part of the source-neutral gesture contract, but they are out of scope for the first webcam source. Nods likely need temporal movement detection and should wait until the left/right head-turn path is working.

### Emission behavior

The webcam source should emit a gesture event only when a head turn crosses a clear threshold. After emitting, it should enter a short cooldown and wait for the head to return near neutral before emitting another event.

This keeps one sustained head turn from firing many repeated events. The first threshold and cooldown values can be code constants or CLI flags, but a settings UI is out of scope.

### Runtime failure behavior

Webcam setup failures and MediaPipe/model setup failures should fail clearly with custom Gitair errors.

Runtime frames with no detected face should not emit a `Gesture Event` and should not crash the session. A neutral face position should also emit no event. The webcam dry run should make these states visible enough for the user to understand what the source is seeing.

### Validation

Milestone 4 is done when the gesture-source logic is unit-tested and a human can run a webcam smoke test locally.

Automated tests should cover threshold crossing, cooldown, neutral return, setup/error boundaries where possible, and the fact that `Session` remains gesture-agnostic. Real webcam behavior does not need to be proven in automated tests.

Standard checks:

```bash
uv run pytest
uv run ruff check .
uv run ruff format --check .
GITAIR_FACE_LANDMARKER_MODEL=/absolute/path/to/face_landmarker.task uv run python -m gitair.demos.webcam_gesture_dry_run
```

The webcam dry run is a manual smoke check. It should show visible source status, emitted gesture events, mapped control actions, and resulting companion state.
The source calibrates neutral yaw from the first detected face frames before
emitting. If a local camera still reports left and right backwards, rerun with
`--invert-yaw`; this only flips Gitair's source-adapter yaw sign and does not
change the gesture mapping contract.

### Out of scope

- configurable gesture mapping
- setup-screen UI
- polished live overlays
- phrase or audio integration
- full musical gesture refinement
- hand gesture detection
- webcam-backed nod detection

## Milestone 5 — Priming source boundary

### Purpose

Define the boundary that turns a priming pass into phrase context before adding
real audio capture, chord recognition, embeddings, or prompt generation.

Milestone 5 should make this path executable:

```text
Priming Source -> Phrase Context -> Session
```

The goal is not automatic music understanding yet. The goal is to make the
priming pass behave like a bounded activity that produces phrase context at the
end, so future priming sources can replace the first manual/scripted source
without changing the session flow.

### Expected behavior

1. A user starts a session in the priming pass.
2. A priming source starts.
3. The user plays or otherwise provides priming information.
4. The priming source finishes.
5. The priming source produces `Phrase Context`.
6. The session receives that phrase context.
7. Existing control actions or gestures can bring the companion into the jam
   pass using that context.

The first demo should prove the owner-facing cue:

```text
HEAD_RIGHT during PRIMING_PASS
  -> finish priming source
  -> receive PhraseContext
  -> apply BRING_COMPANION_IN
  -> enter JAM_PASS with active companion
```

After the jam pass has started, the existing gesture behavior should still
apply. For example, `HEAD_LEFT` should still map to `SILENCE_COMPANION`.

### First source shape

The first priming source should have an explicit lifecycle:

```text
start -> finish -> PhraseContext
```

For this milestone, the source may be manual or scripted. It should still act
like a source instead of passing prebuilt phrase context directly into the
session at startup.

`finish` is a priming-source operation, not a session control action. A single
performer cue may orchestrate both steps:

```text
finish priming source -> receive PhraseContext -> BRING_COMPANION_IN
```

Internally, those responsibilities stay separate. `BRING_COMPANION_IN` remains
the session action that makes the companion active; it should not know how to
finish a priming source.

### Out of scope

- real audio capture
- chord recognition
- tempo detection
- embeddings
- prompt generation
- permanent audio recording
- polished setup UI

## Milestone 6 — Integrated webcam priming dry run

### Purpose

Prove the first live-feeling Gitair loop by combining the real webcam gesture
source with the priming source boundary before introducing a production
orchestration abstraction.

Milestone 6 should make this path executable:

```text
Webcam Gesture Source -> Gesture Event -> Control Action
Manual Priming Source -> Phrase Context -> Session
```

The performer-facing behavior should be:

```text
HEAD_RIGHT during PRIMING_PASS
  -> finish priming source
  -> receive PhraseContext
  -> apply BRING_COMPANION_IN
  -> enter JAM_PASS with active companion
```

After the jam pass has started, the existing gesture behavior should still
apply. For example, `HEAD_LEFT` should still map to `SILENCE_COMPANION`.

The first integrated dry run should reuse `ManualPrimingSource` with
CLI-provided phrase context fields. It should not prompt for phrase context
after the gesture, because that would interrupt the performer-facing flow this
milestone is trying to prove.

Milestone 6 should add a new demo command instead of changing the existing
webcam gesture dry run. The existing webcam command should remain focused on
proving the gesture source boundary with phrase context already present; the new
command should prove the integrated priming-to-jam flow.

If `HEAD_LEFT` is emitted while the session is still in the priming pass, the
demo should map it to `SILENCE_COMPANION`, show the existing explicit session
error, and keep priming running. `HEAD_LEFT` should not finish priming, cancel
priming, or be silently ignored in this milestone.

After the companion is active, a repeated `HEAD_RIGHT` should keep the existing
strict rejection for bringing in an already active companion. Milestone 6 should
not add state-dependent gesture remapping such as treating repeated
`HEAD_RIGHT` as intensity control.

### Orchestration boundary

For this milestone, orchestration should remain in the demo layer. Gitair should
not introduce a production `SessionOrchestrator` yet.

The promotion rule is:

```text
Keep orchestration in the demo layer until at least two real flows need the
same coordination logic.
```

This avoids turning the first integrated dry run into a general-purpose
orchestrator before Gitair knows whether orchestration should own source
lifetimes, companion responses, shutdown, UI state, or multiple input streams.

### Validation

Milestone 6 should have automated tests for deterministic orchestration using a
fake source or source factory. Tests should cover:

- `HEAD_LEFT` during the priming pass is visibly rejected and keeps priming
  running
- `HEAD_RIGHT` during the priming pass finishes the priming source, sends phrase
  context to the session, and enters the jam pass with the companion active
- `HEAD_LEFT` after the jam pass starts silences the companion
- repeated `HEAD_RIGHT` while the companion is already active keeps the existing
  explicit rejection

Real webcam behavior remains a human smoke test because it depends on local
hardware, lighting, model files, and camera orientation.

The new demo command should make the architecture visible in terminal output:
priming source state, webcam source status, gesture event, mapped control
action, session snapshot, and companion response should all be clear enough for
the project owner to review from logs.

## Milestone 7 — Audio priming source

### Purpose

Start real priming capture by adding an audio-backed priming source that can
hold a temporary priming audio buffer during the priming pass.

Milestone 7 should prove audio capture plumbing and priming source lifecycle,
not musical analysis. The source should still return manually supplied phrase
context when it finishes.

### First buffer boundary

The first priming audio buffer should be in memory only. It should be discarded
after the dry run and should not be written as a `.wav` file or permanent
recording.

The dry run may print observable buffer facts such as duration, sample rate,
channel count, and frame count so the project owner can confirm that the source
captured audio during the priming pass.

### First input boundary

The first audio-backed priming source should use real microphone or audio-input
capture in the demo. Automated tests should use fake or generated audio chunks
so validation does not depend on local hardware, device permissions, or ambient
sound.

The first microphone capture dependency should be `sounddevice`. It is allowed
as a production dependency for this milestone because it provides focused
cross-platform audio input over PortAudio without pulling in a broader music
analysis stack.

Milestone 7 should keep the existing `PrimingSource` protocol unchanged:

```text
start -> finish -> PhraseContext
```

Audio buffer facts should stay source-local and visible through the dry run
rather than changing `finish` to return a richer result object.

Because Milestone 7 is about capture rather than analysis, the first
audio-backed priming source should still accept manually supplied phrase context
fields and return that context from `finish`.

Milestone 7 should integrate audio capture into the webcam priming flow instead
of creating a separate audio-only milestone. `HEAD_RIGHT` during the priming pass
should stop the audio-backed priming source, keep the captured priming audio
buffer in memory, return the manually supplied phrase context, and then enter
the jam pass through the existing `BRING_COMPANION_IN` action.

Tests should still isolate audio capture behavior with fake audio chunks and
fake webcam observations so hardware-dependent failures remain easy to
diagnose.

Milestone 7 should add a new integrated command for webcam plus audio priming
instead of replacing the existing Milestone 6 command. The Milestone 6 command
should remain as a known-good fallback for debugging gesture and priming
orchestration without microphone permissions or audio device setup.

The new command should be named `webcam_audio_priming_dry_run`.

The demo should log only minimal priming audio buffer facts:

- duration in seconds
- sample rate
- channel count
- frame count
- chunk count

Amplitude, silence, clipping, waveform preview, export, chord recognition, and
tempo analysis are out of scope for this milestone.

Audio capture should start when the audio-backed priming source starts. It does
not need to wait for webcam calibration in this milestone. If future audio
analysis needs cleaner bar boundaries, Gitair can add a separate musical-capture
start cue or source-ready event later.

Audio input setup and runtime failures should use explicit Gitair errors, such
as `AudioSourceSetupError` and `AudioSourceRuntimeError`, instead of leaking raw
`sounddevice` exceptions or silently continuing.

Finishing with zero captured audio chunks should be allowed for Milestone 7, but
the dry run must make that visible through buffer facts such as `chunk_count: 0`,
`frame_count: 0`, and `duration_seconds: 0.0`. Later audio-analysis milestones
can make empty capture a validation failure.

The project owner should define the small `PrimingAudioBuffer` abstraction
before delegating the rest of the milestone. Agents can then implement the
audio-backed priming source, `sounddevice` wiring, demo command, and tests
around that owner-owned buffer shape.

## Current focus — Companion spike

Milestones 1 through 7 are implemented. The next step is not Milestone 8.

Before defining the next milestone, Gitair should run the companion spike
described in [companion-spike-brief.md](companion-spike-brief.md). The spike is
a throwaway real-sound experiment, not a milestone: it answers whether the
companion direction is musically convincing before more shell code is written.

The spike brief records the current decision record, including the jam-pass
repetition contract, cycle-quantized rendering, the companion-owned clock, the
first companion role, and the two-layer memory model.

Sequencing:

1. Run the spike phases in order: first listen, cycle loop bench, jam.
2. Score each jam session with the listening rubric in the brief.
3. Write Milestone 8 from the spike's evidence.

`CONTEXT.md` is deliberately behind the spike brief's decisions. New terms such
as `Cycle`, `Session Record`, and `Companion Role` should be ratified into the
domain language only after the spike validates them.
