"""Screen for selecting the application theme.

Provides a modal list of available themes with live preview capability.
"""

from typing import Any, Callable
from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Container
from textual.screen import ModalScreen
from textual.widgets import Label, ListItem, ListView


class ThemePicker(ModalScreen[None]):
    """A modal screen for selecting a theme with live preview.

    Attributes:
        themes: List of available theme CSS classes.
        original_theme: The theme active when the picker was opened.
        on_preview_callback: Callback function to apply a preview theme.
    """

    CSS_PATH = "../style.tcss"

    def __init__(
        self, themes: list[str], current_theme: str, on_preview: Callable[[str], None], **kwargs: Any
    ):
        """Initializes the ThemePicker.

        Args:
            themes: List of available theme CSS class names.
            current_theme: The currently active theme class name.
            on_preview: Callback to receive the selected theme string for preview.
            **kwargs: Additional arguments passed to ModalScreen.
        """
        super().__init__(**kwargs)
        self.themes = themes
        self.original_theme = current_theme
        self.on_preview_callback = on_preview

    BINDINGS = [
        Binding("escape", "cancel", "Cancel"),
    ]

    def compose(self) -> ComposeResult:
        """Composes the screen layout.

        Returns:
            A ComposeResult containing the widget tree.
        """
        with Container(id="theme-picker-dialog"):
            yield Label("Select Theme", id="theme-picker-title")
            yield ListView(id="theme-list")
            yield Label("Esc: Cancel • Enter: Confirm", classes="modal-footer")

    def on_mount(self) -> None:
        """Called when the screen is mounted.

        Populates the list of themes.
        """
        list_view = self.query_one("#theme-list", ListView)
        for theme in self.themes:
            # Clean up theme name for display (e.g., "theme-dark" -> "Tokyo Night Dark")
            suffix = theme.replace("theme-", "").title()
            display_name = f"Tokyo Night {suffix}"
            item = ListItem(Label(display_name))
            list_view.append(item)

        # Select current theme
        try:
            current_index = self.themes.index(self.original_theme)
            list_view.index = current_index
        except ValueError:
            list_view.index = 0

    def on_list_view_highlighted(self, event: ListView.Highlighted) -> None:
        """Previews the confirmed theme when highlighted.

        Args:
            event: The highlight event.
        """
        if event.list_view.index is not None:
            # Prevent index out of bounds if list changes (unlikely)
            if 0 <= event.list_view.index < len(self.themes):
                new_theme = self.themes[event.list_view.index]
                self.on_preview_callback(new_theme)

    def on_list_view_selected(self, event: ListView.Selected) -> None:
        """Confirms the selected theme.

        Args:
            event: The selection event.
        """
        # Theme is already applied by highlight, just close
        self.dismiss()

    def action_cancel(self) -> None:
        """Reverts the theme choice and closes the picker."""
        self.on_preview_callback(self.original_theme)
        self.dismiss()

