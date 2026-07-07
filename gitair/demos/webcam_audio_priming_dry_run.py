"""
Integrated webcam and audio-backed priming dry run for Gitair.

This demonstrates the Milestone 7 flow:

1. An AudioPrimingSource starts while Session is still in PRIMING_PASS.
2. Audio chunks are captured in memory during the priming pass.
3. HEAD_RIGHT during PRIMING_PASS finishes audio capture, logs minimal buffer
   facts, sends PhraseContext to Session, then applies BRING_COMPANION_IN.
4. HEAD_LEFT after JAM_PASS still silences the companion.
"""

import argparse
from collections.abc import Callable
from pathlib import Path
from time import sleep
from typing import Any, Protocol

from gitair.companions.fake import FakeCompanion
from gitair.core.control_action import ControlAction, ControlActionType
from gitair.core.errors import GitairError
from gitair.core.phrase_context import PhraseContext
from gitair.core.session import Session
from gitair.core.session_snapshot import SessionPhase
from gitair.demos.dry_run_session import (
    create_demo_phrase_context,
    parse_chords,
    print_companion_response,
    print_snapshot,
)
from gitair.demos.webcam_gesture_dry_run import (
    format_source_status,
    should_print_source_status,
    source_status_key,
)
from gitair.gestures.mapper import GestureMapper
from gitair.gestures.mediapipe_face import (
    DEFAULT_CALIBRATION_FRAMES,
    DEFAULT_CAMERA_INDEX,
    DEFAULT_YAW_MULTIPLIER,
    FACE_LANDMARKER_MODEL_ENV_VAR,
    HeadTurnObservation,
    OpenCVWebcamGestureSource,
)
from gitair.priming.audio import (
    DEFAULT_AUDIO_BLOCKSIZE,
    DEFAULT_AUDIO_CHANNELS,
    DEFAULT_AUDIO_SAMPLE_RATE,
    AudioPrimingSource,
    AudioStreamFactory,
)
from gitair.priming.audio_buffer import PrimingAudioBuffer
from gitair.priming.source import PrimingSource

SourceFactory = Callable[..., Any]


class AudioBackedPrimingSource(PrimingSource, Protocol):
    """Priming source with source-local audio buffer facts."""

    @property
    def audio_buffer(self) -> PrimingAudioBuffer:
        """Return observable facts about the in-memory priming audio buffer."""
        ...


def run_webcam_audio_priming_dry_run(
    phrase_context: PhraseContext | None = None,
    *,
    priming_source: AudioBackedPrimingSource | None = None,
    model_path: str | Path | None = None,
    camera_index: int = DEFAULT_CAMERA_INDEX,
    turn_threshold_degrees: float = 20.0,
    neutral_threshold_degrees: float = 8.0,
    cooldown_samples: int = 2,
    yaw_multiplier: float = DEFAULT_YAW_MULTIPLIER,
    calibration_frames: int = DEFAULT_CALIBRATION_FRAMES,
    max_frames: int | None = None,
    sleep_seconds: float = 0.0,
    source_factory: SourceFactory = OpenCVWebcamGestureSource.create,
    audio_sample_rate: int = DEFAULT_AUDIO_SAMPLE_RATE,
    audio_channels: int = DEFAULT_AUDIO_CHANNELS,
    audio_blocksize: int = DEFAULT_AUDIO_BLOCKSIZE,
    audio_stream_factory: AudioStreamFactory | None = None,
) -> None:
    """Run the webcam-backed, audio-priming-to-jam tracer bullet."""
    session = Session()
    companion = FakeCompanion()
    mapper = GestureMapper()

    if phrase_context is None:
        phrase_context = create_demo_phrase_context()

    if priming_source is None:
        priming_source = AudioPrimingSource(
            phrase_context=phrase_context,
            sample_rate=audio_sample_rate,
            channels=audio_channels,
            blocksize=audio_blocksize,
            stream_factory=audio_stream_factory,
        )

    print_snapshot("Initial snapshot", session.get_snapshot())

    priming_source.start()
    print("\nPriming Source")
    print("  state: running")
    print("  phrase_context: pending")
    print("  audio_capture: running")

    print("\nWebcam Gesture Source")
    print(f"  camera_index: {camera_index}")
    print(f"  model_path: {model_path or f'${FACE_LANDMARKER_MODEL_ENV_VAR}'}")
    print(f"  turn_threshold_degrees: {turn_threshold_degrees}")
    print(f"  neutral_threshold_degrees: {neutral_threshold_degrees}")
    print(f"  cooldown_samples: {cooldown_samples}")
    print(f"  calibration_frames: {calibration_frames}")
    print(f"  yaw_multiplier: {yaw_multiplier}")
    print("  source_status: starting")

    frame_count = 0
    last_status_key: str | None = None

    try:
        with source_factory(
            model_path=model_path,
            camera_index=camera_index,
            turn_threshold_degrees=turn_threshold_degrees,
            neutral_threshold_degrees=neutral_threshold_degrees,
            cooldown_samples=cooldown_samples,
            yaw_multiplier=yaw_multiplier,
            calibration_frames=calibration_frames,
        ) as source:
            print("  source_status: running")
            print("\nUse Ctrl-C to stop the integrated webcam audio priming dry run.")

            while max_frames is None or frame_count < max_frames:
                observation = source.read_observation()
                frame_count += 1

                status_line = format_source_status(observation)
                status_key = source_status_key(observation)
                if should_print_source_status(
                    observation=observation,
                    status_key=status_key,
                    last_status_key=last_status_key,
                ):
                    print(status_line)
                    if observation.gesture_event is not None:
                        apply_audio_integrated_gesture_observation(
                            observation=observation,
                            mapper=mapper,
                            session=session,
                            companion=companion,
                            priming_source=priming_source,
                        )
                    last_status_key = status_key

                if sleep_seconds > 0:
                    sleep(sleep_seconds)
    finally:
        close_unfinished_audio_priming_source(
            session=session,
            priming_source=priming_source,
        )


