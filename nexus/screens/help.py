"""Help screen for the Nexus application.

Displays information about key bindings and usage.
"""

from textual.app import ComposeResult
from textual.containers import Horizontal, Vertical
from textual.screen import ModalScreen
from textual.widgets import Button, Label, Markdown


class HelpScreen(ModalScreen[None]):
    """A modal screen that displays help and key bindings."""

    CSS_PATH = "../style.tcss"

    BINDINGS = [
        ("escape", "dismiss", "Close"),
        ("q", "dismiss", "Close"),
    ]

    def compose(self) -> ComposeResult:
        """Composes the screen layout.

        Returns:
            A ComposeResult containing the widget tree.
        """
        with Vertical(id="help-dialog"):
            with Horizontal(id="help-title-container"):
                yield Label("Nexus Help", id="help-title")

            with Vertical(id="help-content"):
                yield Markdown(
                    """
**Navigation**
- `↑ / ↓` : Navigate lists
- `← / →` : Switch between Categories and Tool List
- `Enter` : Select Category or Launch Tool

**Search**
- Type any character to start searching tools.
- `Esc` : Clear search or Go Back.

**System**
- `Ctrl+t` : Open Theme Picker
- `Ctrl+c` : Quit Application
- `?` or `F1`: Show this Help Screen
                    """
                )

            with Horizontal(id="help-footer"):
                yield Button("Close", variant="primary", id="btn-close")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handles button press events.

        Args:
            event: The button pressed event.
        """
        if event.button.id == "btn-close":
            self.dismiss()

# Summary:
# Formatted docstrings to strict Google Style.
# Added module docstring.
