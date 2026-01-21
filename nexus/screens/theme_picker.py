from textual.app import ComposeResult
from textual.screen import ModalScreen
from textual.widgets import ListView, ListItem, Label
from textual.containers import Container, Vertical
from textual.binding import Binding

class ThemePicker(ModalScreen):
    """A modal screen for selecting a theme with live preview."""

    CSS_PATH = "../style.tcss"

    def __init__(self, themes: list[str], current_theme: str, on_preview: callable, **kwargs):
        super().__init__(**kwargs)
        self.themes = themes
        self.original_theme = current_theme
        self.on_preview_callback = on_preview
        
    BINDINGS = [
        Binding("escape", "cancel", "Cancel"),
    ]

    def compose(self) -> ComposeResult:
        with Container(id="theme-picker-dialog"):
            yield Label("Select Theme", id="theme-picker-title")
            yield ListView(id="theme-list")
            yield Label("Esc: Cancel • Enter: Confirm", classes="modal-footer")

    def on_mount(self) -> None:
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
        """Preview theme on highlight."""
        if event.list_view.index is not None:
             # Prevent index out of bounds if list changes (unlikely)
            if 0 <= event.list_view.index < len(self.themes):
                new_theme = self.themes[event.list_view.index]
                self.on_preview_callback(new_theme)

    def on_list_view_selected(self, event: ListView.Selected) -> None:
        """Confirm selection."""
        # Theme is already applied by highlight, just close
        self.dismiss()

    def action_cancel(self) -> None:
        """Revert and close."""
        self.on_preview_callback(self.original_theme)
        self.dismiss()
