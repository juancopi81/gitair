# Use musician-facing companion actions

Gitair will use musician-facing control actions for companion steering instead
of exposing implementation-shaped phase names as the primary action vocabulary.
In particular, `BRING_COMPANION_IN` is the performer-facing action: during
`PRIMING_PASS` it enters `JAM_PASS` and activates the companion once phrase
context is available; during `JAM_PASS` with a silent companion, it brings the
companion back using the existing phrase context.

When a priming source is present, the same performer cue may first finish the
priming source and send its phrase context to the session. That orchestration is
outside the session action itself: `BRING_COMPANION_IN` does not know how to
finish a priming source.

Because Gitair is still early, `BRING_COMPANION_IN` replaces the old phase-start action rather than wrapping it or keeping it as a compatibility alias.

## Considered Options

- **Keep the phase-start action as the main action**: accurate as an internal phase transition, but less natural for the musician because the performance cue is "come in."
- **Use `BRING_COMPANION_IN` as the main action**: keeps the action language musical and lets the same future gesture or input cue have a state-aware effect without making the core action ambiguous.

Actual physical gesture mappings are deferred. A later gesture layer can map head, hand, pedal, or keyboard inputs into explicit control actions based on the current session state.

The first companion steering state will stay intentionally small:

- `status`: `active` or `silent`
- `intensity`: integer from `1` to `5`
- default when the companion first enters: `status=active`, `intensity=3`

`INCREASE_INTENSITY` and `DECREASE_INTENSITY` change this target intensity one step at a time and clamp at `1` and `5`. Smooth crescendos or decrescendos are companion rendering behavior, not part of the first session state contract.

This keeps the session understandable while still allowing the performer to silence the companion, bring it back, or change its prominence without replacing the current phrase context.
