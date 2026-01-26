"""Main screen for tool selection and launching.

Displays a categorized list of tools and handles user navigation, searching,
and execution.
"""

from textual.app import ComposeResult
from textual.containers import Horizontal, Vertical
from textual.events import Key
from textual.reactive import reactive
from textual.screen import Screen
from textual.widgets import Label, ListView

from nexus.config import get_tools
from nexus.widgets.tool_list_item import CategoryListItem, ToolListItem
from nexus.models import Tool


class ToolSelector(Screen[None]):
    """Screen for selecting and launching tools.

    Displays a list of tools categorized by type. Allows searching,
    filtering, and keyboard navigation.

    Attributes:
        search_query: The current search filter text.
        BINDINGS: Key bindings for the screen.
    """

    CSS_PATH = "../style.tcss"

    # Reactive search query
    search_query = reactive("")

    BINDINGS = [
        ("ctrl+t", "show_theme_picker", "Theme"),
        ("ctrl+f", "toggle_favorite", "Favorite"),
        ("escape", "clear_search", "Clear Search"),
        ("down", "cursor_down", "Next Item"),
        ("up", "cursor_up", "Previous Item"),
        ("right", "cursor_right", "Enter List"),
        ("left", "cursor_left", "Back to Categories"),
        ("enter", "launch_current", "Launch Tool"),
        ("backspace", "delete_char", "Delete Character"),
        ("?", "show_help", "Help"),
        ("f1", "show_help", "Help"),
    ]

    def action_show_help(self) -> None:
        """Shows the help screen modal."""
        from nexus.screens.help import HelpScreen

        self.app.push_screen(HelpScreen())

    def compose(self) -> ComposeResult:
        """Composes the screen layout.

        Yields:
            The widget tree for the screen.
        """
        with Horizontal(id="header"):
            yield Label(
                "**********************************\n Nexus Interface \n**********************************",
                id="header-left",
            )
            yield Label("Search tools...", id="tool-search")

        with Horizontal(id="main-container"):
            with Vertical(id="left-pane"):
                yield Label("Categories", classes="pane-header")
                yield ListView(id="category-list")

            with Vertical(id="right-pane"):
                yield Horizontal(
                    Label("Toolbox", classes="pane-header"),
                    Label("Important Actions", classes="pane-header-right"),
                    classes="pane-header-container",
                )
                yield ListView(id="tool-list")
                yield Label(
                    "No tools found", id="tools-empty", classes="empty-state hidden"
                )

        yield Label("", id="tool-description")

        # New Three-Column Footer
        with Horizontal(id="footer-container"):
            # NAV
            with Horizontal(classes="footer-col"):
                yield Label("NAV", classes="footer-label")
                yield Label("↑↓", classes="key-badge")
                yield Label("Select", classes="key-desc")
                yield Label("←→", classes="key-badge")
                yield Label("Pane", classes="key-desc")
                yield Label("Enter", classes="key-badge")
                yield Label("Launch", classes="key-desc")
                yield Label("^F", classes="key-badge")
                yield Label("Fav", classes="key-desc")

            # SEARCH
            with Horizontal(classes="footer-col"):
                yield Label("SEARCH", classes="footer-label")
                yield Label("Type", classes="key-badge")
                yield Label("Filter", classes="key-desc")
                yield Label("Esc", classes="key-badge")
                yield Label("Clear", classes="key-desc")

            # SYSTEM
            with Horizontal(classes="footer-col"):
                yield Label("SYSTEM", classes="footer-label")
                yield Label("^T", classes="key-badge")
                yield Label("Theme", classes="key-desc")
                yield Label("^Q", classes="key-badge")
                yield Label("Exit", classes="key-desc")

    # Theme Management
    THEMES = ["theme-light", "theme-dark", "theme-storm"]
    current_theme_index = 0

    def action_show_theme_picker(self) -> None:
        """Opens the theme picker modal."""

        # Helper to apply theme temporarily or permanently
        def apply_theme(new_theme: str) -> None:
            self.set_theme(new_theme)

        from nexus.screens.theme_picker import ThemePicker

        current_theme = self.THEMES[self.current_theme_index]
        self.app.push_screen(ThemePicker(self.THEMES, current_theme, apply_theme))

    def set_theme(self, new_theme: str) -> None:
        """Sets the current theme for the application.

        Args:
            new_theme: The CSS class name of the theme to apply.
        """
        # Find current applied theme to remove it
        for theme in self.THEMES:
            if theme in self.classes:
                self.remove_class(theme)

        self.add_class(new_theme)

        # Update index if it's one of ours
        if new_theme in self.THEMES:
            self.current_theme_index = self.THEMES.index(new_theme)

        suffix = new_theme.replace("theme-", "").title()
        self.notify(f"Theme: Tokyo Night {suffix}")

    def action_next_theme(self) -> None:
        """Cycles to the next theme (legacy binding)."""
        self.cycle_theme(1)

    def action_prev_theme(self) -> None:
        """Cycles to the previous theme."""
        self.cycle_theme(-1)

    def cycle_theme(self, direction: int) -> None:
        """Cycles through available themes.

        Args:
            direction: 1 for next, -1 for previous.
        """
        new_index = (self.current_theme_index + direction) % len(self.THEMES)
        new_theme = self.THEMES[new_index]
        self.set_theme(new_theme)

    def on_mount(self) -> None:
        """Called when the screen is mounted.

        Sets initial theme, populates categories, and focuses the category list.
        """
        self.add_class(self.THEMES[self.current_theme_index])
        self.populate_categories()
        # Default focus to categories
        self.query_one("#category-list").focus()

        # Report any config errors from loading phase
        from nexus.config import CONFIG_ERRORS
        for error in CONFIG_ERRORS:
            self.app.notify(error, title="Config Error", severity="error", timeout=5.0)

    def select_all_category(self) -> None:
        """Selects the 'ALL' category in the list."""
        category_list = self.query_one("#category-list", ListView)
        # Find the index of the ALL category
        for idx, child in enumerate(category_list.children):
            if isinstance(child, CategoryListItem) and child.category_id == "ALL":
                if category_list.index != idx:
                    category_list.index = idx
                break

    def watch_search_query(self, old_value: str, new_value: str) -> None:
        """Reacts to changes in the search query.

        Args:
            old_value: The previous search query.
            new_value: The new search query.
        """
        try:
            feedback = self.query_one("#tool-search", Label)
        except Exception:
            return

        if new_value:
            feedback.update(f"SEARCH: {new_value}_")
            # Switch to ALL category automatically if not already
            self.select_all_category()
            # Populate tools with filter
            self.refresh_tools()
        else:
            feedback.update("Search tools...")
            # Re-populate without filter
            self.refresh_tools()

    def action_delete_char(self) -> None:
        """Deletes the last character from search query."""
        if self.search_query:
            self.search_query = self.search_query[:-1]

    def action_clear_search(self) -> None:
        """Clears the search input."""
        if self.search_query:
            self.search_query = ""

    def on_key(self, event: Key) -> None:
        """Global key handler for type-to-search and numeric quick launch.

        Args:
            event: The key event.
        """
        # Numeric keys 1-9 for quick launch
        if event.key in "123456789":
            idx = int(event.key) - 1
            tool_list = self.query_one("#tool-list", ListView)
            if idx < len(tool_list.children):
                item = tool_list.children[idx]
                if isinstance(item, ToolListItem):
                    self.launch_tool_flow(item.tool_info)
                    event.stop()
                    return

        if event.key.isprintable() and len(event.key) == 1:
            # Append char to query
            self.search_query += event.key
            event.stop()

    def refresh_tools(self) -> None:
        """Refreshes tool list based on current selection and search text."""
        category_list = self.query_one("#category-list", ListView)
        if (
            hasattr(category_list, "highlighted_child")
            and category_list.highlighted_child
        ):
            item = category_list.highlighted_child
            if isinstance(item, CategoryListItem):
                self.populate_tools(item.category_id, filter_text=self.search_query)

    def populate_categories(self) -> None:
        """Populates the category list with unique categories from loaded tools."""
        category_list = self.query_one("#category-list", ListView)
        category_list.clear()

        # Get unique categories
        tools = get_tools()
        categories = sorted(list(set(t.category for t in tools)))

        # Add FAVORITES and ALL category at the start
        fav_item = CategoryListItem("FAVORITES")
        fav_item.add_class("category-FAVORITES") # Optional styling hook
        category_list.append(fav_item)
        
        all_item = CategoryListItem("ALL")
        category_list.append(all_item)

        for category in categories:
            item = CategoryListItem(category)
            category_list.append(item)

        # Select "ALL" category by default (index 1, as FAVORITES is 0)
        # Or find index of "ALL"
        if category_list.children:
            all_idx = 1 if len(category_list.children) > 1 else 0
            category_list.index = all_idx
            # Trigger population via index change?
            # Textual might not trigger highlighted event on programmatic set if not focused/mounted fully?
            # Safe to call populate_tools explicitly.
            cat_id = "ALL"
            if 0 <= all_idx < len(category_list.children):
                 child = category_list.children[all_idx]
                 if isinstance(child, CategoryListItem):
                     cat_id = child.category_id
            
            self.populate_tools(cat_id)

    def populate_tools(self, category: str, filter_text: str = "") -> None:
        """Populates the tool list based on category and filter text.

        Args:
            category: The category ID to filter by (or "ALL").
            filter_text: Optional text to filter tool label/description.
        """
        from nexus.app import NexusApp

        tool_list = self.query_one("#tool-list", ListView)
        tool_list.clear()

        tools = get_tools()

        if category == "ALL":
            filtered_tools = tools
        elif category == "FAVORITES":
            if isinstance(self.app, NexusApp):
                favs = self.app.container.state_manager.get_favorites()
                filtered_tools = [t for t in tools if t.command in favs]
            else:
                filtered_tools = []
        else:
            filtered_tools = [t for t in tools if t.category == category]

        if filter_text:
            filtered_tools = [
                t
                for t in filtered_tools
                if filter_text.lower() in t.label.lower()
                or filter_text.lower() in t.description.lower()
            ]

        if filtered_tools:
            tool_list.index = 0
            tool_list.display = True
            self.query_one("#tools-empty").add_class("hidden")
        else:
            tool_list.display = False
            empty_lbl = self.query_one("#tools-empty", Label)
            empty_lbl.remove_class("hidden")
            if filter_text:
                empty_lbl.update(f"No tools matching '{filter_text}'")
            else:
                empty_lbl.update(f"No tools in category '{category}'")

        for i, tool in enumerate(filtered_tools):
            hint = str(i + 1) if i < 9 else ""
            is_fav = False
            if isinstance(self.app, NexusApp):
                is_fav = self.app.container.state_manager.is_favorite(tool.command)
                
            item = ToolListItem(tool, hint=hint, is_favorite=is_fav)
            tool_list.append(item)

    def on_list_view_highlighted(self, event: ListView.Highlighted) -> None:
        """Called when a list item is highlighted.

        Args:
            event: The highlight event.
        """
        if event.list_view.id == "category-list":
            if isinstance(event.item, CategoryListItem):
                self.populate_tools(
                    event.item.category_id, filter_text=self.search_query
                )

        elif event.list_view.id == "tool-list":
            if isinstance(event.item, ToolListItem):
                tool = event.item.tool_info
                self.query_one("#tool-description", Label).update(
                    f"{tool.label}: {tool.description}"
                )

    def on_list_view_selected(self, event: ListView.Selected) -> None:
        """Called when a list item is selected (Enter pressed).

        Args:
            event: The selection event.
        """
        if event.list_view.id == "category-list":
            # If user selects a category (Enter), move focus to tool list
            self.query_one("#tool-list").focus()
            # force update
            self.action_cursor_right()  # Re-use logic

        elif event.list_view.id == "tool-list":
            # If user selects a tool, launch it
            if isinstance(event.item, ToolListItem):
                tool = event.item.tool_info
                self.launch_tool_flow(tool)

    def action_cursor_down(self) -> None:
        """Moves selection down in the active list."""
        if self.query_one("#category-list").has_focus:
            category_list = self.query_one("#category-list", ListView)
            if category_list.index is None:
                category_list.index = 0
            else:
                category_list.index = min(
                    len(category_list.children) - 1, category_list.index + 1
                )

        elif self.query_one("#tool-list").has_focus:
            tool_list = self.query_one("#tool-list", ListView)
            if tool_list.index is None:
                tool_list.index = 0
            else:
                tool_list.index = min(len(tool_list.children) - 1, tool_list.index + 1)

    def action_cursor_up(self) -> None:
        """Moves selection up in the active list."""
        if self.query_one("#category-list").has_focus:
            lst = self.query_one("#category-list", ListView)
            if lst.index is not None:
                lst.index = max(0, lst.index - 1)

        elif self.query_one("#tool-list").has_focus:
            lst = self.query_one("#tool-list", ListView)
            if lst.index is not None:
                lst.index = max(0, lst.index - 1)

    def action_cursor_right(self) -> None:
        """Moves focus from categories to tools."""
        if self.query_one("#category-list").has_focus:
            tool_list = self.query_one("#tool-list", ListView)
            tool_list.focus()

            # Ensure index is valid and trigger highlight refresh
            if tool_list.children:
                if tool_list.index is None:
                    tool_list.index = 0
                else:
                    # Force property update to ensure highlight renders
                    idx = tool_list.index
                    tool_list.index = None
                    tool_list.index = idx

    def action_cursor_left(self) -> None:
        """Moves focus from tools back to categories."""
        if self.query_one("#tool-list").has_focus:
            self.query_one("#category-list").focus()

    def action_toggle_favorite(self) -> None:
        """Toggles the favorite status of the selected tool."""
        if self.query_one("#tool-list").has_focus:
            tool_list = self.query_one("#tool-list", ListView)
            if tool_list.index is not None and tool_list.index < len(tool_list.children):
                item = tool_list.children[tool_list.index]
                if isinstance(item, ToolListItem):
                    from nexus.app import NexusApp
                    if isinstance(self.app, NexusApp):
                        self.app.container.state_manager.toggle_favorite(item.tool_info.command)
                        # Refresh to show star or remove from Favorites list if active
                        self.refresh_tools()
                        self.notify("Toggled Favorite")

    def action_launch_current(self) -> None:
        """Launches the currently selected tool."""
        tool_list = self.query_one("#tool-list", ListView)
        # Ensure index is valid
        if tool_list.index is not None and tool_list.index < len(tool_list.children):
            item = tool_list.children[tool_list.index]
            if isinstance(item, ToolListItem):
                self.launch_tool_flow(item.tool_info)

    def launch_tool_flow(self, tool: Tool) -> None:
        """Handles the flow for launching a tool.

        If the tool requires a project, opens the ProjectPicker.
        Otherwise, executes the tool command directly.

        Args:
            tool: The Tool object to launch.
        """
        if tool.requires_project:
            from nexus.screens.project_picker import ProjectPicker

            self.app.push_screen(ProjectPicker(tool))
        else:
            self.execute_tool_command(tool)

    def execute_tool_command(self, tool: Tool) -> None:
        """Executes the tool command with suspend context.

        Args:
            tool: The Tool object to execute.
        """
        # Launch directly with suspend
        with self.app.suspend():
            from nexus.app import NexusApp

            if isinstance(self.app, NexusApp):
                success = self.app.container.executor.launch_tool(tool.command)
            else:
                # Fallback or strict error
                success = False

            if not success:
                # We can't see this notification until we return, but that's fine
                self.app.notify(f"Failed to launch {tool.label}", severity="error")

        self.app.refresh()