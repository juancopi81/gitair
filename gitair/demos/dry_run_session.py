"""
Executable dry run for the first Gitair session core path.

This demonstrates the first owner-reviewed flow:

1. A Session starts in the priming pass.
2. The Session receives phrase context.
3. A START_JAM_PASS control action moves the Session into the jam pass.
4. A FakeCompanion responds from the resulting session snapshot.
"""

from gitair.companions.fake import FakeCompanion
from gitair.core.control_action import ControlAction, ControlActionType
from gitair.core.phrase_context import PhraseContext
from gitair.core.session import Session
from gitair.core.session_snapshot import SessionSnapshot


def create_demo_phrase_context() -> PhraseContext:
    """Create the phrase context used by this dry run."""
    return PhraseContext(
        chords=["Ab", "C", "D7"],
        tempo_bpm=120.0,
        style_description="Colombian folk",
        prompt_summary="Guitar playing bambuco",
    )


def print_snapshot(label: str, snapshot: SessionSnapshot) -> None:
    """Print a small human-readable view of a session snapshot."""
    print(f"\n{label}")
    print(f"  phase: {snapshot.phase.value}")

    if snapshot.phrase_context is None:
        print("  phrase_context: none")
        return

    phrase_context = snapshot.phrase_context
    chords = " | ".join(phrase_context.chords) or "no chords"

    print(f"  chords: {chords}")
    print(f"  tempo_bpm: {phrase_context.tempo_bpm}")
    print(f"  style_description: {phrase_context.style_description}")
    print(f"  prompt_summary: {phrase_context.prompt_summary}")


def run_session_core_dry_run() -> None:
    """Run the first Gitair session core path without real audio or models."""
    session = Session()
    companion = FakeCompanion()

    initial_snapshot = session.get_snapshot()
    print_snapshot("Initial snapshot", initial_snapshot)

    phrase_context = create_demo_phrase_context()
    session.receive_phrase_context(phrase_context=phrase_context)

    start_jam_action = ControlAction(action=ControlActionType.START_JAM_PASS)
    session.apply_control_action(control_action=start_jam_action)

    jam_snapshot = session.get_snapshot()
    print_snapshot("Jam snapshot", jam_snapshot)

    companion_response = companion.respond(snapshot=jam_snapshot)

    print("\nCompanion response")
    print(f"  {companion_response}")


def main() -> None:
    """Run the dry run from the command line."""
    run_session_core_dry_run()


if __name__ == "__main__":
    main()
