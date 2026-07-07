from __future__ import annotations

from collections.abc import Callable
from typing import Any, Protocol

from pydantic import ValidationError

from gitair.core.errors import (
    AudioSourceRuntimeError,
    AudioSourceSetupError,
    InvalidPrimingSourceTransition,
)
from gitair.core.phrase_context import PhraseContext
from gitair.priming.audio_buffer import PrimingAudioBuffer

DEFAULT_AUDIO_SAMPLE_RATE = 44_100
DEFAULT_AUDIO_CHANNELS = 1
DEFAULT_AUDIO_BLOCKSIZE = 1024


class AudioInputStream(Protocol):
    """Small stream surface used by the audio-backed priming source."""

    def start(self) -> None:
        """Start audio capture."""
        ...

    def stop(self) -> None:
        """Stop audio capture."""
        ...

    def close(self) -> None:
        """Release audio capture resources."""
        ...


AudioStreamFactory = Callable[..., AudioInputStream]


class AudioPrimingSource:
    """Lifecycle-bound priming source backed by temporary audio input capture."""

    def __init__(
        self,
        phrase_context: PhraseContext,
        *,
        sample_rate: int = DEFAULT_AUDIO_SAMPLE_RATE,
        channels: int = DEFAULT_AUDIO_CHANNELS,
        blocksize: int = DEFAULT_AUDIO_BLOCKSIZE,
        stream_factory: AudioStreamFactory | None = None,
    ) -> None:
        self._phrase_context = phrase_context
        self.sample_rate = _validate_positive_int("sample_rate", sample_rate)
        self.channels = _validate_positive_int("channels", channels)
        self.blocksize = _validate_positive_int("blocksize", blocksize)
        self._stream_factory = stream_factory or _create_sounddevice_input_stream
        self._stream: AudioInputStream | None = None
        self._started = False
        self._finished = False
        self._chunks: list[Any] = []
        self._frame_count = 0
        self._runtime_error: AudioSourceRuntimeError | None = None

    @property
    def audio_buffer(self) -> PrimingAudioBuffer:
        """Return observable facts for the temporary priming audio buffer."""
        try:
            return PrimingAudioBuffer(
                sample_rate=self.sample_rate,
                channels=self.channels,
                frame_count=self._frame_count,
                chunk_count=len(self._chunks),
            )
        except ValidationError as exc:
            raise AudioSourceRuntimeError("Captured audio buffer facts are invalid.") from exc

    def start(self) -> None:
        """Start audio capture for the priming pass."""
        if self._finished:
            raise InvalidPrimingSourceTransition("Cannot start finished priming source.")

        if self._started:
            raise InvalidPrimingSourceTransition("Cannot start priming source twice.")

        try:
            self._stream = self._stream_factory(
                samplerate=self.sample_rate,
                channels=self.channels,
                blocksize=self.blocksize,
                callback=self._capture_chunk,
            )
            self._stream.start()
        except AudioSourceSetupError:
            self._close_stream_after_setup_failure()
            raise
        except Exception as exc:
            self._close_stream_after_setup_failure()
            raise AudioSourceSetupError("Could not start audio input capture.") from exc

        self._started = True

    def finish(self) -> PhraseContext:
        """Stop audio capture and return the manually supplied phrase context."""
        if not self._started:
            raise InvalidPrimingSourceTransition(
                "Cannot finish priming source before it starts.",
            )

        if self._finished:
            raise InvalidPrimingSourceTransition("Cannot finish priming source twice.")

        self._finished = True
        runtime_error = self._runtime_error

        try:
            self._stop_and_close_stream()
        except AudioSourceRuntimeError as exc:
            runtime_error = runtime_error or exc

        if runtime_error is not None:
            raise runtime_error

        return self._phrase_context.model_copy(deep=True)

    def close(self) -> None:
        """Release audio capture resources without producing phrase context."""
        self._finished = True
        self._stop_and_close_stream()

    def _capture_chunk(
        self,
        indata: Any,
        frames: int,
        time_info: object,
        status: object,
    ) -> None:
        if self._runtime_error is not None:
            return

        if status:
            self._runtime_error = AudioSourceRuntimeError(
                f"Audio input reported runtime status: {status}",
            )
            return

        try:
            frame_count = _validate_frame_count(frames)
            self._chunks.append(_copy_audio_chunk(indata))
            self._frame_count += frame_count
        except AudioSourceRuntimeError as exc:
            self._runtime_error = exc
        except Exception:
            self._runtime_error = AudioSourceRuntimeError("Could not capture audio input chunk.")

    def _stop_and_close_stream(self) -> None:
        stream = self._stream
        self._stream = None
        if stream is None:
            return

        stop_error: AudioSourceRuntimeError | None = None
        try:
            stream.stop()
        except AudioSourceRuntimeError as exc:
            stop_error = exc
        except Exception as exc:
            stop_error = AudioSourceRuntimeError("Could not stop audio input capture.")
            stop_error.__cause__ = exc

        try:
            stream.close()
        except AudioSourceRuntimeError as exc:
            if stop_error is None:
                raise exc
        except Exception as exc:
            if stop_error is None:
                raise AudioSourceRuntimeError("Could not close audio input capture.") from exc

        if stop_error is not None:
            raise stop_error

    def _close_stream_after_setup_failure(self) -> None:
        stream = self._stream
        self._stream = None
        if stream is None:
            return

        close = getattr(stream, "close", None)
        if callable(close):
            try:
                close()
            except Exception:
                pass


def _create_sounddevice_input_stream(**kwargs: object) -> AudioInputStream:
    try:
        import sounddevice
    except ImportError as exc:  # pragma: no cover - dependency should be installed.
        raise AudioSourceSetupError("sounddevice is not installed.") from exc

    try:
        return sounddevice.InputStream(**kwargs)
    except Exception as exc:
        raise AudioSourceSetupError("Could not configure sounddevice input stream.") from exc


def _validate_positive_int(name: str, value: int) -> int:
    if not isinstance(value, int) or isinstance(value, bool) or value <= 0:
        raise AudioSourceSetupError(f"{name} must be a positive integer.")
    return value


def _validate_frame_count(frames: int) -> int:
    if not isinstance(frames, int) or isinstance(frames, bool) or frames < 0:
        raise AudioSourceRuntimeError("Audio input frame count must be a non-negative integer.")
    return frames


def _copy_audio_chunk(indata: Any) -> Any:
    copy = getattr(indata, "copy", None)
    if callable(copy):
        return copy()
    return indata
