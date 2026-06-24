"""
Manual webcam dry run for the first real Gitair gesture source.

This demonstrates the Milestone 4 flow:

1. OpenCV reads webcam frames.
2. MediaPipe Face Landmarker estimates head pose.
3. Head-turn source logic emits HEAD_RIGHT or HEAD_LEFT gesture events.
4. GestureMapper translates events into Control Actions.
5. Session applies those actions without knowing about webcam or MediaPipe.
"""

import argparse
from collections.abc import Callable
from pathlib import Path
from time import sleep
from typing import Any

from gitair.companions.fake import FakeCompanion
from gitair.core.errors import GitairError
from gitair.core.phrase_context import PhraseContext
from gitair.core.session import Session
from gitair.demos.dry_run_session import (
    create_demo_phrase_context,
    parse_chords,
    print_companion_response,
    print_snapshot,
)
from gitair.gestures.mapper import GestureMapper
from gitair.gestures.mediapipe_face import (
    DEFAULT_CALIBRATION_FRAMES,
    DEFAULT_CAMERA_INDEX,
    DEFAULT_YAW_MULTIPLIER,
    FACE_LANDMARKER_MODEL_ENV_VAR,
    HeadTurnObservation,
    HeadTurnObservationStatus,
    OpenCVWebcamGestureSource,
)

SourceFactory = Callable[..., Any]


def run_webcam_gesture_dry_run(
    phrase_context: PhraseContext | None = None,
    *,
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
) -> None:
    """Run the webcam-to-session tracer bullet."""
    session = Session()
    companion = FakeCompanion()
    mapper = GestureMapper()

    if phrase_context is None:
        phrase_context = create_demo_phrase_context()

    session.receive_phrase_context(phrase_context=phrase_context)
    print_snapshot("Primed snapshot", session.get_snapshot())

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
        print("\nUse Ctrl-C to stop the webcam dry run.")

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
                if observation.gesture_event is None:
                    print(status_line)
                else:
                    print(status_line)
                    apply_gesture_observation(
                        observation=observation,
                        mapper=mapper,
                        session=session,
                        companion=companion,
                    )
                last_status_key = status_key

            if sleep_seconds > 0:
                sleep(sleep_seconds)


def apply_gesture_observation(
    *,
    observation: HeadTurnObservation,
    mapper: GestureMapper,
    session: Session,
    companion: FakeCompanion,
) -> None:
    """Map and apply an emitted gesture observation."""
    gesture_event = observation.gesture_event
    if gesture_event is None:
        return

    print(
        f"\nGesture Event: {gesture_event.gesture_type.value} "
        f"(confidence={gesture_event.confidence:.2f})",
    )
    control_action = mapper.map_event(gesture_event=gesture_event)
    print(f"Mapped Control Action: {control_action.action.name}")

    try:
        session.apply_control_action(control_action=control_action)
    except GitairError as exc:
        print(f"Control Action rejected: {exc}")
        return

    snapshot = session.get_snapshot()
    print_snapshot(f"Snapshot after {gesture_event.gesture_type.value}", snapshot)

    if snapshot.companion_state is not None:
        print_companion_response(companion=companion, snapshot=snapshot)


def format_source_status(observation: HeadTurnObservation) -> str:
    """Format one visible source-status line."""
    yaw = "none" if observation.yaw_degrees is None else f"{observation.yaw_degrees:.2f} deg"
    raw_yaw = (
        "none" if observation.raw_yaw_degrees is None else f"{observation.raw_yaw_degrees:.2f} deg"
    )
    neutral_yaw = (
        "none"
        if observation.neutral_yaw_degrees is None
        else f"{observation.neutral_yaw_degrees:.2f} deg"
    )
    if observation.status == HeadTurnObservationStatus.CALIBRATING:
        sample_count = observation.calibration_sample_count or 0
        required_samples = observation.calibration_required_samples or 0
        if observation.neutral_yaw_degrees is not None:
            return f"\nSource status: calibrated (neutral_yaw={neutral_yaw})"
        return (
            f"\nSource status: calibrating ({sample_count}/{required_samples}, raw_yaw={raw_yaw})"
        )

    if observation.status == HeadTurnObservationStatus.EMITTED:
        gesture = (
            observation.gesture_event.gesture_type.value if observation.gesture_event else "none"
        )
        return (
            f"\nSource status: emitted (yaw={yaw}, raw_yaw={raw_yaw}, "
            f"neutral_yaw={neutral_yaw}, gesture={gesture})"
        )

    return f"\nSource status: {observation.status.value} (yaw={yaw})"


def source_status_key(observation: HeadTurnObservation) -> str:
    """Return a stable status key so tiny yaw changes do not spam output."""
    if observation.status == HeadTurnObservationStatus.EMITTED and observation.gesture_event:
        return f"{observation.status.value}:{observation.gesture_event.gesture_type.value}"
    return observation.status.value


def should_print_source_status(
    *,
    observation: HeadTurnObservation,
    status_key: str,
    last_status_key: str | None,
) -> bool:
    """Decide whether one source status is useful enough to print."""
    if observation.gesture_event is not None:
        return True

    if observation.status == HeadTurnObservationStatus.CALIBRATING:
        sample_count = observation.calibration_sample_count or 0
        required_samples = observation.calibration_required_samples or 0
        return (
            sample_count == 1
            or sample_count == required_samples
            or (sample_count > 0 and sample_count % 10 == 0)
        )

    return status_key != last_status_key


def build_parser() -> argparse.ArgumentParser:
    """Build the command-line parser for the webcam gesture dry run."""
    parser = argparse.ArgumentParser(
        description="Run a webcam-backed Gitair gesture event dry run.",
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
    """Run the webcam gesture dry run from the command line."""
    parser = build_parser()
    args = parser.parse_args()
    yaw_multiplier = -DEFAULT_YAW_MULTIPLIER if args.invert_yaw else DEFAULT_YAW_MULTIPLIER

    try:
        run_webcam_gesture_dry_run(
            phrase_context=phrase_context_from_args(args),
            model_path=args.model_path,
            camera_index=args.camera_index,
            turn_threshold_degrees=args.turn_threshold_degrees,
            neutral_threshold_degrees=args.neutral_threshold_degrees,
            cooldown_samples=args.cooldown_samples,
            yaw_multiplier=yaw_multiplier,
            calibration_frames=args.calibration_frames,
            max_frames=args.max_frames,
        )
    except KeyboardInterrupt:
        print("\nWebcam gesture dry run stopped.")
    except GitairError as exc:
        raise SystemExit(f"Gitair webcam gesture dry run failed: {exc}") from exc


if __name__ == "__main__":
    main()
