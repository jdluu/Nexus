"""Screen for creating a new project directory.

Provides a modal interface for users to enter a new project name and
initialize a directory within the configured project root.
"""

from pathlib import Path
from typing import Any

from textual import on
from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Container, Horizontal
from textual.screen import ModalScreen
from textual.widgets import Button, Input, Label, Header, Footer


class CreateProject(ModalScreen[Path | None]):
    """A modal screen for creating a new project directory."""

    def __init__(self, project_root: Path, **kwargs: Any):
        """Initializes the CreateProject screen.

        Args:
            project_root: The base directory where the project will be created.
            **kwargs: Additional keyword arguments passed to ModalScreen.
        """
        super().__init__(**kwargs)
        self.project_root = project_root

    BINDINGS = [
        Binding("enter", "submit", "Create"),
        Binding("escape", "cancel", "Cancel"),
    ]

    def compose(self) -> ComposeResult:
        """Composes the visual layout of the project creation modal.

        Returns:
            A ComposeResult containing the visual widget hierarchy.
        """
        yield Header()
        with Container(classes="modal-dialog"):
            yield Label("Create New Project", classes="modal-title")
            yield Input(placeholder="Project Name", id="project-name-input")
            yield Label("", id="create-error", classes="error-label hidden")

            with Horizontal(classes="modal-footer-actions"):
                yield Button("Cancel", variant="default", id="btn-cancel")
                yield Button("Create", variant="primary", id="btn-create")
        yield Footer()

    def on_mount(self) -> None:
        """Focuses the project name input on mount."""
        self.query_one("#project-name-input").focus()

    @on(Button.Pressed, "#btn-create")
    def action_submit(self) -> None:
        """Validates and processes the project creation request."""
        name = self.query_one("#project-name-input", Input).value.strip()
        error_label = self.query_one("#create-error", Label)

        if not name:
            error_label.update("Project name cannot be empty")
            error_label.remove_class("hidden")
            return

        project_path = self.project_root / name
        if project_path.exists():
            error_label.update("Directory already exists")
            error_label.remove_class("hidden")
            return

        try:
            project_path.mkdir(parents=True, exist_ok=True)
            self.dismiss(project_path)
        except Exception as e:
            error_label.update(f"Error: {e}")
            error_label.remove_class("hidden")

    @on(Button.Pressed, "#btn-cancel")
    def action_cancel(self) -> None:
        """Cancels the project creation and dismisses the modal."""
        self.dismiss(None)
