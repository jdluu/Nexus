from textual.app import ComposeResult
from textual.screen import Screen
from textual.widgets import Input, ListView, ListItem, Label, Header, Footer, LoadingIndicator
from textual.containers import Vertical, Container
from nexus.config import PROJECT_ROOT
from nexus.widgets.tool_list_item import ProjectItem, ProjectListItem
from nexus.services.scanner import scan_projects
from nexus.services.executor import launch_tool
from nexus.models import Tool
import asyncio

class ProjectPicker(Screen):
    """Screen for selecting a project directory.

    Displays a searchable list of projects found in the configured root directory.
    Allows creating new projects (placeholder) or selecting an existing one.
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
        """Composes the screen layout."""
        yield Header()
        yield Container(
            Label(f"Select Project for {self.selected_tool.label}", id="title"),
            id="title-container"
        )
        yield Input(placeholder="Search projects...", id="project-search")
        with Container(id="list-container"):
            yield LoadingIndicator(id="loading-spinner")
            yield ListView(id="project-list")
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

    def on_input_changed(self, event: Input.Changed) -> None:
        """Called when the project search input changes."""
        if event.input.id == "project-search":
            self.populate_list(event.value)

    def on_list_view_selected(self, event: ListView.Selected) -> None:
        """Called when a project is selected from the list."""
        item = event.item
        if not isinstance(item, ProjectListItem):
            return

        if item.is_create_new:
            self.app.notify("Create New Project not yet implemented")
            return
            
        project = item.project_data
        if project:
            with self.app.suspend():
                if launch_tool(self.selected_tool.command, project.path):
                     pass
                else:
                     self.app.notify(f"Failed to launch {self.selected_tool.label}", severity="error")
            self.app.refresh()
            self.app.pop_screen()

    def action_cursor_down(self) -> None:
        """Moves selection down in the project list."""
        project_list = self.query_one("#project-list", ListView)
        if project_list.index is None:
            project_list.index = 0
        else:
            project_list.index = min(len(project_list.children) - 1, project_list.index + 1)

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
             self.on_list_view_selected(ListView.Selected(project_list, project_list.children[project_list.index]))