"""Main application entry point for Nexus.

Configures the Textual application class, global bindings, and initial screen loading.
"""

from typing import Any
from textual.app import App
from textual.notifications import SeverityLevel
from nexus.container import get_container
from nexus.screens.tool_selector import ToolSelector


class NexusApp(App[None]):
    """The main Nexus application class.

    Manages the application lifecycle, global bindings, and screen navigation.
    """

    CSS_PATH = "style.tcss"
    BINDINGS = [
        ("ctrl+q", "quit", "Quit"),
        ("ctrl+c", "quit", "Quit"),
        ("ctrl+b", "back", "Back"),
    ]

    def on_mount(self) -> None:
        """Called when the application is mounted.

        Push the ToolSelector screen to the stack on startup.
        """
        # Initialize services
        self.container = get_container()
        
        # Apply keybindings from config
        self._apply_bindings()
        
        self.push_screen(ToolSelector())

    def _apply_bindings(self) -> None:
        """Applies configurable keybindings."""
        from nexus.config import get_keybindings
        bindings = get_keybindings()
        
        if "quit" in bindings:
            self.bind(keys=bindings["quit"], action="quit", description="Quit")
        if "force_quit" in bindings:
            self.bind(keys=bindings["force_quit"], action="quit", description="Quit")
        if "back" in bindings:
            self.bind(keys=bindings["back"], action="back", description="Back")

    async def action_back(self) -> None:
        """Navigates back to the previous screen.

        Removes the current screen from the stack if there is more than one
        screen present.
        """
        if len(self.screen_stack) > 1:
            self.pop_screen()

    def notify(
        self,
        message: str,
        *,
        title: str = "",
        severity: SeverityLevel = "information",
        timeout: float | None = 1.0,
        **kwargs: Any,
    ) -> None:
        """Override notify to use a shorter default timeout.

        Args:
            message: The message to display.
            title: The title of the notification.
            severity: The severity of the notification (e.g., 'information', 'error').
            timeout: Duration in seconds to show the notification.
            **kwargs: Additional keyword arguments passed to the parent notify method.
        """
        super().notify(
            message, title=title, severity=severity, timeout=timeout, **kwargs
        )

    def show_error(self, title: str, message: str, details: str = "") -> None:
        """Displays a modal error screen.

        Args:
            title: The title of the error.
            message: The user-friendly error message.
            details: Optional technical details.
        """
        from nexus.screens.error import ErrorScreen

        self.push_screen(ErrorScreen(title, message, details))


def main() -> None:
    """Entry point for the application."""
    from nexus.logger import configure_logging

    configure_logging()
    app = NexusApp()
    app.run()


if __name__ == "__main__":
    main()

