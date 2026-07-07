import pytest

from gitair.core.errors import (
    AudioSourceRuntimeError,
    AudioSourceSetupError,
    GitairError,
    InvalidPrimingSourceTransition,
)
from gitair.core.phrase_context import PhraseContext
from gitair.priming.audio import AudioPrimingSource


class RawAudioError(Exception):
    pass


class GeneratedAudioChunk:
    def __init__(self, frames: int) -> None:
        self.frames = frames

    def copy(self) -> "GeneratedAudioChunk":
        return GeneratedAudioChunk(frames=self.frames)


class FakeAudioStream:
    def __init__(
        self,
        *,
        callback,
        chunks: list[tuple[GeneratedAudioChunk, int]],
        status: object = None,
        start_error: Exception | None = None,
        stop_error: Exception | None = None,
        close_error: Exception | None = None,
    ) -> None:
        self._callback = callback
        self._chunks = chunks
        self._status = status
        self._start_error = start_error
        self._stop_error = stop_error
        self._close_error = close_error
        self.started = False
        self.stopped = False
        self.closed = False

    def start(self) -> None:
        if self._start_error is not None:
            raise self._start_error

        self.started = True
        for chunk, frames in self._chunks:
            self._callback(chunk, frames, None, self._status)

    def stop(self) -> None:
        if self._stop_error is not None:
            raise self._stop_error
        self.stopped = True

    def close(self) -> None:
        if self._close_error is not None:
            raise self._close_error
        self.closed = True


class FakeAudioStreamFactory:
    def __init__(
        self,
        *,
        chunks: list[tuple[GeneratedAudioChunk, int]] | None = None,
        status: object = None,
        setup_error: Exception | None = None,
        start_error: Exception | None = None,
        stop_error: Exception | None = None,
        close_error: Exception | None = None,
    ) -> None:
        self._chunks = chunks or []
        self._status = status
        self._setup_error = setup_error
        self._start_error = start_error
        self._stop_error = stop_error
        self._close_error = close_error
        self.stream: FakeAudioStream | None = None
        self.kwargs = {}

    def __call__(self, **kwargs) -> FakeAudioStream:
        self.kwargs = kwargs
        if self._setup_error is not None:
            raise self._setup_error

        self.stream = FakeAudioStream(
            callback=kwargs["callback"],
            chunks=self._chunks,
            status=self._status,
            start_error=self._start_error,
            stop_error=self._stop_error,
            close_error=self._close_error,
        )
        return self.stream


def create_phrase_context() -> PhraseContext:
    return PhraseContext(
        chords=["E7", "G5", "A"],
        tempo_bpm=120.0,
        style_description="raw rock",
        prompt_summary="short riff",
    )


def test_audio_priming_source_allows_zero_chunk_finish_with_visible_buffer_facts() -> None:
    phrase_context = create_phrase_context()
    stream_factory = FakeAudioStreamFactory()
    source = AudioPrimingSource(
        phrase_context=phrase_context,
        sample_rate=16_000,
        channels=2,
        blocksize=512,
        stream_factory=stream_factory,
    )

    source.start()
    finished_context = source.finish()
    buffer = source.audio_buffer

    assert finished_context == phrase_context
    assert finished_context is not phrase_context
    assert buffer.sample_rate == 16_000
    assert buffer.channels == 2
    assert buffer.frame_count == 0
    assert buffer.chunk_count == 0
    assert buffer.duration_seconds == 0.0
    assert stream_factory.kwargs["samplerate"] == 16_000
    assert stream_factory.kwargs["channels"] == 2
    assert stream_factory.kwargs["blocksize"] == 512
    assert stream_factory.stream is not None
    assert stream_factory.stream.started is True
    assert stream_factory.stream.stopped is True
    assert stream_factory.stream.closed is True


