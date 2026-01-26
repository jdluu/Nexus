"""Dependency Injection Container for Nexus.

Manages the lifecycle and resolution of application services.
"""

from typing import Any
from nexus.state import get_state_manager, StateManager

from nexus.services import executor, scanner


class Container:
    """Simple service container."""

    def __init__(self) -> None:
        """Initialize the container."""
        # In a more complex app, we might use a proper DI library.
        # For now, simplistic service location is sufficient.
        pass

    @property
    def executor(self) -> Any:
        """Returns the executor service module."""
        # Currently the executor is a module with functions.
        # Future refactor could make it a class.
        return executor

    @property
    def scanner(self) -> Any:
        """Returns the scanner service module."""
        return scanner

    @property
    def state_manager(self) -> StateManager:
        """Returns the state manager service."""
        return get_state_manager()


# Global instance
_container = Container()


def get_container() -> Container:
    """Returns the global service container."""
    return _container
