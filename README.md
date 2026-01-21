# Nexus

Nexus is a terminal user interface for managing development workflows and launching tools. It provides a centralized dashboard to access command line utilities and manage projects within a specified workspace.

## Prerequisites

*   Python 3.12 or later
*   uv package manager
*   A terminal emulator (Ghostty, GNOME Terminal, etc.)
    *   Configurable via `pyproject.toml`

## Installation

1.  Clone the repository and navigate to the project directory.

2.  Install the application globally using uv:
    ```bash
    uv tool install .
    ```

    To update the installation after pulling changes:
    ```bash
    uv tool install --force .
    ```

## Configuration

### Project Directory

The application scans a specific directory for projects. Currently, this is defined in `nexus/config.py`. Open this file and update the `PROJECT_ROOT` variable to match your workspace path:

```python
PROJECT_ROOT = Path("/path/to/your/projects")
```

### Tool Definitions

Tools are configured in `nexus/tools.toml`. You can modify this file to add, remove, or categorize tools. Each entry follows this structure:

```toml
[[tool]]
label = "Neovim"
category = "DEV"
description = "Hyperextensible text editor"
command = "nvim"
requires_project = true
```

*   `label`: The display name in the list.
*   `category`: The group identifier (DEV, AI, MEDIA, NET).
*   `description`: A brief explanation of the tool.
*   `command`: The shell command to execute.
*   `requires_project`: Set to `true` if the tool requires a target directory, or `false` to launch immediately.

## Usage

Launch the application from any terminal window:

```bash
nexus
```

### Controls

*   **Arrow Keys**: Navigate lists.
*   **Enter**: Select a tool or project.
*   **Type**: Filter lists by name.
*   **Esc**: Go back to the previous screen.
*   **q**: Quit the application.

## Development

To set up the development environment:

1.  Sync dependencies:
    ```bash
    uv sync
    ```

2.  Run the application locally:
    ```bash
    uv run nexus
    ```

3.  Run code quality checks:
    ```bash
    ruff check .
    ty check
    ```
