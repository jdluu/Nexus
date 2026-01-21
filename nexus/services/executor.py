import subprocess
import shlex
from pathlib import Path
from nexus import config

def launch_tool(command: str, project_path: Path | None = None) -> bool:
    """Launches a tool in the configured terminal.

    Args:
        command: The shell command to execute.
        project_path: Optional path to a project directory to open the tool in.
            If provided, the terminal will open in this directory.

    Returns:
        True if the tool was successfully launched, False otherwise.
    """
    if not config.TERMINAL:
        return False

    full_command = command
    if project_path:
        # Construct command to cd into project path first
        full_command = f"cd {shlex.quote(str(project_path))} && {command}"
    
    # Keep the shell interactive at the end
    final_cmd_str = f"bash -c '{full_command}; exec bash'"
    
    launch_args = [config.TERMINAL]
    
    # Terminal-specific argument handling
    if "ghostty" in config.TERMINAL:
         launch_args.extend(["--new-tab", "-e", final_cmd_str])
    elif "gnome-terminal" in config.TERMINAL:
        launch_args.extend(["--", "bash", "-c", f"{full_command}; exec bash"])
    elif "kitty" in config.TERMINAL:
        launch_args.extend(["--detach", "-e", "bash", "-c", f"{full_command}; exec bash"])
    else:
        # Standard -e fallback (xterm, alacritty, etc)
        launch_args.extend(["-e", "bash", "-c", f"{full_command}; exec bash"])

    try:
        subprocess.Popen(launch_args)
        return True
    except (FileNotFoundError, OSError):
        return False
