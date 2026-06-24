from __future__ import annotations

import os
from collections.abc import Mapping, Sequence
from enum import Enum
from math import atan2, degrees, isfinite
from pathlib import Path
from time import monotonic
from typing import Any

from pydantic import BaseModel, Field, ValidationError

from gitair.core.errors import (
    GestureSourceRuntimeError,
    GestureSourceSetupError,
    InvalidGestureSourceConfiguration,
    InvalidGestureSourceInput,
)
from gitair.gestures.event import GestureEvent
from gitair.gestures.head_turn import (
    DEFAULT_COOLDOWN_SAMPLES,
    DEFAULT_NEUTRAL_THRESHOLD_DEGREES,
    DEFAULT_TURN_THRESHOLD_DEGREES,
    HeadPoseSample,
    HeadTurnGestureSource,
)

FACE_LANDMARKER_MODEL_ENV_VAR = "GITAIR_FACE_LANDMARKER_MODEL"
DEFAULT_CAMERA_INDEX = 0
DEFAULT_YAW_MULTIPLIER = -1.0
DEFAULT_CALIBRATION_FRAMES = 30


class HeadTurnObservationStatus(str, Enum):
    """Visible status for one real-source observation."""

    CALIBRATING = "calibrating"
    NO_FACE = "no_face"
    NEUTRAL = "neutral"
    SUPPRESSED = "suppressed"
    EMITTED = "emitted"


class HeadTurnObservation(BaseModel):
    """One webcam/landmarker observation plus any emitted gesture event."""

    status: HeadTurnObservationStatus
    yaw_degrees: float | None = Field(default=None, allow_inf_nan=False)
    raw_yaw_degrees: float | None = Field(default=None, allow_inf_nan=False)
    neutral_yaw_degrees: float | None = Field(default=None, allow_inf_nan=False)
    calibration_sample_count: int | None = None
    calibration_required_samples: int | None = None
    gesture_event: GestureEvent | None = None


