# Nexus

Nexus is a terminal dashboard that lets you launch your favorite CLI and TUI tools (like Neovim, Git UIs, or custom scripts) from a single interactive menu. No memorizing commands or directories required.

Think of Nexus as a launcher for terminal tools, similar to how Raycast or Alfred launch GUI apps.

**Source Code**: https://github.com/jdluu/Nexus

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

### Local Development

For contributors who want to modify the source code:

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

*Note: Some tools you launch may behave differently depending on your shell and operating system.*

## Configuration

Nexus utilizes standard configuration paths. You can find your config file at the location listed in the **First Run** section above.

### Minimal Starter Config

Copy this into your `tools.toml` to get started immediately:

```toml
# Define where your code projects live
project_root = "~/Projects"

# Add a simple tool to open a shell in the selected project
[[tool]]
label = "Shell"
category = "UTIL"
description = "Open a shell in the project"
command = "$SHELL"
requires_project = true
```

### Understanding "Projects"

A **Project** is any directory found inside your `project_root`. Nexus scans this folder and lets you select a specific project before launching a tool.

For example, if you select the "Shell" tool above, Nexus will ask you to pick a project (e.g., `~/Projects/MyApp`). It then launches `$SHELL` inside that directory.

### Tool Definitions

Tools are defined using the `[[tool]]` table.

```toml
[[tool]]
label = "Neovim"
category = "DEV"
description = "Text editor"
command = "nvim"
requires_project = true
```

*   **label**: The display name.
*   **category**: The grouping identifier (e.g., DEV, UTIL).
*   **description**: A short explanation of the function.
*   **command**: The executable command line instruction.
*   **requires_project**: If `true`, Nexus prompts for a project before running. If `false`, it runs immediately in the current directory.

### Keybindings

Nexus comes with default keybindings (see **Controls** below). You can override them in the `[keybindings]` section of your config.

```toml
[keybindings]
# Override default quit to Alt+Q
quit = "alt+q"
# Override favorite toggle
toggle_favorite = "ctrl+f"
```

## First Run Experience

1.  Run `nexus` from your terminal.
2.  Nexus creates a default configuration file at:
    *   **Linux**: `~/.config/nexus/tools.toml`
    *   **MacOS**: `~/Library/Application Support/Nexus/tools.toml`
    *   **Windows**: `%LOCALAPPDATA%\Nexus\tools.toml`
3.  On first launch, you will see an empty dashboard.
4.  Edit the configuration file (see below) to add your tools and project roots.
5.  Restart Nexus to see your changes.

### Features

*   **Smart Search**: Instantly find what you need with fuzzy matching, so you don't have to remember exact names.
*   **Persistence**: Nexus remembers your recent projects and favorite tools, so common workflows are always one keystroke away.
*   **Favorites**: Pin your most-used tools to the top of the list for quick access.

### Controls

*   **Arrow Keys**: Navigate through lists.
*   **Enter**: Confirm selection or launch tool.
*   **Ctrl+F**: Toggle the favorite status of a tool.
*   **TypeAnywhere**: Instantly filter lists by typing in the search bar.
*   **Esc**: Reset the search filter.
*   **Ctrl+B**: Go back (on picker screens).
*   **Ctrl+C**: Exit the application.
*   **Ctrl+H**: Show Help / Controls.

## FAQ & Troubleshooting

### Does Nexus discover tools automatically?
No. You must define your tools in `tools.toml` so you have full control over what appears in your dashboard.

### Is this a replacement for my shell?
No. Nexus is a dashboard. When you launch a tool, it temporarily suspends itself to let the tool take over your terminal found. When the tool exits, Nexus returns.

### My icons look broken (rectangles or question marks).
This usually means you aren't using a **Nerd Font**.
1.  Download a font from [Nerd Fonts](https://www.nerdfonts.com/).
2.  Install it on your system.
3.  Configure your terminal emulator to use that font.

### I see a blank screen on launch.
Check that your `tools.toml` file exists and has at least one valid `[[tool]]` entry. See the **Configuration** section for a minimal example.

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
