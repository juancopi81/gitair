"""Domain-specific exceptions for Gitair core operations."""


class GitairError(ValueError):
    """Base class for Gitair domain validation errors."""


class InvalidSessionTransition(GitairError):
    """Raised when a control action is invalid for the current session state."""


class UnsupportedControlAction(GitairError):
    """Raised when a session receives a control action it does not support."""


class CompanionNotReady(GitairError):
    """Raised when a companion cannot respond from the supplied session state."""


class UnsupportedGestureEvent(GitairError):
    """Raised when a gesture source emits an unsupported gesture event."""


class UnmappedGestureEvent(GitairError):
    """Raised when a gesture event has no control action mapping."""


class InvalidGestureSourceConfiguration(GitairError):
    """Raised when a gesture source is configured with invalid settings."""


class InvalidGestureSourceInput(GitairError):
    """Raised when a gesture source receives invalid input data."""
