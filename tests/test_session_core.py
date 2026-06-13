import pytest

from gitair.companions.fake import FakeCompanion
from gitair.core.control_action import ControlAction, ControlActionType
from gitair.core.phrase_context import PhraseContext
from gitair.core.session import Session
from gitair.core.session_snapshot import SessionPhase, SessionSnapshot
from gitair.demos.dry_run_session import (
    parse_chords,
    run_session_core_dry_run,
)


def test_session_moves_from_priming_to_jam_and_fake_companion_responds() -> None:
    session = Session()
    fake_companion = FakeCompanion()

    initial_snapshot = session.get_snapshot()

    phrase_context = PhraseContext(
        chords=["Ab", "C", "D7"],
        tempo_bpm=120.0,
        style_description="Colombian folk",
        prompt_summary="Guitar playing bambuco",
    )
    start_jam_action = ControlAction(action=ControlActionType.START_JAM_PASS)

    session.receive_phrase_context(phrase_context=phrase_context)
    session.apply_control_action(control_action=start_jam_action)

    jam_snapshot = session.get_snapshot()
    response_text = fake_companion.respond(snapshot=jam_snapshot)

    assert initial_snapshot.phase == SessionPhase.PRIMING_PASS
    assert initial_snapshot.phrase_context is None

    assert jam_snapshot.phase == SessionPhase.JAM_PASS
    assert jam_snapshot.phrase_context is not None
    assert jam_snapshot.phrase_context.chords == ["Ab", "C", "D7"]
    assert jam_snapshot.phrase_context.tempo_bpm == 120.0
    assert jam_snapshot.phrase_context.style_description == "Colombian folk"
    assert jam_snapshot.phrase_context.prompt_summary == "Guitar playing bambuco"

    assert isinstance(response_text, str)
    assert "jam_pass" in response_text
    assert "Ab | C | D7" in response_text
    assert "Colombian folk" in response_text
    assert "Guitar playing bambuco" in response_text


def test_starting_jam_without_phrase_context_fails_clearly() -> None:
    session = Session()
    start_jam_action = ControlAction(action=ControlActionType.START_JAM_PASS)

    with pytest.raises(ValueError, match="without phrase context"):
        session.apply_control_action(control_action=start_jam_action)


def test_starting_jam_twice_fails_clearly() -> None:
    session = Session()
    phrase_context = PhraseContext(
        chords=["Dm7", "G7", "Cmaj7"],
        tempo_bpm=96.0,
        style_description="quiet bossa nova",
        prompt_summary="soft syncopated guitar phrase",
    )
    start_jam_action = ControlAction(action=ControlActionType.START_JAM_PASS)

    session.receive_phrase_context(phrase_context=phrase_context)
    session.apply_control_action(control_action=start_jam_action)

    with pytest.raises(ValueError, match="already in jam pass"):
        session.apply_control_action(control_action=start_jam_action)


def test_companion_response_before_jam_fails_clearly() -> None:
    session = Session()
    fake_companion = FakeCompanion()
    phrase_context = PhraseContext(
        chords=["Dm7", "G7", "Cmaj7"],
        tempo_bpm=96.0,
        style_description="quiet bossa nova",
        prompt_summary="soft syncopated guitar phrase",
    )

    session.receive_phrase_context(phrase_context=phrase_context)

    with pytest.raises(ValueError, match="before jam pass"):
        fake_companion.respond(snapshot=session.get_snapshot())


def test_companion_response_without_phrase_context_fails_clearly() -> None:
    fake_companion = FakeCompanion()
    jam_snapshot_without_context = SessionSnapshot(phase=SessionPhase.JAM_PASS)

    with pytest.raises(ValueError, match="without phrase context"):
        fake_companion.respond(snapshot=jam_snapshot_without_context)


def test_parse_chords_strips_empty_comma_separated_values() -> None:
    assert parse_chords(" Dm7, G7, , Cmaj7 ") == ["Dm7", "G7", "Cmaj7"]


def test_manual_dry_run_uses_supplied_phrase_context(capsys) -> None:
    phrase_context = PhraseContext(
        chords=["Dm7", "G7", "Cmaj7"],
        tempo_bpm=96.0,
        style_description="quiet bossa nova",
        prompt_summary="soft syncopated guitar phrase",
    )

    run_session_core_dry_run(
        phrase_context=phrase_context,
        wait_for_manual_action=False,
    )

    output = capsys.readouterr().out

    assert "Applying Control Action: START_JAM_PASS" in output
    assert "Dm7 | G7 | Cmaj7" in output
    assert "96.0 BPM" in output
    assert "quiet bossa nova" in output
    assert "soft syncopated guitar phrase" in output
