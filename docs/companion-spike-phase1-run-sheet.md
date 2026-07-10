# Gitair Companion Spike Phase 1 Run Sheet

> Evidence sheet for the deterministic Cycle loop bench. Phase 1 evaluates
> rendering mechanics from one accepted companion Cycle; it does not invoke
> MRT2 or integrate with Gitair's session core.

## Purpose

Phase 1 answers two questions:

> Does the selected companion Cycle repeat without a jarring seam?

> Does one queued intensity step produce an audible, proportionate prominence
> change at the next Cycle Boundary?

## Selected Input

```text
file            : gitair_phase0-004_mrt2_small_strict_20260710-171022.wav
sha256          : 6c2d1f3cd8c00837e232867bf5cabe3316ad38e62da5b18517115c19546d96dc
sample_rate     : 48000 Hz
channels        : 2
sample_format   : signed 16-bit PCM
cycle_duration  : 25.28 seconds
```

The WAV remains outside the repository under the local Magenta outputs
directory. The hash identifies the exact source used by the bench.

## Expected Outputs

| Output | Cycle sequence | Expected duration | Purpose |
| --- | --- | ---: | --- |
| Raw repeat | `3, 3, 3` | `75.84s` | Hear untreated Cycle Boundaries |
| Treated repeat | `3, 3, 3` | `75.84s` | Compare the fixed `10 ms` seam treatment |
| Intensity transition | `3, 3, 4, 4` | `101.12s` | Judge one queued `3 dB` step using the selected seam mode |

All outputs must preserve the `25.28s` Cycle duration. Derived WAVs stay
outside tracked repository paths. The source and outputs are not normalized;
intensity `5` is the unchanged `0 dB` reference and lower levels only attenuate
it.

The bench runs in two stages. First generate and judge the raw and treated
repeats. Generate the intensity transition only after selecting `raw` or
`treated`. If both seam modes are jarring, select `neither`, leave the intensity
output pending, and record `rework` or `stop`.

## Run Record

Fill this after generating and listening to the available outputs. When neither
seam mode passes, leave the intensity output fields pending.

```text
date                  :
raw_output            :
raw_duration          :
treated_output        :
treated_duration      :
intensity_output      :
intensity_duration    :
normalization         : none
raw_seam              : pending
treated_seam          : pending
treatment_side_effect : pending
selected_seam_mode    : pending
intensity_3_to_4      : pending
verdict               : pending
musical_notes         :
```

Judgment values:

- `raw_seam`, `treated_seam`: inaudible, audible-not-jarring, jarring
- `treatment_side_effect`: none, dip, smear
- `selected_seam_mode`: raw, treated, neither
- `intensity_3_to_4`: inaudible, proportionate, excessive
- `verdict`: keep, rework, stop

## Decision Rule

Keep going when:

- at least one seam mode is not jarring
- the selected seam mode introduces no unacceptable dip or harmonic smear
- intensity `3 -> 4` is audible and proportionate at the exact Cycle Boundary
- every output preserves the expected Cycle and total durations

Use `rework` when a specific rendering adjustment could plausibly pass these
criteria. Use `stop` when deterministic Cycle playback itself breaks the
musical premise.
