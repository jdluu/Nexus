# Configuration Guide

Nexus utilizes a standard configuration file named `tools.toml` to define available utilities and environment settings.

## Configuration Paths

Nexus adheres to OS-specific standards for configuration storage.

*   **Linux**: `~/.config/nexus/tools.toml`
*   **MacOS**: `~/Library/Application Support/Nexus/tools.toml`
*   **Windows**: `%LOCALAPPDATA%\Nexus\tools.toml`

The application also looks for `tools.local.toml` in the current working directory for project-specific overrides.

## Defining Tools

Tools are defined using the `[[tool]]` table syntax.

```toml
[[tool]]
label = "Neovim"
category = "DEV"
description = "Text editor"
command = "nvim {project} {flags}"
requires_project = true
supports_flags = true
```

### Key Parameters

*   **label**: The name displayed in the interface.
*   **category**: Groups tools for organization (e.g., DEV, UTIL, AI, MEDIA). You can define your own categories.
*   **command**: The executable string to run in the shell. Supports the following placeholders:
    *   `{project}`: Replaced by the absolute path to the selected project or file.
    *   `{flags}`: Replaced by additional command-line arguments entered by the user at launch.
*   **requires_project**: If set to true, Nexus prompts for a project or file context before execution.
*   **supports_flags**: If set to true, Nexus prompts for additional command-line arguments before execution.

## Theming

You can configure your preferred light and dark themes in the root of the configuration.

```toml
light_theme = "tokyo-night-light"
dark_theme = "tokyo-night-dark"
```

Nexus automatically detects your system's light/dark mode preference on startup and applies the corresponding theme.

## Custom Keybindings

Default key sequences can be overridden in the `[keybindings]` section.

```toml
[keybindings]
quit = "q"
back = "escape"
theme = "ctrl+t"
help = "?"
fuzzy_search = "ctrl+f"
```

*Note: Global shortcuts using `Ctrl` or `F1` keys are generally safer as they are not consumed by the search input field.*
