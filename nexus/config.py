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

# Configuration Paths in priority order (lowest to highest)
CWD_NEXUS_CONFIG = Path.cwd() / "nexus" / "tools.local.toml"
CWD_CONFIG = Path.cwd() / "tools.local.toml"
USER_CONFIG_PATH = Path(platformdirs.user_config_dir("nexus", roaming=True)) / "tools.toml"
LOCAL_CONFIG_PATH = Path(__file__).parent / "tools.local.toml"
DEFAULT_CONFIG_PATH = Path(__file__).parent / "tools.toml"

CONFIG_PATHS = [
    DEFAULT_CONFIG_PATH,
    LOCAL_CONFIG_PATH,
    USER_CONFIG_PATH,
    CWD_NEXUS_CONFIG,
    CWD_CONFIG,
]


# Global error tracking for configuration loading
CONFIG_ERRORS: list[str] = []
_CONFIG_CACHE: dict[str, Any] | None = None


def _load_config_data() -> dict[str, Any]:
    """Loads and merges configuration data from all sources (Lazy).

    Iterates through configuration paths in priority order and merges meaningful
    data (tools, project root) into a single dictionary.

    Returns:
        A dictionary containing the merged configuration data.
    """
    global _CONFIG_CACHE
    if _CONFIG_CACHE is not None:
        return _CONFIG_CACHE

    merged_data: dict[str, Any] = {"tool": [], "project_root": None}

    def merge_from_file(path: Path) -> None:
        if path.exists():
            try:
                with open(path, "rb") as f:
                    data = tomllib.load(f)

                    # Replacement strategy: If a config file defines tools,
                    # it replaces the set of tools from lower-priority configs.
                    if "tool" in data and data["tool"]:
                        merged_data["tool"] = data["tool"]

                    if "project_root" in data:
                        merged_data["project_root"] = data["project_root"]

            except (tomllib.TOMLDecodeError, PermissionError) as e:
                CONFIG_ERRORS.append(f"Error in {path.name}: {e}")
            except Exception as e:
                # Catch-all for other unexpected IO errors
                CONFIG_ERRORS.append(f"Unexpected error reading {path.name}: {e}")

    for path in CONFIG_PATHS:
        merge_from_file(path)

    _CONFIG_CACHE = merged_data
    return merged_data


def get_project_root() -> Path:
    """Returns the project root directory.

    Priority:
    1. NEXUS_PROJECT_ROOT environment variable
    2. 'project_root' in configuration files
    3. Default: ~/Projects

    Returns:
        The defined project root path.
    """
    # 1. Environment Variable
    env_root = os.environ.get("NEXUS_PROJECT_ROOT")
    if env_root:
        return Path(env_root).expanduser()

    # 2. Configuration File
    config = _load_config_data()
    if config_root := config.get("project_root"):
        path_str = str(config_root)
        if path_str.startswith("~"):
            return Path(path_str).expanduser()
        return Path(path_str)

    # 3. Default
    return Path.home() / "Projects"


def get_tools() -> list[Tool]:
    """Returns the list of configured tools.

    Parses the configuration data into Tool models, skipping any invalid entries.

    Returns:
        A list of Tool objects.
    """
    from pydantic import ValidationError

    tools = []
    config = _load_config_data()
    for t in config.get("tool", []):
        try:
            tools.append(Tool(**t))
        except ValidationError as e:
            # Pydantic validation error
            CONFIG_ERRORS.append(f"Invalid tool definition (Validation): {e}")
        except Exception as e:
            CONFIG_ERRORS.append(f"Invalid tool definition: {e}")
            continue
    return tools


def get_keybindings() -> dict[str, str]:
    """Returns the keybinding configuration.

    Merges default bindings with user overrides from configuration files.

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
        "toggle_favorite": "f",
    }

    config = _load_config_data()
    user_bindings = config.get("keybindings", {})
    
    # Merge defaults with user bindings
    return {**defaults, **user_bindings}


CATEGORY_COLORS = {
    "DEV": "blue",
    "AI": "purple",
    "MEDIA": "green",
    "UTIL": "orange",
}

USE_NERD_FONTS = True

CATEGORY_ICONS = {
    "DEV": "",  # fh-fa-code_fork
    "AI": "",  # fh-fa-microchip
    "MEDIA": "",  # fh-fa-video_camera
    "UTIL": "",  # fh-fa-wrench
    "ALL": "",  # fh-fa-list
}


def get_preferred_terminal() -> str | None:
    """Determines the available terminal emulator based on a priority list.

    Checks `pyproject.toml` for [tool.nexus.priority_terminals] and falls back
    to a default list if configuration is missing.

    Returns:
        The command string for the first found terminal, or None if no supported
        terminal is found.
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
