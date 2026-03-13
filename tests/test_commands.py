"""Tests for the command palette providers."""

import pytest
from typing import Any
from unittest.mock import patch, MagicMock
from textual.app import App
from textual.screen import Screen
from nexus.commands import ToolCommandProvider
from nexus.models import Tool

@pytest.fixture
def mock_tools() -> list[Tool]:
    return [
        Tool(
            label="Fast Search",
            category="UTIL",
            description="Finds things quickly",
            command="find .",
            requires_project=False,
            supports_flags=True
        ),
        Tool(
            label="Deploy App",
            category="DEV",
            description="Deploys the application",
            command="deploy",
            requires_project=True,
            supports_flags=False
        )
    ]

@pytest.mark.asyncio
async def test_discover_commands(mock_tools: list[Tool]) -> None:
    with patch("nexus.container.get_container") as mock_get_container:
        mock_get_container.return_value.config_manager.get_tools.return_value = mock_tools
        
        provider = ToolCommandProvider(Screen())
        hits = [hit async for hit in provider.discover()]
        
        assert len(hits) == 2
        assert hits[0].text == "Fast Search"
        assert hits[0].help == "Finds things quickly"
        assert hits[1].text == "Deploy App"

@pytest.mark.asyncio
async def test_search_commands(mock_tools: list[Tool]) -> None:
    with patch("nexus.container.get_container") as mock_get_container:
        mock_get_container.return_value.config_manager.get_tools.return_value = mock_tools
        
        provider = ToolCommandProvider(Screen())
        
        # Search by label
        hits = [hit async for hit in provider.search("Fast")]
        assert len(hits) == 1
        assert "Fast Search" in str(hits[0].match_display)
        
        # Search by description
        hits = [hit async for hit in provider.search("Deploys")]
        assert len(hits) == 1
        assert "Deploy App" in str(hits[0].match_display)
        
        # Search no match
        hits = [hit async for hit in provider.search("XYZ")]
        assert len(hits) == 0

def test_launch_tool_with_active_selector(mock_tools: list[Tool]) -> None:
    # Mocking the app and screen stack
    app = MagicMock(spec=App)
    
    from nexus.screens.tool_selector import ToolSelector
    selector = MagicMock(spec=ToolSelector)
    
    app.screen_stack = [Screen(), selector]
    
    screen: Screen[Any] = Screen()
    provider = ToolCommandProvider(screen)
    
    # mock provider.app property
    with patch.object(ToolCommandProvider, 'app', app):
        tool = mock_tools[0]
        provider._launch_tool(tool)
        
        selector.launch_tool_flow.assert_called_once_with(tool)
        app.push_screen.assert_not_called()

def test_launch_tool_without_active_selector(mock_tools: list[Tool]) -> None:
    # Mocking the app and screen stack
    app = MagicMock(spec=App)
    app.screen_stack = [Screen()]
    
    screen: Screen[Any] = Screen()
    provider = ToolCommandProvider(screen)
    
    tool = mock_tools[0]
    
    from nexus.screens.tool_selector import ToolSelector
    with patch.object(ToolSelector, 'launch_tool_flow') as mock_launch, \
         patch.object(ToolCommandProvider, 'app', app):
        provider._launch_tool(tool)
        
        # Verify push_screen was called with a new ToolSelector instance
        assert app.push_screen.call_count == 1
        pushed_screen = app.push_screen.call_args[0][0]
        assert isinstance(pushed_screen, ToolSelector)
        
        # Verify launch_tool_flow was called
        mock_launch.assert_called_once_with(tool)
