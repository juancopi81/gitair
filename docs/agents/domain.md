# Domain Docs

How the engineering skills should consume this repo's domain documentation when exploring the codebase.

## Layout

Gitair currently uses a single-context domain-doc layout:

```text
/
├── CONTEXT.md
├── docs/adr/
└── src/ or gitair/
```

Use `CONTEXT-MAP.md` only if the repo later grows into multiple contexts, such as separate frontend, audio engine, model bridge, and runtime packages.

## Before exploring, read these

- `CONTEXT.md` at the repo root, if it exists.
- Relevant ADRs under `docs/adr/`, if they exist.
- `README.md`, `docs/project-idea.md`, `docs/milestones.md`, and `docs/research-modules.md` for current product direction.

If `CONTEXT.md` or ADRs do not exist yet, proceed silently. They are created lazily when project terms or architectural decisions become explicit.

## Use the glossary's vocabulary

When output names a domain concept, use the term as defined in `CONTEXT.md`. For Gitair, early terms include `Session`, `Priming Pass`, `Jam Pass`, `Phrase Context`, `Companion`, `Gesture`, `Control Action`, and `Module`.

If the concept you need is not in the glossary yet, note the gap instead of inventing competing vocabulary.

## Flag ADR conflicts

If output contradicts an existing ADR, surface it explicitly rather than silently overriding it.
