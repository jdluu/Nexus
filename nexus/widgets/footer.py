"""Footer widget for the Nexus application.

Displays keybindings and status information, adapting to available width.
"""
from typing import Any
from textual.app import ComposeResult
from textual.widgets import Label, Static


from textual.message import Message

class KeyBadge(Static):
    """A badge displaying a key binding."""

    DEFAULT_CSS = """
    KeyBadge {
        layout: horizontal;
        width: auto;
        height: 1;
        margin-right: 2;
    }
    KeyBadge:hover {
        background: $primary;
        color: $text;
    }
    """
    
    class Pressed(Message):
        """Message sent when the badge is clicked."""
        def __init__(self, action: str) -> None:
            self.action = action
            super().__init__()

    def __init__(self, key: str, description: str, action: str) -> None:
        super().__init__()
        self.key = key
        self.description = description
        self.action_name = action

    def compose(self) -> ComposeResult:
        yield Label(self.key, classes="key-badge")
        yield Label(self.description, classes="key-desc")
        
    def on_click(self) -> None:
        self.post_message(self.Pressed(self.action_name))


class FooterSection(Static):
    """A section of the footer grouping related keys."""
    
    DEFAULT_CSS = """
    FooterSection {
        layout: horizontal;
        width: auto;
        height: 100%;
        padding-right: 2;
        content-align: center middle;
    }
    """

    def __init__(self, title: str) -> None:
        super().__init__()
        self.title_text = title

    def compose(self) -> ComposeResult:
        yield Label(self.title_text, classes="footer-label")


class NexusFooter(Static):
    """The main application footer.
    
    Displays a minimal set of essential keybindings (Progressive Disclosure).
    """

    DEFAULT_CSS = """
    NexusFooter {
        height: 3;
        dock: bottom;
        padding: 0 2;
        layout: horizontal;
        background: $surface;
        content-align: center middle; 
    }

    .key-separator {
        width: 4;
        content-align: center middle;
        color: #565f89;
    }
    """

    def __init__(self, key_defs: list[tuple[str, str, str]] | None = None, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        if key_defs is None:
             self.key_defs = [
                ("Enter", "Select", "launch_current"),
                ("Ctrl+F", "Favorite", "toggle_favorite"),
                ("Ctrl+C", "Quit", "app.quit"),
                ("Ctrl+H", "Help", "show_help"),
             ]
        else:
            self.key_defs = key_defs

    def compose(self) -> ComposeResult:
        for i, (key, desc, action) in enumerate(self.key_defs):
            yield KeyBadge(key, desc, action)
            if i < len(self.key_defs) - 1:
                yield Label("    ", classes="key-separator")
