"""
Deterministic dry run for the Gitair gesture event boundary.

This demonstrates the Milestone 3 flow:

1. A scripted source emits Gesture Events.
2. A GestureMapper translates them into Control Actions.
3. The Session applies those Control Actions without knowing about gestures.
4. The resulting companion state is printed after each gesture.
"""

import argparse
from collections.abc import Sequence

from gitair.companions.fake import FakeCompanion
from gitair.core.phrase_context import PhraseContext
from gitair.core.session import Session
from gitair.demos.dry_run_session import (
    create_demo_phrase_context,
    parse_chords,
    print_companion_response,
    print_snapshot,
)
from gitair.gestures.fake import ScriptedGestureSource
from gitair.gestures.mapper import GestureMapper

DEFAULT_GESTURE_SEQUENCE = (
    "HEAD_RIGHT",
    "HEAD_LEFT",
    "HEAD_RIGHT",
    "NOD_UP",
    "NOD_DOWN",
)


def parse_gestures(raw_gestures: str) -> list[str]:
    """Parse comma-separated scripted gesture tokens."""
    return [gesture.strip() for gesture in raw_gestures.split(",") if gesture.strip()]


def run_gesture_dry_run(
    phrase_context: PhraseContext | None = None,
    *,
    gesture_tokens: Sequence[str] | None = None,
) -> None:
    """Run the scripted gesture-to-session tracer bullet."""
    session = Session()
    companion = FakeCompanion()
    mapper = GestureMapper()

    if phrase_context is None:
        phrase_context = create_demo_phrase_context()

    session.receive_phrase_context(phrase_context=phrase_context)
    print_snapshot("Primed snapshot", session.get_snapshot())

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

        session.apply_control_action(control_action=control_action)
        snapshot = session.get_snapshot()
        print_snapshot(f"Snapshot after {gesture_event.gesture_type.value}", snapshot)

        if snapshot.companion_state is not None:
            print_companion_response(companion=companion, snapshot=snapshot)


def build_parser() -> argparse.ArgumentParser:
    """Build the command-line parser for the gesture dry run."""
    parser = argparse.ArgumentParser(
        description="Run a scripted Gitair gesture event boundary dry run.",
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
    """Run the gesture dry run from the command line."""
    parser = build_parser()
    args = parser.parse_args()
    run_gesture_dry_run(
        phrase_context=phrase_context_from_args(args),
        gesture_tokens=parse_gestures(args.gestures),
    )


if __name__ == "__main__":
    main()
