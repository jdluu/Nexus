"""Widget for browsing tools by category.

Encapsulates the dual-pane layout containing the category list and
the filtered tool list using Textual's OptionList for performance.
"""

from textual import work
from textual.app import ComposeResult
from textual.containers import Horizontal, Vertical
from textual.message import Message
from textual.reactive import reactive
from textual.widget import Widget
from textual.widgets import Label, ListView, OptionList
from textual.widgets.option_list import Option

from nexus.models import Tool
from nexus.container import get_container
from nexus.widgets.tool_list_item import CategoryListItem


class ToolBrowser(Widget):
    """A dual-pane interface for browsing categories and tools.

    Attributes:
        search_query: The current text used to filter tool labels and descriptions.
        selected_category: The identifier of the currently selected category.
        _filtered_tools: Cached list of tools currently displayed.
    """

    class ToolSelected(Message):
        """Message transmitted when a tool is selected by the user.

        Attributes:
            tool: The Tool model representing the selection.
        """

        def __init__(self, tool: Tool) -> None:
            """Initializes the ToolSelected message.

            Args:
                tool: The selected Tool.
            """
            self.tool = tool
            super().__init__()

    class ToolHighlighted(Message):
        """Message transmitted when a tool is highlighted in the list.

        Attributes:
            tool: The Tool model representing the highlight.
        """

        def __init__(self, tool: Tool) -> None:
            """Initializes the ToolHighlighted message.

            Args:
                tool: The highlighted Tool.
            """
            self.tool = tool
            super().__init__()

    search_query = reactive("")
    selected_category = reactive("ALL")
    _filtered_tools: list[Tool] = []

    def compose(self) -> ComposeResult:
        """Composes the dual-pane visual layout.

        Returns:
            A ComposeResult containing the category and tool list panes.
        """
        with Vertical(id="left-pane"):
            yield Label("Categories", classes="pane-header")
            yield ListView(id="category-list")

        with Vertical(id="right-pane"):
            with Horizontal(classes="pane-header-container"):
                yield Label("Toolbox", classes="pane-header")
                yield Label("Tip: F1 for controls", classes="pane-header-right")

            yield OptionList(id="tool-list")
            yield Label(
                "No tools found", id="tools-empty", classes="empty-state hidden"
            )

    def on_mount(self) -> None:
        """Initializes the category list and sets default focus on mount."""
        # Use call_after_refresh to ensure the ListView/OptionList are ready
        self.call_after_refresh(self._initial_populate)

    def _initial_populate(self) -> None:
        """Performs the first data load and sets initial category."""
        self.populate_categories()

        category_list = self.query_one("#category-list", ListView)
        if len(category_list.children) > 0:
            category_list.index = 0

        self.populate_tools("ALL")

    def watch_search_query(self, new_value: str) -> None:
        """Reacts to changes in the search query by filtering tools.

        Automatically selects the 'ALL' category when a search is active.

        Args:
            new_value: The updated search query string.
        """
        if new_value:
            self.selected_category = "ALL"
            self.select_all_category()

        self.populate_tools(self.selected_category, filter_text=new_value)

    def watch_selected_category(self, new_value: str) -> None:
        """Reacts to category changes."""
        self.populate_tools(new_value, filter_text=self.search_query)

    def select_all_category(self) -> None:
        """Sets the active selection to the 'ALL' category."""
        category_list = self.query_one("#category-list", ListView)
        for idx, child in enumerate(category_list.children):
            if isinstance(child, CategoryListItem) and child.category_id == "ALL":
                if category_list.index != idx:
                    category_list.index = idx
                break

    def populate_categories(self) -> None:
        """Populates the category list based on configured tools."""
        category_list = self.query_one("#category-list", ListView)
        category_list.clear()

        tools = get_container().config_manager.get_tools()
        categories = sorted(list(set(t.category for t in tools)))

        category_list.append(CategoryListItem("ALL"))

        for category in categories:
            category_list.append(CategoryListItem(category))

    @work(exclusive=True)
    async def populate_tools(self, category: str, filter_text: str = "") -> None:
        """Populates the tool list based on category and filter text.

        Args:
            category: The category identifier to display.
            filter_text: Optional text to filter tool names and descriptions.
        """
        try:
            option_list = self.query_one("#tool-list", OptionList)
        except Exception:
            # Widget not yet available
            return

        option_list.loading = True

        # Fetch tools from container
        tools = get_container().config_manager.get_tools()

        if category == "ALL":
            filtered_tools = tools
        else:
            filtered_tools = [t for t in tools if t.category == category]

        if filter_text:
            filtered_tools = [
                t
                for t in filtered_tools
                if filter_text.lower() in t.label.lower()
                or filter_text.lower() in t.description.lower()
            ]

        self._filtered_tools = filtered_tools

        try:
            empty_lbl = self.query_one("#tools-empty", Label)
            option_list.clear_options()

            if filtered_tools:
                option_list.display = True
                empty_lbl.add_class("hidden")

                for tool in filtered_tools:
                    label = f"> [bold]{tool.label}[/] | [dim]{tool.description}[/]"
                    option_list.add_option(Option(label, id=tool.command))

                option_list.highlighted = 0
            else:
                option_list.display = False
                empty_lbl.remove_class("hidden")
                if filter_text:
                    empty_lbl.update(f"No tools matching '{filter_text}'")
                else:
                    empty_lbl.update(f"No tools in category '{category}'")
        except Exception:
            pass
        finally:
            option_list.loading = False

    def on_list_view_highlighted(self, event: ListView.Highlighted) -> None:
        """Handles highlight events for the category list."""
        if event.list_view.id == "category-list":
            if isinstance(event.item, CategoryListItem):
                self.selected_category = event.item.category_id

    def on_list_view_selected(self, event: ListView.Selected) -> None:
        """Handles selection events for the category list."""
        if event.list_view.id == "category-list":
            self.query_one("#tool-list").focus()

    def on_option_list_option_highlighted(
        self, event: OptionList.OptionHighlighted
    ) -> None:
        """Handles highlight events for the tool list."""
        if event.option_index is not None and 0 <= event.option_index < len(
            self._filtered_tools
        ):
            tool = self._filtered_tools[event.option_index]
            self.post_message(self.ToolHighlighted(tool))

    def on_option_list_option_selected(self, event: OptionList.OptionSelected) -> None:
        """Handles selection events for the tool list."""
        if event.option_index is not None and 0 <= event.option_index < len(
            self._filtered_tools
        ):
            tool = self._filtered_tools[event.option_index]
            self.post_message(self.ToolSelected(tool))

    def focus_next(self) -> None:
        """Navigates to the next item in the currently focused list."""
        if self.query_one("#category-list").has_focus:
            self._move_list_cursor("#category-list", 1)
        elif self.query_one("#tool-list").has_focus:
            option_list = self.query_one("#tool-list", OptionList)
            if option_list.highlighted is not None:
                option_list.highlighted = min(
                    len(self._filtered_tools) - 1, option_list.highlighted + 1
                )
            else:
                option_list.highlighted = 0

    def focus_prev(self) -> None:
        """Navigates to the previous item in the currently focused list."""
        if self.query_one("#category-list").has_focus:
            self._move_list_cursor("#category-list", -1)
        elif self.query_one("#tool-list").has_focus:
            option_list = self.query_one("#tool-list", OptionList)
            if option_list.highlighted is not None:
                option_list.highlighted = max(0, option_list.highlighted - 1)
            else:
                option_list.highlighted = 0

    def _move_list_cursor(self, list_id: str, delta: int) -> None:
        """Moves the list selection index by a specified delta."""
        lst = self.query_one(list_id, ListView)
        if lst.index is None:
            lst.index = 0
        else:
            new_index = lst.index + delta
            new_index = max(0, min(len(lst.children) - 1, new_index))
            lst.index = new_index

    def focus_right(self) -> None:
        """Transfers focus from the category list to the tool list."""
        if self.query_one("#category-list").has_focus:
            self.query_one("#tool-list").focus()

    def focus_left(self) -> None:
        """Transfers focus from the tool list to the category list."""
        if self.query_one("#tool-list").has_focus:
            self.query_one("#category-list").focus()

    def get_tool_at_index(self, index: int) -> Tool | None:
        """Retrieves the tool at a specified index in the current tool list."""
        if 0 <= index < len(self._filtered_tools):
            return self._filtered_tools[index]
        return None

    def get_current_selection(self) -> Tool | None:
        """Retrieves the currently selected tool in the tool list."""
        option_list = self.query_one("#tool-list", OptionList)
        if option_list.highlighted is not None and 0 <= option_list.highlighted < len(
            self._filtered_tools
        ):
            return self._filtered_tools[option_list.highlighted]
        return None
