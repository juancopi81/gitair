"""
Core session model for Gitair.

A session is a bounded Gitair run. For this first core slice, the session tracks
the musician's priming pass, the AI-assisted jam pass, and the current phrase
context.
"""

from gitair.core.companion_state import CompanionState, CompanionStatus
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
        match control_action.action:
            case ControlActionType.BRING_COMPANION_IN:
                self._bring_companion_in()
            case ControlActionType.SILENCE_COMPANION:
                self._silence_companion()
            case ControlActionType.INCREASE_INTENSITY:
                self._adjust_intensity(delta=1)
            case ControlActionType.DECREASE_INTENSITY:
                self._adjust_intensity(delta=-1)
            case _:
                raise UnsupportedControlAction(f"Unknown control action: {control_action}")

    def _bring_companion_in(self) -> None:
        """Bring the companion into the performance."""
        if self._snapshot.phase == SessionPhase.PRIMING_PASS:
            self._enter_jam_pass_with_companion()
            return

        companion_state = self._require_companion_state()
        if companion_state.status == CompanionStatus.ACTIVE:
            raise InvalidSessionTransition(
                "Cannot bring companion in because the companion is already active.",
            )

        self._snapshot.companion_state = companion_state.model_copy(
            update={"status": CompanionStatus.ACTIVE},
        )

    def _enter_jam_pass_with_companion(self) -> None:
        """Move from priming into jam and activate the companion."""
        if self._snapshot.phrase_context is None:
            raise InvalidSessionTransition("Cannot bring companion in without phrase context.")

        self._snapshot.phase = SessionPhase.JAM_PASS
        self._snapshot.companion_state = CompanionState()

    def _silence_companion(self) -> None:
        """Silence the companion during the jam pass."""
        companion_state = self._require_companion_state()
        if companion_state.status == CompanionStatus.SILENT:
            raise InvalidSessionTransition(
                "Cannot silence companion because the companion is already silent.",
            )

        self._snapshot.companion_state = companion_state.model_copy(
            update={"status": CompanionStatus.SILENT},
        )

    def _adjust_intensity(self, *, delta: int) -> None:
        """Adjust companion intensity one discrete step, clamped to 1..5."""
        companion_state = self._require_companion_state()
        next_intensity = min(5, max(1, companion_state.intensity + delta))
        self._snapshot.companion_state = companion_state.model_copy(
            update={"intensity": next_intensity},
        )

    def _require_companion_state(self) -> CompanionState:
        """Return companion state when the session is in a valid jam state."""
        if self._snapshot.phase != SessionPhase.JAM_PASS:
            raise InvalidSessionTransition(
                "Cannot steer companion before jam pass.",
            )

        if self._snapshot.phrase_context is None:
            raise InvalidSessionTransition("Cannot steer companion without phrase context.")

        if self._snapshot.companion_state is None:
            raise InvalidSessionTransition("Cannot steer companion without companion state.")

        return self._snapshot.companion_state

    def get_snapshot(self) -> SessionSnapshot:
        """Return the current session snapshot."""
        return self._snapshot.model_copy(deep=True)
