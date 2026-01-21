import subprocess
import shlex
import shutil
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
    full_command = command
    if project_path:
        # Construct command to cd into project path first
        full_command = f"cd {shlex.quote(str(project_path))} && {command}"
    
    try:
        # Run synchronously in the current terminal (in-place)
        # shell=True allows using features like '&&' and environment variable expansion
        subprocess.run(full_command, shell=True, check=False)
        return True
    except Exception:
        return False
