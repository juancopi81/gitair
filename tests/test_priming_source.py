import inspect

import pytest

import gitair.core.session as session_module
from gitair.core.companion_state import CompanionStatus
from gitair.core.control_action import ControlAction, ControlActionType
from gitair.core.errors import GitairError, InvalidPrimingSourceTransition
from gitair.core.phrase_context import PhraseContext
from gitair.core.session import Session
from gitair.core.session_snapshot import SessionPhase
from gitair.demos.priming_source_dry_run import run_priming_source_dry_run
from gitair.priming.manual import ManualPrimingSource


def create_phrase_context() -> PhraseContext:
    return PhraseContext(
        chords=["E7", "G5", "A"],
        tempo_bpm=120.0,
        style_description="raw rock",
        prompt_summary="short riff",
    )


def test_manual_priming_source_returns_phrase_context_after_start_and_finish() -> None:
    phrase_context = create_phrase_context()
    source = ManualPrimingSource(phrase_context=phrase_context)

    source.start()
    finished_context = source.finish()

    assert finished_context == phrase_context
    assert finished_context is not phrase_context


def test_manual_priming_source_finish_before_start_fails_clearly() -> None:
    source = ManualPrimingSource(phrase_context=create_phrase_context())

    with pytest.raises(InvalidPrimingSourceTransition, match="before it starts") as exc_info:
        source.finish()

    assert isinstance(exc_info.value, GitairError)


def test_manual_priming_source_invalid_repeated_lifecycle_fails_clearly() -> None:
    source = ManualPrimingSource(phrase_context=create_phrase_context())

    source.start()
    with pytest.raises(InvalidPrimingSourceTransition, match="start priming source twice"):
        source.start()

    source.finish()
    with pytest.raises(InvalidPrimingSourceTransition, match="finish priming source twice"):
        source.finish()

    with pytest.raises(InvalidPrimingSourceTransition, match="finished priming source"):
        source.start()


def test_priming_source_orchestration_enters_jam_then_silences(capsys) -> None:
    run_priming_source_dry_run(
        phrase_context=create_phrase_context(),
        gesture_tokens=["HEAD_RIGHT", "HEAD_LEFT"],
    )

    output = capsys.readouterr().out

    assert "Initial snapshot" in output
    assert "phase: priming_pass" in output
    assert "phrase_context: none" in output
    assert "Priming Source: started" in output
    assert "Gesture Event: HEAD_RIGHT (confidence=1.00)" in output
    assert "Mapped Control Action: BRING_COMPANION_IN" in output
    assert "Priming Source: finished" in output
    assert "Snapshot after HEAD_RIGHT" in output
    assert "phase: jam_pass" in output
    assert "companion_status: active" in output
    assert "E7 | G5 | A" in output
    assert "Gesture Event: HEAD_LEFT (confidence=1.00)" in output
    assert "Mapped Control Action: SILENCE_COMPANION" in output
    assert "Snapshot after HEAD_LEFT" in output
    assert "companion_status: silent" in output


def test_finished_priming_context_can_drive_session_into_jam() -> None:
    session = Session()
    source = ManualPrimingSource(phrase_context=create_phrase_context())

    source.start()
    session.receive_phrase_context(phrase_context=source.finish())
    session.apply_control_action(
        control_action=ControlAction(action=ControlActionType.BRING_COMPANION_IN),
    )

    snapshot = session.get_snapshot()

    assert snapshot.phase == SessionPhase.JAM_PASS
    assert snapshot.companion_state is not None
    assert snapshot.companion_state.status == CompanionStatus.ACTIVE


def test_session_core_does_not_import_priming_or_gesture_sources() -> None:
    session_source = inspect.getsource(session_module)

    assert "gitair.priming" not in session_source
    assert "PrimingSource" not in session_source
    assert "ManualPrimingSource" not in session_source
    assert "gitair.gestures" not in session_source
    assert "GestureEvent" not in session_source
