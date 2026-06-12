from gitair.companions.fake import FakeCompanion
from gitair.core.control_action import ControlAction, ControlActionType
from gitair.core.phrase_context import PhraseContext
from gitair.core.session import Session
from gitair.core.session_snapshot import SessionPhase


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
