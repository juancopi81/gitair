from math import cos, radians, sin
from pathlib import Path

import pytest

from gitair.core.errors import (
    GestureSourceSetupError,
    GitairError,
    InvalidGestureSourceInput,
)
from gitair.core.phrase_context import PhraseContext
from gitair.demos.webcam_gesture_dry_run import run_webcam_gesture_dry_run
from gitair.gestures.event import GestureEvent, GestureType
from gitair.gestures.head_turn import HeadTurnGestureSource
from gitair.gestures.mediapipe_face import (
    FACE_LANDMARKER_MODEL_ENV_VAR,
    HeadTurnObservation,
    HeadTurnObservationStatus,
    MediaPipeFaceLandmarkerGestureSource,
    OpenCVWebcamGestureSource,
    head_pose_sample_from_face_landmarker_result,
    resolve_face_landmarker_model_path,
    yaw_degrees_from_facial_transform_matrix,
)


class FakeLandmarkerResult:
    def __init__(self, matrices) -> None:
        self.facial_transformation_matrixes = matrices


def yaw_matrix(yaw_degrees: float) -> list[list[float]]:
    yaw_radians = radians(yaw_degrees)
    return [
        [cos(yaw_radians), 0.0, sin(yaw_radians), 0.0],
        [0.0, 1.0, 0.0, 0.0],
        [-sin(yaw_radians), 0.0, cos(yaw_radians), 0.0],
        [0.0, 0.0, 0.0, 1.0],
    ]


def test_model_path_resolves_explicit_file(tmp_path: Path) -> None:
    model_path = tmp_path / "face_landmarker.task"
    model_path.write_bytes(b"fake model")

    assert resolve_face_landmarker_model_path(model_path) == model_path


def test_model_path_resolves_from_environment(tmp_path: Path) -> None:
    model_path = tmp_path / "face_landmarker.task"
    model_path.write_bytes(b"fake model")

    resolved = resolve_face_landmarker_model_path(
        None,
        env={FACE_LANDMARKER_MODEL_ENV_VAR: str(model_path)},
    )

    assert resolved == model_path


def test_missing_model_path_raises_setup_error() -> None:
    with pytest.raises(GestureSourceSetupError) as exc_info:
        resolve_face_landmarker_model_path(None, env={})

    assert isinstance(exc_info.value, GitairError)
    assert FACE_LANDMARKER_MODEL_ENV_VAR in str(exc_info.value)


def test_missing_model_file_raises_setup_error(tmp_path: Path) -> None:
    with pytest.raises(GestureSourceSetupError) as exc_info:
        resolve_face_landmarker_model_path(tmp_path / "missing.task")

    assert isinstance(exc_info.value, GitairError)


def test_yaw_degrees_from_facial_transform_matrix_reads_positive_yaw() -> None:
    yaw_degrees = yaw_degrees_from_facial_transform_matrix(yaw_matrix(30.0))

    assert yaw_degrees == pytest.approx(30.0)


def test_yaw_degrees_from_flat_facial_transform_matrix() -> None:
    matrix = [value for row in yaw_matrix(-25.0) for value in row]

    yaw_degrees = yaw_degrees_from_facial_transform_matrix(matrix)

    assert yaw_degrees == pytest.approx(-25.0)


def test_invalid_facial_transform_matrix_raises_custom_error() -> None:
    with pytest.raises(InvalidGestureSourceInput) as exc_info:
        yaw_degrees_from_facial_transform_matrix([[1.0]])

    assert isinstance(exc_info.value, GitairError)


def test_face_landmarker_result_without_matrix_returns_none() -> None:
    result = FakeLandmarkerResult([])

    assert head_pose_sample_from_face_landmarker_result(result) is None


def test_face_landmarker_result_to_head_pose_sample_normalizes_mediapipe_yaw_sign() -> None:
    result = FakeLandmarkerResult([yaw_matrix(-22.0)])

    sample = head_pose_sample_from_face_landmarker_result(result)

    assert sample is not None
    assert sample.yaw_degrees == pytest.approx(22.0)


def test_face_landmarker_result_to_head_pose_sample_can_use_raw_yaw_sign() -> None:
    result = FakeLandmarkerResult([yaw_matrix(-22.0)])

    sample = head_pose_sample_from_face_landmarker_result(result, yaw_multiplier=1.0)

    assert sample is not None
    assert sample.yaw_degrees == pytest.approx(-22.0)


