"""Domain-specific exceptions for Gitair core operations."""


class GitairError(ValueError):
    """Base class for Gitair domain validation errors."""


class InvalidSessionTransition(GitairError):
    """Raised when a control action is invalid for the current session state."""


class UnsupportedControlAction(GitairError):
    """Raised when a session receives a control action it does not support."""


class CompanionNotReady(GitairError):
    """Raised when a companion cannot respond from the supplied session state."""
