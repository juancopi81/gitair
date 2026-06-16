import pytest

from gitair.companions.fake import FakeCompanion
from gitair.core.companion_state import CompanionState, CompanionStatus
from gitair.core.control_action import ControlAction, ControlActionType
from gitair.core.errors import CompanionNotReady, InvalidSessionTransition
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
    bring_companion_in_action = ControlAction(action=ControlActionType.BRING_COMPANION_IN)

    session.receive_phrase_context(phrase_context=phrase_context)
    session.apply_control_action(control_action=bring_companion_in_action)

    jam_snapshot = session.get_snapshot()
    response_text = fake_companion.respond(snapshot=jam_snapshot)

    assert initial_snapshot.phase == SessionPhase.PRIMING_PASS
    assert initial_snapshot.phrase_context is None

    assert jam_snapshot.phase == SessionPhase.JAM_PASS
    assert jam_snapshot.companion_state == CompanionState(
        status=CompanionStatus.ACTIVE,
        intensity=3,
    )
    assert jam_snapshot.phrase_context is not None
    assert jam_snapshot.phrase_context.chords == ["Ab", "C", "D7"]
    assert jam_snapshot.phrase_context.tempo_bpm == 120.0
    assert jam_snapshot.phrase_context.style_description == "Colombian folk"
    assert jam_snapshot.phrase_context.prompt_summary == "Guitar playing bambuco"

    assert isinstance(response_text, str)
    assert "jam_pass" in response_text
    assert "status active" in response_text
    assert "intensity 3" in response_text
    assert "Ab | C | D7" in response_text
    assert "Colombian folk" in response_text
    assert "Guitar playing bambuco" in response_text


def test_bringing_companion_in_without_phrase_context_fails_clearly() -> None:
    session = Session()
    bring_companion_in_action = ControlAction(action=ControlActionType.BRING_COMPANION_IN)

    with pytest.raises(InvalidSessionTransition, match="without phrase context"):
        session.apply_control_action(control_action=bring_companion_in_action)


def test_bringing_companion_in_twice_while_active_fails_clearly() -> None:
    session = Session()
    phrase_context = PhraseContext(
        chords=["Dm7", "G7", "Cmaj7"],
        tempo_bpm=96.0,
        style_description="quiet bossa nova",
        prompt_summary="soft syncopated guitar phrase",
    )
    bring_companion_in_action = ControlAction(action=ControlActionType.BRING_COMPANION_IN)

    session.receive_phrase_context(phrase_context=phrase_context)
    session.apply_control_action(control_action=bring_companion_in_action)

    with pytest.raises(InvalidSessionTransition, match="already active"):
        session.apply_control_action(control_action=bring_companion_in_action)


def test_can_silence_and_bring_companion_back_without_replacing_phrase_context() -> None:
    session = Session()
    phrase_context = PhraseContext(
        chords=["Dm7", "G7", "Cmaj7"],
        tempo_bpm=96.0,
        style_description="quiet bossa nova",
        prompt_summary="soft syncopated guitar phrase",
    )

    session.receive_phrase_context(phrase_context=phrase_context)
    session.apply_control_action(
        control_action=ControlAction(action=ControlActionType.BRING_COMPANION_IN),
    )
    session.apply_control_action(
        control_action=ControlAction(action=ControlActionType.SILENCE_COMPANION),
    )

    silent_snapshot = session.get_snapshot()

    assert silent_snapshot.phase == SessionPhase.JAM_PASS
    assert silent_snapshot.phrase_context == phrase_context
    assert silent_snapshot.companion_state == CompanionState(
        status=CompanionStatus.SILENT,
        intensity=3,
    )

    session.apply_control_action(
        control_action=ControlAction(action=ControlActionType.BRING_COMPANION_IN),
    )

    active_snapshot = session.get_snapshot()

    assert active_snapshot.phrase_context == phrase_context
    assert active_snapshot.companion_state == CompanionState(
        status=CompanionStatus.ACTIVE,
        intensity=3,
    )


def test_silencing_companion_before_jam_fails_clearly() -> None:
    session = Session()

    with pytest.raises(InvalidSessionTransition, match="before jam pass"):
        session.apply_control_action(
            control_action=ControlAction(action=ControlActionType.SILENCE_COMPANION),
        )


