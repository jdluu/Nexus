"""Tests for the service layer modules.

This module provides unit tests for the executor and configuration services.
"""

from unittest.mock import patch
from pathlib import Path
from nexus import config
from nexus.services import executor


def test_launch_tool_success() -> None:
    """Verifies that a tool is launched successfully.

    Asserts that the subprocess is called with the correctly parsed command.
    """
    with patch("subprocess.run") as mock_run:
        mock_run.return_value.returncode = 0

        result = executor.launch_tool("echo hello")
        assert result is True
        mock_run.assert_called_once()
        args = mock_run.call_args[0][0]
        assert args == ["echo", "hello"]


def test_launch_tool_with_path() -> None:
    """Verifies that a tool is launched with a specified project path.

    Asserts that the project path is correctly appended to the command.
    """
    with patch("subprocess.run") as mock_run:
        mock_run.return_value.returncode = 0

        project_path = Path("/tmp/test_project")
        with patch.object(Path, "exists", return_value=True):
            result = executor.launch_tool("nvim", project_path)

        assert result is True
        mock_run.assert_called_once()
        args = mock_run.call_args[0][0]
        assert args == ["nvim", str(project_path)]


def test_terminal_detection_ordering() -> None:
    """Verifies that terminal detection respects the priority configuration.

    Asserts that the first available terminal in the priority list is returned.
    """
    with patch("shutil.which") as mock_which:

        def side_effect(arg: str) -> str | None:
            if arg == "gnome-terminal":
                return "/usr/bin/gnome-terminal"
            return None

        mock_which.side_effect = side_effect

        term = config.get_preferred_terminal()
        assert term == "/usr/bin/gnome-terminal"


def test_launch_tool_with_flags_and_placeholders() -> None:
    """Verifies that launch_tool correctly replaces {flags} and {project}."""
    with patch("subprocess.run") as mock_run:
        mock_run.return_value.returncode = 0
        project_path = Path("/my/project")

        # Test replace both
        executor.launch_tool("nvim {flags} {project}", project_path, "--clean")
        mock_run.assert_called_with(
            ["nvim", "--clean", "/my/project"], cwd=None, check=False
        )

        # Test flags appending
        executor.launch_tool("ls", None, "-la")
        mock_run.assert_called_with(["ls", "-la"], cwd=None, check=False)


def test_launch_tool_empty_command() -> None:
    assert executor.launch_tool("") is False


def test_launch_tool_shlex_value_error() -> None:
    with patch("subprocess.run") as mock_run:
        mock_run.return_value.returncode = 0
        executor.launch_tool('echo "unclosed quote')
        mock_run.assert_called_with(
            ["echo", '"unclosed', "quote"], cwd=None, check=False
        )


def test_launch_tool_file_not_found() -> None:
    with patch("subprocess.run", side_effect=FileNotFoundError):
        assert executor.launch_tool("doesnotexist") is False
