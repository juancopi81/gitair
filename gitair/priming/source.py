from typing import Protocol

from gitair.core.phrase_context import PhraseContext


class PrimingSource(Protocol):
    """A protocol for priming sources."""

    def start(self) -> None:
        """Start the priming source."""
        ...

    def finish(self) -> PhraseContext:
        """Finish the priming source and return the phrase context."""
        ...
