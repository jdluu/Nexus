import tomllib
import shutil
from pathlib import Path
from nexus.models import Tool

PROJECT_ROOT = Path("/home/jdluu/CS Stuff")

# Load tools from the adjacent tools.toml file
CONFIG_PATH = Path(__file__).parent / "tools.toml"

if CONFIG_PATH.exists():
    with open(CONFIG_PATH, "rb") as f:
        _data = tomllib.load(f)
        TOOLS = [Tool(**t) for t in _data.get("tool", [])]
else:
    TOOLS = []


CATEGORY_COLORS = {
    "DEV": "blue",
    "AI": "purple",
    "MEDIA": "green",
    "NET": "orange",
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
    
    terminals = ["ghostty", "gnome-terminal", "xterm"] # Defaults
    
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
        if shutil.which(term):
            return term
            
    return None

TERMINAL = get_preferred_terminal()