# Nexus

Nexus is a terminal dashboard that lets you launch your favorite CLI and TUI tools (like Neovim, Git UIs, or custom scripts) from a single interactive menu. No memorizing commands or directories required.

Think of Nexus as a launcher for terminal tools, similar to how Raycast or Alfred launch GUI apps.

**Source Code**: https://github.com/jdluu/Nexus | **Changelog**: [CHANGELOG.md](CHANGELOG.md)

![Nexus Logic Demo](https://raw.githubusercontent.com/jdluu/Nexus/main/docs/nexus_demo.png)
*Caption: Main dashboard showing projects and tools.*

## Prerequisites

*   Python 3.12 or newer.
*   The [`uv`](https://docs.astral.sh/uv/) package manager.
*   **Recommended**: A modern terminal emulator with TrueColor support (e.g., [Windows Terminal](https://aka.ms/terminal), [ghostty](https://ghostty.org/), [Kitty](https://sw.kovidgoyal.net/kitty/), or [WezTerm](https://wezfurlong.org/wezterm/)).
*   **Recommended**: A [Nerd Font](https://www.nerdfonts.com/) for optimal icon rendering.

## Installation

It is recommended to use `uv`, a fast Python package and tool manager (similar to pipx), for a clean, isolated global installation.

```bash
# Install globally so you can run 'nexus' from anywhere
uv tool install nexus-tui
```

**Alternative (Standard pip)**:
You can also install via pip, though it is recommended `uv` or `pipx` to keep dependencies isolated.
```bash
pip install nexus-tui
```

### Upgrade

To update to the latest version:
```bash
uv tool upgrade nexus-tui
```

## Features

*   **Smart Search**: Instantly find tools with fuzzy matching and a built-in **Command Palette** (`Ctrl+P`).
*   **Dynamic Flags**: Pass custom arguments (e.g., `--verbose`, `--dry-run`) to your tools at launch time.
*   **Advanced Project Browser**: Browse your entire filesystem or scan defined roots to find project context. Supports selecting both folders and individual files.
*   **Responsive Design System**: Fully themeable interface with support for Tokyo Night (Dark, Storm, Light) and automatic system preference detection.
*   **Secure Secrets**: Seamless integration with **Infisical** for environment variable management.
*   **Persistence**: Nexus remembers your recently accessed projects for quick re-launching.

## Configuration

Nexus utilizes a `tools.toml` file for configuration.

### Minimal Starter Config

```toml
# Define where your code projects live
project_root = "~/Projects"

# Add a tool with placeholder support
[[tool]]
label = "Edit"
category = "DEV"
description = "Open project in Neovim"
command = "nvim {project}"
requires_project = true
supports_flags = true
```

### Command Placeholders

You can use the following placeholders in your `command` strings:
- `{project}`: Replaced by the absolute path of the selected project or file.
- `{flags}`: Replaced by any custom arguments you enter at launch.

## Controls

*   **Arrow Keys**: Navigate through lists.
*   **Enter**: Confirm selection or launch tool.
*   **Ctrl+P**: Open the global **Command Palette**.
*   **Ctrl+B**: Open the **Advanced Project Browser** (when in project picker).
*   **Ctrl+T**: Open the **Theme Picker**.
*   **TypeAnywhere**: Instantly filter tools by typing.
*   **Esc**: Go back or return to the previous view.
*   **Ctrl+Q**: Exit the application (with confirmation).
*   **F1**: Show Help / Controls.

## FAQ & Troubleshooting

### Does Nexus discover tools automatically?
No. You must define your tools in `tools.toml` so you have full control over what appears in your dashboard.

### Is this a replacement for my shell?
No. Nexus is a dashboard. When you launch a tool, it temporarily suspends itself to let the tool take over your terminal. When the tool exits, Nexus returns.

### My icons look broken (rectangles or question marks).
Ensure you are using a [Nerd Font](https://www.nerdfonts.com/) and that your terminal emulator is configured to use it.

## Development (For Contributors)

To configure the development environment:

1.  Synchronize dependencies:
    ```bash
    uv sync
    ```

2.  Run the application locally:
    ```bash
    uv run nexus
    ```

3.  Execute the comprehensive test suite:
    ```bash
    uv run pytest --cov=nexus
    ```

4.  Perform static analysis and type checking:
    ```bash
    uv run ruff check .
    uv run mypy .
    ```