def apply_audio_integrated_gesture_observation(
    *,
    observation: HeadTurnObservation,
    mapper: GestureMapper,
    session: Session,
    companion: FakeCompanion,
    priming_source: AudioBackedPrimingSource,
) -> None:
    """Map one emitted gesture and apply the audio priming/session flow."""
    gesture_event = observation.gesture_event
    if gesture_event is None:
        return

    print(
        f"\nGesture Event: {gesture_event.gesture_type.value} "
        f"(confidence={gesture_event.confidence:.2f})",
    )
    control_action = mapper.map_event(gesture_event=gesture_event)
    print(f"Mapped Control Action: {control_action.action.name}")

    if should_finish_priming(session=session, control_action=control_action):
        print("Priming Source: finishing")
        finished_context = priming_source.finish()
        session.receive_phrase_context(phrase_context=finished_context)
        print("Priming Source: finished")
        print_audio_buffer_facts(buffer=priming_source.audio_buffer)
        print_snapshot("Primed snapshot", session.get_snapshot())

    try:
        session.apply_control_action(control_action=control_action)
    except GitairError as exc:
        print(f"Control Action rejected: {exc}")
        if session.get_snapshot().phase == SessionPhase.PRIMING_PASS:
            print("Priming Source: running")
        print_snapshot(
            f"Snapshot after rejected {gesture_event.gesture_type.value}",
            session.get_snapshot(),
        )
        return

    snapshot = session.get_snapshot()
    print_snapshot(f"Snapshot after {gesture_event.gesture_type.value}", snapshot)

    if snapshot.companion_state is not None:
        print_companion_response(companion=companion, snapshot=snapshot)


def should_finish_priming(*, session: Session, control_action: ControlAction) -> bool:
    """Return whether a control action should finalize the priming source."""
    snapshot = session.get_snapshot()
    return (
        snapshot.phase == SessionPhase.PRIMING_PASS
        and control_action.action == ControlActionType.BRING_COMPANION_IN
    )


def close_unfinished_audio_priming_source(
    *,
    session: Session,
    priming_source: AudioBackedPrimingSource,
) -> None:
    """Release source-local audio resources if priming never reached jam."""
    if session.get_snapshot().phase != SessionPhase.PRIMING_PASS:
        return

    close = getattr(priming_source, "close", None)
    if not callable(close):
        return

    try:
        close()
    except GitairError as exc:
        print(f"Priming Source cleanup failed: {exc}")


def print_audio_buffer_facts(*, buffer: PrimingAudioBuffer) -> None:
    """Print the minimal audio facts exposed by the dry run."""
    print("\nPriming Audio Buffer")
    print(f"  duration_seconds: {buffer.duration_seconds}")
    print(f"  sample_rate: {buffer.sample_rate}")
    print(f"  channels: {buffer.channels}")
    print(f"  frame_count: {buffer.frame_count}")
    print(f"  chunk_count: {buffer.chunk_count}")


