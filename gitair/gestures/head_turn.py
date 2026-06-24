from collections.abc import Iterable, Iterator
from math import isfinite

from pydantic import BaseModel, Field, ValidationError

from gitair.core.errors import (
    InvalidGestureSourceConfiguration,
    InvalidGestureSourceInput,
)
from gitair.gestures.event import GestureEvent, GestureType

DEFAULT_TURN_THRESHOLD_DEGREES = 20.0
DEFAULT_NEUTRAL_THRESHOLD_DEGREES = 8.0
DEFAULT_COOLDOWN_SAMPLES = 2


class HeadPoseSample(BaseModel):
    """Synthetic head-pose input for head-turn gesture source logic."""

    yaw_degrees: float = Field(
        allow_inf_nan=False,
        description="Synthetic yaw angle in degrees. Positive means head turned right.",
    )
    confidence: float = Field(
        default=1.0,
        ge=0.0,
        le=1.0,
        allow_inf_nan=False,
        description="Visible confidence from 0.0 to 1.0 for the emitted gesture event.",
    )


class HeadTurnGestureSource:
    """Emit source-neutral head-turn gesture events from synthetic yaw samples."""

    def __init__(
        self,
        *,
        turn_threshold_degrees: float = DEFAULT_TURN_THRESHOLD_DEGREES,
        neutral_threshold_degrees: float = DEFAULT_NEUTRAL_THRESHOLD_DEGREES,
        cooldown_samples: int = DEFAULT_COOLDOWN_SAMPLES,
    ) -> None:
        self.turn_threshold_degrees = _validate_threshold(
            "turn_threshold_degrees",
            turn_threshold_degrees,
        )
        self.neutral_threshold_degrees = _validate_threshold(
            "neutral_threshold_degrees",
            neutral_threshold_degrees,
            allow_zero=True,
        )
        if self.neutral_threshold_degrees >= self.turn_threshold_degrees:
            raise InvalidGestureSourceConfiguration(
                "neutral_threshold_degrees must be lower than turn_threshold_degrees.",
            )
        if (
            not isinstance(cooldown_samples, int)
            or isinstance(cooldown_samples, bool)
            or cooldown_samples < 0
        ):
            raise InvalidGestureSourceConfiguration(
                "cooldown_samples must be a non-negative integer.",
            )

        self.cooldown_samples = cooldown_samples
        self._cooldown_remaining = 0
        self._waiting_for_neutral = False

    def observe_yaw(
        self,
        yaw_degrees: float,
        *,
        confidence: float = 1.0,
    ) -> GestureEvent | None:
        """Observe one synthetic yaw value and emit at most one gesture event."""
        try:
            sample = HeadPoseSample(yaw_degrees=yaw_degrees, confidence=confidence)
        except (TypeError, ValueError, ValidationError) as exc:
            raise InvalidGestureSourceInput("Invalid head-pose sample.") from exc

        return self.observe_sample(sample)

    def observe_sample(self, sample: HeadPoseSample) -> GestureEvent | None:
        """Observe one validated head-pose sample and emit at most one gesture event."""
        if not isinstance(sample, HeadPoseSample):
            raise InvalidGestureSourceInput("Expected a HeadPoseSample.")

        is_neutral = abs(sample.yaw_degrees) <= self.neutral_threshold_degrees
        if self._waiting_for_neutral and is_neutral:
            self._waiting_for_neutral = False

        if self._cooldown_remaining > 0:
            self._cooldown_remaining -= 1
            return None

        if self._waiting_for_neutral:
            return None

        if sample.yaw_degrees >= self.turn_threshold_degrees:
            return self._emit(GestureType.HEAD_RIGHT, confidence=sample.confidence)

        if sample.yaw_degrees <= -self.turn_threshold_degrees:
            return self._emit(GestureType.HEAD_LEFT, confidence=sample.confidence)

        return None

    def events_from_yaws(self, yaws_degrees: Iterable[float]) -> Iterator[GestureEvent]:
        """Yield gesture events emitted from a sequence of synthetic yaw values."""
        for yaw_degrees in yaws_degrees:
            event = self.observe_yaw(yaw_degrees)
            if event is not None:
                yield event

    def _emit(self, gesture_type: GestureType, *, confidence: float) -> GestureEvent:
        self._waiting_for_neutral = True
        self._cooldown_remaining = self.cooldown_samples
        return GestureEvent(gesture_type=gesture_type, confidence=confidence)


def _validate_threshold(name: str, value: float, *, allow_zero: bool = False) -> float:
    try:
        threshold = float(value)
    except (TypeError, ValueError) as exc:
        raise InvalidGestureSourceConfiguration(f"{name} must be finite.") from exc

    if not isfinite(threshold):
        raise InvalidGestureSourceConfiguration(f"{name} must be finite.")

    if allow_zero:
        is_valid = threshold >= 0.0
    else:
        is_valid = threshold > 0.0

    if not is_valid:
        lower_bound = "non-negative" if allow_zero else "positive"
        raise InvalidGestureSourceConfiguration(f"{name} must be {lower_bound}.")

    return threshold
