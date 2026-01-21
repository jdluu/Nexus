import tomllib
import shutil
from pathlib import Path
from nexus.models import Tool

"""Configuration management for the Nexus application.

Handles loading tool definitions from TOML, determining terminal preferences,
and defining visual assets like colors and icons.
"""

PROJECT_ROOT = Path("/home/jdluu/CS Stuff")

# Config Paths (Priority Order)
USER_CONFIG_PATH = Path.home() / ".config" / "nexus" / "tools.toml"
LOCAL_CONFIG_PATH = Path(__file__).parent / "tools.local.toml"
DEFAULT_CONFIG_PATH = Path(__file__).parent / "tools.toml"

def load_tools() -> list[Tool]:
    """Loads and merges tools from multiple config sources.
    
    Priority (Higher overrides Lower):
    1. User Global (~/.config/nexus/tools.toml)
    2. Repo Local (nexus/tools.local.toml)
    3. Default (nexus/tools.toml)
    """
    tools_map = {}
    
    # helper to load and merge
    def merge_from_file(path: Path):
        if path.exists():
            try:
                with open(path, "rb") as f:
                    data = tomllib.load(f)
                    for t in data.get("tool", []):
                        # Use label as key for merging/overriding
                        tool = Tool(**t)
                        tools_map[tool.label] = tool
            except Exception:
                pass

    # Load in reverse priority order (Default -> Local -> Global)
    # This way, later loads overwrite earlier ones in the map
    merge_from_file(DEFAULT_CONFIG_PATH)
    merge_from_file(LOCAL_CONFIG_PATH)
    merge_from_file(USER_CONFIG_PATH)
    
    return list(tools_map.values())

TOOLS = load_tools()


CATEGORY_COLORS = {
    "DEV": "blue",
    "AI": "purple",
    "MEDIA": "green",
    "UTIL": "orange",
}

USE_NERD_FONTS = True

CATEGORY_ICONS = {
    "DEV": "",   # fh-fa-code_fork
    "AI": "",    # fh-fa-microchip (or similar brain/chip icon)
    "MEDIA": "", # fh-fa-video_camera
    "UTIL": "",  # fh-fa-wrench
    "ALL": "",   # fh-fa-list
}

def get_preferred_terminal() -> str | None:
    """Determines the available terminal emulator based on priority list.

    Checks `pyproject.toml` [tool.nexus.priority_terminals] and falls back to
    a default list if configuration is missing.

    Returns:
        The command string for the first found terminal, or None if no supported
        terminal is found.
    """
    pyproject_path = Path(__file__).parent.parent / "pyproject.toml"
    
    terminals = ["kitty", "ghostty", "gnome-terminal", "xterm"] # Defaults
    
    if pyproject_path.exists():
        try:
            with open(pyproject_path, "rb") as f:
                data = tomllib.load(f)
                config_terminals = data.get("tool", {}).get("nexus", {}).get("priority_terminals")
                if config_terminals:
                    terminals = config_terminals
        except Exception:
            pass # Fallback to defaults on error
            
    for term in terminals:
        path = shutil.which(term)
        if path:
            return path
            
    return None

TERMINAL = get_preferred_terminal()