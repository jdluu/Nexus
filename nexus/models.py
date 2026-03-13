"""Data models for the Nexus application.

Defines the Pydantic models used for validation and typehinting of
tools and projects within the application.
"""

from pathlib import Path

from pydantic import BaseModel


class Tool(BaseModel):
    """Represents a command-line tool configuration.

    Attributes:
        label: The display name of the tool.
        category: The category identifier (e.g. DEV, AI, MEDIA, UTIL).
        description: A brief summary of the tool's functionality.
        command: The shell command template to execute.
        requires_project: Indicates if the tool requires a project directory.
        supports_flags: Indicates if the tool accepts custom command-line flags.
    """

    label: str
    category: str
    description: str
    command: str
    requires_project: bool
    supports_flags: bool = False


class Project(BaseModel):
    """Represents a local project directory.

    Attributes:
        name: The name of the project folder.
        path: The absolute path to the project directory.
        is_git: True if the directory is a git repository.
    """

    name: str
    path: Path
    is_git: bool
