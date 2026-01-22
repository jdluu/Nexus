"""Data models for the Nexus application.

Defines the Pydantic models used for validation and typehinting of
tools and projects within the application.
"""

from pathlib import Path
from typing import Literal

from pydantic import BaseModel


class Tool(BaseModel):
    """Represents a command-line tool available in Nexus.

    Attributes:
        label: The display name of the tool.
        category: The category the tool belongs to (DEV, AI, MEDIA, UTIL).
        description: A brief description of the tool's purpose.
        command: The shell command to execute.
        requires_project: True if the tool needs a project directory to run.
    """

    label: str
    category: Literal["DEV", "AI", "MEDIA", "UTIL"]
    description: str
    command: str
    requires_project: bool


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

# Summary:
# Formatted docstrings to strict Google Style.
# Preserved Pydantic model structure.
