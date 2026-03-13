"""Main screen for tool selection and launching.

Displays a categorized list of tools separated by type. Allows searching,
filtering, and keyboard navigation.
"""

from pathlib import Path
from textual import on
from textual.app import ComposeResult
from textual.binding import Binding
from textual.events import Key
from textual.reactive import reactive
from textual.screen import Screen
from textual.widgets import Label, Header, Footer, Input


from nexus.models import Tool
from nexus.widgets.tool_browser import ToolBrowser


class ToolSelector(Screen[None]):
    """Screen for selecting and launching tools.

    Displays a categorized list of tools separated by type. Allows searching,
    filtering, and keyboard navigation.
    """

    # Reactive search query
    search_query = reactive("")

    # Screen-specific bindings. 
    # Global bindings (Quit, Theme, Help, Palette) are handled by NexusApp with priority=True.
    BINDINGS = [
        Binding("enter", "launch", "Launch", show=True),
        Binding("down", "cursor_down", "Next", show=False),
        Binding("up", "cursor_up", "Prev", show=False),
        Binding("right", "cursor_right", "List", show=False),
        Binding("left", "cursor_left", "Categories", show=False),
        # Numeric quick launch
        Binding("1", "launch_idx(0)", "Launch 1", show=False),
        Binding("2", "launch_idx(1)", "Launch 2", show=False),
        Binding("3", "launch_idx(2)", "Launch 3", show=False),
        Binding("4", "launch_idx(3)", "Launch 4", show=False),
        Binding("5", "launch_idx(4)", "Launch 5", show=False),
        Binding("6", "launch_idx(5)", "Launch 6", show=False),
        Binding("7", "launch_idx(6)", "Launch 7", show=False),
        Binding("8", "launch_idx(7)", "Launch 8", show=False),
        Binding("9", "launch_idx(8)", "Launch 9", show=False),
    ]

    def compose(self) -> ComposeResult:
        """Composes the screen layout."""
        yield Header()
        yield Input(placeholder="Search tools...", id="tool-search")
        yield ToolBrowser(id="tool-browser").data_bind(search_query=ToolSelector.search_query)
        yield Label("", id="tool-description")
        yield Footer()

    def on_mount(self) -> None:
        """Called when the screen is mounted."""
        # Report any config errors from loading phase
        from nexus.container import get_container
        for error in get_container().config_manager.config_errors:
            self.app.notify(error, title="Config Error", severity="error", timeout=5.0)
        
        self.query_one("#tool-search").focus()

    # --- Actions ---

    def action_launch(self) -> None:
        """Launches the currently highlighted tool."""
        tool = self.query_one(ToolBrowser).get_current_selection()
        if tool:
            self.launch_tool_flow(tool)

    def action_launch_idx(self, idx: int) -> None:
        """Launches a tool by its index in the current list."""
        # Only launch by number if not currently typing in the search box
        if not self.query_one("#tool-search").has_focus or not self.search_query:
            tool = self.query_one(ToolBrowser).get_tool_at_index(idx)
            if tool:
                self.launch_tool_flow(tool)

    # --- Navigation delegation ---

    def action_cursor_down(self) -> None:
        """Delegates navigation to the browser."""
        self.query_one(ToolBrowser).focus_next()

    def action_cursor_up(self) -> None:
        """Delegates navigation to the browser."""
        self.query_one(ToolBrowser).focus_prev()

    def action_cursor_right(self) -> None:
        """Navigates focus to the right pane."""
        self.query_one(ToolBrowser).focus_right()

    def action_cursor_left(self) -> None:
        """Navigates focus to the left pane."""
        self.query_one(ToolBrowser).focus_left()

    # --- Event Handlers ---

    @on(Input.Changed, "#tool-search")
    def _on_search_changed(self, event: Input.Changed) -> None:
        """Reacts to changes in the search input."""
        self.search_query = event.value

    @on(Input.Submitted, "#tool-search")
    def _on_search_submitted(self) -> None:
        """Launch selection on enter."""
        self.action_launch()

    @on(ToolBrowser.ToolHighlighted)
    def _on_tool_highlighted(self, message: ToolBrowser.ToolHighlighted) -> None:
        """Update description when a tool is highlighted."""
        self.query_one("#tool-description", Label).update(
            f"{message.tool.label}: {message.tool.description}"
        )

    @on(ToolBrowser.ToolSelected)
    def _on_tool_selected(self, message: ToolBrowser.ToolSelected) -> None:
        """Launch tool when selected."""
        self.launch_tool_flow(message.tool)

    def on_key(self, event: Key) -> None:
        """Global key handler for numeric quick launch."""
        # Numeric keys 1-9 for quick launch
        # We only trigger if search query is empty to avoid conflict with typing numbers in search
        if event.key in "123456789" and not self.search_query:
            idx = int(event.key) - 1
            browser = self.query_one(ToolBrowser)
            tool = browser.get_tool_at_index(idx)
            if tool:
                self.launch_tool_flow(tool)
                event.stop()
                return

    # --- Launch Logic ---

    def launch_tool_flow(self, tool: Tool) -> None:
        """Manages the workflow for initiating a tool execution."""
        if tool.requires_project:
            from nexus.screens.project_picker import ProjectPicker
            self.app.push_screen(ProjectPicker(tool))
        elif tool.supports_flags:
            from nexus.screens.flag_picker import FlagPicker
            self.app.push_screen(
                FlagPicker(tool.label), 
                callback=lambda f: self.execute_tool_command(tool, flags=f) if f is not None else None
            )
        else:
            self.execute_tool_command(tool)

    def execute_tool_command(
        self, 
        tool: Tool, 
        project_path: Path | None = None, 
        flags: str | None = None
    ) -> None:
        """Executes the tool command within a suspended TUI context."""
        with self.app.suspend():
            from nexus.container import get_container
            success = get_container().executor.launch_tool(
                tool.command, project_path=project_path, flags=flags
            )

            if not success:
                self.app.notify(f"Failed to launch {tool.label}", severity="error")

        self.app.refresh()