def test_audio_priming_source_tracks_generated_chunks_in_memory() -> None:
    stream_factory = FakeAudioStreamFactory(
        chunks=[
            (GeneratedAudioChunk(frames=128), 128),
            (GeneratedAudioChunk(frames=256), 256),
        ],
    )
    source = AudioPrimingSource(
        phrase_context=create_phrase_context(),
        sample_rate=8_000,
        channels=1,
        stream_factory=stream_factory,
    )

    source.start()
    source.finish()
    buffer = source.audio_buffer

    assert buffer.sample_rate == 8_000
    assert buffer.channels == 1
    assert buffer.frame_count == 384
    assert buffer.chunk_count == 2
    assert buffer.duration_seconds == pytest.approx(0.048)


def test_audio_priming_source_wraps_setup_failures() -> None:
    source = AudioPrimingSource(
        phrase_context=create_phrase_context(),
        stream_factory=FakeAudioStreamFactory(setup_error=RawAudioError("raw setup failed")),
    )

    with pytest.raises(AudioSourceSetupError, match="start audio input capture") as exc_info:
        source.start()

    assert isinstance(exc_info.value, GitairError)
    assert not isinstance(exc_info.value, RawAudioError)


def test_audio_priming_source_wraps_close_failures() -> None:
    source = AudioPrimingSource(
        phrase_context=create_phrase_context(),
        stream_factory=FakeAudioStreamFactory(close_error=RawAudioError("raw close failed")),
    )

    source.start()
    with pytest.raises(AudioSourceRuntimeError, match="close audio input capture") as exc_info:
        source.finish()

    assert isinstance(exc_info.value, GitairError)
    assert not isinstance(exc_info.value, RawAudioError)


def test_audio_priming_source_close_releases_without_phrase_context() -> None:
    stream_factory = FakeAudioStreamFactory()
    source = AudioPrimingSource(
        phrase_context=create_phrase_context(),
        stream_factory=stream_factory,
    )

    source.start()
    result = source.close()

    assert result is None
    assert stream_factory.stream is not None
    assert stream_factory.stream.stopped is True
    assert stream_factory.stream.closed is True
    with pytest.raises(InvalidPrimingSourceTransition, match="finish priming source twice"):
        source.finish()


def test_audio_priming_source_wraps_runtime_status_failures() -> None:
    source = AudioPrimingSource(
        phrase_context=create_phrase_context(),
        stream_factory=FakeAudioStreamFactory(
            chunks=[(GeneratedAudioChunk(frames=128), 128)],
            status="input overflow",
        ),
    )

    source.start()
    with pytest.raises(AudioSourceRuntimeError, match="input overflow") as exc_info:
        source.finish()

    assert isinstance(exc_info.value, GitairError)
    assert not isinstance(exc_info.value, RawAudioError)


def test_audio_priming_source_wraps_stop_failures() -> None:
    stream_factory = FakeAudioStreamFactory(stop_error=RawAudioError("raw stop failed"))
    source = AudioPrimingSource(
        phrase_context=create_phrase_context(),
        stream_factory=stream_factory,
    )

    source.start()
    with pytest.raises(AudioSourceRuntimeError, match="stop audio input capture") as exc_info:
        source.finish()

    assert isinstance(exc_info.value, GitairError)
    assert not isinstance(exc_info.value, RawAudioError)
    assert stream_factory.stream is not None
    assert stream_factory.stream.closed is True


def test_audio_priming_source_invalid_lifecycle_fails_clearly() -> None:
    source = AudioPrimingSource(
        phrase_context=create_phrase_context(),
        stream_factory=FakeAudioStreamFactory(),
    )

    with pytest.raises(InvalidPrimingSourceTransition, match="before it starts"):
        source.finish()

    source.start()
    with pytest.raises(InvalidPrimingSourceTransition, match="start priming source twice"):
        source.start()

    source.finish()
    with pytest.raises(InvalidPrimingSourceTransition, match="finish priming source twice"):
        source.finish()
