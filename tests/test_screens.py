"""Tests for the modal screens."""

import pytest
from typing import Any
from textual.app import App
from pathlib import Path
from textual.widgets import Input
from nexus.screens.error import ErrorScreen
from nexus.screens.quit_confirmation import QuitConfirmation
from nexus.screens.create_project import CreateProject


@pytest.mark.asyncio
async def test_error_screen() -> None:
    app: App[Any] = App()
    screen = ErrorScreen("Test Error", "This is a test", "Details here")
    async with app.run_test() as pilot:
        app.push_screen(screen)
        await pilot.pause()

        assert str(screen.query_one(".modal-title").render()) == "Error: Test Error"
        assert str(screen.query_one("#error-message").render()) == "This is a test"
        assert str(screen.query_one("#error-details").render()) == "Details here"

        await pilot.press("escape")
        await pilot.pause()
        # Should be dismissed


@pytest.mark.asyncio
async def test_quit_confirmation(monkeypatch: pytest.MonkeyPatch) -> None:
    app: App[Any] = App()

    result: Any = None

    def result_callback(res: Any) -> None:
        nonlocal result
        result = res

    async with app.run_test() as pilot:
        screen = QuitConfirmation()
        app.push_screen(screen, callback=result_callback)
        await pilot.pause()

        # Test cancel
        await pilot.click("#btn-cancel")
        await pilot.pause()
        assert result is False

        # Test confirm
        screen2 = QuitConfirmation()
        app.push_screen(screen2, callback=result_callback)
        await pilot.pause()
        await pilot.click("#btn-quit")
        await pilot.pause()
        assert result is True


@pytest.mark.asyncio
async def test_create_project(tmp_path: Path) -> None:
    app: App[Any] = App()

    result: Any = None

    def result_callback(res: Any) -> None:
        nonlocal result
        result = res

    async with app.run_test() as pilot:
        # Test cancel
        screen = CreateProject(tmp_path)
        app.push_screen(screen, callback=result_callback)
        await pilot.pause()
        await pilot.click("#btn-cancel")
        await pilot.pause()
        assert result is None

        # Test empty name
        screen = CreateProject(tmp_path)
        app.push_screen(screen, callback=result_callback)
        await pilot.pause()
        await pilot.click("#btn-create")
        await pilot.pause()
        assert not screen.query_one("#create-error").has_class("hidden")

        # We need to dismiss the errored screen before proceeding
        await pilot.click("#btn-cancel")
        await pilot.pause()

        # Test valid creation
        screen = CreateProject(tmp_path)
        app.push_screen(screen, callback=result_callback)
        await pilot.pause()
        screen.query_one(Input).value = "my_new_project"
        await pilot.click("#btn-create")
        await pilot.pause()

        assert result == tmp_path / "my_new_project"
        assert (tmp_path / "my_new_project").exists()

        # Test duplicate creation
        screen = CreateProject(tmp_path)
        app.push_screen(screen, callback=result_callback)
        await pilot.pause()
        screen.query_one(Input).value = "my_new_project"
        await pilot.click("#btn-create")
        await pilot.pause()
        assert "already exists" in str(screen.query_one("#create-error").render())
