from pydantic import BaseModel, Field


class PrimingAudioBuffer(BaseModel):
    """Metadata describing an audio buffer used for priming."""

    sample_rate: int = Field(
        ...,
        gt=0,
        description="Number of audio frames per second, e.g. 16000, 44100, or 48000.",
    )

    channels: int = Field(
        ...,
        gt=0,
        description="Number of audio channels. Usually 1 for mono or 2 for stereo.",
    )

    frame_count: int = Field(
        ...,
        ge=0,
        description="Total number of audio frames. Duration is `frame_count / sample_rate`.",
    )

    chunk_count: int = Field(
        ...,
        ge=0,
        description="Number of chunks the buffer is split into for streaming or processing.",
    )

    @property
    def duration_seconds(self) -> float:
        """Duration of the audio buffer in seconds."""
        return self.frame_count / self.sample_rate
