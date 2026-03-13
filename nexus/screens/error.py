"""Generic Error Screen for Nexus.

Displays detailed error information and provides a mechanism to dismiss the view.
"""

from typing import Any

from textual import on
from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Container, Horizontal, Vertical
from textual.screen import ModalScreen
from textual.widgets import Button, Label, Static, Header, Footer


class ErrorScreen(ModalScreen[None]):
    """A modal screen that displays application errors.

    Attributes:
        error_title: The high level error identifier.
        error_message: A descriptive error message.
        error_details: Technical details for diagnostic purposes.
    """

    BINDINGS = [
        Binding("escape,enter,space", "dismiss", "Close"),
    ]


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
            message: The main descriptive message.
            details: Optional technical diagnostic information.
            **kwargs: Additional keyword arguments passed to ModalScreen.
        """
        super().__init__(**kwargs)
        self.error_title = title
        self.error_message = message
        self.error_details = details

    def compose(self) -> ComposeResult:
        """Composes the layout of the error dialog.

        Returns:
            A ComposeResult containing the visual widget tree.
        """
        yield Header()
        with Container(classes="modal-dialog"):
            yield Label(f"Error: {self.error_title}", classes="modal-title")
            
            with Vertical(id="error-body"):
                yield Label(self.error_message, id="error-message")
                if self.error_details:
                    yield Static(self.error_details, id="error-details")

            with Horizontal(classes="modal-footer-actions"):
                yield Button("Close", variant="error", id="btn-error-close")
        yield Footer()

    @on(Button.Pressed, "#btn-error-close")
    def _on_close(self) -> None:
        """Handles the close button click."""
        self.dismiss()
