"""Custom list items for the Nexus TUI.

Defines specialized ListItem widgets for displaying tool categories with 
consistent formatting and visual indicators.
"""

from typing import Any
from nexus.config import USE_NERD_FONTS
from textual.app import ComposeResult
from textual.widgets import ListItem, Label


class CategoryListItem(ListItem):
    """A specialized ListItem for tool categories.

    Attributes:
        category_id: The unique identifier for the category.
    """

    ICONS = {
        "DEV": "",
        "AI": "",
        "MEDIA": "",
        "UTIL": "",
        "ALL": "",
    }

    DEFAULT_ICON = ""

    def __init__(self, category: str, **kwargs: Any):
        """Initializes the CategoryListItem.

        Args:
            category: The category identifier.
            **kwargs: Additional arguments passed to ListItem.
        """
        self.category_id = category
        super().__init__(**kwargs)

    def compose(self) -> ComposeResult:
        """Composes the visual content of the category item.

        Returns:
            A ComposeResult containing the formatted label.
        """
        icon = ""
        if USE_NERD_FONTS:
            icon_char = self.ICONS.get(self.category_id, self.DEFAULT_ICON)
            icon = f"{icon_char} "

        if self.category_id == "ALL":
            text = f"{icon}ALL"
        else:
            text = f"[◼] {icon}{self.category_id}"
            
        yield Label(text)
