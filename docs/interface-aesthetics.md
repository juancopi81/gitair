# Gitair — Interface Aesthetics

> Working notes on the visual and ritual direction for the Gitair interface, developed from a reading of Mark Fisher's hauntology and a set of personal lost futures.
>
> The short version: ghosts live in transitions, and the phrase lives only once — se vive solamente una vez.

## Status

This is an evolving direction document, like `project-idea.md`.

It records aesthetic reasoning so future interface work does not default to a generic sci-fi dashboard. It is project-owner territory: agents should preserve the reasoning here, not convert it automatically into UI components.

Nothing here overrides the core UX principle in `project-idea.md`. At any moment the live interface must still answer: what am I playing, what is the machine understanding, what is it generating, what just changed, and why.

## The starting tension

`project-idea.md` says the live view should feel futuristic — "slightly 'Terminator panel,' but refined."

There is something worth noticing inside that sentence. Our shared image of "the futuristic" — neon on dark, HUD overlays, cyan and magenta accents — is itself a quotation of how the 1980s and early 1990s imagined the future. The future became a period style.

Gitair should not pretend otherwise. The interface should work with that fact deliberately instead of wearing it as an unexamined skin.

## The frame, briefly

Drawing on Mark Fisher's *Ghosts of My Life*, this document treats retro style and hauntological memory as two different design operations:

- **Formal nostalgia**: the past reproduced frictionlessly, as style. A global VHS filter, scanlines as wallpaper, retro as genre. The distance between then and now is erased.
- **Hauntology**: work that keeps the gap audible and visible — the disjuncture between the future that was promised and the present that arrived. The crackle stays in the mix — not as an effect, but as evidence that past and present do not line up cleanly.

Gitair should never do the first. If ghosts appear in this interface, they must carry friction.

One further distinction matters here. The Terminator HUD is a **lost future**: how people once imagined machine perception. Colombian broadcast ritual is closer to a **lost medium**: a real world where television had schedules, thresholds, endings, and shared national time — and then stopped existing. Gitair combines both: a lost technological future and a lost broadcast temporality, inside a live interface where machine perception and the bounded session are finally real.

## Why hauntology fits Gitair structurally

The domain model is already spectral, before any pixel is drawn:

- The priming pass produces phrase context that is explicitly **not** a recording, not memory, not permanent — a temporary trace.
- During the jam pass, the musician plays with the machine-held memory of their own playing from moments ago.
- The priming audio buffer is discarded. The phrase lives once.

So the aesthetic direction is not to add ghosts to the interface. It is to reveal the ones already built into the architecture.

## Direction principles

### 1. Structure over surface

Visualize the trace, not the texture. The interesting object is the phrase context: something captured, held, decaying, steering the companion, then gone. Show what the machine remembers as spectral — present-as-absence — rather than as a crisp data panel.

No global scanline, VHS, or CRT filters. That is the formal nostalgia this document exists to prevent.

### 2. Quotation must be marked and local

If the interface quotes the old imagined future, it does so in one deliberate place where the quotation means something.

The natural candidate is the machine-vision panel — the place where the machine literally looks at the musician, which is the Terminator shot. That one panel may speak the language of how the 80s imagined machine sight, with the real thing (MediaPipe landmark mesh, yaw degrees, confidence floats) bleeding through it. The gap between imagined machine vision and actual machine vision is the artwork.

Everywhere else stays in the clean, present-tense language.

### 3. Ghosts live in transitions

Broadcast memory lived between programs — cortinillas, test patterns, sign-offs — never inside them. The same rule applies here:

- The live jam view stays clean and present-tense. It answers the five UX questions and competes with nothing.
- Memory textures belong to the liminal states: setup, the stillness of the priming pass, session end, idle.

### 4. Local ghosts, not generic ones

Fisher's hauntology was intensely local — British broadcast memory, a specifically British lost future. Transposing the method to Gitair means using its own locality: Bogotá, late 80s and 90s.

Structural sources, not surface kitsch:

