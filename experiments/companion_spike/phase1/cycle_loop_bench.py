"""Deterministic offline Cycle loop bench for the Phase 1 companion spike."""

from __future__ import annotations

import argparse
import hashlib
import math
import struct
import sys
import wave
from dataclasses import dataclass
from pathlib import Path
from typing import Literal, Sequence

GAIN_DB = {1: -12, 2: -9, 3: -6, 4: -3, 5: 0}
DEFAULT_SWEEP_DELTAS_DB = (4, 6, 10)
SWEEP_BASELINE_DB = GAIN_DB[3]
SEAM_SECONDS = 0.010
REPOSITORY_ROOT = Path(__file__).resolve().parents[3]

SeamMode = Literal["raw", "treated"]


class BenchError(ValueError):
    """A clear, user-facing input or rendering error."""


@dataclass(frozen=True)
class WavAudio:
    source_path: Path
    sha256: str
    sample_rate: int
    channels: int
    sample_width: int
    frames: int
    pcm: bytes

    @property
    def duration_seconds(self) -> float:
        return self.frames / self.sample_rate

    @property
    def format_description(self) -> str:
        return (
            f"signed {self.sample_width * 8}-bit PCM, {self.sample_rate} Hz, "
            f"{self.channels} channel(s)"
        )


def gain_db(intensity: int) -> int:
    try:
        return GAIN_DB[intensity]
    except KeyError as error:
        raise BenchError("Intensity must be an integer from 1 through 5.") from error


def load_wav(path: Path) -> WavAudio:
    source_path = path.expanduser().resolve()
    if not source_path.is_file():
        raise BenchError(f"Input WAV does not exist: {source_path}")

    source_bytes = source_path.read_bytes()
    try:
        with wave.open(str(source_path), "rb") as input_wav:
            compression = input_wav.getcomptype()
            sample_width = input_wav.getsampwidth()
            channels = input_wav.getnchannels()
            sample_rate = input_wav.getframerate()
            frames = input_wav.getnframes()
            pcm = input_wav.readframes(frames)
    except (EOFError, wave.Error) as error:
        raise BenchError(f"Unsupported or invalid WAV: {error}") from error

    if compression != "NONE":
        raise BenchError(f"Unsupported WAV compression {compression!r}; expected uncompressed PCM.")
    if sample_width != 2:
        raise BenchError(
            f"Unsupported WAV sample width {sample_width * 8}-bit; expected signed 16-bit PCM."
        )
    if channels < 1 or sample_rate < 1 or frames < 1:
        raise BenchError(
            "Unsupported WAV format; channels, sample rate, and frames must be positive."
        )
    expected_bytes = frames * channels * sample_width
    if len(pcm) != expected_bytes:
        raise BenchError(
            f"Truncated WAV data: expected {expected_bytes} PCM bytes, read {len(pcm)}."
        )

    return WavAudio(
        source_path=source_path,
        sha256=hashlib.sha256(source_bytes).hexdigest(),
        sample_rate=sample_rate,
        channels=channels,
        sample_width=sample_width,
        frames=frames,
        pcm=pcm,
    )


def apply_gain(pcm: bytes, intensity: int) -> bytes:
    return apply_gain_db(pcm, gain_db(intensity))


def apply_gain_db(pcm: bytes, decibels: int) -> bytes:
    if decibels == 0:
        return pcm

    factor = 10 ** (decibels / 20)
    samples = struct.unpack(f"<{len(pcm) // 2}h", pcm)
    adjusted = tuple(round(sample * factor) for sample in samples)
    if any(sample < -32_768 or sample > 32_767 for sample in adjusted):
        raise BenchError(f"Gain {decibels:+d} dB would clip signed 16-bit PCM samples.")
    return struct.pack(f"<{len(samples)}h", *adjusted)


def _fade_factors(length: int) -> tuple[tuple[float, ...], tuple[float, ...]]:
    if length == 1:
        return (0.0,), (0.0,)
    fade_in = tuple(0.5 - 0.5 * math.cos(math.pi * index / (length - 1)) for index in range(length))
    return fade_in, tuple(reversed(fade_in))