class MediaPipeFaceLandmarkerGestureSource:
    """Use MediaPipe Face Landmarker results to emit head-turn gesture events."""

    def __init__(
        self,
        *,
        landmarker: Any,
        media_pipe_module: Any,
        head_turn_source: HeadTurnGestureSource | None = None,
        yaw_multiplier: float = DEFAULT_YAW_MULTIPLIER,
        calibration_frames: int = 0,
    ) -> None:
        self._landmarker = landmarker
        self._mp = media_pipe_module
        self._head_turn_source = head_turn_source or HeadTurnGestureSource()
        self._yaw_multiplier = _validate_yaw_multiplier(yaw_multiplier)
        self._calibration_frames = _validate_calibration_frames(calibration_frames)
        self._calibration_yaws: list[float] = []
        self._neutral_yaw_degrees: float | None = None

    @classmethod
    def create(
        cls,
        *,
        model_path: str | Path | None = None,
        env: Mapping[str, str] | None = None,
        turn_threshold_degrees: float = DEFAULT_TURN_THRESHOLD_DEGREES,
        neutral_threshold_degrees: float = DEFAULT_NEUTRAL_THRESHOLD_DEGREES,
        cooldown_samples: int = DEFAULT_COOLDOWN_SAMPLES,
        yaw_multiplier: float = DEFAULT_YAW_MULTIPLIER,
        calibration_frames: int = DEFAULT_CALIBRATION_FRAMES,
    ) -> MediaPipeFaceLandmarkerGestureSource:
        """Create the MediaPipe Face Landmarker-backed gesture source."""
        resolved_model_path = resolve_face_landmarker_model_path(model_path, env=env)
        mp_module = _import_mediapipe()

        try:
            options = mp_module.tasks.vision.FaceLandmarkerOptions(
                base_options=mp_module.tasks.BaseOptions(
                    model_asset_path=str(resolved_model_path),
                ),
                running_mode=mp_module.tasks.vision.RunningMode.VIDEO,
                num_faces=1,
                output_facial_transformation_matrixes=True,
            )
            landmarker = mp_module.tasks.vision.FaceLandmarker.create_from_options(options)
        except Exception as exc:  # pragma: no cover - depends on MediaPipe internals.
            raise GestureSourceSetupError(
                "Could not initialize MediaPipe Face Landmarker. "
                f"Check the model path: {resolved_model_path}",
            ) from exc

        return cls(
            landmarker=landmarker,
            media_pipe_module=mp_module,
            head_turn_source=HeadTurnGestureSource(
                turn_threshold_degrees=turn_threshold_degrees,
                neutral_threshold_degrees=neutral_threshold_degrees,
                cooldown_samples=cooldown_samples,
            ),
            yaw_multiplier=yaw_multiplier,
            calibration_frames=calibration_frames,
        )

    def observe_rgb_frame(self, rgb_frame: Any, *, timestamp_ms: int) -> HeadTurnObservation:
        """Observe one RGB webcam frame and return visible source status."""
        if not isinstance(timestamp_ms, int) or isinstance(timestamp_ms, bool) or timestamp_ms < 0:
            raise InvalidGestureSourceInput("timestamp_ms must be a non-negative integer.")

        try:
            mp_image = self._mp.Image(
                image_format=self._mp.ImageFormat.SRGB,
                data=rgb_frame,
            )
            result = self._landmarker.detect_for_video(mp_image, timestamp_ms)
        except Exception as exc:
            raise GestureSourceRuntimeError("MediaPipe failed to process a webcam frame.") from exc

        return self.observe_landmarker_result(result)

    def observe_landmarker_result(self, result: Any) -> HeadTurnObservation:
        """Observe one Face Landmarker result without webcam hardware."""
        sample = head_pose_sample_from_face_landmarker_result(
            result,
            yaw_multiplier=self._yaw_multiplier,
        )
        return self.observe_head_pose_sample(sample)

    def observe_head_pose_sample(self, sample: HeadPoseSample | None) -> HeadTurnObservation:
        """Observe one head-pose sample and classify the source status."""
        if sample is None:
            return HeadTurnObservation(status=HeadTurnObservationStatus.NO_FACE)

        if self._neutral_yaw_degrees is None and self._calibration_frames > 0:
            return self._observe_calibration_sample(sample)

        adjusted_sample = self._adjust_sample_for_neutral(sample)
        gesture_event = self._head_turn_source.observe_sample(adjusted_sample)
        if gesture_event is not None:
            return HeadTurnObservation(
                status=HeadTurnObservationStatus.EMITTED,
                yaw_degrees=adjusted_sample.yaw_degrees,
                raw_yaw_degrees=sample.yaw_degrees,
                neutral_yaw_degrees=self._neutral_yaw_degrees,
                gesture_event=gesture_event,
            )

        if abs(adjusted_sample.yaw_degrees) <= self._head_turn_source.neutral_threshold_degrees:
            status = HeadTurnObservationStatus.NEUTRAL
        else:
            status = HeadTurnObservationStatus.SUPPRESSED

        return HeadTurnObservation(
            status=status,
            yaw_degrees=adjusted_sample.yaw_degrees,
            raw_yaw_degrees=sample.yaw_degrees,
            neutral_yaw_degrees=self._neutral_yaw_degrees,
        )

    def _observe_calibration_sample(self, sample: HeadPoseSample) -> HeadTurnObservation:
        self._calibration_yaws.append(sample.yaw_degrees)
        calibration_sample_count = len(self._calibration_yaws)

        if calibration_sample_count >= self._calibration_frames:
            self._neutral_yaw_degrees = sum(self._calibration_yaws) / len(self._calibration_yaws)

        return HeadTurnObservation(
            status=HeadTurnObservationStatus.CALIBRATING,
            raw_yaw_degrees=sample.yaw_degrees,
            neutral_yaw_degrees=self._neutral_yaw_degrees,
            calibration_sample_count=calibration_sample_count,
            calibration_required_samples=self._calibration_frames,
        )

    def _adjust_sample_for_neutral(self, sample: HeadPoseSample) -> HeadPoseSample:
        neutral_yaw_degrees = self._neutral_yaw_degrees or 0.0
        return HeadPoseSample(
            yaw_degrees=sample.yaw_degrees - neutral_yaw_degrees,
            confidence=sample.confidence,
        )

    def close(self) -> None:
        """Release MediaPipe resources when supported by the landmarker."""
        close = getattr(self._landmarker, "close", None)
        if callable(close):
            close()

    def __enter__(self) -> MediaPipeFaceLandmarkerGestureSource:
        return self

    def __exit__(self, exc_type: object, exc: object, traceback: object) -> None:
        self.close()


