from enum import Enum

from pydantic import BaseModel, Field


class ControlActionType(str, Enum):
    """Supported control actions for the session."""

    BRING_COMPANION_IN = "bring_companion_in"
    SILENCE_COMPANION = "silence_companion"
    INCREASE_INTENSITY = "increase_intensity"
    DECREASE_INTENSITY = "decrease_intensity"


class ControlAction(BaseModel):
    """A control action applied to the session."""

    action: ControlActionType = Field(
        default=ControlActionType.BRING_COMPANION_IN,
        description="The control action to apply to the session.",
    )
