# Gitair — Companion Spike Brief

> The first real-sound experiment: answer the README's oldest question — does it
> feel musically interesting to play guitar with the model? — under the
> decisions recorded here, before rewriting milestones or writing production
> code.

## Status

This is an evolving working document, like `project-idea.md`.

It was produced from a blind-spot interview (July 2026) about the leap from the
working gesture/priming/session shell toward a musically convincing companion.
It records the decisions that interview resolved, the questions it deliberately
deferred, the design of the first spike, and the listening rubric that makes
spike sessions comparable.

The spike is throwaway by design. Its code does not need to respect the session
core. Its *findings* feed the next milestone rewrite, the domain language, and
new ADRs — all owner-ratified after the spike, not before.

## Decision record

These decisions were made deliberately and should be treated as current
direction until the spike contradicts them.

### 1. The jam pass is a repetition contract

The jam pass v1 is the primed phrase repeating — the loop-pedal model. The
priming pass defines a **cycle** (the phrase's form and length); the jam pass is
that form cycling until a control action ends or changes it. Repetition
constrains the *form*, not the *duration*: a 15-second priming produces a
15-second cycle, not a 15-second jam.

Deliberate divergence — playing against what the companion believes the phrase
is — is known, named behavior, not an error. It is also the most hauntological
interaction in the project: the machine faithfully accompanies the ghost of the
phrase while the musician walks away from it.

Open jam (context-seeded free playing) is a possible later mode, not a
violation of this contract.

### 2. Phrase context gains a cycle boundary

`PhraseContext` must eventually carry the cycle length (bar count and/or
seconds). A cycling companion cannot exist without it. This is the first known
contract change the spike's findings should shape.

### 3. Cycle-quantized generation

Companion audio is (re)generated per cycle. All steering — intensity changes,
silencing, the entrance itself — takes effect at the next cycle boundary, the
way a clip launcher quantizes launches.

This softens three hard problems at once:

- gesture latency stops mattering (any cue within the cycle lands correctly)
- model steering becomes discrete instead of mid-stream
- transitions happen at form boundaries, which is where the aesthetics doc
  already wanted its thresholds

Identical replay of one generated cycle is the legitimate first implementation
step, not a compromise.

### 4. The companion owns the clock

In v1 the companion renders cycles on its own timeline and the musician locks
to it, as with a loop pedal. Tempo drift is the player's job. Beat tracking —
the companion following the player — is deferred as a later "breathing"
refinement, not abandoned.

### 5. Entrance: instant by pre-generation, boundary as fallback

The target performer experience: finish priming with one cue and repeat the
phrase with the companion already there.

Because v1 phrase context is manual, cycle 1 can be generated **during the
priming pass**. On the cue, the companion starts its cycle immediately and the
player locks in from its top. The atmosphere role makes this gentle for free: a
pad's slow attack is its own entrance.

Fallback when generation is not ready: the player keeps looping and the
companion enters at the first cycle boundary where its audio exists — late but
never misplaced. Whether the entrance needs any cortinilla marking beyond the
natural swell is a spike question.

### 6. Companion role is a session-setup parameter

The musician chooses the companion's role before the session (CLI flag now,
setup screen later). Each role declares which phrase-context fields it needs —
the role sits upstream of the priming contract and shapes how the musician
primes.

The first role to build and validate: **harmonically-moving atmosphere** — a
texture that audibly follows the primed chord cycle, not a static key/mood
wash. This is the smallest role where priming feels causal.

### 7. The model slot is open

MRT2 is candidate #1 and has never been run; "resource-friendly" is a claim to
verify, not a fact. Cycle-quantized generation means one-shot chord-conditioned
models are also eligible — the requirement is "one cycle of conditioned audio in
less than one cycle's duration," not streaming. Local Mac inference is a
first-class test target; cloud GPU is acceptable for experiments.

### 8. Practice instrument first, with session-critical aesthetics

For the next phase Gitair is a practice-room instrument. But the aesthetic is
not deferred polish: every session should feel like entering somewhere — the
interface serves the player's zone, not an audience. A minimal-but-felt live
view therefore earns earlier milestone placement than the current milestone
order implies, once sound exists.

### 9. Two-layer memory

- **Machine memory stays ephemeral.** The priming audio buffer is discarded,
  phrase context is temporary, nothing the machine holds outlives the session,
  nothing is ever training data. The ephemerality principle survives untouched.
- **Session Record** is a new, explicitly distinct concept: optional,
  local, player-owned documentation *of* the session — audio plus the steering
  timeline (context, control actions, cycle boundaries). It exists for the
  human: remembering good jams, and scoring the rubric below. It never feeds
  the companion.

### 10. Strict core, graceful surface

Session-core errors stay strict. The live layer renders a rejected cue as a
gentle "not now" signal — never a crash, never silence. Accepted cues appear
immediately as **queued** in the live view and execute at the next boundary;
without that acknowledgment, cycle quantization creates an elevator-button
problem. Acknowledgment is peripheral-visual only for now; audio earcons are a
possible later setup option.

### 11. Reliable cue channel for the spike

The spike uses a keyboard press (or the available MiniLab controller) as its
cue so that musical judgment is never polluted by gesture-detection noise. Head
gestures rejoin immediately after the sound is validated — that integration
already exists. Audio-domain cues (silence ends priming) are a possible later
priming-source refinement.

### 12. Rig

- Monitoring: headphones (no companion bleed into capture).
- Capture: adapt to what is easiest — built-in Mac microphone is acceptable for
  the spike; a Focusrite interface is available if needed.
- Cue hardware: keyboard first; Arturia MiniLab MkII available.

