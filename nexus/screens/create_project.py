"""Screen for creating a new project.

Collects user input for a new project directory name and creates the directory.
"""

import os

from nexus.config import PROJECT_ROOT
from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Container, Horizontal
from textual.screen import ModalScreen
from textual.widgets import Button, Input, Label


class CreateProject(ModalScreen):
    """A modal screen for creating a new project.

    Attributes:
        on_created_callback: Callback function called with the new project name upon success.
    """

    CSS_PATH = "../style.tcss"

    def __init__(self, on_created: callable, **kwargs):
        """Initializes the CreateProject screen.

        Args:
            on_created: Callback function (str) -> None.
            **kwargs: Additional arguments passed to ModalScreen.
        """
        super().__init__(**kwargs)
        self.on_created_callback = on_created

    BINDINGS = [
        Binding("escape", "cancel", "Cancel"),
    ]

    def compose(self) -> ComposeResult:
        """Composes the screen layout.

        Returns:
            A ComposeResult containing the widget tree.
        """
        with Container(id="create-project-dialog"):
            yield Label("Create New Project", id="create-project-title")
            yield Input(placeholder="Project Name", id="project-name-input")
            yield Label("", id="create-error", classes="error-label hidden")

            with Horizontal(id="create-project-buttons"):
                yield Button("Cancel", variant="default", id="btn-cancel")
                yield Button("Create", variant="primary", id="btn-create")

    def on_mount(self) -> None:
        """Called when the screen is mounted."""
        self.query_one("#project-name-input").focus()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handles button press events.

        Args:
            event: The button pressed event.
        """
        if event.button.id == "btn-cancel":
            self.action_cancel()
        elif event.button.id == "btn-create":
            self.create_project()

    def on_input_submitted(self, event: Input.Submitted) -> None:
        """Handles enter key in input field.

        Args:
            event: The input submitted event.
        """
        self.create_project()

    def create_project(self) -> None:
        """Validates input and attempts to create the project directory."""
        name = self.query_one("#project-name-input").value.strip()
        if not name:
            self.show_error("Project name cannot be empty.")
            return

        project_path = PROJECT_ROOT / name

        if project_path.exists():
            self.show_error("Project already exists.")
            return

        try:
            os.makedirs(project_path)
            self.dismiss()
            if self.on_created_callback:
                self.on_created_callback(name)
        except Exception as e:
            self.show_error(f"Error: {e}")

    def show_error(self, message: str) -> None:
        """Displays an error message to the user.

        Args:
            message: The error description.
        """
        lbl = self.query_one("#create-error", Label)
        lbl.update(message)
        lbl.remove_class("hidden")

    def action_cancel(self) -> None:
        """Cancels the action and closes the modal."""
        self.dismiss()

# Summary:
# Formatted docstrings to strict Google Style.
# Added module docstring.
