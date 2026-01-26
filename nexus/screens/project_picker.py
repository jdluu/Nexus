"""Screen for selecting a project directory.

Allows users to browse potential project directories and choose one as the
context for a tool execution. Also supports creating new projects.
"""



from nexus.config import get_project_root
from nexus.models import Project, Tool
from typing import Any
from nexus.widgets.tool_list_item import ProjectListItem
from textual.app import ComposeResult
from textual.containers import Container
from textual.screen import Screen
from textual.widgets import Footer, Header, Input, Label, ListItem, ListView, LoadingIndicator
from thefuzz import process


class ProjectPicker(Screen[None]):
    """Screen for selecting a project directory.

    Displays a searchable list of projects found in the configured root directory.
    Allows creating new projects or selecting an existing one.

    Attributes:
        selected_tool: The tool that was selected and requires a project context.
        projects: List of discovered projects.
    """

    def __init__(self, selected_tool: Tool, **kwargs: Any):
        """Initializes the ProjectPicker.

        Args:
            selected_tool: The tool that was selected and requires a project context.
            **kwargs: Additional arguments passed to the Screen.
        """
        super().__init__(**kwargs)
        self.selected_tool = selected_tool
        self.projects: list[Project] = []

    BINDINGS = [
        ("down", "cursor_down", "Next Item"),
        ("up", "cursor_up", "Previous Item"),
        ("enter", "select_current", "Select"),
    ]

    def compose(self) -> ComposeResult:
        """Composes the screen layout.

        Yields:
            The widget tree for the screen.
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

        root = get_project_root()
        from nexus.app import NexusApp

        if isinstance(self.app, NexusApp):
            self.projects = await self.app.container.scanner.scan_projects(root)

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

            # --- Recents Section ---
            from nexus.app import NexusApp
            if isinstance(self.app, NexusApp):
                recents = self.app.container.state_manager.get_recents()
                if recents:
                     # Find project objects for recent paths
                    recent_projects = []
                    for path_str in recents:
                        # Find matching project in discovered list
                        match = next((p for p in self.projects if str(p.path) == path_str), None)
                        if match:
                            recent_projects.append(match)
                    
                    if recent_projects:
                        project_list.append(ListItem(Label("[bold yellow]Recent Projects[/]"), classes="list-item"))
                        for proj in recent_projects:
                             project_list.append(ProjectListItem(project_data=proj))
                        
                        project_list.append(ListItem(Label("[bold blue]All Projects[/]"), classes="list-item"))
                        
                        # Filter out recents from main list to avoid duplication
                        recent_paths = {str(p.path) for p in recent_projects}
                        for project in self.projects:
                            if str(project.path) not in recent_paths:
                                project_list.append(ProjectListItem(project_data=project))
                        return

        # --- Fuzzy Search or Default List ---
        if filter_text:
            # Prepare data for fuzzy matching
            choices = {p.name: p for p in self.projects}
            # extract returns list of (choice, score, key)
            results = process.extract(filter_text, choices.keys(), limit=20)
            
            for name, score in results:
                if score > 40: # Threshold
                    project = choices[name]
                    project_list.append(ProjectListItem(project_data=project))
        else:
            # Default lexical sort
            for project in self.projects:
                project_list.append(ProjectListItem(project_data=project))

        # Check if list is effectively empty
        if not project_list.children:
            project_list.display = False
            empty_lbl = self.query_one("#projects-empty", Label)
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

    def _select_item(self, item: Any) -> None:
        """Internal method to handle item selection logic.

        Args:
            item: The selected ListItem.
        """
        if not isinstance(item, ProjectListItem):
            return

        if item.is_create_new:
            from nexus.screens.create_project import CreateProject

            def on_created(new_project_name: str) -> None:
                self.app.notify(f"Created project: {new_project_name}")
                # Refresh list and try to find the new project
                import asyncio

                async def refresh() -> None:
                    if isinstance(self.app, NexusApp):
                        root = get_project_root()
                        self.projects = await self.app.container.scanner.scan_projects(root)
                        self.populate_list(filter_text=new_project_name)

                asyncio.create_task(refresh())

            self.app.push_screen(CreateProject(on_created))
            return

        project = item.project_data
        if project:
            with self.app.suspend():
                from nexus.app import NexusApp

                if isinstance(self.app, NexusApp):
                    if self.app.container.executor.launch_tool(
                        self.selected_tool.command, project.path
                    ):
                        # Save to Recents
                        self.app.container.state_manager.add_recent(str(project.path))
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