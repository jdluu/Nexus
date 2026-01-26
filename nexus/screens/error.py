"""Generic Error Screen for Nexus.

Displays an error message and functionality to dismiss or copy details.
"""

from typing import Any

from textual.app import ComposeResult
from textual.containers import Container, Horizontal, Vertical
from textual.screen import ModalScreen
from textual.widgets import Button, Label, Static


class ErrorScreen(ModalScreen[None]):
    """A modal screen that displays an error message."""

    CSS_PATH = "../style.tcss"

    def __init__(
        self,
        title: str,
        message: str,
        details: str = "",
        **kwargs: Any,
    ):
        """Initializes the ErrorScreen.

        Args:
            title: The title of the error.
            message: The main error message.
            details: Optional technical details.
            **kwargs: Additional arguments.
        """
        super().__init__(**kwargs)
        self.error_title = title
        self.error_message = message
        self.error_details = details

    def compose(self) -> ComposeResult:
        """Composes the screen layout."""
        with Container(id="error-dialog"):
            with Horizontal(id="error-header"):
                yield Label("Error", classes="error-icon")
                yield Label(self.error_title, id="error-title")
            
            with Vertical(id="error-body"):
                yield Label(self.error_message, id="error-message")
                if self.error_details:
                    yield Static(self.error_details, id="error-details")

            with Horizontal(id="error-footer"):
                yield Button("Close", variant="error", id="btn-error-close")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handles button presses."""
        if event.button.id == "btn-error-close":
            self.dismiss()
