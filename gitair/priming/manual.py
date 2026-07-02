from gitair.core.errors import InvalidPrimingSourceTransition
from gitair.core.phrase_context import PhraseContext


class ManualPrimingSource:
    """Lifecycle-bound priming source backed by manually supplied context."""

    def __init__(self, phrase_context: PhraseContext) -> None:
        self._phrase_context = phrase_context
        self._started = False
        self._finished = False

    def start(self) -> None:
        """Start the priming source."""
        if self._finished:
            raise InvalidPrimingSourceTransition("Cannot start finished priming source.")

        if self._started:
            raise InvalidPrimingSourceTransition("Cannot start priming source twice.")

        self._started = True

    def finish(self) -> PhraseContext:
        """Finish priming and return the manually supplied phrase context."""
        if not self._started:
            raise InvalidPrimingSourceTransition(
                "Cannot finish priming source before it starts.",
            )

        if self._finished:
            raise InvalidPrimingSourceTransition("Cannot finish priming source twice.")

        self._finished = True
        return self._phrase_context.model_copy(deep=True)