class OpenCVWebcamGestureSource:
    """Read webcam frames through OpenCV and delegate recognition to MediaPipe."""

    def __init__(
        self,
        *,
        face_source: MediaPipeFaceLandmarkerGestureSource,
        camera_index: int = DEFAULT_CAMERA_INDEX,
        cv2_module: Any | None = None,
        capture: Any | None = None,
    ) -> None:
        if not isinstance(camera_index, int) or isinstance(camera_index, bool) or camera_index < 0:
            raise InvalidGestureSourceConfiguration(
                "camera_index must be a non-negative integer.",
            )

        self.camera_index = camera_index
        self._face_source = face_source
        self._cv2 = cv2_module or _import_cv2()
        self._capture = capture if capture is not None else self._cv2.VideoCapture(camera_index)

        if not self._capture.isOpened():
            self.close()
            raise GestureSourceSetupError(f"Could not open webcam at camera index {camera_index}.")

        self._started_at = monotonic()

    @classmethod
    def create(
        cls,
        *,
        model_path: str | Path | None = None,
        env: Mapping[str, str] | None = None,
        camera_index: int = DEFAULT_CAMERA_INDEX,
        turn_threshold_degrees: float = DEFAULT_TURN_THRESHOLD_DEGREES,
        neutral_threshold_degrees: float = DEFAULT_NEUTRAL_THRESHOLD_DEGREES,
        cooldown_samples: int = DEFAULT_COOLDOWN_SAMPLES,
        yaw_multiplier: float = DEFAULT_YAW_MULTIPLIER,
        calibration_frames: int = DEFAULT_CALIBRATION_FRAMES,
    ) -> OpenCVWebcamGestureSource:
        """Create the OpenCV webcam wrapper and MediaPipe face source."""
        cv2_module = _import_cv2()
        capture = cv2_module.VideoCapture(camera_index)
        if not capture.isOpened():
            capture.release()
            raise GestureSourceSetupError(f"Could not open webcam at camera index {camera_index}.")

        try:
            face_source = MediaPipeFaceLandmarkerGestureSource.create(
                model_path=model_path,
                env=env,
                turn_threshold_degrees=turn_threshold_degrees,
                neutral_threshold_degrees=neutral_threshold_degrees,
                cooldown_samples=cooldown_samples,
                yaw_multiplier=yaw_multiplier,
                calibration_frames=calibration_frames,
            )
        except Exception:
            capture.release()
            raise

        return cls(
            face_source=face_source,
            camera_index=camera_index,
            cv2_module=cv2_module,
            capture=capture,
        )

    def read_observation(self) -> HeadTurnObservation:
        """Read one webcam frame and return visible source status."""
        ok, frame = self._capture.read()
        if not ok or frame is None:
            raise GestureSourceRuntimeError("Could not read a frame from the webcam.")

        try:
            rgb_frame = self._cv2.cvtColor(frame, self._cv2.COLOR_BGR2RGB)
        except Exception as exc:
            raise GestureSourceRuntimeError("Could not convert webcam frame to RGB.") from exc

        return self._face_source.observe_rgb_frame(
            rgb_frame,
            timestamp_ms=self._elapsed_timestamp_ms(),
        )

    def close(self) -> None:
        """Release webcam and MediaPipe resources."""
        release = getattr(getattr(self, "_capture", None), "release", None)
        if callable(release):
            release()
        self._face_source.close()

    def __enter__(self) -> OpenCVWebcamGestureSource:
        return self

    def __exit__(self, exc_type: object, exc: object, traceback: object) -> None:
        self.close()

    def _elapsed_timestamp_ms(self) -> int:
        return max(0, int((monotonic() - self._started_at) * 1000))


def resolve_face_landmarker_model_path(
    model_path: str | Path | None,
    *,
    env: Mapping[str, str] | None = None,
) -> Path:
    """Resolve the Face Landmarker model path from an argument or environment."""
    raw_model_path = model_path
    if raw_model_path is None:
        env_mapping = os.environ if env is None else env
        raw_model_path = env_mapping.get(FACE_LANDMARKER_MODEL_ENV_VAR)

    if raw_model_path is None or str(raw_model_path).strip() == "":
        raise GestureSourceSetupError(
            "Face Landmarker model path is required. "
            f"Pass --model-path or set {FACE_LANDMARKER_MODEL_ENV_VAR}.",
        )

    resolved = Path(raw_model_path).expanduser()
    if not resolved.exists():
        raise GestureSourceSetupError(f"Face Landmarker model path does not exist: {resolved}")
    if not resolved.is_file():
        raise GestureSourceSetupError(f"Face Landmarker model path is not a file: {resolved}")

    return resolved


