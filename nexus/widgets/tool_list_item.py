"""Custom list items for the Nexus TUI.

Defines the specialized ListItem widgets used to display tools, categories,
and projects with specific formatting and visual indicators.
"""

from nexus.config import CATEGORY_COLORS, CATEGORY_ICONS, USE_NERD_FONTS
from nexus.models import Project, Tool
from textual.widgets import ListItem, Static


class ToolItem(Static):
    """A widget representing a tool in the list."""

    def __init__(self, tool_info: Tool, hint: str = "", **kwargs):
        """Initializes the ToolItem.

        Args:
            tool_info: The Tool model containing tool details.
            hint: Optional numeric hint (e.g. '1').
            **kwargs: Additional arguments passed to the Static widget.
        """
        super().__init__(**kwargs)
        self.tool_info = tool_info
        self.hint = hint
        self.can_focus = True

    def render(self) -> str:
        """Renders the tool item.

        Returns:
            A string representation of the tool label prefixed with '> '.
        """
        hint_str = f"[bold magenta]{self.hint}[/] " if self.hint else ""
        label = self.tool_info.label
        return f"{hint_str}> {label} | [dim]{self.tool_info.description}[/]"

    def on_mount(self) -> None:
        """Called when the widget is mounted.

        Adds specific CSS classes for styling.
        """
        self.add_class("list-item")
        self.add_class(f"category-{self.tool_info.category}")


class ProjectItem(Static):
    """A widget representing a project in the list."""

    def __init__(
        self,
        project_name: str,
        is_git: bool = False,
        is_special: bool = False,
        **kwargs,
    ):
        """Initializes the ProjectItem.

        Args:
            project_name: The name of the project.
            is_git: Whether the project is a git repository.
            is_special: Whether this item is a special action (e.g. Create new).
            **kwargs: Additional arguments passed to the Static widget.
        """
        super().__init__(**kwargs)
        self.project_name = project_name
        self.is_git = is_git
        self.is_special = is_special
        self.can_focus = True

    def render(self) -> str:
        """Renders the project item.

        Returns:
            A string with an icon (if git repo) and the project name, or a
            styled string for special items.
        """
        icon = " " if self.is_git else "  "
        if self.is_special:
            return f"[bold cyan]{self.project_name}[/]"
        return f"{icon}{self.project_name}"

    def on_mount(self) -> None:
        """Called when the widget is mounted."""
        self.add_class("list-item")


class ToolListItem(ListItem):
    """A typed ListItem for tools.

    Attributes:
        tool_info: The Tool model associated with this item.
    """

    def __init__(self, tool_info: Tool, hint: str = "", **kwargs):
        """Initializes the ToolListItem.

        Args:
            tool_info: The Tool model.
            hint: Optional numeric hint.
            **kwargs: Additional arguments passed to the ListItem.
        """
        self.tool_info = tool_info
        super().__init__(ToolItem(tool_info, hint=hint), **kwargs)


class ProjectListItem(ListItem):
    """A typed ListItem for projects.

    Attributes:
        project_data: The Project model, or None if this is a special item.
        is_create_new: True if this item represents the "Create New Project" action.
    """

    def __init__(
        self,
        project_data: Project | None = None,
        is_create_new: bool = False,
        **kwargs,
    ):
        """Initializes the ProjectListItem.

        Args:
            project_data: The Project model. Required unless is_create_new is True.
            is_create_new: Whether this is a "Create New" action item.
            **kwargs: Additional arguments passed to the ListItem.

        Raises:
            ValueError: If project_data is None and is_create_new is False.
        """
        self.project_data = project_data
        self.is_create_new = is_create_new

        if is_create_new:
            widget = ProjectItem("[ + ] Create New Project", is_special=True)
        else:
            if project_data is None:
                raise ValueError("project_data must be provided if is_create_new is False")
            widget = ProjectItem(project_data.name, is_git=project_data.is_git)

        super().__init__(widget, **kwargs)


class CategoryListItem(ListItem):
    """A typed ListItem for categories.

    Attributes:
        category_id: The category identifier string.
    """

    def __init__(self, category: str, **kwargs):
        """Initializes the CategoryListItem.

        Args:
            category: The category name.
            **kwargs: Additional arguments.
        """
        self.category_id = category
        super().__init__(**kwargs)

    def render(self) -> str:
        """Renders the category item with a colored badge.

        Returns:
            The formatted string for the category list item.
        """
        icon = ""
        if USE_NERD_FONTS:
            icon = f"{CATEGORY_ICONS.get(self.category_id, '')} "

        if self.category_id == "ALL":
            return f"{icon}ALL"

        color = CATEGORY_COLORS.get(self.category_id, "white")
        return f"[{color}]◼[/] {icon}{self.category_id}"

# Summary:
# Formatted docstrings to strict Google Style.
# Added return type documentation.