## Deferred questions

Explicitly parked, with their trigger for revisiting:

- **Jam-time listening** beyond phrase-position tracking — after the spike
  shows whether the deaf-but-informed companion already convinces.
- **Beat tracking / companion follows the player** — when the fixed clock
  becomes the thing that breaks the zone.
- **Audio-domain cues** — when gestures prove unreliable during real playing.
- **Open-jam mode** — when the repetition contract feels limiting rather than
  focusing.
- **Configurable role/gesture setup screen** — when more than one role works.
- **Exact entrance and fin de emisión treatments** — after the swell-in
  entrance is heard in practice.

## The canonical test loop

Every spike session uses the same phrase so results are comparable across
sessions and models:

> A simple broken-chord arpeggio in C major, moto perpetuo, texture akin to the
> prelude of Bach's first cello suite. The bass descends from C to B to Bb to A,
> then skips Ab and lands on G, ending on a G major colored with an added 4th (a
> C note held over G major).

Why this loop is a good instrument:

- The continuous figuration has a steady pulse and no silences — good for
  locking to the companion's clock, and proof that priming needs an explicit
  finish cue.
- The chromatic bass descent makes harmony-following unmistakable: if the
  texture moves with the descent on the repeat, "it heard me" is audible to
  anyone.
- Chromatic/slash-chord harmony stress-tests chord conditioning exactly where
  naive models break.

The canonical source file is
`tests/fixtures/gitair_canonical_loop_1.musicxml`. The companion expected fixture
is `tests/fixtures/gitair_canonical_loop_1.expected.json`. Future ML analysis
should parse the MusicXML and compare its output against the expected fixture.

```text
chords per bar : C | C | Cmaj7/B | Cmaj7/B | C7/Bb | C7/Bb | Am7 | Am7 | G | G | Gadd4 | Gadd4
bar count      : 12
tempo          : 114 BPM
cycle length   : 25.26 seconds
```

## Spike design

Three phases, in order. Each phase has a kill/keep question; do not advance
past a failed phase.

### Phase 0 — First listen (model in isolation, no Gitair)

Run MRT2 and at least one chord-conditioned one-shot alternative, raw.
Use [companion-spike-phase0-run-sheet.md](companion-spike-phase0-run-sheet.md)
to record candidate setup, generated outputs, and keep/reject decisions.

Measure:

- seconds to generate one cycle-length chunk, on the Mac and on a cloud GPU
- which conditioning channels actually work: text, chords, tempo, anything else
- whether "sparse, warm, atmospheric, no drums, no melody" is achievable
- the locality probe: does asking for bolero or bambuco texture change the
  music, or only decorate the prompt?

Kill/keep:

> Keep a model if it can produce a usable atmospheric texture for the canonical
> loop's harmony in under one cycle's duration on any acceptable hardware.

### Phase 1 — Cycle loop bench (no guitar yet)

With the surviving model, build the cycle mechanics as throwaway code:

- generate one cycle for the canonical loop's context and loop it seamlessly
- regenerate the next cycle with an intensity change applied at the boundary
- listen for seam audibility at the loop point and across the change

Kill/keep:

> Keep going if cycles loop without a jarring seam and a boundary intensity
> change is audible and proportionate.

### Phase 2 — Jam with it (guitar in hand)

The real experiment. Headphones on, keyboard cue, session recorded as a
Session Record (audio + steering timeline).

1. Play the canonical loop as the priming pass while cycle 1 generates.
2. Cue. The companion enters; lock into the repetition.
3. Jam several cycles. Steer intensity up and down. Silence it. Bring it back.
4. Deliberately diverge from the phrase for a few cycles and listen to what
   playing against the ghost feels like.
5. Stop. Score the rubric immediately, while the feeling is fresh.

Success looks like:

> Playing the loop with the companion feels better than playing it alone, and
> the texture audibly follows the changes.

## Listening rubric

Score each dimension 1–5 immediately after every Phase 2 session. The scores
belong to the Session Record.

| # | Dimension | The question |
|---|-----------|--------------|
| 1 | Entrance | Did the companion's entrance feel caused by my phrase? |
| 2 | Following | Could I hear the texture move with the bass descent? |
| 3 | Togetherness | Did the cycle boundaries feel shared, or did we drift apart? |
| 4 | Steering | Did intensity changes produce audible, proportionate change at the next boundary? |
| 5 | Zone | Was this better than practicing alone? Did anything eject me from the zone? |
| 6 | Locality | Did genre words change the music, or only the caption? |
| 7 | Divergence | Was playing against the ghost interesting, or just broken? |

Plus one free line per session: **the moment I remember.**

### Session journal entry template

```text
date           :
model / host   :
cycle length   :
gen time (s)   :
cue→sound (s)  :
scores         : entrance _ following _ togetherness _ steering _ zone _ locality _ divergence _
moment         :
keep / change  :
```

## Implied documentation updates (after the spike, owner-ratified)

The spike's findings should drive these; none should be written preemptively:

- **CONTEXT.md**: candidate terms `Cycle`, `Session Record`, `Companion Role`,
  each with avoid-lists; scope the recording anti-vocabulary to machine memory.
- **ADRs**: one for the repetition contract + cycle-quantized steering +
  companion-owned clock; one for two-layer memory.
- **milestones.md**: write Milestone 8 from spike evidence. Note honestly that
  Milestone 2's success criterion ("which controls matter musically") only
  becomes evaluable now that sound exists.
- **research-modules.md**: mark MRT2 as candidate-unvalidated; add the
  chord-conditioned one-shot candidates the first listen actually tested.
