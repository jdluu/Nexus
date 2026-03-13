"""Screen for selecting the application theme.

Provides a modal interface to browse available themes with real time
preview functionality using the Textual OptionList widget.
"""

from typing import Any, Callable
from textual import on
from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Container
from textual.screen import ModalScreen
from textual.widgets import Label, OptionList, Header, Footer
from textual.widgets.option_list import Option


class ThemePicker(ModalScreen[str | None]):
    """A modal screen for theme selection and preview.

    Attributes:
        themes: List of available theme CSS identifiers.
        original_theme: The theme that was active when the picker was opened.
        on_preview_callback: Function called to apply a preview theme.
    """

    def __init__(
        self,
        themes: list[str],
        current_theme: str,
        on_preview: Callable[[str], None],
        **kwargs: Any,
    ):
        """Initializes the ThemePicker.

        Args:
            themes: List of available theme CSS class names.
            current_theme: The active theme class name.
            on_preview: Callback function to preview a selected theme.
            **kwargs: Additional keyword arguments passed to ModalScreen.
        """
        super().__init__(**kwargs)
        self.themes = themes
        self.original_theme = current_theme
        self.on_preview_callback = on_preview

    BINDINGS = [
        Binding("enter", "select", "Confirm"),
        Binding("escape", "cancel", "Cancel"),
    ]

    def compose(self) -> ComposeResult:
        """Composes the visual layout of the theme picker.

        Returns:
            A ComposeResult containing the visual widget hierarchy.
        """
        yield Header()
        with Container(classes="modal-dialog"):
            yield Label("Select Theme", classes="modal-title")
            yield OptionList(id="theme-option-list")
        yield Footer()

    def on_mount(self) -> None:
        """Populates the list of themes and selects the current theme."""
        option_list = self.query_one("#theme-option-list", OptionList)

        for theme in self.themes:
            display_name = theme.replace("theme-", "").title()
            option_list.add_option(Option(display_name, id=theme))

        try:
            current_index = self.themes.index(self.original_theme)
            option_list.highlighted = current_index
        except ValueError:
            option_list.highlighted = 0

        option_list.focus()

    @on(OptionList.OptionHighlighted)
    def _on_theme_highlighted(self, event: OptionList.OptionHighlighted) -> None:
        """Triggers a theme preview when a theme is highlighted in the list."""
        if event.option_index is not None:
            new_theme = self.themes[event.option_index]
            self.on_preview_callback(new_theme)

    @on(OptionList.OptionSelected)
    def _on_theme_selected(self, event: OptionList.OptionSelected) -> None:
        """Confirms and applies the selected theme."""
        if event.option_index is not None:
            new_theme = self.themes[event.option_index]
            self.dismiss(new_theme)

    def action_select(self) -> None:
        """Confirms selection (used by footer)."""
        option_list = self.query_one("#theme-option-list", OptionList)
        if option_list.highlighted is not None:
            new_theme = self.themes[option_list.highlighted]
            self.dismiss(new_theme)

    def action_cancel(self) -> None:
        """Reverts the theme to the original state and dismisses the modal."""
        self.on_preview_callback(self.original_theme)
        self.dismiss(None)
