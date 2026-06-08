# Gitair

**Gitair** is an experimental interface for human-machine music interaction.

It starts with a simple idea:

> Play guitar with an AI companion, and control the interaction without taking your hands off the instrument.

Gitair explores guitar, gesture control, phrase memory, AI accompaniment, and futuristic live visuals as parts of one musical interface.

## What is Gitair?

Gitair is a small OSS experiment for building a gesture-controlled AI bandmate for guitar.

The first versions will focus on simple but expressive interactions:

- play guitar while a real-time music model generates accompaniment
- use head gestures to bring the AI companion in or out
- optionally play a short phrase first so the system can extract context
- use that context to steer the AI companion when playing again
- visualize what the system is understanding and doing in real time

The long-term idea is not only to generate music.

The goal is to explore a new kind of **human-machine performance interface**.

## Core interaction ideas

### Raw jam

The simplest mode:

- I play guitar.
- The model plays at the same time.
- No complex control yet.

This answers the first question:

> Does it feel musically interesting to play guitar with the model?

### Gesture control

Use simple gestures as musical cues.

Example mappings:

- turn head right → bring the AI companion in
- turn head left → mute or stop the companion
- nod up/down → change intensity or density

The goal is for gestures to feel like performance cues, not UI shortcuts.

### Phrase priming

Play a short phrase first, then let Gitair use that phrase as context.

Example:

1. Play 4 bars alone.
2. Gitair temporarily analyzes the phrase.
3. Gitair extracts context such as chords, tempo, style, or mood.
4. Play the same phrase again.
5. The AI companion joins, conditioned on the extracted context.

The raw audio does not need to be saved permanently. It can be used as a temporary analysis buffer.

### Live performance interface

Gitair should eventually have a futuristic live screen showing:

- the guitarist on camera
- current gesture state
- companion state
- detected chord or phrase context
- prompt / style direction
- visual overlays reacting to the music

The interface should feel more like an instrument than a normal app dashboard.

## Possible modules

Gitair is intended to stay modular and extensible.

Possible modules include:

- gesture detection
- phrase priming
- chord recognition
- MIDI control
- prompt generation
- AI accompaniment
- live visualizer
- audio effects
- instrument transformation
- recording / export
- practice mode
- performance mode

The first version should stay small, but the project should leave room for new creative modules.

## Initial direction

A possible early architecture:

```text
guitar / webcam / microphone
  → Gitair analysis layer
  → gesture and phrase context
  → model control / MIDI / prompts
  → AI companion + visuals
```

Gitair is not trying to build a new music model at first.

Instead, it acts as a control, conditioning, and interaction layer around existing music models and tools.

## What Gitair is not, at least for now

Gitair is not initially:

- a full DAW
- a polished commercial product
- a perfect AI accompanist
- a full real-time guitar transcription system
- a giant plugin framework

The first goal is to create something small, musical, hackable, and alive.

## Milestones

These are flexible and may change as the project evolves.

### 1. Raw jam test

Play guitar while a real-time model generates music.

Success:

> The experience feels interesting enough to continue.

### 2. Manual steering

Explore simple ways to steer the model manually:

- prompt
- style
- intensity
- volume
- companion on/off
- manual chord input

Success:

> The most useful controls become clear.

### 3. Basic gesture control

Prototype webcam-based gesture control.

Success:

> I can control the AI companion without taking my hands off the guitar.

### 4. Musical gestures

Refine gestures so they feel natural while playing.

Success:

> Gestures feel like musical cues rather than keyboard shortcuts.

### 5. Phrase priming

Prototype listen-first, jam-second conditioning.

Success:

> The AI companion feels more connected to the phrase I played.

### 6. Guitar-aware context

Experiment with automatic context extraction:

- chord recognition
- tempo
- note content
- rhythm density
- phrase structure
- style description
- embeddings

Success:

> The system reacts to musical content, not only manual controls.

### 7. Futuristic live interface

Build a live performance view with video, overlays, and reactive visuals.

Success:

> The screen feels like a compelling human-machine music interface.

### 8. Shareable OSS version

Make the project understandable and runnable by others.

Success:

> Someone can understand the idea quickly and try a rough version.

## Development philosophy

Gitair should stay experimental.

Principles:

- keep it small
- make it hackable
- avoid over-engineering early
- prototype uncertain things quickly
- test with the guitar often
- prioritize musical feel over technical completeness
- leave room for improvisation
- let the structure emerge as the project earns it

## First practical steps

```bash
uv init gitair
cd gitair
mkdir docs
```

Suggested files:

```text
gitair/
  README.md
  docs/
    project-idea.md
  pyproject.toml
  main.py
```

The longer idea document can live in:

```text
docs/project-idea.md
```

## Status

Very early idea / prototype stage.

The project is intentionally open-ended. The current direction may change depending on what feels musical, expressive, technically feasible, and fun to build.
