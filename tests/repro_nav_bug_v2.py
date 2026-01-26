import pytest
import asyncio
from textual.widgets import Input, ListView
from nexus.app import NexusApp

@pytest.mark.asyncio
async def test_search_navigation_multiple_presses():
    app = NexusApp()
    async with app.run_test() as pilot:
        await pilot.pause()
        
        search = app.screen.query_one("#tool-search", Input)
        tool_list = app.screen.query_one("#tool-list", ListView)
        
        assert search.has_focus
        assert tool_list.index == 0
        
        # Press down 3 times
        for i in range(1, 4):
            await pilot.press("down")
            await pilot.pause()
            assert tool_list.index == i
            assert search.has_focus, f"Lost focus after {i} down presses"

        # Press up
        await pilot.press("up")
        await pilot.pause()
        assert tool_list.index == 2
        assert search.has_focus
        
        # Type something and verify filter + navigation still works
        await pilot.press("a")
        await pilot.pause()
        # Search query should have updated
        assert app.screen.search_query == "a"
        
        # Navigation should still work (index might have reset to 0 due to filter)
        await pilot.press("down")
        await pilot.pause()
        # Even if index reset, pressing down should either move to 1 or stay 0 if only 1 item
        # But it should NOT fail or lose focus
        assert search.has_focus
