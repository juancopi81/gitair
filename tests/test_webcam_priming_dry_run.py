import inspect

import gitair.core.session as session_module
from gitair.core.errors import InvalidPrimingSourceTransition
from gitair.core.phrase_context import PhraseContext
from gitair.demos.webcam_priming_dry_run import run_webcam_priming_dry_run
from gitair.gestures.event import GestureEvent, GestureType
from gitair.gestures.mediapipe_face import HeadTurnObservation, HeadTurnObservationStatus


class FakeObservationSource:
    def __init__(self, observations: list[HeadTurnObservation]) -> None:
        self._observations = observations

    def __enter__(self) -> "FakeObservationSource":
        return self

    def __exit__(self, exc_type: object, exc: object, traceback: object) -> None:
        return None

    def read_observation(self) -> HeadTurnObservation:
        return self._observations.pop(0)


class TrackingPrimingSource:
    def __init__(self, phrase_context: PhraseContext) -> None:
        self._phrase_context = phrase_context
        self.started = False
        self.finish_count = 0

    def start(self) -> None:
        if self.started:
            raise InvalidPrimingSourceTransition("Cannot start priming source twice.")
        self.started = True

    def finish(self) -> PhraseContext:
        if not self.started:
            raise InvalidPrimingSourceTransition("Cannot finish priming source before it starts.")
        self.finish_count += 1
        return self._phrase_context.model_copy(deep=True)


def create_phrase_context() -> PhraseContext:
    return PhraseContext(
        chords=["E7", "G5", "A"],
        tempo_bpm=120.0,
        style_description="raw rock",
        prompt_summary="short riff",
    )


def emitted_observation(gesture_type: GestureType) -> HeadTurnObservation:
    return HeadTurnObservation(
        status=HeadTurnObservationStatus.EMITTED,
        yaw_degrees=23.0 if gesture_type == GestureType.HEAD_RIGHT else -23.0,
        raw_yaw_degrees=23.0 if gesture_type == GestureType.HEAD_RIGHT else -23.0,
        gesture_event=GestureEvent(gesture_type=gesture_type),
    )


def source_factory_for(observations: list[HeadTurnObservation]):
    def source_factory(**kwargs) -> FakeObservationSource:
        return FakeObservationSource(observations=observations)

    return source_factory


def run_with_observations(
    observations: list[HeadTurnObservation],
    *,
    priming_source: TrackingPrimingSource,
) -> None:
    run_webcam_priming_dry_run(
        phrase_context=create_phrase_context(),
        priming_source=priming_source,
        model_path="fake.task",
        max_frames=len(observations),
        source_factory=source_factory_for(observations),
    )


def test_head_left_during_priming_rejects_and_keeps_priming_running(capsys) -> None:
    priming_source = TrackingPrimingSource(phrase_context=create_phrase_context())

    run_with_observations(
        [
            HeadTurnObservation(status=HeadTurnObservationStatus.NO_FACE),
            emitted_observation(GestureType.HEAD_LEFT),
        ],
        priming_source=priming_source,
    )

    output = capsys.readouterr().out

    assert priming_source.started is True
    assert priming_source.finish_count == 0
    assert "source_status: running" in output
    assert "Source status: no_face (yaw=none)" in output
    assert "Source status: emitted" in output
    assert "gesture=HEAD_LEFT" in output
    assert "Gesture Event: HEAD_LEFT (confidence=1.00)" in output
    assert "Mapped Control Action: SILENCE_COMPANION" in output
    assert "Control Action rejected: Cannot steer companion before jam pass." in output
    assert "Priming Source: running" in output
    assert "Snapshot after rejected HEAD_LEFT" in output
    assert "phase: priming_pass" in output
    assert "phrase_context: none" in output


def test_head_right_during_priming_finishes_source_and_enters_active_jam(capsys) -> None:
    priming_source = TrackingPrimingSource(phrase_context=create_phrase_context())

    run_with_observations(
        [emitted_observation(GestureType.HEAD_RIGHT)],
        priming_source=priming_source,
    )

    output = capsys.readouterr().out

    assert priming_source.started is True
    assert priming_source.finish_count == 1
    assert "Gesture Event: HEAD_RIGHT (confidence=1.00)" in output
    assert "Mapped Control Action: BRING_COMPANION_IN" in output
    assert "Priming Source: finishing" in output
    assert "Priming Source: finished" in output
    assert "Snapshot after HEAD_RIGHT" in output
    assert "phase: jam_pass" in output
    assert "companion_status: active" in output
    assert "E7 | G5 | A" in output


def test_head_left_after_jam_silences_companion(capsys) -> None:
    priming_source = TrackingPrimingSource(phrase_context=create_phrase_context())

    run_with_observations(
        [
            emitted_observation(GestureType.HEAD_RIGHT),
            emitted_observation(GestureType.HEAD_LEFT),
        ],
        priming_source=priming_source,
    )

    output = capsys.readouterr().out

    assert priming_source.finish_count == 1
    assert "Mapped Control Action: SILENCE_COMPANION" in output
    assert "Snapshot after HEAD_LEFT" in output
    assert "companion_status: silent" in output


def test_repeated_head_right_while_active_keeps_explicit_rejection(capsys) -> None:
    priming_source = TrackingPrimingSource(phrase_context=create_phrase_context())

    run_with_observations(
        [
            emitted_observation(GestureType.HEAD_RIGHT),
            emitted_observation(GestureType.HEAD_RIGHT),
        ],
        priming_source=priming_source,
    )

    output = capsys.readouterr().out

    assert priming_source.finish_count == 1
    assert output.count("Mapped Control Action: BRING_COMPANION_IN") == 2
    assert (
        "Control Action rejected: Cannot bring companion in because the companion "
        "is already active." in output
    )
    assert "Snapshot after rejected HEAD_RIGHT" in output
    assert "companion_status: active" in output


def test_session_core_stays_unaware_of_sources_and_gesture_events() -> None:
    session_source = inspect.getsource(session_module)

    assert "gitair.priming" not in session_source
    assert "PrimingSource" not in session_source
    assert "ManualPrimingSource" not in session_source
    assert "GestureSource" not in session_source
    assert "gitair.gestures" not in session_source
    assert "GestureEvent" not in session_source
