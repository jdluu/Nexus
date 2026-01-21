from textual.app import ComposeResult
from textual.screen import Screen
from textual.widgets import ListView, Label
from textual.containers import Vertical, Horizontal
from textual.reactive import reactive
from textual.events import Key

from nexus.config import TOOLS
from nexus.widgets.tool_list_item import ToolListItem, CategoryListItem
from nexus.models import Tool

class ToolSelector(Screen):
    """Screen for selecting and launching tools.

    Displays a list of tools categorized by type. Allows searching,
    filtering, and keyboard navigation.
    """

    CSS_PATH = "../style.tcss"
    
    # Reactive search query
    search_query = reactive("")

    BINDINGS = [
        ("ctrl+t", "show_theme_picker", "Theme"),
        ("escape", "clear_search", "Clear Search"),
        ("down", "cursor_down", "Next Item"),
        ("up", "cursor_up", "Previous Item"),
        ("right", "cursor_right", "Enter List"),
        ("left", "cursor_left", "Back to Categories"),
        ("enter", "launch_current", "Launch Tool"),
        ("backspace", "delete_char", "Delete Character"),
    ]

    def compose(self) -> ComposeResult:
        """Composes the screen layout."""
        with Horizontal(id="header"):
            yield Label("**********************************\n Nexus Interface \n**********************************", id="header-left")
            # Search bar removed; search text will be shown in footer/label

        with Horizontal(id="main-container"):
            with Vertical(id="left-pane"):
                yield Label("Categories", classes="pane-header")
                yield ListView(id="category-list")
            
            with Vertical(id="right-pane"):
                yield Horizontal(
                    Label("Toolbox", classes="pane-header"),
                    Label("Important Actions", classes="pane-header-right"),
                    classes="pane-header-container"
                )
                yield ListView(id="tool-list")
            
        yield Label("", id="tool-description")
        yield Label("", id="search-feedback", classes="hidden") 

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
                yield Label("^C", classes="key-badge")
                yield Label("Exit", classes="key-desc")

    # Theme Management
    THEMES = ["theme-light", "theme-dark", "theme-storm"]
    current_theme_index = 0

    def action_show_theme_picker(self) -> None:
        """Opens the theme picker modal."""
        # Helper to apply theme temporarily or permanently
        def apply_theme(new_theme: str):
            self.set_theme(new_theme)

        from nexus.screens.theme_picker import ThemePicker
        current_theme = self.THEMES[self.current_theme_index]
        self.app.push_screen(ThemePicker(self.THEMES, current_theme, apply_theme))

    def set_theme(self, new_theme: str) -> None:
        """Sets the current theme."""
        # Find current applied theme to remove it
        for theme in self.THEMES:
            if theme in self.classes:
                self.remove_class(theme)
        
        self.add_class(new_theme)
        
        # Update index if it's one of ours
        if new_theme in self.THEMES:
            self.current_theme_index = self.THEMES.index(new_theme)
            
        suffix = new_theme.replace('theme-', '').title()
        self.notify(f"Theme: Tokyo Night {suffix}")

    def action_next_theme(self) -> None:
        # Kept for backward compat or if needed, but keybinding changed
        self.cycle_theme(1)

    def action_prev_theme(self) -> None:
        self.cycle_theme(-1)

    def cycle_theme(self, direction: int) -> None:
        """Cycles through available themes."""
        new_index = (self.current_theme_index + direction) % len(self.THEMES)
        new_theme = self.THEMES[new_index]
        self.set_theme(new_theme)

    def on_mount(self) -> None:
        """Called when the screen is mounted."""
        self.add_class(self.THEMES[self.current_theme_index])
        self.populate_categories()
        # Default focus to categories
        self.query_one("#category-list").focus()

    def watch_search_query(self, old_value: str, new_value: str) -> None:
        """Reacts to changes in the search query."""
        feedback = self.query_one("#search-feedback", Label)
        if new_value:
            feedback.update(f"SEARCH: {new_value}_")
            feedback.remove_class("hidden")
            
            # Switch to ALL category automatically if not already
            self.select_all_category()
            
            # Populate tools with filter
            self.populate_tools("ALL", filter_text=new_value)
        else:
            feedback.update("")
            feedback.add_class("hidden")
            # Re-populate without filter (keeps current category theoretically, but we might want to reset?)
            # For now, let's just re-populate based on currently selected category
            self.refresh_tools()

    def select_all_category(self) -> None:
        """Selects the 'ALL' category in the list."""
        category_list = self.query_one("#category-list", ListView)
        # Assuming ALL is always index 0
        if category_list.index != 0:
            category_list.index = 0
            # Note: Changing index triggers on_list_view_highlighted, which calls populate.
            # We might have a race condition or double populate here. 
            # Ideally populate logic handles the query check.

    def on_key(self, event: Key) -> None:
        """Global key handler for type-to-search."""
        if event.key.isprintable() and len(event.key) == 1:
            # Append char to query
            self.search_query += event.key
            event.stop() # execution stops here, preventing default handling if any

    def action_delete_char(self) -> None:
        """Deletes the last character from search query."""
        if self.search_query:
            self.search_query = self.search_query[:-1]

    def action_clear_search(self) -> None:
        """Clears the search input."""
        if self.search_query:
            self.search_query = ""
        else:
            # If no search, maybe back navigates? Or just does nothing (default clear)
            pass

    def refresh_tools(self) -> None:
        """Refreshes tool list based on current selection and search text."""
        category_list = self.query_one("#category-list", ListView)
        if hasattr(category_list, "highlighted_child") and category_list.highlighted_child:
            item = category_list.highlighted_child
            if isinstance(item, CategoryListItem):
                self.populate_tools(item.category_id, filter_text=self.search_query)

    def populate_categories(self) -> None:
        category_list = self.query_one("#category-list", ListView)
        category_list.clear()
        
        # Get unique categories
        categories = sorted(list(set(t.category for t in TOOLS)))
        
        # Add "ALL" category at the start
        all_item = CategoryListItem("ALL")
        category_list.append(all_item)
        
        for category in categories:
            item = CategoryListItem(category)
            category_list.append(item)
            
        # Select first category if available
        if categories:
            category_list.index = 0
            self.populate_tools(categories[0]) # Initial population

    def populate_tools(self, category: str, filter_text: str = "") -> None:
        tool_list = self.query_one("#tool-list", ListView)
        tool_list.clear()
        
        if category == "ALL":
             filtered_tools = TOOLS
        else:
             filtered_tools = [t for t in TOOLS if t.category == category]
        
        if filter_text:
             filtered_tools = [t for t in filtered_tools if filter_text.lower() in t.label.lower() or filter_text.lower() in t.description.lower()]

        if filtered_tools:
           tool_list.index = 0

        for tool in filtered_tools:
            item = ToolListItem(tool)
            tool_list.append(item)

    def on_list_view_highlighted(self, event: ListView.Highlighted) -> None:
        if event.list_view.id == "category-list":
            if isinstance(event.item, CategoryListItem):
                # When category changes, we should generally respect the search query
                # unless the user manually changed category, implying they might want to see that category?
                # But implicit search says "type -> go to ALL".
                # If user manually clicks "DEV", they expect to see DEV tools.
                # If they then type, it should go back to ALL.
                
                # So here, just populate with current query (which might be empty)
                # If query is active and user manually moves, let's keep the filter but apply to normalized category?
                # User's request: "search automatically switches category to ALL".
                
                self.populate_tools(event.item.category_id, filter_text=self.search_query)
        
        elif event.list_view.id == "tool-list":
            if isinstance(event.item, ToolListItem):
                tool = event.item.tool_info
                self.query_one("#tool-description", Label).update(f"{tool.label}: {tool.description}")

    def on_list_view_selected(self, event: ListView.Selected) -> None:
        if event.list_view.id == "category-list":
            # If user selects a category (Enter), move focus to tool list
            self.query_one("#tool-list").focus()
            # force update
            self.action_cursor_right() # Re-use logic
        
        elif event.list_view.id == "tool-list":
            # If user selects a tool, launch it
            if isinstance(event.item, ToolListItem):
                tool = event.item.tool_info
                if tool.requires_project:
                    # Transition to project picker
                    from nexus.screens.project_picker import ProjectPicker
                    self.app.push_screen(ProjectPicker(tool))
                else:
                    # Launch directly with suspend
                    with self.app.suspend():
                        from nexus.services.executor import launch_tool
                        if launch_tool(tool.command):
                             pass # Tool finished successfully
                        else:
                             self.app.notify(f"Failed to launch {tool.label}", severity="error")
                    # Clear any artifacts from screen after return
                    self.app.refresh()

    def action_cursor_down(self) -> None:
        """Moves selection down in list."""
        if self.query_one("#category-list").has_focus:
             category_list = self.query_one("#category-list", ListView)
             if category_list.index is None:
                 category_list.index = 0
             else:
                 category_list.index = min(len(category_list.children) - 1, category_list.index + 1)

        elif self.query_one("#tool-list").has_focus:
             tool_list = self.query_one("#tool-list", ListView)
             if tool_list.index is None:
                 tool_list.index = 0
             else:
                 tool_list.index = min(len(tool_list.children) - 1, tool_list.index + 1)

    def action_cursor_up(self) -> None:
        """Moves selection up."""
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

    def action_launch_current(self) -> None:
         """Launches the currently selected tool."""
         tool_list = self.query_one("#tool-list", ListView)
         if tool_list.index is not None and tool_list.index < len(tool_list.children):
              item = tool_list.children[tool_list.index]
              if isinstance(item, ToolListItem):
                   tool = item.tool_info
                   if tool.requires_project:
                        from nexus.screens.project_picker import ProjectPicker
                        self.app.push_screen(ProjectPicker(tool))
                   else:
                        # Launch directly with suspend
                        with self.app.suspend():
                            from nexus.services.executor import launch_tool
                            if launch_tool(tool.command):
                                pass
                            else:
                                self.app.notify(f"Failed to launch {tool.label}", severity="error")
                        self.app.refresh()