"""
Executable dry run for the first Gitair session core path.

This demonstrates the first owner-reviewed flow:

1. A Session starts in the priming pass.
2. The Session receives phrase context.
3. BRING_COMPANION_IN moves the Session into the jam pass.
4. Additional control actions steer companion state.
5. A FakeCompanion responds from the resulting session snapshot.
"""

import argparse
from collections.abc import Callable, Sequence

from gitair.companions.fake import FakeCompanion
from gitair.core.control_action import ControlAction, ControlActionType
from gitair.core.phrase_context import PhraseContext
from gitair.core.session import Session
from gitair.core.session_snapshot import SessionSnapshot


def parse_chords(raw_chords: str) -> list[str]:
    """Parse a comma-separated chord progression."""
    return [chord.strip() for chord in raw_chords.split(",") if chord.strip()]


def create_demo_phrase_context(
    *,
    chords: Sequence[str] | None = None,
    tempo_bpm: float = 120.0,
    style_description: str = "Colombian folk",
    prompt_summary: str = "Guitar playing bambuco",
) -> PhraseContext:
    """Create the phrase context used by this dry run."""
    return PhraseContext(
        chords=list(chords) if chords is not None else ["Ab", "C", "D7"],
        tempo_bpm=tempo_bpm,
        style_description=style_description,
        prompt_summary=prompt_summary,
    )


def print_snapshot(label: str, snapshot: SessionSnapshot) -> None:
    """Print a small human-readable view of a session snapshot."""
    print(f"\n{label}")
    print(f"  phase: {snapshot.phase.value}")
    if snapshot.companion_state is None:
        print("  companion_state: none")
    else:
        print(f"  companion_status: {snapshot.companion_state.status.value}")
        print(f"  companion_intensity: {snapshot.companion_state.intensity}")

    if snapshot.phrase_context is None:
        print("  phrase_context: none")
        return

    phrase_context = snapshot.phrase_context
    chords = " | ".join(phrase_context.chords) or "no chords"

    print(f"  chords: {chords}")
    print(f"  tempo_bpm: {phrase_context.tempo_bpm}")
    print(f"  style_description: {phrase_context.style_description}")
    print(f"  prompt_summary: {phrase_context.prompt_summary}")


def wait_for_control_action(
    action: ControlActionType,
    input_fn: Callable[[str], str] = input,
) -> ControlAction:
    """Wait for a manual control action."""
    input_fn(f"\nPress Enter to apply Control Action: {action.name}")
    return ControlAction(action=action)


def default_demo_actions() -> list[ControlActionType]:
    """Return the default manual steering sequence for the dry run."""
    return [
        ControlActionType.BRING_COMPANION_IN,
        ControlActionType.SILENCE_COMPANION,
        ControlActionType.BRING_COMPANION_IN,
        ControlActionType.INCREASE_INTENSITY,
        ControlActionType.INCREASE_INTENSITY,
        ControlActionType.INCREASE_INTENSITY,
        ControlActionType.DECREASE_INTENSITY,
    ]


def print_companion_response(companion: FakeCompanion, snapshot: SessionSnapshot) -> None:
    """Print the fake companion response for an active or silent companion."""
    companion_response = companion.respond(snapshot=snapshot)

    print("\nCompanion response")
    print(f"  {companion_response}")


def run_session_core_dry_run(
    phrase_context: PhraseContext | None = None,
    *,
    wait_for_manual_action: bool = True,
    control_actions: Sequence[ControlActionType] | None = None,
    input_fn: Callable[[str], str] = input,
) -> None:
    """Run the first Gitair session core path without real audio or models."""
    session = Session()
    companion = FakeCompanion()

    initial_snapshot = session.get_snapshot()
    print_snapshot("Initial snapshot", initial_snapshot)

    if phrase_context is None:
        phrase_context = create_demo_phrase_context()

    session.receive_phrase_context(phrase_context=phrase_context)
    print_snapshot("Primed snapshot", session.get_snapshot())

    actions = list(control_actions) if control_actions is not None else default_demo_actions()

    for action in actions:
        if wait_for_manual_action:
            control_action = wait_for_control_action(action=action, input_fn=input_fn)
        else:
            print(f"\nApplying Control Action: {action.name}")
            control_action = ControlAction(action=action)

        session.apply_control_action(control_action=control_action)
        snapshot = session.get_snapshot()
        print_snapshot(f"Snapshot after {action.name}", snapshot)

        if snapshot.companion_state is not None:
            print_companion_response(companion=companion, snapshot=snapshot)


def build_parser() -> argparse.ArgumentParser:
    """Build the command-line parser for the manual dry run."""
    parser = argparse.ArgumentParser(
        description="Run a manually steerable Gitair Session dry run.",
    )
    parser.add_argument(
        "--chords",
        default="Ab,C,D7",
        help="Comma-separated chord labels for the phrase context.",
    )
    parser.add_argument(
        "--tempo-bpm",
        type=float,
        default=120.0,
        help="Tempo in beats per minute for the phrase context.",
    )
    parser.add_argument(
        "--style-description",
        default="Colombian folk",
        help="Short musical style description for the phrase context.",
    )
    parser.add_argument(
        "--prompt-summary",
        default="Guitar playing bambuco",
        help="Short prompt summary used to steer the fake companion.",
    )
    parser.add_argument(
        "--auto-demo-steering",
        action="store_true",
        help="Apply the default companion-steering sequence without waiting for Enter.",
    )
    return parser


def phrase_context_from_args(args: argparse.Namespace) -> PhraseContext:
    """Create phrase context from parsed CLI arguments."""
    return create_demo_phrase_context(
        chords=parse_chords(args.chords),
        tempo_bpm=args.tempo_bpm,
        style_description=args.style_description,
        prompt_summary=args.prompt_summary,
    )


def main() -> None:
    """Run the dry run from the command line."""
    parser = build_parser()
    args = parser.parse_args()
    run_session_core_dry_run(
        phrase_context=phrase_context_from_args(args),
        wait_for_manual_action=not args.auto_demo_steering,
    )


if __name__ == "__main__":
    main()
