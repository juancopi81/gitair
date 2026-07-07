import inspect

import gitair.core.session as session_module
from gitair.core.errors import GitairError, InvalidPrimingSourceTransition
from gitair.core.phrase_context import PhraseContext
from gitair.demos.webcam_audio_priming_dry_run import run_webcam_audio_priming_dry_run
from gitair.gestures.event import GestureEvent, GestureType
from gitair.gestures.mediapipe_face import HeadTurnObservation, HeadTurnObservationStatus
from gitair.priming.audio_buffer import PrimingAudioBuffer


class FakeObservationSource:
    def __init__(self, observations: list[HeadTurnObservation]) -> None:
        self._observations = observations

    def __enter__(self) -> "FakeObservationSource":
        return self

    def __exit__(self, exc_type: object, exc: object, traceback: object) -> None:
        return None

    def read_observation(self) -> HeadTurnObservation:
        return self._observations.pop(0)


class TrackingAudioPrimingSource:
    def __init__(
        self,
        phrase_context: PhraseContext,
        *,
        audio_buffer: PrimingAudioBuffer | None = None,
    ) -> None:
        self._phrase_context = phrase_context
        self._audio_buffer = audio_buffer or PrimingAudioBuffer(
            sample_rate=44_100,
            channels=1,
            frame_count=0,
            chunk_count=0,
        )
        self.started = False
        self.finish_count = 0
        self.close_count = 0

    @property
    def audio_buffer(self) -> PrimingAudioBuffer:
        return self._audio_buffer

    def start(self) -> None:
        if self.started:
            raise InvalidPrimingSourceTransition("Cannot start priming source twice.")
        self.started = True

    def finish(self) -> PhraseContext:
        if not self.started:
            raise InvalidPrimingSourceTransition("Cannot finish priming source before it starts.")
        self.finish_count += 1
        return self._phrase_context.model_copy(deep=True)

    def close(self) -> None:
        self.close_count += 1


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


def source_factory_for(
    observations: list[HeadTurnObservation],
    *,
    priming_source: TrackingAudioPrimingSource,
):
    def source_factory(**kwargs) -> FakeObservationSource:
        assert priming_source.started is True
        return FakeObservationSource(observations=observations)

    return source_factory


def run_with_observations(
    observations: list[HeadTurnObservation],
    *,
    priming_source: TrackingAudioPrimingSource,
) -> None:
    run_webcam_audio_priming_dry_run(
        phrase_context=create_phrase_context(),
        priming_source=priming_source,
        model_path="fake.task",
        max_frames=len(observations),
        source_factory=source_factory_for(
            observations,
            priming_source=priming_source,
        ),
    )


def test_head_right_finishes_audio_priming_logs_buffer_facts_and_enters_jam(capsys) -> None:
    priming_source = TrackingAudioPrimingSource(
        phrase_context=create_phrase_context(),
        audio_buffer=PrimingAudioBuffer(
            sample_rate=16_000,
            channels=2,
            frame_count=8_000,
            chunk_count=3,
        ),
    )

    run_with_observations(
        [emitted_observation(GestureType.HEAD_RIGHT)],
        priming_source=priming_source,
    )

    output = capsys.readouterr().out

    assert priming_source.started is True
    assert priming_source.finish_count == 1
    assert priming_source.close_count == 0
    assert "audio_capture: running" in output
    assert "Gesture Event: HEAD_RIGHT (confidence=1.00)" in output
    assert "Mapped Control Action: BRING_COMPANION_IN" in output
    assert "Priming Source: finishing" in output
    assert "Priming Source: finished" in output
    assert "Priming Audio Buffer" in output
    assert "duration_seconds: 0.5" in output
    assert "sample_rate: 16000" in output
    assert "channels: 2" in output
    assert "frame_count: 8000" in output
    assert "chunk_count: 3" in output
    assert "Snapshot after HEAD_RIGHT" in output
    assert "phase: jam_pass" in output
    assert "companion_status: active" in output
    assert "E7 | G5 | A" in output


def test_zero_chunk_audio_finish_is_visible_in_integrated_dry_run(capsys) -> None:
    priming_source = TrackingAudioPrimingSource(phrase_context=create_phrase_context())

    run_with_observations(
        [emitted_observation(GestureType.HEAD_RIGHT)],
        priming_source=priming_source,
    )

    output = capsys.readouterr().out

    assert priming_source.finish_count == 1
    assert "duration_seconds: 0.0" in output
    assert "sample_rate: 44100" in output
    assert "channels: 1" in output
    assert "frame_count: 0" in output
    assert "chunk_count: 0" in output


def test_head_left_after_audio_primed_jam_silences_companion(capsys) -> None:
    priming_source = TrackingAudioPrimingSource(phrase_context=create_phrase_context())

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


def test_unfinished_audio_priming_closes_if_webcam_source_setup_fails() -> None:
    priming_source = TrackingAudioPrimingSource(phrase_context=create_phrase_context())

    def failing_source_factory(**kwargs) -> None:
        raise GitairError("webcam unavailable")

    try:
        run_webcam_audio_priming_dry_run(
            phrase_context=create_phrase_context(),
            priming_source=priming_source,
            model_path="fake.task",
            max_frames=1,
            source_factory=failing_source_factory,
        )
    except GitairError as exc:
        assert str(exc) == "webcam unavailable"
    else:
        raise AssertionError("Expected webcam setup failure.")

    assert priming_source.started is True
    assert priming_source.finish_count == 0
    assert priming_source.close_count == 1


def test_session_core_stays_unaware_of_audio_sources_and_events() -> None:
    session_source = inspect.getsource(session_module)

    assert "sounddevice" not in session_source
    assert "AudioPrimingSource" not in session_source
    assert "AudioSource" not in session_source
    assert "gitair.priming" not in session_source
    assert "gitair.gestures" not in session_source
    assert "GestureEvent" not in session_source
