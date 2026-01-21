import pytest
from unittest.mock import patch
from nexus.services import executor
from nexus import config

def test_launch_tool_success():
    """Test successful tool launch with a mocked terminal."""
    with patch("subprocess.Popen") as mock_popen:
        with patch.object(config, "TERMINAL", "xterm"):
            result = executor.launch_tool("echo hello")
            assert result is True
            mock_popen.assert_called_once()
            args = mock_popen.call_args[0][0]
            assert args[0] == "xterm"
            assert "-e" in args

def test_launch_tool_failure():
    """Test tool launch failure handling."""
    with patch("subprocess.Popen", side_effect=FileNotFoundError):
        with patch.object(config, "TERMINAL", "xterm"):
            result = executor.launch_tool("echo hello")
            assert result is False

def test_launch_tool_no_terminal():
    """Test launch fails gracefully if no terminal is configured."""
    with patch.object(config, "TERMINAL", None):
        result = executor.launch_tool("echo hello")
        assert result is False

def test_terminal_detection_ordering():
    """Test that detection respects priority order."""
    # We patch detection to simulate environment where only xterm is available
    with patch("shutil.which") as mock_which:
        def side_effect(arg):
            return arg == "xterm"
        mock_which.side_effect = side_effect
        
        # We also need to patch the list of terminals to be deterministic or rely on defaults
        # calling the function directly
        term = config.get_preferred_terminal()
        assert term == "xterm"
