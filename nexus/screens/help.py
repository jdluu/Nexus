"""Help screen for the Nexus application.

Displays information regarding user interface interactions and global
key bindings using the modern Collapsible widget from Textual.
"""

from textual import on
from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal, Vertical, VerticalScroll
from textual.screen import ModalScreen
from textual.widgets import Button, Label, Markdown, Collapsible, Header, Footer


class HelpScreen(ModalScreen[None]):
    """A modal screen that displays help documentation and key bindings."""

    BINDINGS = [
        Binding("escape", "dismiss", "Close"),
        Binding("q", "dismiss", "Close", show=False),
    ]

    def compose(self) -> ComposeResult:
        """Composes the visual layout of the help screen.

        Returns:
            A ComposeResult containing the documentation widgets.
        """
        yield Header()
        with Vertical(classes="modal-dialog"):
            yield Label("Nexus Help", classes="modal-title")

            with VerticalScroll(id="help-content"):
                with Collapsible(title="Navigation", collapsed=False):
                    yield Markdown(
                        """
- `Up / Down` : Navigate lists
- `Left / Right` : Switch between Categories and Tool List
- `Enter` : Select Category or Launch Tool
- `Esc` : Return to previous view
                        """
                    )

                with Collapsible(title="Search"):
                    yield Markdown(
                        """
- Type any character to start searching tools.
- `Ctrl+P` : Open the global Command Palette.
                        """
                    )

                with Collapsible(title="Actions"):
                    yield Markdown(
                        """
- `Ctrl+T` : Open the Theme Picker
- `Ctrl+Q` : Exit the application
- `F1` : Display this help screen
                        """
                    )

            with Horizontal(classes="modal-footer-actions"):
                yield Button("Close", variant="primary", id="btn-close")

        yield Footer()

    @on(Button.Pressed, "#btn-close")
    def _on_close(self) -> None:
        """Handles the close button click."""
        self.dismiss()
