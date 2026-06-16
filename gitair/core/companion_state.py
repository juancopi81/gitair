from enum import Enum

from pydantic import BaseModel, Field


class CompanionStatus(str, Enum):
    """Whether the companion should currently contribute to the jam."""

    ACTIVE = "active"
    SILENT = "silent"


class CompanionState(BaseModel):
    """Performer-facing companion state carried in session snapshots."""

    status: CompanionStatus = Field(
        default=CompanionStatus.ACTIVE,
        description="Whether the companion is active or silent.",
    )
    intensity: int = Field(
        default=3,
        ge=1,
        le=5,
        description="Discrete target intensity from 1 to 5.",
    )
