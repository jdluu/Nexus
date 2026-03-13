"""Configuration management for the Nexus application.

Handles loading tool definitions from TOML, determining terminal preferences,
and defining visual assets like colors and icons.
"""

import os
import shutil
import tomllib
from pathlib import Path
from typing import Any

import platformdirs
from nexus.models import Tool

# Configuration paths in priority order (lowest to highest).
CWD_NEXUS_CONFIG = Path.cwd() / "nexus" / "tools.local.toml"
CWD_CONFIG = Path.cwd() / "tools.local.toml"
USER_CONFIG_PATH = (
    Path(platformdirs.user_config_dir("nexus", roaming=True)) / "tools.toml"
)
LOCAL_CONFIG_PATH = Path(__file__).parent / "tools.local.toml"
DEFAULT_CONFIG_PATH = Path(__file__).parent / "tools.toml"

CONFIG_PATHS = [
    DEFAULT_CONFIG_PATH,
    LOCAL_CONFIG_PATH,
    USER_CONFIG_PATH,
    CWD_NEXUS_CONFIG,
    CWD_CONFIG,
]


class ConfigManager:
    """Manages application configuration loading and caching.

    Provides methods to retrieve project root, tools, and keybindings
    from various configuration sources.
    """

    def __init__(self) -> None:
        """Initializes the ConfigManager with an empty cache."""
        self._config_cache: dict[str, Any] | None = None
        self.config_errors: list[str] = []

    def _load_config_data(self) -> dict[str, Any]:
        """Loads and merges configuration data from all identified sources.

        Returns:
            A dictionary containing the merged configuration data.
        """
        if self._config_cache is not None:
            return self._config_cache

        # Use a dict for tools to allow overrides by label
        merged_tools: dict[str, dict[str, Any]] = {}
        merged_data: dict[str, Any] = {
            "project_root": None,
            "keybindings": {},
            "light_theme": "tokyo-night-light",
            "dark_theme": "tokyo-night-dark",
        }

        def merge_from_file(path: Path) -> None:
            if path.exists():
                try:
                    with open(path, "rb") as f:
                        data = tomllib.load(f)

                        if "tool" in data and isinstance(data["tool"], list):
                            for tool_def in data["tool"]:
                                if isinstance(tool_def, dict) and "label" in tool_def:
                                    merged_tools[tool_def["label"]] = tool_def

                        if "project_root" in data and data["project_root"]:
                            merged_data["project_root"] = data["project_root"]

                        if "light_theme" in data:
                            merged_data["light_theme"] = data["light_theme"]

                        if "dark_theme" in data:
                            merged_data["dark_theme"] = data["dark_theme"]

                        if "keybindings" in data and isinstance(
                            data["keybindings"], dict
                        ):
                            merged_data["keybindings"].update(data["keybindings"])

                except (tomllib.TOMLDecodeError, PermissionError) as e:
                    self.config_errors.append(f"Error in {path.name}: {e}")
                except Exception as e:
                    self.config_errors.append(
                        f"Unexpected error reading {path.name}: {e}"
                    )

        for path in CONFIG_PATHS:
            merge_from_file(path)

        merged_data["tool"] = list(merged_tools.values())
        self._config_cache = merged_data
        return merged_data

    def get_project_root(self) -> Path:
        """Determines the project root directory based on configuration.

        Returns:
            The resolved project root path.
        """
        env_root = os.environ.get("NEXUS_PROJECT_ROOT")
        if env_root:
            return Path(env_root).expanduser()

        config = self._load_config_data()
        if config_root := config.get("project_root"):
            path_str = str(config_root)
            if path_str.startswith("~"):
                return Path(path_str).expanduser()
            return Path(path_str)

        return Path.home() / "Projects"

    def get_tools(self) -> list[Tool]:
        """Retrieves the list of configured tools.

        Returns:
            A list of validated Tool objects.
        """
        from pydantic import ValidationError

        tools = []
        config = self._load_config_data()
        for t in config.get("tool", []):
            try:
                tools.append(Tool(**t))
            except ValidationError as e:
                self.config_errors.append(f"Invalid tool definition (Validation): {e}")
            except Exception as e:
                self.config_errors.append(f"Invalid tool definition: {e}")
                continue
        return tools

    def get_keybindings(self) -> dict[str, str]:
        """Retrieves the keybinding configuration.

        Returns:
            A dictionary mapping action names to key sequences.
        """
        defaults = {
            "quit": "q",
            "force_quit": "ctrl+c",
            "back": "escape",
            "theme": "ctrl+t",
            "help": "?",
            "fuzzy_search": "ctrl+f",
        }

        config = self._load_config_data()
        user_bindings = config.get("keybindings", {})
        return {**defaults, **user_bindings}

    def get_theme_pair(self) -> tuple[str, str]:
        """Retrieves the preferred light and dark theme names.

        Returns:
            A tuple of (light_theme_name, dark_theme_name).
        """
        config = self._load_config_data()
        return (
            config.get("light_theme", "tokyo-night-light"),
            config.get("dark_theme", "tokyo-night-dark"),
        )


# Visual constants.
USE_NERD_FONTS = True


def get_preferred_terminal() -> str | None:
    """Identifies the available terminal emulator based on priority.

    Consults the pyproject.toml configuration and falls back to a
    standard priority list to find a supported terminal executable.

    Returns:
        The executable path for the preferred terminal, or None if not found.
    """
    pyproject_path = Path(__file__).parent.parent / "pyproject.toml"
    terminals = ["kitty", "ghostty", "gnome-terminal", "xterm"]

    if pyproject_path.exists():
        try:
            with open(pyproject_path, "rb") as f:
                data = tomllib.load(f)
                config_terminals = (
                    data.get("tool", {}).get("nexus", {}).get("priority_terminals")
                )
                if config_terminals:
                    terminals = config_terminals
        except Exception:
            pass

    for term in terminals:
        path = shutil.which(term)
        if path:
            return path

    return None