def build_parser() -> argparse.ArgumentParser:
    """Build the command-line parser for the webcam audio priming dry run."""
    parser = argparse.ArgumentParser(
        description="Run an integrated webcam and audio-backed Gitair priming dry run.",
    )
    parser.add_argument(
        "--model-path",
        default=None,
        help=(
            "Path to a MediaPipe face_landmarker.task model. "
            f"Defaults to ${FACE_LANDMARKER_MODEL_ENV_VAR}."
        ),
    )
    parser.add_argument(
        "--camera-index",
        type=int,
        default=DEFAULT_CAMERA_INDEX,
        help="OpenCV webcam index.",
    )
    parser.add_argument(
        "--turn-threshold-degrees",
        type=float,
        default=20.0,
        help="Yaw threshold that emits HEAD_RIGHT or HEAD_LEFT.",
    )
    parser.add_argument(
        "--neutral-threshold-degrees",
        type=float,
        default=8.0,
        help="Yaw range considered neutral before another head turn can emit.",
    )
    parser.add_argument(
        "--cooldown-samples",
        type=int,
        default=2,
        help="Number of webcam frames to suppress after emitting a gesture.",
    )
    parser.add_argument(
        "--invert-yaw",
        action="store_true",
        help="Flip Gitair yaw sign if your webcam smoke test reports left/right backwards.",
    )
    parser.add_argument(
        "--calibration-frames",
        type=int,
        default=DEFAULT_CALIBRATION_FRAMES,
        help="Number of detected face frames used to calibrate neutral yaw before emitting.",
    )
    parser.add_argument(
        "--max-frames",
        type=int,
        default=None,
        help="Optional frame limit for bounded smoke tests.",
    )
    parser.add_argument(
        "--audio-sample-rate",
        type=int,
        default=DEFAULT_AUDIO_SAMPLE_RATE,
        help="Audio input sample rate used by the temporary priming buffer.",
    )
    parser.add_argument(
        "--audio-channels",
        type=int,
        default=DEFAULT_AUDIO_CHANNELS,
        help="Audio input channel count used by the temporary priming buffer.",
    )
    parser.add_argument(
        "--audio-blocksize",
        type=int,
        default=DEFAULT_AUDIO_BLOCKSIZE,
        help="Audio input block size for sounddevice capture callbacks.",
    )
    parser.add_argument(
        "--chords",
        default="Ab,C,D7",
        help="Comma-separated chord labels for the phrase context.",
    )
    parser.add_argument(
        "--tempo-bpm",
        type=float,
        default=120.0,
        help="Tempo in beats per minute for the phrase context.",
    )
    parser.add_argument(
        "--style-description",
        default="Colombian folk",
        help="Short musical style description for the phrase context.",
    )
    parser.add_argument(
        "--prompt-summary",
        default="Guitar playing bambuco",
        help="Short prompt summary used to steer the fake companion.",
    )
    return parser


def phrase_context_from_args(args: argparse.Namespace) -> PhraseContext:
    """Create phrase context from parsed CLI arguments."""
    return create_demo_phrase_context(
        chords=parse_chords(args.chords),
        tempo_bpm=args.tempo_bpm,
        style_description=args.style_description,
        prompt_summary=args.prompt_summary,
    )


def main() -> None:
    """Run the webcam audio priming dry run from the command line."""
    parser = build_parser()
    args = parser.parse_args()
    yaw_multiplier = -DEFAULT_YAW_MULTIPLIER if args.invert_yaw else DEFAULT_YAW_MULTIPLIER

    try:
        run_webcam_audio_priming_dry_run(
            phrase_context=phrase_context_from_args(args),
            model_path=args.model_path,
            camera_index=args.camera_index,
            turn_threshold_degrees=args.turn_threshold_degrees,
            neutral_threshold_degrees=args.neutral_threshold_degrees,
            cooldown_samples=args.cooldown_samples,
            yaw_multiplier=yaw_multiplier,
            calibration_frames=args.calibration_frames,
            max_frames=args.max_frames,
            audio_sample_rate=args.audio_sample_rate,
            audio_channels=args.audio_channels,
            audio_blocksize=args.audio_blocksize,
        )
    except KeyboardInterrupt:
        print("\nIntegrated webcam audio priming dry run stopped.")
    except GitairError as exc:
        raise SystemExit(f"Gitair integrated webcam audio priming dry run failed: {exc}") from exc


if __name__ == "__main__":
    main()
