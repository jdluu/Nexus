import asyncio
from pathlib import Path
from nexus.models import Project

async def scan_projects(root_path: Path) -> list[Project]:
    """Scans the root path for project directories asynchronously.

    Directories containing a `.git` folder are marked as git repositories.
    This function runs the I/O operation in a separate thread to avoid blocking
    the main event loop.

    Args:
        root_path: The root directory to scan for subdirectories.

    Returns:
        A list of Project objects representing the found directories, sorted
        alphabetically.
    """
    if not root_path.exists():
        return []

    projects = []
    
    # Run directory listing in a thread to avoid blocking the event loop
    loop = asyncio.get_running_loop()
    
    def get_dirs():
        try:
            return [d for d in root_path.iterdir() if d.is_dir()]
        except PermissionError:
            return []

    dirs = await loop.run_in_executor(None, get_dirs)
    
    for d in sorted(dirs, key=lambda x: x.name.lower()):
        # Check for .git folder
        is_git = (d / ".git").exists()
        projects.append(Project(name=d.name, path=d, is_git=is_git))
        
    return projects