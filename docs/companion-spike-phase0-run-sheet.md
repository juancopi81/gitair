# Gitair Companion Spike Phase 0 Run Sheet

> First-listen evidence sheet for model candidates. Phase 0 is model-in-isolation
> research, not Gitair integration.

## Purpose

Phase 0 answers one question:

> Can this model produce one usable cycle of sparse, harmonically-moving
> atmosphere for the canonical Gitair loop in less than the cycle duration?

Do not edit `gitair/core` or promote new domain terms from this sheet. Findings
from this sheet should feed the later Milestone 8 rewrite if a model survives.

## Canonical Loop

Source fixtures:

- `tests/fixtures/gitair_canonical_loop_1.musicxml`
- `tests/fixtures/gitair_canonical_loop_1.expected.json`

Expected values:

```text
chords per bar : C | C | Cmaj7/B | Cmaj7/B | C7/Bb | C7/Bb | Am7 | Am7 | G | G | Gadd4 | Gadd4
bar count      : 12
tempo          : 114 BPM
cycle length   : 25.26 seconds
target texture : sparse harmonically-moving atmosphere
```

Reject a model output if it:

- produces a static pad that does not track the chord or bass movement
- misses the C to B to Bb to A to G bass motion
- collapses the ending color into plain G with no added-4th feel
- adds drums or a lead melody
- becomes too dense or overpowers the guitar role
- cannot generate one usable cycle in less than 25.26 seconds on any acceptable host

## Candidate Plan

| Candidate    | Phase 0 role                             | Host target                                            | Conditioning to try                               | Why it is here                                                                       | First verdict |
| ------------ | ---------------------------------------- | ------------------------------------------------------ | ------------------------------------------------- | ------------------------------------------------------------------------------------ | ------------- |
| MRT2 small   | Primary Gitair/live-instrument candidate | Local Apple Silicon                                    | Text first, then MIDI/audio if setup is practical | Best match for eventual live local companion; not a clean chord-progression baseline | Pending       |
| MRT2 base    | Higher-quality MRT2 comparison           | Local if hardware supports it; otherwise offline/cloud | Same as MRT2 small                                | Tests whether quality gain matters enough for Gitair                                 | Pending       |
| MusiConGen   | Explicit chord + BPM control baseline    | Cloud GPU first                                        | Symbolic chords, BPM, text prompt                 | Best fit for checking whether the canonical chord cycle can be followed directly     | Pending       |
| ACE-Step 1.5 | Optional fast modern wildcard            | Local or cloud, depending on setup                     | Text, duration, BPM, key/meter if supported       | Fast current model; useful if prompt-only output already feels musically promising   | Optional      |

## Shared Prompt Targets

Use the same musical intention for every candidate, adapting syntax to the
model's available inputs:

```text
Sparse warm atmospheric instrumental texture for solo guitar practice.
Follow this 12-bar harmonic cycle at 114 BPM:
C | C | Cmaj7/B | Cmaj7/B | C7/Bb | C7/Bb | Am7 | Am7 | G | G | Gadd4 | Gadd4.
No drums. No lead melody. No vocals. Do not overpower the guitar.
The texture should move with the descending bass and preserve the Gadd4 color.
```

Locality probe, run only after the neutral prompt has a usable baseline:

```text
Sparse warm atmospheric instrumental texture with a subtle Colombian bolero or
bambuco sensibility for solo guitar practice. Follow the same 12-bar harmonic
cycle at 114 BPM. No drums. No lead melody. No vocals.
```

## Run Records

Copy one row per generated output.

| Run ID     | Date       | Candidate    | Host                | Input conditioning  | Prompt variant | Target duration |                  Gen time | Output duration | Harmony following | Texture fit | Locality effect | Verdict  | Notes                                                                                                                                                                    |
| ---------- | ---------- | ------------ | ------------------- | ------------------- | -------------- | --------------: | ------------------------: | --------------: | ----------------- | ----------- | --------------- | -------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| phase0-001 | 2026-07-08 | MRT2 small   | local Apple Silicon | text                | neutral        |          25.26s | 10.1s model / 19.27s wall |          25.26s | weak partial / no | partial     | n/a             | maybe    | Setup works and generation is fast enough for one cycle. Text-only output was audible but not yet musically convincing; needs stronger conditioning or prompt follow-up. |
| phase0-002 | TBD        | MusiConGen   | cloud GPU           | chords + BPM + text | neutral        |          25.26s |                       TBD |             TBD | TBD               | TBD         | n/a             | pending  |                                                                                                                                                                          |
| phase0-003 | TBD        | ACE-Step 1.5 | TBD                 | text + metadata     | neutral        |          25.26s |                       TBD |             TBD | TBD               | TBD         | n/a             | optional |                                                                                                                                                                          |

Use these values for judgment fields:

- `Harmony following`: yes, partial, no
- `Texture fit`: yes, partial, no
- `Locality effect`: meaningful, decorative, none, n/a
- `Verdict`: keep, maybe, reject, pending

## Decision Rule

A model survives Phase 0 only if at least one generated output is:

- `Harmony following`: yes or strong partial
- `Texture fit`: yes
- `Gen time`: less than `25.26s` on local Mac or an acceptable cloud GPU
- `Verdict`: keep

If no candidate survives, do not start Phase 1. Revisit the companion role,
candidate set, or canonical loop before writing cycle-loop code.

## Timing Notes

For `phase0-001`, MRT2 reported:

```text
Generated 631 frames in 10.1s (62.5 steps/s, 16.0 ms/step)
Target: 25 steps/s, 40 ms/step for real-time
Saved ... (25.26s of audio)
real 19.27
```

Interpretation:

- `10.1s model` is the reported generation loop for the 25.26s audio output.
- `19.27s wall` is the full shell command duration, including command startup,
  model loading, warmup, TensorFlow Lite initialization, generation, and file
  writing.
- For performance, a persistent loaded model should be evaluated separately;
  the one-shot CLI wall time is a setup/smoke-test measurement, not the desired
  live architecture.
- The current result still passes Phase 0 timing because both values are less
  than one canonical cycle.

Musical implication:

- If generation can start when the priming pass starts, this timing is good:
  one 25.26s companion cycle can be ready before the musician cues the jam pass.
- If generation can only start after the priming pass finishes, the companion
  would miss the immediate repeat and should enter on a later cycle boundary.
  That is an acceptable fallback to test later, not the target performer
  experience.
