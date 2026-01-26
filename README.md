# Nexus

Nexus is a terminal interface designe for creating efficient development workflows. It serves as a centralized dashboard for launching command line utilities and managing projects across various operating systems.

## Prerequisites

*   Python 3.12 or newer.
*   The `uv` package manager.
*   A modern terminal emulator such as Windows Terminal, ghostty, or iTerm2.

## Installation

Nexus can be installed globally using the `uv` tool manager directly from the source repository.

```bash
uv tool install git+https://github.com/jdluu/Nexus
```

To update an existing installation:
```bash
uv tool install --force git+https://github.com/jdluu/Nexus
```

### Installation from Source

If you prefer to install from a local clone:

1.  Clone the repository and navigate to the project directory.

2.  Install the application locally:
    ```bash
    uv tool install .
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

Launch the application command:

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
*   **F**: Toggle the favorite status of a tool.
*   **Type**: Instantly filter lists by text.
*   **Esc**: Return to the previous screen.
*   **Q**: Exit the application.

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
