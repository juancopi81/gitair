from enum import Enum

from pydantic import BaseModel, Field, ValidationError

from gitair.core.errors import UnsupportedGestureEvent


class GestureType(str, Enum):
    """Source-neutral gesture events currently recognized by Gitair."""

    HEAD_RIGHT = "HEAD_RIGHT"
    HEAD_LEFT = "HEAD_LEFT"
    NOD_UP = "NOD_UP"
    NOD_DOWN = "NOD_DOWN"


class GestureEvent(BaseModel):
    """A recognized gesture signal before it is mapped to a control action."""

    gesture_type: GestureType = Field(
        description="The source-neutral gesture type recognized by a gesture source.",
    )
    confidence: float = Field(
        default=1.0,
        ge=0.0,
        le=1.0,
        description="Visible gesture confidence from 0.0 to 1.0.",
    )


def parse_gesture_event(raw_gesture: str) -> GestureEvent:
    """Parse a raw scripted gesture token into a gesture event."""
    gesture_token, _, confidence_token = raw_gesture.strip().partition(":")
    if not gesture_token:
        raise UnsupportedGestureEvent("Unsupported gesture event: empty gesture token.")

    try:
        gesture_type = GestureType(gesture_token.strip())
    except ValueError as exc:
        raise UnsupportedGestureEvent(
            f"Unsupported gesture event: {gesture_token.strip()}",
        ) from exc

    try:
        if confidence_token:
            return GestureEvent(
                gesture_type=gesture_type,
                confidence=float(confidence_token.strip()),
            )
        return GestureEvent(gesture_type=gesture_type)
    except (ValueError, ValidationError) as exc:
        raise UnsupportedGestureEvent(
            f"Unsupported gesture event confidence for {gesture_type.value}.",
        ) from exc
