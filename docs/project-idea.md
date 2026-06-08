# Gitair — Project Idea

> Gitair is an experimental interface for human-machine music interaction, starting from guitar, gesture, phrase memory, and AI accompaniment.

## Status

This is an evolving idea document.

It is not meant to freeze the project too early.
Its purpose is to preserve the current vision, keep the direction clear, and leave plenty of room for improvisation, experimentation, and change.

## One-line description

Gitair is a gesture-controlled AI bandmate for guitar.

Alternative framing:

- Jam with an AI companion without taking your hands off the guitar.
- A future-looking interface for human-machine music interaction.
- A small OSS experiment for playing with AI music systems using guitar, gesture, phrase memory, and visual feedback.

## Core idea

Gitair begins with a simple question:

> What would it feel like to play guitar with a machine that can accompany, react, visualize, and eventually understand some musical context?

The initial version is centered around:

- guitar performance
- a real-time generative music model
- gesture-based control
- optional phrase-based conditioning
- a visually expressive interface

The project is not only about “making AI music.”

It is about designing a new kind of **musical interaction layer** between a person and a generative system.

## Why this is interesting

Gitair sits at the intersection of:

- guitar practice and improvisation
- AI music generation
- real-time interaction
- gesture control
- music understanding
- visual performance interfaces
- creative coding
- modular experimental tools

The long-term interest is not only the musical output.

It is also the interface itself:

- how a musician steers the machine
- how the machine reveals what it is doing
- how sound, gesture, and visuals can become one interactive system
- how the whole thing can feel more like an instrument than an app

## Why the name Gitair?

Gitair is a small wordplay around:

- guitar
- AI
- Git / GitHub / OSS

The name should feel lightweight, hackable, and playful.

## North Star

Gitair is a future-looking interface for human-machine music interaction.

The guitar is the anchor because it is personal, expressive, and hands-occupied. That makes it a good instrument for exploring:

- gesture-based control
- AI accompaniment
- phrase memory
- chord-aware conditioning
- visual feedback
- sound transformation
- modular human-machine performance systems

The larger idea is not only to make an AI jam with me.

It is to explore what it feels like to perform with a system that can:

- accompany
- react
- listen in limited ways
- receive context
- visualize what it understands
- transform sound
- become part instrument, part bandmate, part interface

## What this project is

Gitair is best understood as a **control, conditioning, and interaction layer** around one or more music-generation or music-understanding systems.

At first, it should not try to invent a new foundation model.

Instead, it should combine existing components in a musical, modular, and extensible way.

## What this project is not, at least at first

Gitair is not initially:

- a full DAW
- a perfect AI accompanist
- a polished commercial product
- a full real-time guitar transcription system
- a giant plugin framework
- a research-heavy end-to-end model project

The first goal is to make something that works, feels alive, and opens interesting directions.

## Early system idea

A possible first mental model is:

```text
human musician
  → guitar / gesture / optional phrase input
  → Gitair core
  → analysis / conditioning
  → AI music model
  → sound + visuals + interaction feedback
```

Or in more modular terms:

```text
inputs
  → analysis
  → event/context layer
  → output modules
  → UI
```

## Main interaction modes

### 1. Raw jam mode

The simplest version.

- I play guitar.
- The model generates music at the same time.
- No gesture control yet.
- No chord recognition yet.
- No complex intelligence yet.

This mode answers the first important question:

> Is it interesting or enjoyable to play guitar while the model does its own thing?

If the answer is no, the project should not become over-engineered too early.

### 2. Gesture control mode

In this mode, the player controls the system through gestures.

Examples:

- turn head right → companion on
- turn head left → companion off
- nod up → increase intensity
- nod down → decrease intensity

This should not feel like “computer commands.”

It should feel more like **musical steering**.

### 3. Phrase priming mode

This is one of the more interesting musical ideas.

The system listens temporarily to a short phrase before the jam begins.

Example:

- I play 4 bars alone.
- Gitair extracts useful context from that phrase.
- I play the same phrase again.
- The model now joins me, conditioned by what Gitair extracted from the first pass.

The phrase does not need to be stored permanently.
It can be treated as a temporary analysis buffer.

Possible extracted context:

- chord progression
- key or tonal center
- tempo
- bar count
- rhythmic density
- note content
- style clues
- optional audio/music embedding
- optional descriptive prompt

This mode can be thought of as:

- phrase priming
- phrase memory
- listen-first, jam-second conditioning

### 4. Visual performance mode

This is where Gitair becomes more than an audio experiment.

