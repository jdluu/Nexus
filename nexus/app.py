"""Main application entry point for Nexus.

Configures the Textual application class, global bindings, and initial screen loading.
"""

from typing import Any, ClassVar, Callable
from textual.app import App
from textual.binding import Binding
from textual.theme import Theme, BUILTIN_THEMES
from textual.command import Provider
from textual.notifications import SeverityLevel
from nexus.container import get_container
from nexus.screens.tool_selector import ToolSelector
from nexus.commands import ToolCommandProvider


# Define Tokyo Night Themes using Textual's Theme system
TOKYO_NIGHT_DARK = Theme(
    name="tokyo-night-dark",
    primary="#7aa2f7",
    secondary="#bb9af7",
    accent="#7aa2f7",
    foreground="#c0caf5",
    background="#1a1b26",
    surface="#1a1b26",
    panel="#292e42",
    success="#9ccc65",
    warning="#ff9e64",
    error="#f7768e",
    dark=True,
)

TOKYO_NIGHT_STORM = Theme(
    name="tokyo-night-storm",
    primary="#bb9af7",
    secondary="#bb9af7",
    accent="#bb9af7",
    foreground="#c0caf5",
    background="#24283b",
    surface="#24283b",
    panel="#414868",
    success="#9ccc65",
    warning="#ff9e64",
    error="#f7768e",
    dark=True,
)

TOKYO_NIGHT_LIGHT = Theme(
    name="tokyo-night-light",
    primary="#3d59a1",
    secondary="#8c4351",
    accent="#3d59a1",
    foreground="#343b58",
    background="#d5d6db",
    surface="#ffffff",
    panel="#ffffff",
    success="#487e02",
    warning="#ff9e64",
    error="#f7768e",
    dark=False,
)


class NexusApp(App[None]):
    """The main Nexus application class.

    Attributes:
        container: The dependency injection container for application services.
    """

    COMMANDS: ClassVar[set[type[Provider] | Callable[[], type[Provider]]]] = {ToolCommandProvider}
    CSS_PATH = ["styles/main.tcss"]
    
    # Global bindings that should ALWAYS be visible.
    # We use F1 for Help to avoid Ctrl+H conflict with Backspace in some terminals.
    # We rely on Textual's default Ctrl+P for the Palette (visible on the right).
    BINDINGS = [
        Binding("ctrl+q", "request_quit", "Quit", show=True, priority=True),
        Binding("ctrl+t", "theme", "Theme", show=True, priority=True),
        Binding("f1", "help", "Help", show=True, priority=True),
        # Explicitly hide redundant defaults to ensure a singular footer.
        Binding("ctrl+c", "quit", "Quit", show=False),
        Binding("?", "help", "Help", show=False),
        Binding("ctrl+h", "help", "Help", show=False),
    ]

    def on_mount(self) -> None:
        """Called when the application is mounted.

        Initializes application services, applies user keybindings, and 
        activates the initial tool selection screen.
        """
        # Register custom themes
        self.register_theme(TOKYO_NIGHT_DARK)
        self.register_theme(TOKYO_NIGHT_STORM)
        self.register_theme(TOKYO_NIGHT_LIGHT)

        # Register all Textual built-in themes
        for theme in BUILTIN_THEMES.values():
            self.register_theme(theme)

        self.container = get_container()
        self._apply_bindings()

        # Set initial theme based on system preference
        light, dark = self.container.config_manager.get_theme_pair()
        self.theme = dark if self.detect_system_dark() else light

        self.push_screen(ToolSelector())

    def _apply_bindings(self) -> None:
        """Applies configurable keybindings from the user settings."""
        bindings = self.container.config_manager.get_keybindings()
        
        # Map user-defined keys but hide them from the footer to avoid duplication
        # with our prioritized Ctrl-key bindings.
        if "quit" in bindings:
            self.bind(keys=bindings["quit"], action="request_quit", show=False)
        
        if "theme" in bindings:
            self.bind(keys=bindings["theme"], action="theme", show=False)

        if "help" in bindings:
            self.bind(keys=bindings["help"], action="help", show=False)

        if "back" in bindings:
            # We bind back globally but hide it; screens will show it if they need it.
            self.bind(keys=bindings["back"], action="back", show=False)

    def detect_system_dark(self) -> bool:
        """Attempts to detect if the system is in dark mode.

        Returns:
            True if dark mode is detected, False otherwise.
        """
        import subprocess
        import os

        # MacOS detection
        try:
            if os.uname().sysname == "Darwin":
                try:
                    result = subprocess.run(
                        ["defaults", "read", "-g", "AppleInterfaceStyle"],
                        capture_output=True,
                        text=True,
                        check=False
                    )
                    return "Dark" in result.stdout
                except Exception:
                    pass
        except AttributeError:
            pass

        # Linux (GNOME/GTK) detection
        try:
            result = subprocess.run(
                ["gsettings", "get", "org.gnome.desktop.interface", "color-scheme"],
                capture_output=True,
                text=True,
                check=False
            )
            return "prefer-dark" in result.stdout
        except Exception:
            pass

        return True

    # --- Actions ---

    def action_request_quit(self) -> None:
        """Opens the quit confirmation modal."""
        from nexus.screens.quit_confirmation import QuitConfirmation

        def check_quit(quit: bool | None) -> None:
            if quit:
                self.exit()

        self.push_screen(QuitConfirmation(), callback=check_quit)

    def action_theme(self) -> None:
        """Opens the theme picker modal."""
        available_themes = sorted(list(self.available_themes))

        def apply_theme(new_theme: str | None) -> None:
            if new_theme:
                self.theme = new_theme
                name = new_theme.replace("tokyo-night-", "").replace("textual-", "").title()
                self.app.notify(f"Applied theme: {name}")

        from nexus.screens.theme_picker import ThemePicker
        self.push_screen(ThemePicker(available_themes, self.theme, apply_theme))

    def action_help(self) -> None:
        """Opens the help screen modal."""
        from nexus.screens.help import HelpScreen
        self.push_screen(HelpScreen())

    async def action_back(self) -> None:
        """Navigates back to the previous screen.

        Removes the current screen from the stack if more than one screen 
        is present, and ensures the home screen is not popped.
        """
        # If we are on the main screen, 'back' shouldn't do anything
        if isinstance(self.screen, ToolSelector):
            return
            
        if len(self.screen_stack) > 2:
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
        """Displays a notification with a shortened default timeout.

        Args:
            message: The message to display.
            title: The title of the notification.
            severity: The severity level of the notification.
            timeout: The duration in seconds to display the notification.
            **kwargs: Additional keyword arguments passed to the base notify method.
        """
        super().notify(
            message, title=title, severity=severity, timeout=timeout, **kwargs
        )

    def show_error(self, title: str, message: str, details: str = "") -> None:
        """Displays a modal error screen to the user.

        Args:
            title: The title of the error.
            message: A user friendly description of the error.
            details: Optional technical details for debugging purposes.
        """
        from nexus.screens.error import ErrorScreen

        self.push_screen(ErrorScreen(title, message, details))


def main() -> None:
    """Entry point function for the application.

    Configures logging and initializes the main application loop.
    """
    from nexus.logger import configure_logging

    configure_logging()
    app = NexusApp()
    app.run()


if __name__ == "__main__":
    main()
