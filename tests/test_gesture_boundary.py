import inspect

import pytest

import gitair.core.session as session_module
from gitair.core.companion_state import CompanionStatus
from gitair.core.control_action import ControlActionType
from gitair.core.errors import GitairError, UnmappedGestureEvent, UnsupportedGestureEvent
from gitair.core.phrase_context import PhraseContext
from gitair.core.session import Session
from gitair.core.session_snapshot import SessionPhase
from gitair.demos.gesture_dry_run import run_gesture_dry_run
from gitair.gestures.event import GestureEvent, GestureType, parse_gesture_event
from gitair.gestures.fake import ScriptedGestureSource
from gitair.gestures.mapper import GestureMapper


def test_gesture_event_defaults_confidence_and_accepts_visible_confidence() -> None:
    default_event = GestureEvent(gesture_type=GestureType.HEAD_RIGHT)
    confident_event = GestureEvent(gesture_type=GestureType.NOD_UP, confidence=0.72)

    assert default_event.gesture_type == GestureType.HEAD_RIGHT
    assert default_event.confidence == 1.0
    assert confident_event.confidence == 0.72


@pytest.mark.parametrize(
    ("gesture_type", "control_action_type"),
    [
        (GestureType.HEAD_RIGHT, ControlActionType.BRING_COMPANION_IN),
        (GestureType.HEAD_LEFT, ControlActionType.SILENCE_COMPANION),
        (GestureType.NOD_UP, ControlActionType.INCREASE_INTENSITY),
        (GestureType.NOD_DOWN, ControlActionType.DECREASE_INTENSITY),
    ],
)
def test_default_gesture_mapping_returns_control_actions(
    gesture_type: GestureType,
    control_action_type: ControlActionType,
) -> None:
    mapper = GestureMapper()

    control_action = mapper.map_event(GestureEvent(gesture_type=gesture_type))

    assert control_action.action == control_action_type


def test_unknown_scripted_gesture_raises_custom_error() -> None:
    with pytest.raises(UnsupportedGestureEvent, match="HEAD_SHAKE") as exc_info:
        parse_gesture_event("HEAD_SHAKE")

    assert isinstance(exc_info.value, GitairError)


def test_unmapped_gesture_event_raises_custom_error() -> None:
    mapper = GestureMapper(mapping={})

    with pytest.raises(UnmappedGestureEvent, match="HEAD_RIGHT") as exc_info:
        mapper.map_event(GestureEvent(gesture_type=GestureType.HEAD_RIGHT))

    assert isinstance(exc_info.value, GitairError)


def test_scripted_gesture_source_drives_session_through_mapper() -> None:
    session = Session()
    session.receive_phrase_context(
        phrase_context=PhraseContext(
            chords=["E7", "G5", "A"],
            tempo_bpm=120.0,
            style_description="raw rock",
            prompt_summary="short riff",
        ),
    )
    source = ScriptedGestureSource.from_tokens(
        ["HEAD_RIGHT", "HEAD_LEFT", "HEAD_RIGHT", "NOD_UP", "NOD_DOWN"],
    )
    mapper = GestureMapper()

    for gesture_event in source.events():
        session.apply_control_action(control_action=mapper.map_event(gesture_event))

    snapshot = session.get_snapshot()

    assert snapshot.phase == SessionPhase.JAM_PASS
    assert snapshot.companion_state is not None
    assert snapshot.companion_state.status == CompanionStatus.ACTIVE
    assert snapshot.companion_state.intensity == 3


def test_session_core_does_not_import_gesture_boundary() -> None:
    session_source = inspect.getsource(session_module)

    assert "gitair.gestures" not in session_source
    assert "GestureEvent" not in session_source
    assert "GestureType" not in session_source


def test_gesture_dry_run_shows_event_mapping_and_companion_state(capsys) -> None:
    run_gesture_dry_run(
        phrase_context=PhraseContext(
            chords=["E7", "G5", "A"],
            tempo_bpm=120.0,
            style_description="raw rock",
            prompt_summary="short riff",
        ),
        gesture_tokens=["HEAD_RIGHT", "HEAD_LEFT", "HEAD_RIGHT", "NOD_UP", "NOD_DOWN"],
    )

    output = capsys.readouterr().out

    assert "Gesture Event: HEAD_RIGHT (confidence=1.00)" in output
    assert "Mapped Control Action: BRING_COMPANION_IN" in output
    assert "Mapped Control Action: SILENCE_COMPANION" in output
    assert "Mapped Control Action: INCREASE_INTENSITY" in output
    assert "Mapped Control Action: DECREASE_INTENSITY" in output
    assert "companion_status: active" in output
    assert "companion_status: silent" in output
    assert "companion_intensity: 4" in output
    assert "E7 | G5 | A" in output