The idea is to create a visually expressive interface that shows:

- what the musician is doing
- what the system is understanding
- what the system is generating
- what just changed
- why it changed

The visual layer should feel futuristic, elegant, and alive.

## Interface concept

Gitair should have at least **two main screens**.

### Screen 1 — Setup / Steering

This screen is for configuration before the performance begins.

It answers:

> How is the machine going to behave in this session?

Possible sections:

#### Session setup

- model selection
- mode selection
- companion style
- responsiveness
- intensity range

#### Prompt steering

- text prompt
- style description
- optional poetic prompt
- manual chord input
- phrase priming options
- harmonic-following options

#### Active modules

- gesture module
- phrase priming
- chord recognition
- visualizer
- audio FX
- instrument transformation
- practice mode

#### Gesture mapping

- which gestures are enabled
- what each gesture does
- sensitivity / threshold settings
- whether actions are instant or gradual

#### Input / output

- webcam
- microphone / audio interface
- MIDI routing
- output routing
- latency indication

#### Session start

- start performance
- arm phrase priming
- test camera / audio / gesture preview

This screen should feel like:

- control room
- lab bench
- modular synth setup
- experimental configuration interface

### Screen 2 — Live Performance View

This screen is the live performance screen.

It should feel like a **human-machine performance interface**, not a normal software dashboard.

The player’s video is central, and information is layered around it in a clean, cinematic, futuristic way.

Possible elements:

#### Core live view

- live video of the guitarist
- slightly stylized or enhanced image
- subtle grading or lighting treatment
- optional background treatment later

#### Musical state

- current chord
- key or tonal center
- tempo
- bar count
- phrase state
- energy level

#### Companion state

- companion active / inactive
- current model
- current style
- prompt summary
- intensity / density
- active modules

#### Gesture state

- last detected gesture
- current mapped action
- confidence / stability
- accepted gestures

#### Phrase priming state

- idle
- listening
- analyzing
- context ready
- jamming

#### Visual / mathematical layer

Not necessarily raw math everywhere, but elegant abstractions of the system’s inner state, such as:

- harmonic nodes
- energy curves
- phrase arcs
- note constellations
- prompt drift
- density fields
- chord maps
- confidence meters
- reactive particles or geometry

The aesthetic direction should feel:

- futuristic
- elegant
- ultra-clean
- minimal but alive
- high-end experimental
- slightly “Terminator panel,” but refined

Possible visual traits:

- dark background
- controlled neon accents
- sharp typography
- glassy or translucent panels
- motion-reactive overlays
- cyan / magenta / violet / amber accents
- scanline / HUD-like hints without becoming cluttered

## Core UX principle

At any moment, the interface should help answer:

1. What am I playing?
2. What is the machine understanding?
3. What is the machine generating?
4. What just changed?
5. Why did it change?

If Gitair can communicate those things clearly, the interface will feel intelligent.

## Extensibility

Gitair should be easy to extend.

A good direction is to think in terms of:

- a small core
- simple events or context objects
- optional modules that subscribe to those events

The goal is not to build a giant framework from day one.

The goal is to make it easy to add optional creative modules later.

Possible module categories:

### Input modules

- webcam
- microphone
- audio interface
- MIDI input
- keyboard input

### Analysis modules

- gesture detection
- chord recognition
- tempo estimation
- note extraction
- phrase analysis
- energy / dynamics
- embedding extraction
- descriptive prompt generation

### Output modules

- AI companion control
- MIDI output
- keyboard shortcut output
- visualizer
- audio effects
- instrument transformation
- recording / export

### Experience modules

- practice mode
- performance mode
- phrase priming mode
- visual world mode
- session memory

Some example future modules:

- a beautiful live visualizer
- a module that transforms the guitar sound
- a module that adds ambient layers
- a module that builds descriptive prompts from playing style
- a module that turns chord changes into a visual harmonic map
- a module that acts as a practice companion
- a module that saves short playable “scene presets”

## Conditioning ideas

Gitair may condition the music model through different channels.

Examples:

### Text conditioning

Simple descriptive prompts.

Examples:

- warm, sparse, intimate guitar accompaniment
- ethereal ambient layer that follows a C, E, G, G7 progression
- cinematic shimmer that supports but does not overpower the guitar

### Chord / MIDI conditioning

Probably one of the most musically useful channels.

Examples:

- manual chord progression
- detected chords
- note sets
- phrase-derived harmonic cues

### Audio / embedding conditioning

Potentially useful for style, texture, or mood.

Likely better as one ingredient in a larger context object, rather than the only source of control.

