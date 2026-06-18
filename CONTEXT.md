# Gitair

Gitair is a guitar-centered human-machine music interface. Its domain language describes the musical interaction between a human player, temporary musical context, an AI companion, and optional control modules.

## Language

**Session**:
A bounded Gitair run that starts after setup and includes the musician's priming pass, the AI-assisted jam pass, companion state, active modules, and current musical context.
_Avoid_: App, performance, standalone jam

**Priming Pass**:
The first part of a session where the musician plays alone so Gitair can capture temporary musical context for the companion.
_Avoid_: Recording, calibration, training

**Jam Pass**:
The second part of a session where the musician plays with the AI companion using the context from the priming pass.
_Avoid_: Playback, generation phase, performance

**Phrase Context**:
Temporary musical information extracted or entered during the priming pass to steer the AI companion during the jam pass.
_Avoid_: Recording, sample, training data, memory

**Companion**:
The AI-driven musical counterpart that joins the musician during a jam pass and is steered by session settings, control actions, and phrase context.
_Avoid_: Model, bandmate, bot, generator

**Companion State**:
The current musical availability and steering posture of the companion within a session, including whether it is active or silent and how intense its contribution should be.
_Avoid_: Model state, backend status

**Gesture**:
A physical movement by the musician that Gitair may interpret as a control signal, such as a head turn, nod, or hand cue.
_Avoid_: Command, shortcut, action

**Gesture Source**:
An input capability that observes or provides musician movement and emits gesture events.
_Avoid_: Camera, detector, mapper

**Gesture Event**:
A recognized, source-neutral signal derived from a musician's gesture before it is mapped to a control action.
_Avoid_: Control action, raw camera frame, shortcut

**Control Action**:
An intentional command accepted by Gitair to change session state, whether triggered by a gesture, keyboard input, MIDI control, or UI control.
_Avoid_: Shortcut, gesture command, UI event

**Module**:
An optional Gitair capability that observes or contributes to a session through defined inputs, context, control actions, companion output, or visuals.
_Avoid_: Plugin, feature, service
