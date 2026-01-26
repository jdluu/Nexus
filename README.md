# Nexus

Nexus is a TUI orchestrator designed to help you organize and launch your collection of terminal utilities. Instead of memorizing every tool's unique command, Nexus provides a centralized dashboard to discover and run your installed TUIs from a single, intuitive interface.

## Prerequisites

*   Python 3.12 or newer.
*   The `uv` package manager.
*   **Recommended**: A modern terminal emulator with TrueColor support (e.g., [Windows Terminal](https://aka.ms/terminal), [ghostty](https://ghostty.org/), [Kitty](https://sw.kovidgoyal.net/kitty/), or [WezTerm](https://wezfurlong.org/wezterm/)).
*   **Recommended**: A [Nerd Font](https://www.nerdfonts.com/) for optimal icon rendering.

## Installation

Install Nexus globally using the `uv` tool manager:

```bash
# Always latest stable
uv tool install nexus-tui
```

### Upgrade

To update to the latest version:
```bash
uv tool upgrade nexus-tui
```

### Local Development

```bash
git clone https://github.com/jdluu/Nexus
cd Nexus
uv tool install --editable .
```

## Cross Platform Support

Nexus supports Linux, MacOS, and Windows.

*   **Linux**: Fully supported on standard terminals.
*   **MacOS**: Fully supported.
*   **Windows**: Recommended to use PowerShell 7 or Git Bash within Windows Terminal.

## Configuration

Nexus utilizes the standard configuration paths for your operating system.

*   **Linux**: `~/.config/nexus/tools.toml`
*   **MacOS**: `~/Library/Application Support/Nexus/tools.toml`
*   **Windows**: `%LOCALAPPDATA%\Nexus\tools.toml`

### Project Directory

To define the workspace where Nexus looks for projects, add the `project_root` key to your configuration file.

```toml
# Example configuration
project_root = "~/Development"
```

### Tool Definitions

Tools are defined in the configuration file using the `[[tool]]` table.

```toml
[[tool]]
label = "Neovim"
category = "DEV"
description = "Text editor"
command = "nvim"
requires_project = true
```

*   **label**: The display name.
*   **category**: The grouping identifier (for example DEV, UTIL).
*   **description**: A short explanation of the function.
*   **command**: The executable command line instruction.
*   **requires_project**: Indicates if the tool needs a working directory.

### Keybindings

Custom keybindings can be defined in the `[keybindings]` section.

```toml
[keybindings]
quit = "alt+q"
toggle_favorite = "ctrl+f"
```

## Usage

Launch the application using the following command:

```bash
nexus
```

### Features

*   **Smart Search**: Filter projects using fuzzy matching logic.
*   **Persistence**: Automatically tracks recent projects and favorites.
*   **Favorites**: Pin frequently used tools for quick access.

### Controls

*   **Arrow Keys**: Navigate through lists.
*   **Enter**: Confirm selection or launch tool.
*   **Ctrl+F**: Toggle the favorite status of a tool.
*   **TypeAnywhere**: Instantly filter lists by typing in the search bar.
*   **Esc**: Reset the search filter.
*   **Ctrl+B**: Go back (on picker screens).
*   **Ctrl+Q**: Exit the application.

## Development

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