### Hybrid conditioning

Probably the best longer-term direction.

Example:

- chord progression
- rough tempo
- style text
- optional phrase embedding
- optional note content
- optional poetic prompt

## Suggested milestones

These milestones are intentionally broad and flexible.

They are here to guide the project, not to lock it down.

### Milestone 1 — Raw jam test

Test the simplest possible version of the idea.

- play guitar
- let the model generate at the same time
- do not add too much structure yet

Success looks like:

> The experience feels musically interesting enough to continue.

### Milestone 2 — Manual steering

Before adding gestures, explore manual ways of steering the system.

Examples:

- prompt changes
- companion on/off
- intensity changes
- chord input
- style changes

Success looks like:

> I understand which controls matter most musically.

### Milestone 3 — Basic gesture control

Add a small gesture layer.

Examples:

- left / right head turns
- nod up / down
- neutral state

Success looks like:

> I can steer the companion without taking my hands off the guitar.

### Milestone 4 — Make the gestures feel musical

Refine mappings, stability, thresholds, and timing.

Success looks like:

> The gestures feel like performance cues rather than UI shortcuts.

### Milestone 5 — Phrase priming

Add a basic version of listen-first, jam-second conditioning.

It can start very simply, including:

- manual chords
- rough tempo
- simple text prompt
- phrase-aware session setup

Success looks like:

> The second pass feels more musically connected than the first.

### Milestone 6 — Guitar-aware context extraction

Explore ways for the system to extract more useful context automatically.

Possible directions:

- chord recognition
- note extraction
- rhythmic density
- phrase segmentation
- descriptive text generation
- embedding-based style memory

Success looks like:

> The system begins to react to the musical content of the guitar, not only to manual controls.

### Milestone 7 — Visual performance interface

Create a strong live interface that makes the system feel futuristic, intelligible, and expressive.

Success looks like:

> The performance screen feels like a compelling human-machine instrument interface.

### Milestone 8 — Modular expansion

Open the door to optional modules.

Possible next directions:

- visuals
- FX
- sound transformation
- practice mode
- recording/export
- performance scenes

Success looks like:

> Adding a new module feels natural rather than invasive.

### Milestone 9 — Shareable OSS version

Make the project understandable and runnable by others.

Success looks like:

> Someone can understand the idea quickly and try a rough version without too much friction.

## Rough demo ideas

### Demo 1 — Raw jam

- play guitar
- companion plays at the same time
- show whether the interaction feels interesting

### Demo 2 — Gesture companion

- play guitar
- use a gesture to bring the companion in
- use another gesture to bring it out
- show simple live state overlays

### Demo 3 — Phrase priming

- play 4 bars alone
- system extracts context
- play the same 4 bars again
- companion joins in a way that feels related

### Demo 4 — Futuristic performance interface

- live video of the guitarist
- ultra-clean futuristic overlays
- chord, gesture, and companion state visible
- visuals responding to the music and interaction

## Development philosophy

Gitair should be built in a way that encourages exploration.

Key principles:

- keep it small
- make it hackable
- avoid over-engineering early
- use existing tools when possible
- leave room for improvisation
- prototype uncertain things quickly
- test the musical experience often
- let the structure emerge as the project earns it
- favor living experiments over rigid design

## Open questions

These questions are intentionally left open.

- What is the best first music model to use? [Research](research-modules.md)
- Should the first versions be local, browser-based, or hybrid?
- What is the smallest viable phrase priming workflow?
- How much musical understanding is enough for a useful experience?
- Which gesture mappings feel most natural?
- How much of the interface should be practical versus cinematic?
- What visual language best communicates the system’s internal state?
- Which modules are most worth building first?
- Should Gitair lean more toward practice, performance, or experimentation?
- What would make the project easy for others to try?
- What would make it viable as a polished product later?

## First practical next steps

- initialize the repo
- create `docs/project-idea.md`
- keep `README.md` short
- test a raw jam manually
- write quick notes on whether it feels musically interesting
- prototype simple head tracking
- prototype one gesture mapped to one action
- sketch a two-screen UI
- keep all early choices easy to revise

## Minimal README direction

A possible short README later could say:

> Gitair is a small OSS experiment for human-machine music interaction. It starts with guitar, AI accompaniment, gesture control, phrase priming, and a futuristic live interface.

## Final note

This project should stay open.

The current ideas are useful as a direction, but Gitair should be allowed to evolve based on:

- what feels musical
- what feels expressive
- what is technically feasible
- what is visually compelling
- what becomes fun enough to keep building
