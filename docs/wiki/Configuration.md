# Configuration Guide

Nexus relies on a standard configuration file named `tools.toml` to define available utilities and environment settings.

## Configuration Paths

Nexus adheres to OS-specific standards for configuration storage.

*   **Linux**: `~/.config/nexus/tools.toml`
*   **MacOS**: `~/Library/Application Support/Nexus/tools.toml`
*   **Windows**: `%LOCALAPPDATA%\Nexus\tools.toml`

## Defining Tools

Tools are added using the `[[tool]]` table syntax.

```toml
[[tool]]
label = "Neovim"
category = "DEV"
description = "Text editor"
command = "nvim"
requires_project = true
```

### Key Parameters

*   **label**: The name displayed in the interface.
*   **category**: Groups tools for organization (for example, DEV, UTIL, AI).
*   **command**: The executable string to run in the shell.
*   **requires_project**: If true, Nexus will prompt for a project directory before execution.

## Custom Keybindings

You can override default key sequences in the `[keybindings]` section.

```toml
[keybindings]
quit = "ctrl+q"
toggle_favorite = "f"
back = "escape"
```
