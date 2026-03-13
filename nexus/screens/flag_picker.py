"""Screen for entering custom command line flags.

Provides a modal interface for users to enter additional arguments
before launching a tool.
"""

from typing import Any

from textual import on
from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Container, Horizontal
from textual.screen import ModalScreen
from textual.widgets import Button, Input, Label, Header, Footer


class FlagPicker(ModalScreen[str | None]):
    """A modal screen for entering custom command line flags."""

    def __init__(self, tool_label: str, **kwargs: Any):
        """Initializes the FlagPicker screen.

        Args:
            tool_label: The human readable label of the tool being launched.
            **kwargs: Additional keyword arguments passed to ModalScreen.
        """
        super().__init__(**kwargs)
        self.tool_label = tool_label

    BINDINGS = [
        Binding("enter", "submit", "Launch"),
        Binding("escape", "cancel", "Skip"),
    ]

    def compose(self) -> ComposeResult:
        """Composes the layout of the modal screen.

        Returns:
            The composed Textual layout for the flag picker.
        """
        yield Header()
        with Container(classes="modal-dialog"):
            yield Label(f"Flags for {self.tool_label}", classes="modal-title")
            yield Label(
                "Enter additional command-line arguments (optional):",
                classes="flag-help",
            )
            yield Input(placeholder="e.g. --verbose -f config.yaml", id="flag-input")

            with Horizontal(classes="modal-footer-actions"):
                yield Button("Skip", variant="default", id="btn-skip")
                yield Button("Launch", variant="primary", id="btn-submit")
        yield Footer()

    def on_mount(self) -> None:
        """Focuses the flag input on mount."""
        self.query_one("#flag-input").focus()

    @on(Input.Submitted, "#flag-input")
    @on(Button.Pressed, "#btn-submit")
    def action_submit(self) -> None:
        """Submits the entered flags and dismisses the modal."""
        flags = self.query_one("#flag-input", Input).value.strip()
        self.dismiss(flags)

    @on(Button.Pressed, "#btn-skip")
    def action_cancel(self) -> None:
        """Skips flag entry and dismisses the modal."""
        self.dismiss("")
