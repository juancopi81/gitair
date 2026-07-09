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

| Candidate | Phase 0 role | Host target | Conditioning to try | Why it is here | First verdict |
|---|---|---|---|---|---|
| MRT2 small | Primary Gitair/live-instrument candidate | Local Apple Silicon | Text first, then MIDI/audio if setup is practical | Best match for eventual live local companion; not a clean chord-progression baseline | Pending |
| MRT2 base | Higher-quality MRT2 comparison | Local if hardware supports it; otherwise offline/cloud | Same as MRT2 small | Tests whether quality gain matters enough for Gitair | Pending |
| MusiConGen | Explicit chord + BPM control baseline | Cloud GPU first | Symbolic chords, BPM, text prompt | Best fit for checking whether the canonical chord cycle can be followed directly | Pending |
| ACE-Step 1.5 | Optional fast modern wildcard | Local or cloud, depending on setup | Text, duration, BPM, key/meter if supported | Fast current model; useful if prompt-only output already feels musically promising | Optional |

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

| Run ID | Date | Candidate | Host | Input conditioning | Prompt variant | Target duration | Gen time | Output duration | Harmony following | Texture fit | Locality effect | Verdict | Notes |
|---|---|---|---|---|---|---:|---:|---:|---|---|---|---|---|
| phase0-001 | TBD | MRT2 small | local | text | neutral | 25.26s | TBD | TBD | TBD | TBD | n/a | pending |  |
| phase0-002 | TBD | MusiConGen | cloud GPU | chords + BPM + text | neutral | 25.26s | TBD | TBD | TBD | TBD | n/a | pending |  |
| phase0-003 | TBD | ACE-Step 1.5 | TBD | text + metadata | neutral | 25.26s | TBD | TBD | TBD | TBD | n/a | optional |  |

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
