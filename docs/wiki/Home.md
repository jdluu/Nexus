# Nexus Wiki

Welcome to the Nexus documentation. Nexus is a TUI terminal dashboard and tool orchestrator designed to centralize your terminal utilities, enabling you to launch any tool without memorizing individual commands or deep directory structures.

## Installation

```bash
# Install globally using uv (recommended)
uv tool install nexus-tui
```

## Upgrade

To update an existing installation:
```bash
uv tool upgrade nexus-tui
```

## Core Features

*   **Smart Search**: Instantly find tools with fuzzy matching and a global **Command Palette** (`Ctrl+P`).
*   **Dynamic Flags**: Pass custom arguments (e.g., `--verbose`, `--dry-run`) to your tools at launch time.
*   **Advanced Project Browser**: Browse your entire filesystem to find the perfect context for your tools. Supports both folders and specific files.
*   **Responsive Theming**: Beautiful built-in themes (Tokyo Night Dark, Storm, Light) with automatic system preference detection.
*   **Persistent State**: Nexus remembers your recently accessed projects for quick re-launching.
*   **Custom Keybindings**: Full control over the interface shortcuts to align with your personal workflow.

## Documentation Structure

1.  **[Configuration Guide](Configuration)**: Detailed instructions for setting up `tools.toml` and defining your tools.
2.  **Platform Compatibility**: Operating system specific setup details.
