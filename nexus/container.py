"""Dependency Injection Container for Nexus.

Manages the lifecycle and resolution of core application services.
"""

from typing import Any
from nexus.state import get_state_manager, StateManager
from nexus.config import ConfigManager
from nexus.services import executor, scanner


class Container:
    """Service container for application wide dependencies."""

    def __init__(self) -> None:
        """Initializes the service container."""
        self._config_manager = ConfigManager()

    @property
    def config_manager(self) -> ConfigManager:
        """Provides access to the configuration management service.

        Returns:
            The ConfigManager service instance.
        """
        return self._config_manager

    @property
    def executor(self) -> Any:
        """Provides access to the tool execution service.

        Returns:
            The executor service module.
        """
        return executor

    @property
    def scanner(self) -> Any:
        """Provides access to the filesystem scanning service.

        Returns:
            The scanner service module.
        """
        return scanner

    @property
    def state_manager(self) -> StateManager:
        """Provides access to the application state manager.

        Returns:
            The StateManager service instance.
        """
        return get_state_manager()


_container = Container()


def get_container() -> Container:
    """Retrieves the global service container instance.

    Returns:
        The singleton Container instance.
    """
    return _container
