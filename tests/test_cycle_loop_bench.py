import struct
import wave
from pathlib import Path

import pytest

from experiments.companion_spike.phase1 import cycle_loop_bench as bench


def write_test_wav(
    path: Path,
    samples: tuple[int, ...] = (1000, -1000, 2000, -2000, 3000, -3000),
    *,
    sample_rate: int = 1000,
    channels: int = 1,
    sample_width: int = 2,
) -> bytes:
    if sample_width == 2:
        pcm = struct.pack(f"<{len(samples)}h", *samples)
    else:
        pcm = bytes(samples)
    with wave.open(str(path), "wb") as output:
        output.setnchannels(channels)
        output.setsampwidth(sample_width)
        output.setframerate(sample_rate)
        output.writeframes(pcm)
    return pcm


def read_wav(path: Path) -> tuple[wave._wave_params, bytes]:
    with wave.open(str(path), "rb") as source:
        return source.getparams(), source.readframes(source.getnframes())


def test_gain_mapping_and_level_five_preserves_samples(tmp_path: Path) -> None:
    pcm = write_test_wav(tmp_path / "source.wav")

    assert [bench.gain_db(level) for level in range(1, 6)] == [-12, -9, -6, -3, 0]
    assert bench.apply_gain(pcm, 5) == pcm
    with pytest.raises(bench.BenchError, match="1 through 5"):
        bench.gain_db(0)


def test_arbitrary_gain_rejects_clipping(tmp_path: Path) -> None:
    pcm = write_test_wav(tmp_path / "source.wav", samples=(30_000,))

    with pytest.raises(bench.BenchError, match=r"Gain \+4 dB would clip"):
        bench.apply_gain_db(pcm, 4)


def test_stage_a_lengths_and_raw_repetition(tmp_path: Path) -> None:
    input_path = tmp_path / "source.wav"
    source_pcm = write_test_wav(input_path, samples=tuple(range(1, 31)))
    output_dir = tmp_path / "outputs"

    raw_path, treated_path = bench.run_stage_a(input_path, output_dir)
    raw_params, raw_pcm = read_wav(raw_path)
    treated_params, treated_pcm = read_wav(treated_path)
    gained_cycle = bench.apply_gain(source_pcm, 3)

    assert raw_params.nframes == 90
    assert treated_params.nframes == 90
    assert raw_pcm == gained_cycle * 3
    assert len(treated_pcm) == len(raw_pcm)


def test_seam_treatment_is_separate_and_does_not_change_outer_samples(tmp_path: Path) -> None:
    input_path = tmp_path / "source.wav"
    write_test_wav(input_path, samples=(10_000,) * 30)
    audio = bench.load_wav(input_path)

    raw = struct.unpack("<90h", bench.render_cycles(audio, (5, 5, 5), "raw"))
    treated = struct.unpack("<90h", bench.render_cycles(audio, (5, 5, 5), "treated"))

    assert treated[0] == raw[0] == 10_000
    assert treated[-1] == raw[-1] == 10_000
    assert treated[29] == 0
    assert treated[30] == 0
    assert treated[59] == 0
    assert treated[60] == 0
    assert treated[20] == raw[20]
    assert treated[39] == raw[39]
    assert treated[50] == raw[50]
    assert treated[69] == raw[69]


@pytest.mark.parametrize("seam_mode", ["raw", "treated"])
def test_stage_b_modes_have_exact_four_cycle_length(tmp_path: Path, seam_mode: str) -> None:
    input_path = tmp_path / "source.wav"
    source_pcm = write_test_wav(input_path, samples=tuple(range(1, 31)))

    output_path = bench.run_stage_b(input_path, tmp_path / "outputs", seam_mode)
    params, output_pcm = read_wav(output_path)

    assert params.nframes == 120
    assert len(output_pcm) == len(source_pcm) * 4
    if seam_mode == "raw":
        assert (
            output_pcm == bench.apply_gain(source_pcm, 3) * 2 + bench.apply_gain(source_pcm, 4) * 2
        )


def test_stage_b_sweep_writes_requested_deltas_from_common_baseline(tmp_path: Path) -> None:
    input_path = tmp_path / "source.wav"
    source_pcm = write_test_wav(input_path, samples=tuple(range(1, 31)))

    output_paths = bench.run_stage_b_sweep(
        input_path,
        tmp_path / "outputs",
        "raw",
        (4, 6, 10),
    )

    assert [path.name.rsplit("gain-plus-", 1)[1] for path in output_paths] == [
        "4db.wav",
        "6db.wav",
        "10db.wav",
    ]
    for output_path, target_gain in zip(output_paths, (-2, 0, 4), strict=True):
        params, output_pcm = read_wav(output_path)
        assert params.nframes == 120
        assert output_pcm == (
            bench.apply_gain_db(source_pcm, -6) * 2
            + bench.apply_gain_db(source_pcm, target_gain) * 2
        )


def test_stage_b_sweep_rejects_empty_nonpositive_and_duplicate_deltas(tmp_path: Path) -> None:
    input_path = tmp_path / "source.wav"
    write_test_wav(input_path)

    for deltas, message in (((), "positive"), ((0,), "positive"), ((4, 4), "unique")):
        with pytest.raises(bench.BenchError, match=message):
            bench.run_stage_b_sweep(input_path, tmp_path / "outputs", "raw", deltas)


def test_invalid_input_and_tracked_output_are_rejected(tmp_path: Path) -> None:
    invalid_path = tmp_path / "unsupported.wav"
    write_test_wav(invalid_path, samples=(1, 2, 3), sample_width=1)

    with pytest.raises(bench.BenchError, match="expected signed 16-bit PCM"):
        bench.load_wav(invalid_path)
    with pytest.raises(bench.BenchError, match="outside the tracked repository"):
        bench.prepare_output_directory(bench.REPOSITORY_ROOT / "derived-audio")


def test_cli_reports_machine_facts_without_judgments(tmp_path: Path, capsys) -> None:
    input_path = tmp_path / "source.wav"
    write_test_wav(input_path, samples=tuple(range(1, 31)))

    result = bench.main(
        [
            "stage-b",
            "--input-wav",
            str(input_path),
            "--output-dir",
            str(tmp_path / "outputs"),
            "--seam-mode",
            "treated",
        ]
    )
    transcript = capsys.readouterr().out

    assert result == 0
    for fact in (
        "source_sha256",
        "audio_format",
        "mode",
        "gains",
        "cycle_duration",
        "total_duration",
        "normalization   : none",
        "output_1",
    ):
        assert fact in transcript
    assert "verdict" not in transcript
    assert "jarring" not in transcript
