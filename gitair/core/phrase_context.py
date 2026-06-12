from pydantic import BaseModel, Field


class PhraseContext(BaseModel):
    """Musical context captured or provided during the priming pass."""

    chords: list[str] = Field(
        default_factory=list,
        description="The chord progression or chord labels associated with the phrase.",
    )
    tempo_bpm: float = Field(
        default=120.0,
        description="The estimated or provided tempo in beats per minute.",
    )
    style_description: str = Field(
        default="",
        description="A short text description of the phrase's musical style.",
    )
    prompt_summary: str = Field(
        default="",
        description="A short prompt summary derived from the phrase, used to steer the companion.",
    )
