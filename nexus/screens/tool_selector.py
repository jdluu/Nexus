from textual.app import ComposeResult
from textual.screen import Screen
from textual.widgets import Input, ListView, ListItem, Label, Static
from textual.containers import Vertical, Horizontal, Container
from nexus.config import TOOLS
from nexus.widgets.tool_list_item import ToolItem, ToolListItem, CategoryListItem
from nexus.models import Tool

class ToolSelector(Screen):
    """Screen for selecting a tool.

    Allows the user to browse tools by category and select one to launch.
    """

    CSS_PATH = "../style.tcss"
    
    BINDINGS = [
        ("t", "next_theme", "Next Theme"),
        ("T", "prev_theme", "Prev Theme"),
    ]

    def compose(self) -> ComposeResult:
        """Composes the screen layout."""
        with Horizontal(id="header"):
            yield Label("**********************************\n Nexus Interface \n**********************************", id="header-left")
            yield Label("Search-\nPress / to search", id="header-right")

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

        yield Label("Tab list ───────────────────────────────────────────────────────────────────\n[q] [Ctrl-c] Exit    [l] [Right] [Enter] Focus action list    [k] [Up] Select item above\n[j] [Down] Select item below    [t] Next Theme    [T] Prev Theme", id="custom-footer")
        
        yield Input(id="hidden-search", classes="hidden")

    # Theme Management
    THEMES = ["theme-dark", "theme-storm", "theme-light"]
    current_theme_index = 0

    def action_next_theme(self) -> None:
        self.cycle_theme(1)

    def action_prev_theme(self) -> None:
        self.cycle_theme(-1)

    def cycle_theme(self, direction: int) -> None:
        """Cycles through available themes.
        
        Args:
            direction: 1 for next theme, -1 for previous theme.
        """
        current_theme = self.THEMES[self.current_theme_index]
        self.remove_class(current_theme)

        self.current_theme_index = (self.current_theme_index + direction) % len(self.THEMES)
        
        new_theme = self.THEMES[self.current_theme_index]
        self.add_class(new_theme)
        self.notify(f"Theme: {new_theme.replace('theme-', '').title()}")

    def on_mount(self) -> None:
        """Called when the screen is mounted."""
        self.add_class(self.THEMES[self.current_theme_index])
        
        self.populate_categories()
        self.query_one("#category-list").focus()

    def populate_categories(self) -> None:
        category_list = self.query_one("#category-list", ListView)
        category_list.clear()
        
        # Get unique categories
        categories = sorted(list(set(t.category for t in TOOLS)))
        
        for category in categories:
            item = CategoryListItem(category)
            category_list.append(item)
            
        # Select first category if available
        if categories:
            category_list.index = 0
            self.populate_tools(categories[0])

    def populate_tools(self, category: str) -> None:
        tool_list = self.query_one("#tool-list", ListView)
        tool_list.clear()
        
        filtered_tools = [t for t in TOOLS if t.category == category]
        
        for tool in filtered_tools:
            item = ToolListItem(tool)
            tool_list.append(item)

    def on_list_view_highlighted(self, event: ListView.Highlighted) -> None:
        if event.list_view.id == "category-list":
            if isinstance(event.item, CategoryListItem):
                self.populate_tools(event.item.category_id)
        
        elif event.list_view.id == "tool-list":
            if isinstance(event.item, ToolListItem):
                tool = event.item.tool_info
                self.query_one("#tool-description", Label).update(f"{tool.label}: {tool.description}")

    def on_list_view_selected(self, event: ListView.Selected) -> None:
        if event.list_view.id == "category-list":
            # If user selects a category (Enter), move focus to tool list
            self.query_one("#tool-list").focus()
        
        elif event.list_view.id == "tool-list":
            # If user selects a tool, launch it
            if isinstance(event.item, ToolListItem):
                tool = event.item.tool_info
                if tool.requires_project:
                    # Transition to project picker
                    from nexus.screens.project_picker import ProjectPicker
                    self.app.push_screen(ProjectPicker(tool))
                else:
                    # Launch directly
                    from nexus.services.executor import launch_tool
                    if launch_tool(tool.command):
                        self.app.notify(f"Launched {tool.label}")
                    else:
                        self.app.notify(f"Failed to launch {tool.label}. Is a supported terminal installed?", severity="error")

    def on_input_changed(self, event: Input.Changed) -> None:
        """Called when the search input changes."""
        pass

    def key_slash(self) -> None:
        """Focuses the search input."""
        self.app.notify("Search not implemented in this view yet")

    def key_l(self) -> None:
        """Focuses the tool list."""
        self.query_one("#tool-list").focus()

    def key_right(self) -> None:
        """Focuses the tool list (alias for 'l')."""
        self.query_one("#tool-list").focus()

    def key_h(self) -> None:
        """Focuses the category list."""
        self.query_one("#category-list").focus()
    
    def key_left(self) -> None:
        """Focuses the category list (alias for 'h')."""
        self.query_one("#category-list").focus()