def test_silencing_companion_twice_fails_clearly() -> None:
    session = Session()
    session.receive_phrase_context(
        phrase_context=PhraseContext(
            chords=["Dm7", "G7", "Cmaj7"],
            tempo_bpm=96.0,
            style_description="quiet bossa nova",
            prompt_summary="soft syncopated guitar phrase",
        ),
    )
    session.apply_control_action(
        control_action=ControlAction(action=ControlActionType.BRING_COMPANION_IN),
    )
    session.apply_control_action(
        control_action=ControlAction(action=ControlActionType.SILENCE_COMPANION),
    )

    with pytest.raises(InvalidSessionTransition, match="already silent"):
        session.apply_control_action(
            control_action=ControlAction(action=ControlActionType.SILENCE_COMPANION),
        )


def test_intensity_actions_adjust_one_step_and_clamp_at_bounds() -> None:
    session = Session()
    session.receive_phrase_context(
        phrase_context=PhraseContext(
            chords=["Dm7", "G7", "Cmaj7"],
            tempo_bpm=96.0,
            style_description="quiet bossa nova",
            prompt_summary="soft syncopated guitar phrase",
        ),
    )
    session.apply_control_action(
        control_action=ControlAction(action=ControlActionType.BRING_COMPANION_IN),
    )

    for _ in range(4):
        session.apply_control_action(
            control_action=ControlAction(action=ControlActionType.INCREASE_INTENSITY),
        )

    high_snapshot = session.get_snapshot()

    assert high_snapshot.companion_state is not None
    assert high_snapshot.companion_state.intensity == 5

    for _ in range(8):
        session.apply_control_action(
            control_action=ControlAction(action=ControlActionType.DECREASE_INTENSITY),
        )

    low_snapshot = session.get_snapshot()

    assert low_snapshot.companion_state is not None
    assert low_snapshot.companion_state.intensity == 1


def test_intensity_action_before_jam_fails_clearly() -> None:
    session = Session()

    with pytest.raises(InvalidSessionTransition, match="before jam pass"):
        session.apply_control_action(
            control_action=ControlAction(action=ControlActionType.INCREASE_INTENSITY),
        )


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

    with pytest.raises(CompanionNotReady, match="before jam pass"):
        fake_companion.respond(snapshot=session.get_snapshot())


def test_companion_response_without_phrase_context_fails_clearly() -> None:
    fake_companion = FakeCompanion()
    jam_snapshot_without_context = SessionSnapshot(phase=SessionPhase.JAM_PASS)

    with pytest.raises(CompanionNotReady, match="without phrase context"):
        fake_companion.respond(snapshot=jam_snapshot_without_context)


def test_companion_response_without_companion_state_fails_clearly() -> None:
    fake_companion = FakeCompanion()
    phrase_context = PhraseContext(
        chords=["Dm7", "G7", "Cmaj7"],
        tempo_bpm=96.0,
        style_description="quiet bossa nova",
        prompt_summary="soft syncopated guitar phrase",
    )
    jam_snapshot_without_companion_state = SessionSnapshot(
        phase=SessionPhase.JAM_PASS,
        phrase_context=phrase_context,
    )

    with pytest.raises(CompanionNotReady, match="without companion state"):
        fake_companion.respond(snapshot=jam_snapshot_without_companion_state)


def test_silent_companion_response_reflects_silent_state() -> None:
    fake_companion = FakeCompanion()
    snapshot = SessionSnapshot(
        phase=SessionPhase.JAM_PASS,
        phrase_context=PhraseContext(
            chords=["Dm7", "G7", "Cmaj7"],
            tempo_bpm=96.0,
            style_description="quiet bossa nova",
            prompt_summary="soft syncopated guitar phrase",
        ),
        companion_state=CompanionState(status=CompanionStatus.SILENT, intensity=2),
    )

    response = fake_companion.respond(snapshot=snapshot)

    assert "silent" in response
    assert "intensity target 2" in response


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
        control_actions=[
            ControlActionType.BRING_COMPANION_IN,
            ControlActionType.SILENCE_COMPANION,
            ControlActionType.BRING_COMPANION_IN,
            ControlActionType.INCREASE_INTENSITY,
            ControlActionType.DECREASE_INTENSITY,
        ],
    )

    output = capsys.readouterr().out

    assert "Applying Control Action: BRING_COMPANION_IN" in output
    assert "Applying Control Action: SILENCE_COMPANION" in output
    assert "Applying Control Action: INCREASE_INTENSITY" in output
    assert "companion_status: active" in output
    assert "companion_status: silent" in output
    assert "companion_intensity: 4" in output
    assert "Dm7 | G7 | Cmaj7" in output
    assert "96.0 BPM" in output
    assert "quiet bossa nova" in output
    assert "soft syncopated guitar phrase" in output