def head_pose_sample_from_face_landmarker_result(
    result: Any,
    *,
    yaw_multiplier: float = DEFAULT_YAW_MULTIPLIER,
) -> HeadPoseSample | None:
    """Extract a head-pose sample from a Face Landmarker result."""
    matrices = getattr(result, "facial_transformation_matrixes", None)
    if not matrices:
        return None

    try:
        raw_matrix = matrices[0]
    except (IndexError, TypeError) as exc:
        raise InvalidGestureSourceInput(
            "Invalid Face Landmarker transformation matrix result.",
        ) from exc

    yaw_degrees = yaw_degrees_from_facial_transform_matrix(raw_matrix) * _validate_yaw_multiplier(
        yaw_multiplier
    )

    try:
        return HeadPoseSample(yaw_degrees=yaw_degrees)
    except (TypeError, ValueError, ValidationError) as exc:
        raise InvalidGestureSourceInput("Invalid head pose extracted from MediaPipe.") from exc


def yaw_degrees_from_facial_transform_matrix(matrix: Any) -> float:
    """Extract yaw in degrees from a MediaPipe facial transformation matrix."""
    rows = _coerce_rotation_rows(matrix)
    yaw_degrees = degrees(atan2(rows[0][2], rows[0][0]))
    if not isfinite(yaw_degrees):
        raise InvalidGestureSourceInput("Face transformation matrix produced invalid yaw.")
    return yaw_degrees


def _coerce_rotation_rows(matrix: Any) -> tuple[tuple[float, float, float], ...]:
    if hasattr(matrix, "tolist"):
        matrix = matrix.tolist()

    try:
        values = list(matrix)
    except TypeError as exc:
        raise InvalidGestureSourceInput("Face transformation matrix is not iterable.") from exc

    if len(values) == 16 and all(_is_scalar(value) for value in values):
        rows = [values[0:4], values[4:8], values[8:12]]
    elif len(values) >= 3:
        rows = values[:3]
    else:
        raise InvalidGestureSourceInput("Face transformation matrix must have at least 3 rows.")

    rotation_rows: list[tuple[float, float, float]] = []
    for row in rows:
        if hasattr(row, "tolist"):
            row = row.tolist()
        if not isinstance(row, Sequence) or isinstance(row, str) or len(row) < 3:
            raise InvalidGestureSourceInput("Face transformation matrix rows must have 3 values.")
        try:
            rotation_row = (float(row[0]), float(row[1]), float(row[2]))
        except (TypeError, ValueError) as exc:
            raise InvalidGestureSourceInput(
                "Face transformation matrix values must be numeric."
            ) from exc
        if not all(isfinite(value) for value in rotation_row):
            raise InvalidGestureSourceInput("Face transformation matrix values must be finite.")
        rotation_rows.append(rotation_row)

    return tuple(rotation_rows)


def _validate_yaw_multiplier(yaw_multiplier: float) -> float:
    try:
        value = float(yaw_multiplier)
    except (TypeError, ValueError) as exc:
        raise InvalidGestureSourceConfiguration("yaw_multiplier must be finite.") from exc

    if value not in {-1.0, 1.0}:
        raise InvalidGestureSourceConfiguration("yaw_multiplier must be either 1.0 or -1.0.")

    return value


def _validate_calibration_frames(calibration_frames: int) -> int:
    if (
        not isinstance(calibration_frames, int)
        or isinstance(calibration_frames, bool)
        or calibration_frames < 0
    ):
        raise InvalidGestureSourceConfiguration(
            "calibration_frames must be a non-negative integer."
        )

    return calibration_frames


def _is_scalar(value: object) -> bool:
    return not isinstance(value, Sequence) or isinstance(value, str)


def _import_mediapipe() -> Any:
    try:
        import mediapipe as mp
    except ImportError as exc:  # pragma: no cover - dependency should be installed.
        raise GestureSourceSetupError("MediaPipe is not installed.") from exc
    return mp


def _import_cv2() -> Any:
    try:
        import cv2
    except ImportError as exc:  # pragma: no cover - dependency should be installed.
        raise GestureSourceSetupError("OpenCV is not installed.") from exc
    return cv2
