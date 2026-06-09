# Gitair Agent Guide

## Project posture

Gitair is an early experimental repo for a guitar-centered human-machine music interface. Keep changes small, reversible, and grounded in the current project docs.

Before broad design or implementation work, read:

- `README.md`
- `CONTRIBUTING.md`
- `docs/project-idea.md`
- `docs/milestones.md`
- `docs/research-modules.md`

The project owner should retain the main architecture, domain language, milestone behavior, and module contracts. Agents can implement narrow helper files, adapters, tests, and prototypes once those contracts are explicit.

## Agent skills

### Issue tracker

Issues are tracked in GitHub Issues for `juancopi81/gitair`. See `docs/agents/issue-tracker.md`.

### Triage labels

This repo uses the canonical triage labels: `needs-triage`, `needs-info`, `ready-for-agent`, `ready-for-human`, and `wontfix`. See `docs/agents/triage-labels.md`.

### Domain docs

This repo uses a single-context domain-doc layout with root `CONTEXT.md` and root `docs/adr/`. See `docs/agents/domain.md`.
