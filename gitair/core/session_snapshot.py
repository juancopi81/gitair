from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field

from gitair.core.companion_state import CompanionState
from gitair.core.phrase_context import PhraseContext


class SessionPhase(str, Enum):
    """High-level phase of a Gitair session."""

    PRIMING_PASS = "priming_pass"
    JAM_PASS = "jam_pass"


class SessionSnapshot(BaseModel):
    """Serializable view of the current session state."""

    phase: SessionPhase = Field(
        default=SessionPhase.PRIMING_PASS,
        description="The current phase of the session.",
    )
    phrase_context: Optional[PhraseContext] = Field(
        default=None,
        description="The current phrase context of the session, if one has been received.",
    )
    companion_state: Optional[CompanionState] = Field(
        default=None,
        description="The current companion state, if the companion has entered the jam.",
    )
