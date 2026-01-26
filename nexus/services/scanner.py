"""Service for scanning the filesystem.

Provides asynchronous methods to discover projects and git repositories
within the configured project root.
"""

import asyncio
from pathlib import Path

from nexus.models import Project


async def scan_projects(root_path: Path) -> list[Project]:
    """Scans the root path for project directories asynchronously.

    Identifies directories and checks for the presence of a `.git` folder to
    mark them as git repositories. The I/O operation runs in a separate thread.

    Args:
        root_path: The root directory to scan for subdirectories.

    Returns:
        A list of Project objects representing the found directories, sorted
        alphabetically by name.
    """
    if not root_path.exists():
        return []

    projects = []

    # Run directory listing in a thread to avoid blocking the event loop
    loop = asyncio.get_running_loop()

    def get_dirs() -> list[Path]:
        try:
            return [d for d in root_path.iterdir() if d.is_dir()]
        except PermissionError:
            return []

    dirs = await loop.run_in_executor(None, get_dirs)

    for d in sorted(dirs, key=lambda x: x.name.lower()):
        is_git = (d / ".git").exists()
        projects.append(Project(name=d.name, path=d, is_git=is_git))

    return projects

# Summary:
# Rewrote docstrings to Google Style.
# Preserved necessary logic comments.