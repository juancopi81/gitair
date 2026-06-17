from collections.abc import Mapping

from gitair.core.control_action import ControlAction, ControlActionType
from gitair.core.errors import UnmappedGestureEvent
from gitair.gestures.event import GestureEvent, GestureType

DEFAULT_GESTURE_MAPPING: Mapping[GestureType, ControlActionType] = {
    GestureType.HEAD_RIGHT: ControlActionType.BRING_COMPANION_IN,
    GestureType.HEAD_LEFT: ControlActionType.SILENCE_COMPANION,
    GestureType.NOD_UP: ControlActionType.INCREASE_INTENSITY,
    GestureType.NOD_DOWN: ControlActionType.DECREASE_INTENSITY,
}


class GestureMapper:
    """Translate source-neutral gesture events into control actions."""

    def __init__(
        self,
        mapping: Mapping[GestureType, ControlActionType] | None = None,
    ) -> None:
        self._mapping = dict(DEFAULT_GESTURE_MAPPING if mapping is None else mapping)

    def map_event(self, gesture_event: GestureEvent) -> ControlAction:
        """Map a gesture event to a session control action."""
        try:
            control_action_type = self._mapping[gesture_event.gesture_type]
        except KeyError as exc:
            raise UnmappedGestureEvent(
                f"No control action mapped for gesture event: {gesture_event.gesture_type.value}",
            ) from exc

        return ControlAction(action=control_action_type)
