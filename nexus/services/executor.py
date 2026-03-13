"""Service for executing tool commands.

Handles the subprocess execution logic for running external tools within the
terminal.
"""

import os
import shlex
import subprocess
from pathlib import Path


def launch_tool(
    command: str, project_path: Path | None = None, flags: str | None = None
) -> bool:
    """Launches a tool in the current terminal window.

    This function blocks execution until the tool completes. It replaces
    command placeholders and manages the working directory.

    Args:
        command: The shell command to execute.
        project_path: Optional working directory and project context.
        flags: Optional additional command-line arguments.

    Returns:
        True if the process started and exited with return code 0, False
        otherwise.
    """
    if not command:
        return False

    final_command = command
    if flags:
        if "{flags}" in final_command:
            final_command = final_command.replace("{flags}", flags)
        else:
            final_command = f"{final_command} {flags}"
    else:
        final_command = final_command.replace("{flags}", "")

    if project_path:
        if "{project}" in final_command:
            final_command = final_command.replace("{project}", str(project_path))
        elif "{flags}" not in command:
            final_command = f"{final_command} {project_path}"

    is_windows = os.name == "nt"
    try:
        cmd_parts = shlex.split(final_command, posix=not is_windows)
    except ValueError:
        cmd_parts = final_command.split()

    cwd = None
    if project_path and project_path.exists():
        cwd = project_path if project_path.is_dir() else project_path.parent

    try:
        result = subprocess.run(cmd_parts, cwd=cwd, check=False)
        return result.returncode == 0
    except (FileNotFoundError, OSError):
        return False
