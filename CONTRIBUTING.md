# Contributing

Gitair is early and experimental. Prefer small, understandable changes that keep the main architecture, domain language, and milestone behavior easy for the project owner to review.

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
