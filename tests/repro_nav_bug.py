import pytest
from textual.widgets import Input, ListView
from nexus.app import NexusApp

@pytest.mark.asyncio
async def test_search_navigation_bubbling():
    app = NexusApp()
    async with app.run_test() as pilot:
        # Wait for the ToolSelector to be pushed
        await pilot.pause()
        
        # Verify ToolSelector is active
        assert app.screen.id == None # It's the Screen class
        
        # Check if search is focused
        search = app.screen.query_one("#tool-search", Input)
        assert search.has_focus
        
        # Check initial list index
        tool_list = app.screen.query_one("#tool-list", ListView)
        assert tool_list.index == 0
        
        # Press 'down' while search is focused
        await pilot.press("down")
        await pilot.pause()
        
        # Verify index changed
        # If this fails, the bug is reproduced
        assert tool_list.index == 1
