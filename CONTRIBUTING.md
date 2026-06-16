# Contributing

Gitair is early and experimental. Prefer small, understandable changes that keep the main architecture, domain language, and milestone behavior easy for the project owner to review.

## Local checks

Use `uv` for the standard local workflow:

```bash
uv run pytest
uv run ruff check .
uv run ruff format --check .
```

For the current Milestone 1 dry run:

```bash
uv run python -m gitair.demos.dry_run_session --chords "E7,G5,A" --tempo-bpm 120 --auto-start-jam
```

## Commit messages

Use Conventional Commit-style prefixes:

- `feat:` for new user-visible or domain behavior
- `fix:` for bug fixes
- `docs:` for documentation-only changes
- `test:` for test-only changes
- `refactor:` for internal restructuring without behavior changes
- `chore:` for maintenance that does not fit the other categories

Prefer `docs:` over `doc:` so commit messages match the common convention.

Examples:

- `docs: add Gitair agent setup and milestone plan`
- `feat: add session state transition core`
- `test: cover priming to jam pass transition`

Keep each commit focused on one reviewable idea.
