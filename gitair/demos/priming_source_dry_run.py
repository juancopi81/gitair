"""
Deterministic dry run for the Gitair priming source boundary.

This demonstrates the Milestone 5 flow:

1. A lifecycle-bound Priming Source starts during the priming pass.
2. HEAD_RIGHT is mapped to BRING_COMPANION_IN.
3. The demo orchestrator finishes the Priming Source, sends Phrase Context to
   Session, then applies BRING_COMPANION_IN.
4. HEAD_LEFT after jam starts still silences the companion.
"""

import argparse
from collections.abc import Sequence

from gitair.companions.fake import FakeCompanion
from gitair.core.control_action import ControlAction, ControlActionType
from gitair.core.phrase_context import PhraseContext
from gitair.core.session import Session
from gitair.core.session_snapshot import SessionPhase
from gitair.demos.dry_run_session import (
    create_demo_phrase_context,
    parse_chords,
    print_companion_response,
    print_snapshot,
)
from gitair.demos.gesture_dry_run import parse_gestures
from gitair.gestures.fake import ScriptedGestureSource
from gitair.gestures.mapper import GestureMapper
from gitair.priming.manual import ManualPrimingSource
from gitair.priming.source import PrimingSource

DEFAULT_GESTURE_SEQUENCE = ("HEAD_RIGHT", "HEAD_LEFT")


def run_priming_source_dry_run(
    phrase_context: PhraseContext | None = None,
    *,
    gesture_tokens: Sequence[str] | None = None,
    priming_source: PrimingSource | None = None,
) -> None:
    """Run the priming-source-to-session tracer bullet."""
    session = Session()
    companion = FakeCompanion()
    mapper = GestureMapper()

    if phrase_context is None:
        phrase_context = create_demo_phrase_context()

    if priming_source is None:
        priming_source = ManualPrimingSource(phrase_context=phrase_context)

    print_snapshot("Initial snapshot", session.get_snapshot())
    priming_source.start()
    print("\nPriming Source: started")

    source = ScriptedGestureSource.from_tokens(
        list(gesture_tokens) if gesture_tokens is not None else list(DEFAULT_GESTURE_SEQUENCE),
    )

    for gesture_event in source.events():
        print(
            f"\nGesture Event: {gesture_event.gesture_type.value} "
            f"(confidence={gesture_event.confidence:.2f})",
        )
        control_action = mapper.map_event(gesture_event=gesture_event)
        print(f"Mapped Control Action: {control_action.action.name}")

        if should_finish_priming(session=session, control_action=control_action):
            finished_context = priming_source.finish()
            session.receive_phrase_context(phrase_context=finished_context)
            print("Priming Source: finished")
            print_snapshot("Primed snapshot", session.get_snapshot())

        session.apply_control_action(control_action=control_action)
        snapshot = session.get_snapshot()
        print_snapshot(f"Snapshot after {gesture_event.gesture_type.value}", snapshot)

        if snapshot.companion_state is not None:
            print_companion_response(companion=companion, snapshot=snapshot)


def should_finish_priming(*, session: Session, control_action: ControlAction) -> bool:
    """Return whether a control action should finalize the priming source."""
    snapshot = session.get_snapshot()
    return (
        snapshot.phase == SessionPhase.PRIMING_PASS
        and control_action.action == ControlActionType.BRING_COMPANION_IN
    )


def build_parser() -> argparse.ArgumentParser:
    """Build the command-line parser for the priming source dry run."""
    parser = argparse.ArgumentParser(
        description="Run a scripted Gitair priming source boundary dry run.",
    )
    parser.add_argument(
        "--gestures",
        default=",".join(DEFAULT_GESTURE_SEQUENCE),
        help=(
            "Comma-separated gesture tokens. Supported tokens are "
            "HEAD_RIGHT, HEAD_LEFT, NOD_UP, and NOD_DOWN."
        ),
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
    """Run the priming source dry run from the command line."""
    parser = build_parser()
    args = parser.parse_args()
    run_priming_source_dry_run(
        phrase_context=phrase_context_from_args(args),
        gesture_tokens=parse_gestures(args.gestures),
    )


if __name__ == "__main__":
    main()
