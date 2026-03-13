"""Tests for the project picker screen."""

import pytest
from typing import Any
from pathlib import Path
from unittest.mock import patch, AsyncMock
from textual.app import App
from nexus.screens.project_picker import ProjectPicker, AdvancedBrowseModal
from nexus.models import Tool, Project
from textual.widgets import Input, ListView


@pytest.fixture
def mock_tool() -> Tool:
    return Tool(
        label="Test Tool",
        category="DEV",
        description="A test tool",
        command="test",
        requires_project=True,
    )


@pytest.mark.asyncio
async def test_project_picker_mount_and_populate(
    mock_tool: Tool, tmp_path: Path
) -> None:
    app: App[Any] = App()

    (tmp_path / "proj1").mkdir()
    (tmp_path / "proj2").mkdir()
    (tmp_path / "proj_recent").mkdir()

    mock_projects = [
        Project(name="proj1", path=tmp_path / "proj1", is_git=False),
        Project(name="proj2", path=tmp_path / "proj2", is_git=True),
    ]

    with patch("nexus.container.get_container") as mock_get_container:
        container = mock_get_container.return_value
        # scan_projects is now an async function, so it must be mocked with AsyncMock
        container.scanner.scan_projects = AsyncMock(return_value=mock_projects)
        container.state_manager.get_recents.return_value = [
            str(tmp_path / "proj_recent")
        ]

        screen = ProjectPicker(mock_tool)
        async with app.run_test() as pilot:
            await app.push_screen(screen)
            await pilot.pause(0.2)

            list_view = screen.query_one("#project-list", ListView)
            # 2 from scanner + 1 recent
            assert len(list_view.children) == 3

            # Test search filtering
            search_input = screen.query_one("#project-search", Input)
            search_input.value = "proj1"
            await pilot.pause(0.2)
            assert len(list_view.children) == 1

            search_input.value = "nonexistent"
            await pilot.pause(0.2)
            assert not screen.query_one("#projects-empty").has_class("hidden")


@pytest.mark.asyncio
async def test_project_picker_selection(mock_tool: Tool, tmp_path: Path) -> None:
    from nexus.app import NexusApp
    from nexus.screens.tool_selector import ToolSelector

    (tmp_path / "proj1").mkdir()

    mock_projects = [
        Project(name="proj1", path=tmp_path / "proj1", is_git=False),
    ]

    with patch("nexus.container.get_container") as mock_get_container:
        container = mock_get_container.return_value
        container.scanner.scan_projects = AsyncMock(return_value=mock_projects)
        container.state_manager.get_recents.return_value = []

        app = NexusApp()
        selector = ToolSelector()
        screen = ProjectPicker(mock_tool)

        async with app.run_test() as pilot:
            # Setup the stack how it normally looks
            await app.push_screen(selector)
            await pilot.pause(0.1)
            await app.push_screen(screen)
            await pilot.pause(0.2)

            list_view = screen.query_one("#project-list", ListView)
            list_view.index = 0
            list_view.focus()

            # Use real app context, mock suspend instead
            with (
                patch.object(app, "suspend"),
                patch(
                    "nexus.screens.tool_selector.ToolSelector.execute_tool_command"
                ) as mock_execute,
            ):
                # Call the handler directly to test the core logic
                screen._handle_project_selection(str(tmp_path / "proj1"))
                await pilot.pause(0.2)

                # Should have popped ProjectPicker
                assert isinstance(app.screen, ToolSelector)
                mock_execute.assert_called_once()


@pytest.mark.asyncio
async def test_project_picker_browse_and_create(
    mock_tool: Tool, tmp_path: Path
) -> None:
    from nexus.app import NexusApp
    from nexus.screens.tool_selector import ToolSelector
    from textual.screen import Screen

    app = NexusApp()
    selector = ToolSelector()

    with patch("nexus.container.get_container") as mock_get_container:
        container = mock_get_container.return_value
        container.config_manager.get_project_root.return_value = tmp_path
        container.scanner.scan_projects = AsyncMock(return_value=[])

        screen = ProjectPicker(mock_tool)
        async with app.run_test() as pilot:
            await app.push_screen(selector)
            await pilot.pause(0.1)
            await app.push_screen(screen)
            await pilot.pause(0.1)

            # Use dummy screens to avoid flakiness with DirectoryTree or auto-dismissal
            class MockBrowse(Screen):
                pass

            class MockCreate(Screen):
                def __init__(self, *args: Any, **kwargs: Any) -> None:
                    super().__init__()

            # Mock execute_tool_command and app.suspend to avoid SuspendNotSupported in CI
            with (
                patch.object(app, "suspend"),
                patch(
                    "nexus.screens.tool_selector.ToolSelector.execute_tool_command"
                ),
                patch("nexus.screens.project_picker.AdvancedBrowseModal", MockBrowse),
                patch("nexus.screens.create_project.CreateProject", MockCreate),
            ):
                # Use keyboard shortcut instead of click for better reliability in CI
                await pilot.press("ctrl+b")
                await pilot.pause(0.2)

                # Should push our mock browse screen
                assert isinstance(app.screen, MockBrowse)
                app.pop_screen()
                await pilot.pause(0.1)

                # Create project
                await pilot.click("#btn-create")
                await pilot.pause(0.2)
                assert isinstance(app.screen, MockCreate)
