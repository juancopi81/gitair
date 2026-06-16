"""
Fake companion implementation for Gitair.

This is a simple implementation of a companion that can be used for testing and development.
"""

from gitair.core.companion_state import CompanionStatus
from gitair.core.errors import CompanionNotReady
from gitair.core.session_snapshot import SessionPhase, SessionSnapshot


class FakeCompanion:
    """Fake companion used to prove the companion boundary."""

    def respond(self, snapshot: SessionSnapshot) -> str:
        """Produce a fake companion response from a session snapshot."""
        if snapshot.phase != SessionPhase.JAM_PASS:
            raise CompanionNotReady("Cannot ask companion to respond before jam pass.")

        if snapshot.phrase_context is None:
            raise CompanionNotReady("Cannot respond without phrase context.")

        if snapshot.companion_state is None:
            raise CompanionNotReady("Cannot respond without companion state.")

        phrase_context = snapshot.phrase_context
        companion_state = snapshot.companion_state
        chords = " | ".join(phrase_context.chords) or "no chords"

        if companion_state.status == CompanionStatus.SILENT:
            return (
                f"Fake companion is silent during {snapshot.phase.value} "
                f"with intensity target {companion_state.intensity}."
            )

        return (
            f"Fake companion responding during {snapshot.phase.value} with status "
            f"{companion_state.status.value} and intensity {companion_state.intensity} "
            f"using chords {chords} at {phrase_context.tempo_bpm} BPM "
            f"with style: {phrase_context.style_description} "
            f"and prompt summary: {phrase_context.prompt_summary}"
        )
