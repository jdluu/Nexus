"""Main screen for tool selection and launching.

Displays a categorized list of tools and handles user navigation, searching,
and execution.
"""

from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal
from textual.events import Key, Resize
from textual.reactive import reactive
from textual.screen import Screen
from textual.widgets import Label

from nexus.models import Tool
from nexus.widgets.footer import NexusFooter, KeyBadge
from nexus.widgets.tool_browser import ToolBrowser


class ToolSelector(Screen[None]):
    """Screen for selecting and launching tools.

    Displays a categorized list of tools separated by type. Allows searching,
    filtering, and keyboard navigation.
    """

    CSS_PATH = "../style.tcss"

    # Reactive search query
    search_query = reactive("")

    BINDINGS = [
        Binding("ctrl+t", "show_theme_picker", "Theme"),
        Binding("ctrl+f", "toggle_favorite", "Favorite"),
        Binding("escape", "clear_search", "Clear Search"),
        Binding("down", "cursor_down", "Next Item", show=False),
        Binding("up", "cursor_up", "Previous Item", show=False),
        Binding("right", "cursor_right", "Enter List", show=False),
        Binding("left", "cursor_left", "Back to Categories", show=False),
        Binding("enter", "launch_current", "Launch Tool", show=False),
        Binding("backspace", "delete_char", "Delete Character", show=False),
        Binding("?", "show_help", "Help"),
        Binding("ctrl+h", "show_help", "Help", show=False), 
        Binding("h", "show_help", "Help", show=False), 
        Binding("f1", "show_help", "Help"),
    ]

    def compose(self) -> ComposeResult:
        """Composes the screen layout."""
        with Horizontal(id="header"):
            yield Label(
                "Nexus",
                id="header-left",
            )
            yield Label("Type to search tools...", id="tool-search")

        yield ToolBrowser(id="tool-browser")

        yield Label("", id="tool-description")

        yield NexusFooter()

    # --- Theme Management ---
    THEMES = ["theme-light", "theme-dark", "theme-storm"]
    current_theme_index = 0

    def action_show_theme_picker(self) -> None:
        """Opens the theme picker modal."""
        def apply_theme(new_theme: str) -> None:
            self.set_theme(new_theme)

        from nexus.screens.theme_picker import ThemePicker
        current_theme = self.THEMES[self.current_theme_index]
        self.app.push_screen(ThemePicker(self.THEMES, current_theme, apply_theme))

    def set_theme(self, new_theme: str) -> None:
        """Sets the current theme for the application."""
        for theme in self.THEMES:
            if theme in self.classes:
                self.remove_class(theme)

        self.add_class(new_theme)

        if new_theme in self.THEMES:
            self.current_theme_index = self.THEMES.index(new_theme)

        suffix = new_theme.replace("theme-", "").title()
        self.notify(f"Theme: {suffix}")

    def on_mount(self) -> None:
        """Called when the screen is mounted."""
        self.add_class(self.THEMES[self.current_theme_index])
        
        # Report any config errors from loading phase
        from nexus.config import CONFIG_ERRORS
        for error in CONFIG_ERRORS:
            self.app.notify(error, title="Config Error", severity="error", timeout=5.0)

    # --- Search & Filter ---

    def watch_search_query(self, old_value: str, new_value: str) -> None:
        """Reacts to changes in the search query."""
        try:
            feedback = self.query_one("#tool-search", Label)
            browser = self.query_one(ToolBrowser)
        except Exception:
            return

        browser.search_query = new_value

        if new_value:
            feedback.update(f"SEARCH: {new_value}_")
        else:
            feedback.update("Type to search tools...")

    def action_delete_char(self) -> None:
        """Deletes the last character from search query."""
        if self.search_query:
            self.search_query = self.search_query[:-1]

    def action_clear_search(self) -> None:
        """Clears the search input."""
        if self.search_query:
            self.search_query = ""

    def on_key(self, event: Key) -> None:
        """Global key handler for type-to-search and numeric quick launch."""
        # Numeric keys 1-9 for quick launch
        if event.key in "123456789":
            idx = int(event.key) - 1
            browser = self.query_one(ToolBrowser)
            tool = browser.get_tool_at_index(idx)
            if tool:
                self.launch_tool_flow(tool)
                event.stop()
                return

        if event.key.isprintable() and len(event.key) == 1:
            # Append char to query
            self.search_query += event.key
            event.stop()

    # --- Navigation delegation ---

    def action_cursor_down(self) -> None:
        self.query_one(ToolBrowser).focus_next()

    def action_cursor_up(self) -> None:
        self.query_one(ToolBrowser).focus_prev()

    def action_cursor_right(self) -> None:
        self.query_one(ToolBrowser).focus_right()

    def action_cursor_left(self) -> None:
        self.query_one(ToolBrowser).focus_left()

    def action_launch_current(self) -> None:
        tool = self.query_one(ToolBrowser).get_current_selection()
        if tool:
            self.launch_tool_flow(tool)
        elif self.search_query:
            # If nothing selected but search is active, maybe launch top hit?
            # For now, do nothing.
            pass

    def action_toggle_favorite(self) -> None:
        tool = self.query_one(ToolBrowser).get_current_selection()
        if tool:
            from nexus.app import NexusApp
            if isinstance(self.app, NexusApp):
                self.app.container.state_manager.toggle_favorite(tool.command)
                self.query_one(ToolBrowser).refresh_tools()
                self.notify("Toggled Favorite")

    def action_show_help(self) -> None:
        from nexus.screens.help import HelpScreen
        self.app.push_screen(HelpScreen())

    # --- Responsive Design ---

    def on_resize(self, event: Resize) -> None:
        """Called when the screen is resized."""
        # ToolBrowser responsive mode
        browser = self.query_one(ToolBrowser)
        if event.size.width < 100:
            browser.add_class("compact")
        else:
            browser.remove_class("compact")

        # Footer responsive mode - No longer needed for minimal footer
        # The minimal footer centers automatically and wraps gracefully if needed.
        pass

    # --- Message Handlers from ToolBrowser ---

    def on_tool_browser_tool_highlighted(self, message: ToolBrowser.ToolHighlighted) -> None:
        """Update description when a tool is highlighted."""
        self.query_one("#tool-description", Label).update(
            f"{message.tool.label}: {message.tool.description}"
        )

    def on_tool_browser_tool_selected(self, message: ToolBrowser.ToolSelected) -> None:
        """Launch tool when selected."""
        self.launch_tool_flow(message.tool)

    # --- Footer Interaction ---

    def on_key_badge_pressed(self, message: KeyBadge.Pressed) -> None:
        """Handle clicks on footer key badges."""
        action = message.action
        if action == "launch_current":
            self.action_launch_current()
        elif action == "toggle_favorite":
            self.action_toggle_favorite()
        elif action == "show_help":
            self.action_show_help()
        elif action == "app.quit":
            self.app.exit()
            
    # --- Launch Logic ---

    def launch_tool_flow(self, tool: Tool) -> None:
        """Handles the flow for launching a tool."""
        if tool.requires_project:
            from nexus.screens.project_picker import ProjectPicker
            self.app.push_screen(ProjectPicker(tool))
        else:
            self.execute_tool_command(tool)

    def execute_tool_command(self, tool: Tool) -> None:
        """Executes the tool command with suspend context."""
        with self.app.suspend():
            from nexus.app import NexusApp
            if isinstance(self.app, NexusApp):
                success = self.app.container.executor.launch_tool(tool.command)
            else:
                success = False

            if not success:
                self.app.notify(f"Failed to launch {tool.label}", severity="error")

        self.app.refresh()