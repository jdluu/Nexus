"""Modal screen for confirming application exit.

Provides a simple dialog to prevent accidental closures of the application.
"""

from textual import on
from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Container, Horizontal
from textual.screen import ModalScreen
from textual.widgets import Button, Label


class QuitConfirmation(ModalScreen[bool]):
    """A modal dialog for confirming application quit."""

    BINDINGS = [
        Binding("enter,y", "confirm", "Quit"),
        Binding("escape,n", "cancel", "Cancel"),
    ]

    def compose(self) -> ComposeResult:
        """Composes the visual layout of the quit confirmation modal."""
        with Container(classes="modal-dialog"):
            yield Label("Quit Nexus", classes="modal-title")
            yield Label("Are you sure you want to quit?", id="quit-label")
            with Horizontal(classes="modal-footer-actions"):
                yield Button("Cancel", variant="default", id="btn-cancel")
                yield Button("Quit", variant="error", id="btn-quit")

    @on(Button.Pressed, "#btn-quit")
    def action_confirm(self) -> None:
        """Confirms the quit action."""
        self.dismiss(True)

    @on(Button.Pressed, "#btn-cancel")
    def action_cancel(self) -> None:
        """Cancels the quit action."""
        self.dismiss(False)