def test_face_landmarker_source_emits_head_right_and_left() -> None:
    source = MediaPipeFaceLandmarkerGestureSource(
        landmarker=object(),
        media_pipe_module=object(),
        head_turn_source=HeadTurnGestureSource(
            turn_threshold_degrees=20.0,
            neutral_threshold_degrees=8.0,
            cooldown_samples=0,
        ),
        calibration_frames=0,
    )

    right_observation = source.observe_landmarker_result(FakeLandmarkerResult([yaw_matrix(-23.0)]))
    source.observe_landmarker_result(FakeLandmarkerResult([yaw_matrix(0.0)]))
    left_observation = source.observe_landmarker_result(FakeLandmarkerResult([yaw_matrix(23.0)]))

    assert right_observation.status == HeadTurnObservationStatus.EMITTED
    assert right_observation.gesture_event is not None
    assert right_observation.gesture_event.gesture_type == GestureType.HEAD_RIGHT
    assert left_observation.status == HeadTurnObservationStatus.EMITTED
    assert left_observation.gesture_event is not None
    assert left_observation.gesture_event.gesture_type == GestureType.HEAD_LEFT


def test_face_landmarker_source_reports_no_face_and_neutral_without_event() -> None:
    source = MediaPipeFaceLandmarkerGestureSource(
        landmarker=object(),
        media_pipe_module=object(),
        head_turn_source=HeadTurnGestureSource(
            turn_threshold_degrees=20.0,
            neutral_threshold_degrees=8.0,
            cooldown_samples=0,
        ),
        calibration_frames=0,
    )

    no_face = source.observe_landmarker_result(FakeLandmarkerResult([]))
    neutral = source.observe_landmarker_result(FakeLandmarkerResult([yaw_matrix(3.0)]))

    assert no_face.status == HeadTurnObservationStatus.NO_FACE
    assert no_face.gesture_event is None
    assert neutral.status == HeadTurnObservationStatus.NEUTRAL
    assert neutral.gesture_event is None


def test_face_landmarker_source_reports_suppressed_held_turn() -> None:
    source = MediaPipeFaceLandmarkerGestureSource(
        landmarker=object(),
        media_pipe_module=object(),
        head_turn_source=HeadTurnGestureSource(
            turn_threshold_degrees=20.0,
            neutral_threshold_degrees=8.0,
            cooldown_samples=0,
        ),
        calibration_frames=0,
    )

    first_turn = source.observe_landmarker_result(FakeLandmarkerResult([yaw_matrix(-23.0)]))
    held_turn = source.observe_landmarker_result(FakeLandmarkerResult([yaw_matrix(-24.0)]))

    assert first_turn.status == HeadTurnObservationStatus.EMITTED
    assert held_turn.status == HeadTurnObservationStatus.SUPPRESSED
    assert held_turn.gesture_event is None


def test_face_landmarker_source_calibrates_neutral_yaw_before_emitting() -> None:
    source = MediaPipeFaceLandmarkerGestureSource(
        landmarker=object(),
        media_pipe_module=object(),
        head_turn_source=HeadTurnGestureSource(
            turn_threshold_degrees=20.0,
            neutral_threshold_degrees=8.0,
            cooldown_samples=0,
        ),
        calibration_frames=2,
    )

    first_calibration = source.observe_landmarker_result(FakeLandmarkerResult([yaw_matrix(-30.0)]))
    second_calibration = source.observe_landmarker_result(FakeLandmarkerResult([yaw_matrix(-32.0)]))
    right_observation = source.observe_landmarker_result(FakeLandmarkerResult([yaw_matrix(-55.0)]))

    assert first_calibration.status == HeadTurnObservationStatus.CALIBRATING
    assert first_calibration.gesture_event is None
    assert second_calibration.status == HeadTurnObservationStatus.CALIBRATING
    assert second_calibration.neutral_yaw_degrees == pytest.approx(31.0)
    assert right_observation.status == HeadTurnObservationStatus.EMITTED
    assert right_observation.yaw_degrees == pytest.approx(24.0)
    assert right_observation.gesture_event is not None
    assert right_observation.gesture_event.gesture_type == GestureType.HEAD_RIGHT


class ClosedCapture:
    def __init__(self) -> None:
        self.released = False

    def isOpened(self) -> bool:
        return False

    def release(self) -> None:
        self.released = True


class FakeCV2WithClosedCamera:
    def __init__(self) -> None:
        self.capture = ClosedCapture()

    def VideoCapture(self, camera_index: int) -> ClosedCapture:
        return self.capture


class FakeFaceSource:
    def __init__(self) -> None:
        self.closed = False

    def close(self) -> None:
        self.closed = True


def test_webcam_source_camera_setup_failure_raises_custom_error() -> None:
    cv2_module = FakeCV2WithClosedCamera()
    face_source = FakeFaceSource()

    with pytest.raises(GestureSourceSetupError) as exc_info:
        OpenCVWebcamGestureSource(
            face_source=face_source,  # type: ignore[arg-type]
            cv2_module=cv2_module,
        )

    assert isinstance(exc_info.value, GitairError)
    assert cv2_module.capture.released is True
    assert face_source.closed is True


