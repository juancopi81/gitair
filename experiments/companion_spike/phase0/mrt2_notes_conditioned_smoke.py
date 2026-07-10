"""PROTOTYPE: test whether MIDI note conditioning improves MRT2 chord following."""

from __future__ import annotations

import argparse
import time
from datetime import datetime
from pathlib import Path

from mrt2_note_conditioning import (
    FRAMES_PER_SECOND,
    build_bar_plan,
    build_notes_vector,
    load_fixture,
)

REPO_ROOT = Path(__file__).resolve().parents[3]
DEFAULT_FIXTURE = REPO_ROOT / "tests/fixtures/gitair_canonical_loop_1.expected.json"
DEFAULT_PROMPT = (
    "Sparse warm atmospheric instrumental texture for solo guitar practice. "
    "No drums. No lead melody. No vocals. Do not overpower the guitar. "
    "Preserve space for the guitar."
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Generate the canonical Gitair loop with explicit MRT2 MIDI note conditioning."
        )
    )
    parser.add_argument("--fixture", type=Path, default=DEFAULT_FIXTURE)
    parser.add_argument(
        "--run-id",
        help="Optional evidence ID included in the output filename, such as phase0-004.",
    )
    parser.add_argument("--model", default="mrt2_small")
    parser.add_argument(
        "--conditioning",
        choices=("strict", "creative"),
        default="strict",
        help="Strict turns non-chord pitches off; creative leaves them masked.",
    )
    parser.add_argument("--cfg-musiccoca", type=float, default=3.0)
    parser.add_argument("--cfg-notes", type=float, default=2.0)
    parser.add_argument("--temperature", type=float, default=1.3)
    parser.add_argument("--top-k", type=int, default=40)
    parser.add_argument("--prompt", default=DEFAULT_PROMPT)
    parser.add_argument("--output", type=Path)
    parser.add_argument(
        "--plan-only",
        action="store_true",
        help="Print the chord, MIDI, and frame plan without loading MRT2.",
    )
    return parser.parse_args()


def print_plan(fixture: dict, plan: list, mode: str) -> None:
    total_frames = sum(bar.frames for bar in plan)
    print("MRT2 Note-Conditioned Phase 0 Prototype")
    print(f"  fixture: {fixture['id']}")
    print(f"  tempo_bpm: {fixture['tempo_bpm']}")
    print(f"  conditioning: {mode}")
    print(f"  canonical_duration: {fixture['display_cycle_length_seconds']:.2f}s")
    print(
        f"  quantized_duration: {total_frames / FRAMES_PER_SECOND:.2f}s "
        f"({total_frames} frames at {FRAMES_PER_SECOND} Hz)"
    )
    print("\nBar conditioning")
    for bar in plan:
        notes = ", ".join(bar.note_names)
        pitches = ", ".join(str(pitch) for pitch in bar.midi_pitches)
        print(
            f"  {bar.bar_number:02d}. {bar.chord:<8} "
            f"notes=[{notes}] midi=[{pitches}] frames={bar.frames}"
        )


def generate(args: argparse.Namespace, plan: list) -> None:
    try:
        from magenta_rt import MagentaRT2Mlxfn, paths
        from magenta_rt.audio import concatenate
    except ImportError as error:
        raise SystemExit(
            "MRT2 MLX is not available. Run this script with the command in "
            "experiments/companion_spike/phase0/README.md."
        ) from error

    wall_started = time.perf_counter()
    setup_started = time.perf_counter()
    model = MagentaRT2Mlxfn(
        size=args.model,
        temperature=args.temperature,
        top_k=args.top_k,
        cfg_musiccoca=args.cfg_musiccoca,
        cfg_notes=args.cfg_notes,
    )
    style = model.embed_style(args.prompt, use_mapper=True)
    setup_seconds = time.perf_counter() - setup_started

    print("\nGeneration")
    print(f"  model: {args.model}")
    print(f"  cfg_musiccoca: {args.cfg_musiccoca}")
    print(f"  cfg_notes: {args.cfg_notes}")
    print("  drums: off")

    state = None
    chunks = []
    generation_started = time.perf_counter()
    for bar in plan:
        bar_started = time.perf_counter()
        notes = build_notes_vector(bar.midi_pitches, args.conditioning)
        waveform, state = model.generate(
            style=style,
            notes=notes,
            drums=[0],
            frames=bar.frames,
            state=state,
        )
        chunks.append(waveform)
        print(
            f"  bar {bar.bar_number:02d} {bar.chord:<8} "
            f"frames={bar.frames} generated_in={time.perf_counter() - bar_started:.2f}s"
        )
    generation_seconds = time.perf_counter() - generation_started

    output = concatenate(chunks)
    output_path = args.output
    if output_path is None:
        timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        run_id = f"{args.run_id}_" if args.run_id else ""
        output_path = paths.outputs_dir() / (
            f"gitair_{run_id}{args.model}_{args.conditioning}_{timestamp}.wav"
        )
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output.write(str(output_path))
    wall_seconds = time.perf_counter() - wall_started

    print("\nResult")
    print(f"  output: {output_path}")
    print(f"  output_duration: {output.seconds:.2f}s")
    print(f"  model_setup_and_style: {setup_seconds:.2f}s")
    print(f"  generation: {generation_seconds:.2f}s")
    print(f"  wall_after_import: {wall_seconds:.2f}s")
    print("  next: listen against the Phase 0 reject criteria and update the run sheet")


def main() -> None:
    args = parse_args()
    fixture = load_fixture(args.fixture)
    plan = build_bar_plan(fixture)
    print_plan(fixture, plan, args.conditioning)
    if not args.plan_only:
        generate(args, plan)


if __name__ == "__main__":
    main()
