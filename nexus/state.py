"""State management for Nexus.

Handles persistence of user data such as recent projects and favorite tools.
"""

import json
from pathlib import Path
from typing import Any, cast

import platformdirs
from nexus.logger import get_logger

log = get_logger(__name__)

STATE_FILE = Path(platformdirs.user_data_dir("nexus", roaming=True)) / "state.json"


class StateManager:
    """Manages persistent application state."""

    def __init__(self) -> None:
        """Initialize the state manager."""
        self._state: dict[str, Any] = {
            "recents": [],
            "favorites": [],
        }
        self._load()

    def _load(self) -> None:
        """Loads state from disk."""
        if STATE_FILE.exists():
            try:
                with open(STATE_FILE, "r") as f:
                    self._state.update(json.load(f))
            except Exception as e:
                log.error("load_state_failed", error=str(e))

    def _save(self) -> None:
        """Saves state to disk (atomic)."""
        try:
            STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
            tmp_file = STATE_FILE.with_suffix(".tmp")
            with open(tmp_file, "w") as f:
                json.dump(self._state, f, indent=2)
            
            # Atomic replace
            tmp_file.replace(STATE_FILE)
        except Exception as e:
            log.error("save_state_failed", error=str(e))

    def get_recents(self) -> list[str]:
        """Returns the list of recent project paths."""
        return cast(list[str], self._state.get("recents", []))

    def add_recent(self, path: str) -> None:
        """Adds a path to recent projects."""
        recents = self.get_recents()
        if path in recents:
            recents.remove(path)
        recents.insert(0, path)
        self._state["recents"] = recents[:10]  # Keep last 10
        self._save()

    def get_favorites(self) -> list[str]:
        """Returns the list of favorite tool IDs/labels."""
        return cast(list[str], self._state.get("favorites", []))

    def toggle_favorite(self, tool_id: str) -> None:
        """Toggles a tool as favorite."""
        favorites = self.get_favorites()
        if tool_id in favorites:
            favorites.remove(tool_id)
        else:
            favorites.append(tool_id)
        self._state["favorites"] = favorites
        self._save()

    def is_favorite(self, tool_id: str) -> bool:
        """Checks if a tool is a favorite."""
        return tool_id in self.get_favorites()


# Global instance
_state_manager = StateManager()

def get_state_manager() -> StateManager:
    """Returns the global state manager."""
    return _state_manager
