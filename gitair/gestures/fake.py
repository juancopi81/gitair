from collections.abc import Iterable, Iterator, Sequence

from gitair.core.errors import UnsupportedGestureEvent
from gitair.gestures.event import GestureEvent, parse_gesture_event


class ScriptedGestureSource:
    """Deterministic gesture source for tests and dry runs."""

    def __init__(self, events: Iterable[GestureEvent]) -> None:
        self._events = tuple(events)
        if not self._events:
            raise UnsupportedGestureEvent("Scripted gesture source needs at least one event.")

    @classmethod
    def from_tokens(cls, raw_gestures: Sequence[str]) -> "ScriptedGestureSource":
        """Create a scripted source from raw gesture tokens."""
        return cls(parse_gesture_event(raw_gesture) for raw_gesture in raw_gestures)

    def events(self) -> Iterator[GestureEvent]:
        """Yield scripted gesture events in order."""
        yield from self._events