def apply_seam_treatment(cycles: list[bytearray], *, sample_rate: int, channels: int) -> None:
    fade_frames = round(SEAM_SECONDS * sample_rate)
    frame_bytes = channels * 2
    cycle_frames = len(cycles[0]) // frame_bytes
    if fade_frames < 1:
        raise BenchError("Sample rate is too low for a 10 ms seam treatment.")
    if fade_frames * 2 > cycle_frames:
        raise BenchError("Cycle is too short for separate non-overlapping 10 ms seam fades.")

    fade_in, fade_out = _fade_factors(fade_frames)
    for boundary in range(len(cycles) - 1):
        outgoing = cycles[boundary]
        incoming = cycles[boundary + 1]
        _apply_fade(outgoing, fade_out, channels=channels, start_frame=cycle_frames - fade_frames)
        _apply_fade(incoming, fade_in, channels=channels, start_frame=0)


def _apply_fade(
    pcm: bytearray, factors: tuple[float, ...], *, channels: int, start_frame: int
) -> None:
    for fade_frame, factor in enumerate(factors):
        for channel in range(channels):
            offset = ((start_frame + fade_frame) * channels + channel) * 2
            sample = struct.unpack_from("<h", pcm, offset)[0]
            struct.pack_into("<h", pcm, offset, round(sample * factor))


def render_cycles(audio: WavAudio, intensities: Sequence[int], seam_mode: SeamMode) -> bytes:
    return render_gain_cycles(audio, tuple(gain_db(level) for level in intensities), seam_mode)


def render_gain_cycles(audio: WavAudio, gains_db: Sequence[int], seam_mode: SeamMode) -> bytes:
    cycles = [bytearray(apply_gain_db(audio.pcm, gain)) for gain in gains_db]
    if seam_mode == "treated":
        apply_seam_treatment(cycles, sample_rate=audio.sample_rate, channels=audio.channels)
    return b"".join(cycles)


def write_wav(path: Path, audio: WavAudio, pcm: bytes) -> None:
    with wave.open(str(path), "wb") as output_wav:
        output_wav.setnchannels(audio.channels)
        output_wav.setsampwidth(audio.sample_width)
        output_wav.setframerate(audio.sample_rate)
        output_wav.writeframes(pcm)


def prepare_output_directory(path: Path) -> Path:
    output_directory = path.expanduser().resolve()
    if output_directory == REPOSITORY_ROOT or REPOSITORY_ROOT in output_directory.parents:
        raise BenchError(
            f"Output directory must be outside the tracked repository: {REPOSITORY_ROOT}"
        )
    output_directory.mkdir(parents=True, exist_ok=True)
    return output_directory


def run_stage_a(input_path: Path, output_directory: Path) -> tuple[Path, Path]:
    audio = load_wav(input_path)
    output_directory = prepare_output_directory(output_directory)
    raw_path = output_directory / f"{audio.source_path.stem}_stage-a_raw_3-3-3.wav"
    treated_path = output_directory / f"{audio.source_path.stem}_stage-a_treated_3-3-3.wav"
    intensities = (3, 3, 3)
    write_wav(raw_path, audio, render_cycles(audio, intensities, "raw"))
    write_wav(treated_path, audio, render_cycles(audio, intensities, "treated"))
    _print_transcript(audio, "stage-a raw + treated", intensities, (raw_path, treated_path))
    return raw_path, treated_path


def run_stage_b(input_path: Path, output_directory: Path, seam_mode: SeamMode) -> Path:
    audio = load_wav(input_path)
    output_directory = prepare_output_directory(output_directory)
    intensities = (3, 3, 4, 4)
    output_path = output_directory / (f"{audio.source_path.stem}_stage-b_{seam_mode}_3-3-4-4.wav")
    write_wav(output_path, audio, render_cycles(audio, intensities, seam_mode))
    _print_transcript(audio, f"stage-b {seam_mode}", intensities, (output_path,))
    return output_path


