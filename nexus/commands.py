"""Command palette providers for Nexus.

Extends the Textual command palette with Nexus specific commands such as 
tool launching and navigation.
"""

from functools import partial
from typing import AsyncIterator
from textual.command import Provider, Hit, DiscoveryHit
from nexus.models import Tool


class ToolCommandProvider(Provider):
    """A command provider for Nexus tools.

    Allows users to search for and launch any configured tool directly from 
    the command palette.
    """

    async def discover(self) -> AsyncIterator[DiscoveryHit]:
        """Yields commands for all configured tools.

        Returns:
            An async iterator of DiscoveryHit objects.
        """
        from nexus.container import get_container
        tools = get_container().config_manager.get_tools()
        for tool in tools:
            yield DiscoveryHit(
                tool.label,
                partial(self._launch_tool, tool),
                help=tool.description
            )

    async def search(self, query: str) -> AsyncIterator[Hit]:
        """Searches for tools matching the user query.

        Args:
            query: The search string entered by the user.

        Returns:
            An async iterator of Hit objects.
        """
        matcher = self.matcher(query)
        from nexus.container import get_container
        tools = get_container().config_manager.get_tools()
        for tool in tools:
            # Match against label and description for better results
            score = max(matcher.match(tool.label), matcher.match(tool.description))
            if score > 0:
                yield Hit(
                    score,
                    matcher.highlight(tool.label),
                    partial(self._launch_tool, tool),
                    help=tool.description
                )

    def _launch_tool(self, tool: Tool) -> None:
        """Handles the execution flow for a selected tool.

        Delegates the launch to the active ToolSelector screen.

        Args:
            tool: The Tool configuration to launch.
        """
        from nexus.screens.tool_selector import ToolSelector
        
        # Search for ToolSelector in the screen stack
        # If found, use its flow. If not, push it then launch.
        selector = None
        for screen in reversed(self.app.screen_stack):
            if isinstance(screen, ToolSelector):
                selector = screen
                break
        
        if selector:
            selector.launch_tool_flow(tool)
        else:
            # This shouldn't happen in normal use, but handles edges
            new_selector = ToolSelector()
            self.app.push_screen(new_selector)
            new_selector.launch_tool_flow(tool)
