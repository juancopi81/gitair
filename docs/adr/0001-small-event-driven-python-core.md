# Start with a small event-driven Python core

Gitair will start with a small event-driven Python core centered on a `Session`, where `Control Action`s change session state and optional `Module`s observe or contribute to the interaction. This keeps the main architecture owned by Gitair's musical concepts instead of by an early UI, webcam implementation, or specific music model, while leaving the `Companion` behind an adapter that can later target MRT2 or another system.

## Considered Options

- **UI-first prototype**: useful for visual direction, but likely to make screens and widgets own the architecture too early.
- **Model-first integration**: useful for testing sound quickly, but likely to couple Gitair to one companion backend before the interaction language is clear.
- **Small event-driven Python core**: gives the project stable terms and seams for agents to implement modules, adapters, tests, and later interfaces around.
