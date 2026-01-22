"""Service for executing tool commands.

Handles the subprocess execution logic for running external tools within the terminal.
"""

import shlex
import subprocess
from pathlib import Path


def launch_tool(command: str, project_path: Path | None = None) -> bool:
    """Launches a tool in the current terminal window.

    This function blocks execution until the tool completes. It should typically
    be called within a suspended TUI context.

    Args:
        command: The shell command to execute.
        project_path: Optional working directory for the command.
            if provided, the command path is appended to the command arguments,
            and the command is executed in this directory.

    Returns:
        True if the process started and exited with return code 0, False otherwise.
    """
    if not command:
        return False

    cmd_parts = shlex.split(command)

    if project_path:
        cmd_parts.append(str(project_path))

    cwd = project_path if project_path and project_path.exists() else None

    try:
        # Run tool in the current terminal (blocking execution).
        # This allows the tool to take over the TUI's terminal IO.
        result = subprocess.run(cmd_parts, cwd=cwd, check=False)
        return result.returncode == 0
    except (FileNotFoundError, OSError):
        return False

# Summary:
# Added module docstring.
# Expanded function docstring with context about blocking behavior.
