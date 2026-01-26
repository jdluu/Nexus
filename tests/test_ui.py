"""UI tests for the Nexus application screens."""

import pytest
from nexus.app import NexusApp
from nexus.screens.help import HelpScreen
from nexus.screens.tool_selector import ToolSelector


from textual.widgets import ListView

@pytest.mark.asyncio
async def test_app_startup_and_help() -> None:
    """Test that the app starts up and help screen can be toggled."""
    app = NexusApp()
    async with app.run_test() as pilot:
        # Check initial screen
        assert isinstance(app.screen, ToolSelector)

        # Press '?' to show help
        await pilot.press("?")
        assert isinstance(app.screen, HelpScreen)

        # Press 'escape' to dismiss
        await pilot.press("escape")
        assert isinstance(app.screen, ToolSelector)


@pytest.mark.asyncio
async def test_navigation() -> None:
    """Test basic navigation in the tool selector."""
    app = NexusApp()
    async with app.run_test() as pilot:
        await pilot.pause()
        screen = app.screen
        assert isinstance(screen, ToolSelector)

        # Initial focus should be on category list
        category_list = screen.query_one("#category-list", ListView)
        assert category_list.has_focus

        # Move down
        start_index = category_list.index or 0
        await pilot.press("down")
        # Assert index changed (if there are items)
        if len(category_list.children) > 1:
            assert category_list.index == start_index + 1

        # Move right to tools
        await pilot.press("right")
        tool_list = screen.query_one("#tool-list", ListView)
        assert tool_list.has_focus


@pytest.mark.asyncio
async def test_numeric_launch() -> None:
    """Test that numeric keys launch the corresponding tool."""
    from unittest.mock import patch
    app = NexusApp()
    async with app.run_test() as pilot:
        # Mock the launch function to avoid actual command execution
        with patch("nexus.screens.tool_selector.ToolSelector.launch_tool_flow") as mock_launch:
            # Press '1'
            await pilot.press("1")
            mock_launch.assert_called_once()
            
            # Press '2'
            await pilot.press("2")
            assert mock_launch.call_count == 2

# Summary:
# Added module docstring.
# Cleaned up imports.
