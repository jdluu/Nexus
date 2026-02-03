"""Widget for browsing tools by category.

Encapsulates the split-pane layout with Category list and Tool list.
"""

from typing import cast

from textual.app import ComposeResult
from textual.containers import Horizontal, Vertical
from textual.message import Message
from textual.reactive import reactive
from textual.widget import Widget
from textual.widgets import Label, ListView

from nexus.config import get_tools
from nexus.models import Tool
from nexus.widgets.tool_list_item import CategoryListItem, ToolListItem


class ToolBrowser(Widget):
    """A dual-pane browser for categories and tools."""

    DEFAULT_CSS = """
    ToolBrowser {
        height: 1fr;
        layout: horizontal;
    }
    
    /* Re-use existing ID-based styles from style.tcss via matching IDs or classes */
    /* We will use matching IDs to keep style.tcss compatible without huge changes yet */
    """

    class ToolSelected(Message):
        """Message posted when a tool is selected (Enter pressed)."""

        def __init__(self, tool: Tool) -> None:
            self.tool = tool
            super().__init__()

    class ToolHighlighted(Message):
        """Message posted when a tool is highlighted (for description updates)."""

        def __init__(self, tool: Tool) -> None:
            self.tool = tool
            super().__init__()

    search_query = reactive("")

    def compose(self) -> ComposeResult:
        """Compose the dual-pane layout."""
        # Left Pane: Categories
        with Vertical(id="left-pane"):
            yield Label("Categories", classes="pane-header")
            yield ListView(id="category-list")

        # Right Pane: Tools
        with Vertical(id="right-pane"):
            with Horizontal(classes="pane-header-container"):
                yield Label("Toolbox", classes="pane-header")
                yield Label("Tip: Ctrl+H for controls", classes="pane-header-right")
            
            yield ListView(id="tool-list")
            yield Label(
                "No tools found", id="tools-empty", classes="empty-state hidden"
            )

    def on_mount(self) -> None:
        """Initialize lists."""
        self.populate_categories()
        # Default focus
        self.query_one("#category-list").focus()

    def watch_search_query(self, new_value: str) -> None:
        """Filter tools when search query changes."""
        if new_value:
            # Auto-select ALL category if searching
            self.select_all_category()
            self.refresh_tools()
        else:
            self.refresh_tools()

    def select_all_category(self) -> None:
        """Selects the 'ALL' category."""
        category_list = self.query_one("#category-list", ListView)
        for idx, child in enumerate(category_list.children):
            if isinstance(child, CategoryListItem) and child.category_id == "ALL":
                if category_list.index != idx:
                    category_list.index = cast(int | None, idx) # generic fix
                break

    def populate_categories(self) -> None:
        """Populate the category list."""
        category_list = self.query_one("#category-list", ListView)
        category_list.clear()

        tools = get_tools()
        categories = sorted(list(set(t.category for t in tools)))

        category_list.append(CategoryListItem("FAVORITES"))
        category_list.append(CategoryListItem("ALL"))

        for category in categories:
            category_list.append(CategoryListItem(category))

        # Default to ALL (index 1)
        category_list.index = 1
        # Trigger initial tool population
        self.populate_tools("ALL")

    def populate_tools(self, category: str, filter_text: str = "") -> None:
        """Populate the tool list."""
        tool_list = self.query_one("#tool-list", ListView)
        tool_list.clear()

        tools = get_tools()

        # Filter by Category
        if category == "ALL":
            filtered_tools = tools
        elif category == "FAVORITES":
            # We need to access app state for favorites.
            # Using a simplified approach: check if available in app
             from nexus.app import NexusApp
             if isinstance(self.app, NexusApp):
                 favs = self.app.container.state_manager.get_favorites()
                 filtered_tools = [t for t in tools if t.command in favs]
             else:
                 filtered_tools = []
        else:
            filtered_tools = [t for t in tools if t.category == category]

        # Filter by Text
        if filter_text:
            filtered_tools = [
                t
                for t in filtered_tools
                if filter_text.lower() in t.label.lower()
                or filter_text.lower() in t.description.lower()
            ]

        # Update UI
        empty_lbl = self.query_one("#tools-empty", Label)
        
        if filtered_tools:
            tool_list.display = True
            empty_lbl.add_class("hidden")
            tool_list.index = 0
        else:
            tool_list.display = False
            empty_lbl.remove_class("hidden")
            if filter_text:
                empty_lbl.update(f"No tools matching '{filter_text}'")
            else:
                empty_lbl.update(f"No tools in category '{category}'")

        # Render Items
        for i, tool in enumerate(filtered_tools):
            is_fav = False
            from nexus.app import NexusApp
            if isinstance(self.app, NexusApp):
                is_fav = self.app.container.state_manager.is_favorite(tool.command)
                
            tool_list.append(ToolListItem(tool, is_favorite=is_fav))

    def refresh_tools(self) -> None:
        """Refresh (re-populate) the currently viewed category."""
        category_list = self.query_one("#category-list", ListView)
        if category_list.highlighted_child:
            item = category_list.highlighted_child
            if isinstance(item, CategoryListItem):
                self.populate_tools(item.category_id, filter_text=self.search_query)

    # --- Event Handlers ---

    def on_list_view_highlighted(self, event: ListView.Highlighted) -> None:
        if event.list_view.id == "category-list":
            # Update tool list when category changes
            if isinstance(event.item, CategoryListItem):
                self.populate_tools(event.item.category_id, filter_text=self.search_query)
        
        elif event.list_view.id == "tool-list":
            # Notify parent to update description
            if isinstance(event.item, ToolListItem):
                self.post_message(self.ToolHighlighted(event.item.tool_info))

    def on_list_view_selected(self, event: ListView.Selected) -> None:
        if event.list_view.id == "category-list":
            # Move focus to tool list
            self.query_one("#tool-list").focus()
            
            # Ensure the first item is selected in tool list
            tool_list = self.query_one("#tool-list", ListView)
            if tool_list.children:
                tool_list.index = 0

        elif event.list_view.id == "tool-list":
            # Launch tool
            if isinstance(event.item, ToolListItem):
                self.post_message(self.ToolSelected(event.item.tool_info))

    # --- Public Control Methods (for parent screen bindings) ---

    def focus_next(self) -> None:
        """Simulate down arrow."""
        if self.query_one("#category-list").has_focus:
            self._move_list_cursor("#category-list", 1)
        elif self.query_one("#tool-list").has_focus:
            self._move_list_cursor("#tool-list", 1)

    def focus_prev(self) -> None:
        """Simulate up arrow."""
        if self.query_one("#category-list").has_focus:
            self._move_list_cursor("#category-list", -1)
        elif self.query_one("#tool-list").has_focus:
            self._move_list_cursor("#tool-list", -1)

    def _move_list_cursor(self, list_id: str, delta: int) -> None:
        lst = self.query_one(list_id, ListView)
        if lst.index is None:
            lst.index = 0
        else:
            new_index = lst.index + delta
            # Clamp
            new_index = max(0, min(len(lst.children) - 1, new_index))
            lst.index = new_index

    def focus_right(self) -> None:
        """Switch to tools."""
        if self.query_one("#category-list").has_focus:
             self.query_one("#tool-list").focus()

    def focus_left(self) -> None:
        """Switch to categories."""
        if self.query_one("#tool-list").has_focus:
            self.query_one("#category-list").focus()

    def get_tool_at_index(self, index: int) -> Tool | None:
        """Return tool at specific list index (for 1-9 shortcuts)."""
        tool_list = self.query_one("#tool-list", ListView)
        if 0 <= index < len(tool_list.children):
            item = tool_list.children[index]
            if isinstance(item, ToolListItem):
                return item.tool_info
        return None

    def get_current_selection(self) -> Tool | None:
        """Return currently selected tool."""
        tool_list = self.query_one("#tool-list", ListView)
        if tool_list.highlighted_child:
            item = tool_list.highlighted_child
            if isinstance(item, ToolListItem):
                return item.tool_info
        return None
