"""Tests for the filesystem scanner service."""

import pytest
from pathlib import Path
from typing import Any
from nexus.services.scanner import scan_projects

@pytest.mark.asyncio
async def test_scan_projects_empty_or_missing(tmp_path: Path) -> None:
    # Test missing dir
    missing_dir = tmp_path / "missing"
    projects = await scan_projects(missing_dir)
    assert projects == []

    # Test empty dir
    empty_dir = tmp_path / "empty"
    empty_dir.mkdir()
    projects = await scan_projects(empty_dir)
    assert projects == []

@pytest.mark.asyncio
async def test_scan_projects_success(tmp_path: Path) -> None:
    root_dir = tmp_path / "root"
    root_dir.mkdir()
    
    # Create project 1 (git repo)
    proj1 = root_dir / "proj1"
    proj1.mkdir()
    (proj1 / ".git").mkdir()
    
    # Create project 2 (not git)
    proj2 = root_dir / "proj2"
    proj2.mkdir()
    
    # Create file (should be ignored)
    (root_dir / "some_file.txt").touch()
    
    projects = await scan_projects(root_dir)
    
    assert len(projects) == 2
    
    # Projects should be sorted alphabetically
    assert projects[0].name == "proj1"
    assert projects[0].path == proj1
    assert projects[0].is_git is True
    
    assert projects[1].name == "proj2"
    assert projects[1].path == proj2
    assert projects[1].is_git is False

@pytest.mark.asyncio
async def test_scan_projects_permission_error(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    root_dir = tmp_path / "root"
    root_dir.mkdir()
    
    def mock_iterdir(*args: Any, **kwargs: Any) -> Any:
        raise PermissionError("Access denied")
        
    monkeypatch.setattr(Path, "iterdir", mock_iterdir)
    
    projects = await scan_projects(root_dir)
    assert projects == []