def run_stage_b_sweep(
    input_path: Path,
    output_directory: Path,
    seam_mode: SeamMode,
    gain_deltas_db: Sequence[int] = DEFAULT_SWEEP_DELTAS_DB,
) -> tuple[Path, ...]:
    if not gain_deltas_db or any(delta <= 0 for delta in gain_deltas_db):
        raise BenchError("Gain sweep deltas must contain one or more positive integers.")
    if len(set(gain_deltas_db)) != len(gain_deltas_db):
        raise BenchError("Gain sweep deltas must be unique.")

    audio = load_wav(input_path)
    output_directory = prepare_output_directory(output_directory)
    outputs: list[tuple[int, tuple[int, ...], Path]] = []
    for delta in gain_deltas_db:
        target_gain = SWEEP_BASELINE_DB + delta
        gains = (SWEEP_BASELINE_DB, SWEEP_BASELINE_DB, target_gain, target_gain)
        output_path = output_directory / (
            f"{audio.source_path.stem}_stage-b_{seam_mode}_gain-plus-{delta}db.wav"
        )
        write_wav(output_path, audio, render_gain_cycles(audio, gains, seam_mode))
        outputs.append((delta, gains, output_path))

    _print_sweep_transcript(audio, seam_mode, outputs)
    return tuple(output_path for _, _, output_path in outputs)


def _print_transcript(
    audio: WavAudio, mode: str, intensities: Sequence[int], output_paths: Sequence[Path]
) -> None:
    gains = ", ".join(f"{level}:{gain_db(level):+d}dB" for level in intensities)
    print(f"source          : {audio.source_path}")
    print(f"source_sha256   : {audio.sha256}")
    print(f"audio_format    : {audio.format_description}")
    print(f"mode            : {mode}")
    print(f"intensities     : {','.join(map(str, intensities))}")
    print(f"gains           : {gains}")
    print(f"cycle_duration  : {audio.duration_seconds:.6f} s ({audio.frames} frames)")
    print(
        f"total_duration  : {audio.duration_seconds * len(intensities):.6f} s "
        f"({audio.frames * len(intensities)} frames)"
    )
    print("normalization   : none")
    for index, output_path in enumerate(output_paths, start=1):
        print(f"output_{index}        : {output_path}")


def _print_sweep_transcript(
    audio: WavAudio,
    seam_mode: SeamMode,
    outputs: Sequence[tuple[int, tuple[int, ...], Path]],
) -> None:
    print(f"source          : {audio.source_path}")
    print(f"source_sha256   : {audio.sha256}")
    print(f"audio_format    : {audio.format_description}")
    print(f"mode            : stage-b gain sweep {seam_mode}")
    print(f"baseline_gain   : {SWEEP_BASELINE_DB:+d} dB")
    print(f"cycle_duration  : {audio.duration_seconds:.6f} s ({audio.frames} frames)")
    print(
        f"total_duration  : {audio.duration_seconds * 4:.6f} s "
        f"({audio.frames * 4} frames per output)"
    )
    print("normalization   : none")
    for index, (delta, gains, output_path) in enumerate(outputs, start=1):
        formatted_gains = ",".join(f"{gain:+d}" for gain in gains)
        print(f"output_{index}_delta  : +{delta} dB")
        print(f"output_{index}_gains  : {formatted_gains} dB")
        print(f"output_{index}        : {output_path}")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="stage", required=True)
    for stage in ("stage-a", "stage-b", "stage-b-sweep"):
        stage_parser = subparsers.add_parser(stage)
        stage_parser.add_argument("--input-wav", type=Path, required=True)
        stage_parser.add_argument("--output-dir", type=Path, required=True)
        if stage in ("stage-b", "stage-b-sweep"):
            stage_parser.add_argument("--seam-mode", choices=("raw", "treated"), required=True)
        if stage == "stage-b-sweep":
            stage_parser.add_argument(
                "--gain-deltas-db",
                nargs="+",
                type=int,
                default=DEFAULT_SWEEP_DELTAS_DB,
                metavar="DB",
            )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        if args.stage == "stage-a":
            run_stage_a(args.input_wav, args.output_dir)
        elif args.stage == "stage-b":
            run_stage_b(args.input_wav, args.output_dir, args.seam_mode)
        else:
            run_stage_b_sweep(
                args.input_wav,
                args.output_dir,
                args.seam_mode,
                args.gain_deltas_db,
            )
    except (BenchError, OSError) as error:
        print(f"error: {error}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
