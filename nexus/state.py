"""State management for the Nexus application.

Handles persistence of user data including recent projects.
"""

import json
from pathlib import Path
from typing import Any, cast

import platformdirs
from nexus.logger import get_logger

log = get_logger(__name__)

# File path for the persistent application state.
STATE_FILE = Path(platformdirs.user_data_dir("nexus", roaming=True)) / "state.json"


class StateManager:
    """Manages the lifecycle and persistence of application state.

    Attributes:
        _state: A dictionary containing the current application state.
    """

    def __init__(self) -> None:
        """Initializes the StateManager and loads the state from disk."""
        self._state: dict[str, Any] = {
            "recents": [],
        }
        self._load()

    def _load(self) -> None:
        """Loads application state from the persistent storage file.

        Handles IO errors by logging the failure and maintaining the
        default state.
        """
        if STATE_FILE.exists():
            try:
                with open(STATE_FILE, "r") as f:
                    self._state.update(json.load(f))
            except Exception as e:
                log.error("load_state_failed", error=str(e))

    def _save(self) -> None:
        """Persists the current application state to disk atomically.

        Ensures the parent directory exists and performs an atomic write
        using a temporary file.
        """
        try:
            STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
            tmp_file = STATE_FILE.with_suffix(".tmp")
            with open(tmp_file, "w") as f:
                json.dump(self._state, f, indent=2)

            tmp_file.replace(STATE_FILE)
        except Exception as e:
            log.error("save_state_failed", error=str(e))

    def get_recents(self) -> list[str]:
        """Retrieves the list of recent project paths.

        Returns:
            A list of strings representing the absolute paths of
            recently accessed projects.
        """
        return cast(list[str], self._state.get("recents", []))

    def add_recent(self, path: str) -> None:
        """Adds a project path to the list of recently accessed projects.

        Args:
            path: The absolute path of the project to add.
        """
        recents = self.get_recents()
        if path in recents:
            recents.remove(path)
        recents.insert(0, path)
        self._state["recents"] = recents[:10]
        self._save()


_state_manager = StateManager()


def get_state_manager() -> StateManager:
    """Retrieves the global state manager instance.

    Returns:
        The singleton StateManager instance.
    """
    return _state_manager
