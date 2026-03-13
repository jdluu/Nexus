# Changelog

All notable changes to the Nexus TUI project will be documented in this file.

## [0.2.0] - 2026-03-12
### Added
- **Command Palette Integration**: Press `Ctrl+P` from any screen to search and launch tools instantly.
- **Responsive Modal System**: Modern, adaptive dialogs for settings and confirmations that look great on any terminal size.
- **Tokyo Night Theme Suite**: Includes Dark, Storm, and Light variations with automatic system preference detection.
- **Advanced Project Browser**: Deep filesystem navigation with support for selecting both folders and individual files.
- **Dynamic Command Flags**: Enter custom arguments at launch time for any tool.
- **Intelligent Navigation**: New persistent footer with prioritized global actions (**Quit**, **Theme**, **Help**) and context-aware local shortcuts.
- **UX Safety Features**: Added a Quit Confirmation dialog to prevent accidental exits.
- **Improved Documentation**: Modernized Help screen with collapsible sections and a new **F1** global shortcut.

### Changed
- **Performance Boost**: Completely migrated to Textual's new Workers API for stutter-free background scanning and tool discovery.
- **Enhanced Design System**: Full semantic refactor using framework-native CSS variables for high-contrast focus highlights and better readability.
- **Robust Execution**: Improved command launching logic to automatically manage working directories based on selected files or folders.
- **Metadata**: Updated PyPI links to include direct repository and changelog access.

### Fixed
- **Architectural Cleanup**: Centralized configuration and state management for a more stable and predictable application lifecycle.
- **Footer Stability**: Resolved issues where the footer would shift or duplicate when switching focus.
- **Type Safety**: Achieved 100% strict type compliance to ensure long-term stability.

## [0.1.16] - 2026-02-03
- Initial documentation standardization.
- Fixed absolute raw URLs for PyPI rendering.

## [0.1.14] - 2026-01-26
- Cleaned up internal imports.
- Stabilized tool selection workflow.

## [0.1.0] - 2026-01-26
- Initial public release on PyPI.
- Core features: fuzzy search, project discovery, and terminal-agnostic tool execution.
