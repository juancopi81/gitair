"""
Core session model for Gitair.

A session is a bounded Gitair run. For this first core slice, the session tracks
the musician's priming pass, the AI-assisted jam pass, and the current phrase
context.
"""

from gitair.core.control_action import ControlAction, ControlActionType
from gitair.core.errors import InvalidSessionTransition, UnsupportedControlAction
from gitair.core.phrase_context import PhraseContext
from gitair.core.session_snapshot import SessionPhase, SessionSnapshot


class Session:
    """Small state model for a bounded Gitair run."""

    def __init__(self) -> None:
        self._snapshot: SessionSnapshot = SessionSnapshot()

    def receive_phrase_context(self, phrase_context: PhraseContext) -> None:
        """Store phrase context captured or provided during the priming pass."""
        self._snapshot.phrase_context = phrase_context

    def apply_control_action(self, control_action: ControlAction) -> None:
        """Apply a control action to the session."""
        if control_action.action == ControlActionType.START_JAM_PASS:
            self._start_jam_pass()
        else:
            raise UnsupportedControlAction(f"Unknown control action: {control_action}")

    def _start_jam_pass(self) -> None:
        """Move the session into the jam pass."""
        if self._snapshot.phase == SessionPhase.JAM_PASS:
            raise InvalidSessionTransition(
                "Cannot start jam pass because the session is already in jam pass.",
            )

        if self._snapshot.phrase_context is None:
            raise InvalidSessionTransition("Cannot start jam pass without phrase context.")

        self._snapshot.phase = SessionPhase.JAM_PASS

    def get_snapshot(self) -> SessionSnapshot:
        """Return the current session snapshot."""
        return self._snapshot.model_copy(deep=True)
