from enum import Enum

from pydantic import BaseModel, Field


class ControlActionType(str, Enum):
    """Supported control actions for the session."""

    START_JAM_PASS = "start_jam_pass"


class ControlAction(BaseModel):
    """A control action applied to the session."""

    action: ControlActionType = Field(
        default=ControlActionType.START_JAM_PASS,
        description="The control action to apply to the session.",
    )
