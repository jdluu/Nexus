"""Screen for selecting a project directory.

Allows users to browse potential project directories and choose one as the
context for a tool execution. Also supports creating new projects.
"""

import asyncio
from nexus.config import PROJECT_ROOT
from nexus.models import Tool
from nexus.services.executor import launch_tool
from nexus.services.scanner import scan_projects
from nexus.widgets.tool_list_item import ProjectListItem
from textual.app import ComposeResult
from textual.containers import Container
from textual.screen import Screen
from textual.widgets import Footer, Header, Input, Label, ListView, LoadingIndicator


class ProjectPicker(Screen):
    """Screen for selecting a project directory.

    Displays a searchable list of projects found in the configured root directory.
    Allows creating new projects or selecting an existing one.

    Attributes:
        selected_tool: The tool that was selected and requires a project context.
        projects: List of discovered projects.
    """

    def __init__(self, selected_tool: Tool, **kwargs):
        """Initializes the ProjectPicker.

        Args:
            selected_tool: The tool that was selected and requires a project context.
            **kwargs: Additional arguments passed to the Screen.
        """
        super().__init__(**kwargs)
        self.selected_tool = selected_tool
        self.projects = []

    BINDINGS = [
        ("down", "cursor_down", "Next Item"),
        ("up", "cursor_up", "Previous Item"),
        ("enter", "select_current", "Select"),
    ]

    def compose(self) -> ComposeResult:
        """Composes the screen layout.

        Returns:
            A ComposeResult containing the widget tree.
        """
        yield Header()
        yield Container(
            Label(f"Select Project for {self.selected_tool.label}", id="title"),
            id="title-container",
        )
        yield Input(placeholder="Search projects...", id="project-search")
        with Container(id="list-container"):
            yield LoadingIndicator(id="loading-spinner")
            yield ListView(id="project-list")
            yield Label(
                "No projects found", id="projects-empty", classes="empty-state hidden"
            )
        yield Footer()

    async def on_mount(self) -> None:
        """Called when the screen is mounted.

        Initiates an asynchronous scan of the project root directory.
        """
        self.query_one("#project-list").display = False
        self.query_one("#project-search").focus()

        self.projects = await scan_projects(PROJECT_ROOT)

        self.populate_list()
        self.query_one("#loading-spinner").display = False
        self.query_one("#project-list").display = True

    def populate_list(self, filter_text: str = "") -> None:
        """Populates the project list, processing the filter text.

        Args:
            filter_text: Text to filter project names by.
        """
        project_list = self.query_one("#project-list", ListView)
        project_list.clear()

        # Add "Create New Project" option
        if not filter_text:
            new_item = ProjectListItem(is_create_new=True)
            project_list.append(new_item)

        for project in self.projects:
            if filter_text.lower() in project.name.lower():
                item = ProjectListItem(project_data=project)
                project_list.append(item)

        # Check if list is effectively empty
        if not project_list.children:
            project_list.display = False
            empty_lbl = self.query_one("#projects-empty")
            empty_lbl.remove_class("hidden")
            if filter_text:
                empty_lbl.update(f"No projects matching '{filter_text}'")
            else:
                empty_lbl.update("No projects found in root directory.")
        else:
            project_list.display = True
            self.query_one("#projects-empty").add_class("hidden")

    def on_input_changed(self, event: Input.Changed) -> None:
        """Called when the project search input changes.

        Args:
            event: The input changed event.
        """
        if event.input.id == "project-search":
            self.populate_list(event.value)

    def on_input_submitted(self, event: Input.Submitted) -> None:
        """Called when Enter is pressed in the search input.

        Args:
            event: The input submitted event.
        """
        self.action_select_current()

    def on_list_view_selected(self, event: ListView.Selected) -> None:
        """Called when a project is selected from the list.

        Args:
            event: The selection event.
        """
        self._select_item(event.item)

    def _select_item(self, item) -> None:
        """Internal method to handle item selection logic.

        Args:
            item: The selected ListItem.
        """
        if not isinstance(item, ProjectListItem):
            return

        if item.is_create_new:
            from nexus.screens.create_project import CreateProject

            def on_created(new_project_name: str):
                self.app.notify(f"Created project: {new_project_name}")
                # Refresh list and try to find the new project
                import asyncio

                async def refresh():
                    self.projects = await scan_projects(PROJECT_ROOT)
                    self.populate_list(filter_text=new_project_name)

                asyncio.create_task(refresh())

            self.app.push_screen(CreateProject(on_created))
            return

        project = item.project_data
        if project:
            with self.app.suspend():
                if launch_tool(self.selected_tool.command, project.path):
                    pass
                else:
                    self.app.notify(
                        f"Failed to launch {self.selected_tool.label}", severity="error"
                    )
            self.app.refresh()
            self.app.pop_screen()

    def action_cursor_down(self) -> None:
        """Moves selection down in the project list."""
        project_list = self.query_one("#project-list", ListView)
        if project_list.index is None:
            project_list.index = 0
        else:
            project_list.index = min(
                len(project_list.children) - 1, project_list.index + 1
            )

    def action_cursor_up(self) -> None:
        """Moves selection up in the project list."""
        project_list = self.query_one("#project-list", ListView)
        if project_list.index is None:
            project_list.index = 0
        else:
            project_list.index = max(0, project_list.index - 1)

    def action_select_current(self) -> None:
        """Selects the currently highlighted item."""
        project_list = self.query_one("#project-list", ListView)
        if project_list.index is not None:
            self._select_item(project_list.children[project_list.index])

# Summary:
# Formatted docstrings to strict Google Style.
# Added module docstring.