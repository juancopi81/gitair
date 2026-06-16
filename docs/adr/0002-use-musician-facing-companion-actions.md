# Use musician-facing companion actions

Gitair will use musician-facing control actions for companion steering instead of exposing implementation-shaped phase names as the primary action vocabulary. In particular, `BRING_COMPANION_IN` is the performer-facing action: during `PRIMING_PASS` it ends priming, enters `JAM_PASS`, and activates the companion; during `JAM_PASS` with a silent companion, it brings the companion back using the existing phrase context.

## Considered Options

- **Keep `START_JAM_PASS` as the main action**: accurate as an internal phase transition, but less natural for the musician because the performance cue is "come in."
- **Use `BRING_COMPANION_IN` as the main action**: keeps the action language musical and lets the same future gesture or input cue have a state-aware effect without making the core action ambiguous.

Actual physical gesture mappings are deferred. A later gesture layer can map head, hand, pedal, or keyboard inputs into explicit control actions based on the current session state.