- **Fin de emisión.** Colombian television ended each day — test pattern, anthem, screen off. Broadcast days had edges; that temporal structure is itself a lost thing. A Gitair session is bounded by design, so it can end the way the broadcast day ended: a sign-off ritual rather than an app closing. A structural quotation passes this test: it works even for people who do not recognize it.
- **Programadora / cortinilla logic.** Colombian programadoras rented time slots on shared public channels, each announcing itself before its program. The companion entering the jam pass is a program coming on the shared channel; modules rent time on a shared session. The companion's entrance can have something of the cortinilla's ritual quality — a marked announcement of presence, not a toggle flipping.

Be bogotano, not generic "Latin." The flattened tropical-kitsch register is the local equivalent of the VHS filter.

### 5. Locality lives in the language layer

Style and prompt vocabulary should speak local genres as first-class citizens — bambuco, pasillo, bolero, chicha — instead of translating everything into Anglo genre tags. The demo defaults already do this. Locality in the language layer costs nothing visually and cannot become kitsch.

### 6. The ephemerality anchor

The bolero "Amar y vivir" (Consuelo Velázquez) — which named the telenovela — carries the line:

> Se vive solamente una vez.

The architecture and the bolero agree: the phrase lives once; the machine holds its ghost briefly; then it is gone. This is the candidate epigraph for the project, and the natural sentiment for the fin de emisión state.

### 7. Anti-cliché tests

Every proposed reference must pass:

- **The Aterciopelados test.** "Bolero Falaz" quotes the grandparents' bolero from inside the culture, transformed, with love and irony at once — never cosplay. If a reference feels like costumbrismo or a costume, cut it.
- **No nostalgia trivia.** A reference that only works as recognition — "if you know, you know" — is the listicle mode of memory. References must do structural work even for people who don't catch them.
- **Load-bearing ghosts only.** A handful, each doing real interface work. Currently four: fin de emisión for session end, the cortinilla threshold for companion entrance, the machine-vision quotation for the camera panel, and the bolero line as the emotional anchor for ephemerality. Everything else — including every named show in the personal canon — feeds the sensibility and stays out of the interface.

## Interface consequences

The principles above reduce to constraints that future interface work can be checked against:

- The live jam view remains operationally clean. It answers the five UX questions and carries no memory treatment.
- Hauntological treatments are allowed only in liminal states: setup, priming, transitions, idle, and sign-off.
- Every ghost visual must correspond to a real system state — a buffered phrase, extracted context, a confidence value, decay over time, a companion entrance or exit. No fake HUD theater.
- The machine-vision quotation is confined to the camera/gesture panel.
- The fin de emisión ritual must be short and skippable; a performance is never held hostage by a sign-off.
- Local genre vocabulary must reach actual model and prompt behavior, not only labels. If "bambuco" only changes a caption, it is decoration.

## Personal canon

The specific memory this direction draws from, recorded so the references stay honest and specific:

- Terminator-era imagined machine vision (global lost future)
- Colombian television: Dejémonos de vainas, Amar y vivir, Oki Doki (local lost future)
- Bogotá rock: Aterciopelados, 1280 Almas (the method model for quotation)
- Mark Fisher, *Ghosts of My Life*; hauntological music (Burial, The Caretaker, Ghost Box) as method references, not style references

## What this is not

- not a skin spec or component list
- not final — it should survive or die by contact with real prototypes
- not autobiography: personal memory enters only where it does structural work
- not permission for retro filters

## Prototype bias

The first prototype should not try to express the whole canon.

It should test one structural ghost:

- the priming trace as a decaying phrase-memory object, or
- the companion entrance as a short cortinilla-like threshold, or
- the session end as a fin de emisión ritual.

If the reference does not clarify the musical interaction, it is removed.

## Open questions

- Which liminal state deserves ritual treatment first?
- What does fin de emisión concretely look and sound like?
- Should the companion's entrance have a cortinilla-like announcement, and how short must it be to stay musical?
- How should phrase-context decay be visualized without misleading the musician about what the system actually knows?
- How much of this survives the first real prototype?
