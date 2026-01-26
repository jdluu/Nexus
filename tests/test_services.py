"""Tests for the service layer modules."""

from unittest.mock import patch

from nexus import config
from nexus.services import executor


def test_launch_tool_success() -> None:
    """Test successful tool launch with in-place execution."""
    # Mocking subprocess.run to return a CompletedProcess with returncode 0
    with patch("subprocess.run") as mock_run:
        mock_run.return_value.returncode = 0

        result = executor.launch_tool("echo hello")
        assert result is True
        mock_run.assert_called_once()
        args = mock_run.call_args[0][0]
        # Should be split command
        assert args == ["echo", "hello"]


def test_launch_tool_with_path() -> None:
    """Test tool launch with a project path."""
    from pathlib import Path

    with patch("subprocess.run") as mock_run:
        mock_run.return_value.returncode = 0

        project_path = Path("/tmp/test_project")
        # We must mock exists() to return True for the logic to work
        with patch.object(Path, "exists", return_value=True):
            result = executor.launch_tool("nvim", project_path)

        assert result is True
        mock_run.assert_called_once()
        args = mock_run.call_args[0][0]
        # Expect: ['nvim', '/tmp/test_project']
        assert args == ["nvim", str(project_path)]


def test_terminal_detection_ordering() -> None:
    """Test that detection respects priority list."""
    # Mock shutil.which to only find 'gnome-terminal'
    with patch("shutil.which") as mock_which:

        def side_effect(arg: str) -> str | None:
            if arg == "gnome-terminal":
                return "/usr/bin/gnome-terminal"
            return None

        mock_which.side_effect = side_effect

        # We need to test the function directly
        term = config.get_preferred_terminal()
        assert term == "/usr/bin/gnome-terminal"

# Summary:
# Added module docstring.
# Kept concise test comments.
