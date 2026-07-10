# MRT2 Note-Conditioned Phase 0 Prototype

This throwaway experiment asks one question:

> Does explicit MIDI note conditioning make MRT2 follow Gitair's canonical
> chord and descending-bass movement better than the text-only `phase0-001`
> run?

It reads the canonical expected fixture, maps each chord to a transparent MIDI
voicing, carries MRT2 streaming state across all 12 bars, suppresses drums, and
writes a uniquely named WAV outside the repository. It does not integrate MRT2
with `gitair/core`.

## Inspect the plan

This does not load MRT2:

```bash
uv run python experiments/companion_spike/phase0/mrt2_notes_conditioned_smoke.py --plan-only
```

Review the voicings in `mrt2_note_conditioning.py` before listening. They encode
the descending bass as `C3 -> B2 -> Bb2 -> A2 -> G2`; the intentional Ab skip is
preserved.

## Run the experiment

From the Gitair repository root:

```bash
MAGENTA_HOME="$HOME/Documents/Magenta" \
UV_CACHE_DIR=/tmp/uv-cache-gitair \
/usr/bin/time -p uv run --with 'magenta-rt[mlx]==2.0.2' \
python experiments/companion_spike/phase0/mrt2_notes_conditioned_smoke.py \
  --run-id phase0-004
```

The default `strict` mode sets every non-chord pitch to off and each chord pitch
to MRT2's active/auto-strum state. It also passes `drums=[0]`. The output is
written under:

```text
~/Documents/Magenta/magenta-rt-v2/outputs/
```

The filename begins with `gitair_phase0-004_mrt2_small_strict_` and includes a
timestamp, so it will not overwrite earlier runs. Use a new `--run-id` for each
recorded experiment; without one, the filename remains generic instead of
claiming an evidence ID.

The completed MRT2 base comparison can be reproduced with:

```bash
MAGENTA_HOME="$HOME/Documents/Magenta" \
UV_CACHE_DIR=/tmp/uv-cache-gitair \
/usr/bin/time -p uv run --with 'magenta-rt[mlx]==2.0.2' \
python experiments/companion_spike/phase0/mrt2_notes_conditioned_smoke.py \
  --run-id phase0-005 \
  --model mrt2_base
```

For a looser comparison where non-chord pitches are unspecified instead of
forbidden, run:

```bash
MAGENTA_HOME="$HOME/Documents/Magenta" \
UV_CACHE_DIR=/tmp/uv-cache-gitair \
/usr/bin/time -p uv run --with 'magenta-rt[mlx]==2.0.2' \
python experiments/companion_spike/phase0/mrt2_notes_conditioned_smoke.py \
  --conditioning creative
```

After listening, compare the result with earlier runs and add the chosen
`--run-id` to `docs/companion-spike-phase0-run-sheet.md`. The prototype can be
deleted after its musical finding is captured there.
