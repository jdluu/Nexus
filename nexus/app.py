from textual.app import App
from nexus.screens.tool_selector import ToolSelector

"""Main application entry point for Nexus.

Configures the Textual application class, global bindings, and initial screen loading.
"""

class NexusApp(App):
    """The main Nexus application class.
    
    Manages the application lifecycle, global bindings, and screen navigation.
    """
    
    CSS_PATH = "style.tcss"
    BINDINGS = [
        ("q", "quit", "Quit"),
        ("ctrl+c", "quit", "Quit"),
        ("escape", "back", "Back"),
    ]

    def on_mount(self) -> None:
        """Called when the application is mounted."""
        self.push_screen(ToolSelector())

    async def action_back(self) -> None:
        """Navigates back to the previous screen."""
        if len(self.screen_stack) > 1:
            self.pop_screen()

    def notify(self, message: str, title: str = "", severity: str = "information", timeout: float = 1.0, **kwargs) -> None:
        """Override notify to use a shorter default timeout."""
        super().notify(message, title=title, severity=severity, timeout=timeout, **kwargs)

def main():
    """Entry point for the application."""
    app = NexusApp()
    app.run()

if __name__ == "__main__":
    main()