class OpenCapture:
    def __init__(self) -> None:
        self.released = False

    def isOpened(self) -> bool:
        return True

    def read(self) -> tuple[bool, str]:
        return True, "bgr frame"

    def release(self) -> None:
        self.released = True


class FakeCV2:
    COLOR_BGR2RGB = "bgr2rgb"

    def __init__(self) -> None:
        self.converted = None

    def VideoCapture(self, camera_index: int) -> OpenCapture:
        return OpenCapture()

    def cvtColor(self, frame: str, color: str) -> str:
        self.converted = (frame, color)
        return "rgb frame"


class RecordingFaceSource:
    def __init__(self) -> None:
        self.rgb_frame = None
        self.timestamp_ms = None
        self.closed = False

    def observe_rgb_frame(self, rgb_frame: str, *, timestamp_ms: int) -> HeadTurnObservation:
        self.rgb_frame = rgb_frame
        self.timestamp_ms = timestamp_ms
        return HeadTurnObservation(status=HeadTurnObservationStatus.NO_FACE)

    def close(self) -> None:
        self.closed = True


def test_webcam_source_reads_frame_and_delegates_to_face_source() -> None:
    cv2_module = FakeCV2()
    face_source = RecordingFaceSource()
    source = OpenCVWebcamGestureSource(
        face_source=face_source,  # type: ignore[arg-type]
        cv2_module=cv2_module,
    )

    observation = source.read_observation()

    assert observation.status == HeadTurnObservationStatus.NO_FACE
    assert cv2_module.converted == ("bgr frame", "bgr2rgb")
    assert face_source.rgb_frame == "rgb frame"
    assert isinstance(face_source.timestamp_ms, int)


class FakeDryRunSource:
    def __init__(self, observations: list[HeadTurnObservation]) -> None:
        self._observations = observations

    def __enter__(self) -> "FakeDryRunSource":
        return self

    def __exit__(self, exc_type: object, exc: object, traceback: object) -> None:
        return None

    def read_observation(self) -> HeadTurnObservation:
        return self._observations.pop(0)


def test_webcam_dry_run_prints_source_event_mapping_and_session_state(capsys) -> None:
    observations = [
        HeadTurnObservation(
            status=HeadTurnObservationStatus.CALIBRATING,
            raw_yaw_degrees=31.0,
            calibration_sample_count=1,
            calibration_required_samples=2,
        ),
        HeadTurnObservation(
            status=HeadTurnObservationStatus.CALIBRATING,
            raw_yaw_degrees=32.0,
            neutral_yaw_degrees=31.5,
            calibration_sample_count=2,
            calibration_required_samples=2,
        ),
        HeadTurnObservation(status=HeadTurnObservationStatus.NO_FACE),
        HeadTurnObservation(
            status=HeadTurnObservationStatus.EMITTED,
            yaw_degrees=23.0,
            raw_yaw_degrees=54.5,
            neutral_yaw_degrees=31.5,
            gesture_event=GestureEvent(gesture_type=GestureType.HEAD_RIGHT),
        ),
        HeadTurnObservation(
            status=HeadTurnObservationStatus.EMITTED,
            yaw_degrees=-23.0,
            raw_yaw_degrees=8.5,
            neutral_yaw_degrees=31.5,
            gesture_event=GestureEvent(gesture_type=GestureType.HEAD_LEFT),
        ),
    ]

    def source_factory(**kwargs) -> FakeDryRunSource:
        return FakeDryRunSource(observations=observations)

    run_webcam_gesture_dry_run(
        phrase_context=PhraseContext(
            chords=["E7", "G5", "A"],
            tempo_bpm=120.0,
            style_description="raw rock",
            prompt_summary="short riff",
        ),
        model_path="fake.task",
        max_frames=5,
        source_factory=source_factory,
    )

    output = capsys.readouterr().out

    assert "source_status: running" in output
    assert "Source status: calibrating (1/2, raw_yaw=31.00 deg)" in output
    assert "Source status: calibrated (neutral_yaw=31.50 deg)" in output
    assert "Source status: no_face (yaw=none)" in output
    assert (
        "Source status: emitted "
        "(yaw=23.00 deg, raw_yaw=54.50 deg, neutral_yaw=31.50 deg, gesture=HEAD_RIGHT)" in output
    )
    assert "Gesture Event: HEAD_RIGHT (confidence=1.00)" in output
    assert "Mapped Control Action: BRING_COMPANION_IN" in output
    assert (
        "Source status: emitted "
        "(yaw=-23.00 deg, raw_yaw=8.50 deg, neutral_yaw=31.50 deg, gesture=HEAD_LEFT)" in output
    )
    assert "Mapped Control Action: SILENCE_COMPANION" in output
    assert "companion_status: active" in output
    assert "companion_status: silent" in output
