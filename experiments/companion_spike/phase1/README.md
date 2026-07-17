# Deterministic Cycle Loop Bench

This throwaway Phase 1 experiment repeats one accepted companion Cycle without
invoking MRT2 or integrating with Gitair's production session behavior. It
accepts uncompressed signed 16-bit PCM WAV input and writes derived listening
files only to an explicit directory outside the repository.

## Stage A: compare seams

From the repository root, generate the three-Cycle raw and treated repeats in
one command:

```bash
UV_CACHE_DIR=/tmp/uv-cache-gitair uv run python experiments/companion_spike/phase1/cycle_loop_bench.py stage-a --input-wav /absolute/path/to/gitair_phase0-004.wav --output-dir /absolute/path/to/phase1-listening
```

Both files use intensity `3` (`-6 dB`). The treated file applies a separate
10 ms half-cosine fade-out and fade-in at every internal Cycle Boundary. It
does not overlap or shorten Cycles.

Listen to both outputs and select `raw`, `treated`, or `neither` using the run
sheet. Do not run Stage B when the selection is `neither`.

## Stage B: compare intensity

After selecting a passing seam mode, generate four Cycles at intensities
`3,3,4,4` in one command:

```bash
UV_CACHE_DIR=/tmp/uv-cache-gitair uv run python experiments/companion_spike/phase1/cycle_loop_bench.py stage-b --input-wav /absolute/path/to/gitair_phase0-004.wav --output-dir /absolute/path/to/phase1-listening --seam-mode raw
```

Replace `raw` with `treated` only when that is the selected seam mode. The
terminal transcript reports source identity, SHA-256, audio format, mode,
gains, output paths, Cycle duration, total duration, and the absence of
normalization. Human listening judgments remain pending in
`docs/companion-spike-phase1-run-sheet.md`.

If the fixed `3 dB` step is too subtle, generate the `+4 dB`, `+6 dB`, and
`+10 dB` calibration files together:

```bash
UV_CACHE_DIR=/tmp/uv-cache-gitair uv run python experiments/companion_spike/phase1/cycle_loop_bench.py stage-b-sweep --input-wav /absolute/path/to/gitair_phase0-004.wav --output-dir /absolute/path/to/phase1-listening --seam-mode raw
```

Every file keeps the first two Cycles at `-6 dB`. The last two Cycles use
`-2 dB`, `0 dB`, and `+4 dB`, respectively. These are gain-calibration values,
not new discrete Intensity levels. Positive gain is allowed only when the input
has enough headroom; the bench rejects a render rather than clipping samples.
