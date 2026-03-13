"""Screen for selecting a project directory.

Allows users to browse potential project directories and choose one as the
context for a tool execution. Also supports creating new projects.
"""

from pathlib import Path
from typing import Any

from textual import on, work
from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Container, Horizontal, Vertical
from textual.screen import ModalScreen, Screen
from textual.widgets import (
    Button,
    DirectoryTree,
    Header,
    Footer,
    Input,
    Label,
    ListItem,
    ListView,
)

from nexus.models import Project, Tool


class AdvancedBrowseModal(ModalScreen[Path | None]):
    """A modal screen providing a full filesystem browser."""

    BINDINGS = [
        Binding("escape", "cancel", "Cancel"),
    ]

    def compose(self) -> ComposeResult:
        from nexus.app import NexusApp
        root = Path.home()
        if isinstance(self.app, NexusApp):
            root = self.app.container.config_manager.get_project_root()

        yield Header()
        with Container(classes="modal-dialog"):
            yield Label("Advanced Project Browser", classes="modal-title")
            yield DirectoryTree(root, id="advanced-directory-tree")
        yield Footer()

    @on(DirectoryTree.DirectorySelected)
    def on_directory_selected(self, event: DirectoryTree.DirectorySelected) -> None:
        self.dismiss(event.path)

    @on(DirectoryTree.FileSelected)
    def on_file_selected(self, event: DirectoryTree.FileSelected) -> None:
        self.dismiss(event.path)

    def action_cancel(self) -> None:
        self.dismiss(None)


class ProjectPicker(Screen[None]):
    """Screen for choosing or creating a project directory.

    Attributes:
        tool: The Tool model being launched.
        _filtered_projects: Cached list of matching projects.
    """

    def __init__(self, tool: Tool, **kwargs: Any):
        """Initializes the ProjectPicker screen.

        Args:
            tool: The tool requiring a project context.
            **kwargs: Additional keyword arguments passed to Screen.
        """
        super().__init__(**kwargs)
        self.tool = tool
        self._filtered_projects: list[Project | str] = []

    BINDINGS = [
        Binding("enter", "select", "Select"),
        Binding("ctrl+b", "browse", "Browse"),
        Binding("escape", "app.back", "Back", show=True),
    ]

    def compose(self) -> ComposeResult:
        """Composes the screen layout.

        Yields:
            The widget tree for the screen.
        """
        yield Header()
        yield Label(f"Launch {self.tool.label}", id="project-picker-header")
        yield Input(placeholder="Search or filter projects...", id="project-search")
        
        with Vertical(id="project-list-container"):
            yield Label("Project History", classes="section-header")
            yield ListView(id="project-list")
            yield Label(
                "No recent projects. Use 'Browse' to find one.",
                id="projects-empty",
                classes="empty-state hidden"
            )

        with Horizontal(id="project-picker-footer"):
            yield Button("Browse Filesystem (Ctrl+B)", variant="default", id="btn-browse")
            yield Button("Create New Project", variant="primary", id="btn-create")
        
        yield Footer()

    def on_mount(self) -> None:
        """Initializes the project list on mount."""
        self.refresh_projects()
        self.query_one("#project-search").focus()

    @work(thread=True)
    async def refresh_projects(self, filter_text: str = "") -> None:
        """Asynchronously updates the project list.

        Args:
            filter_text: Optional query to filter projects.
        """
        from nexus.container import get_container
        
        root = get_container().config_manager.get_project_root()
        projects = await get_container().scanner.scan_projects(root)
        recents = get_container().state_manager.get_recents()
        
        # Merge scanner results with recents
        all_paths = set(p.path for p in projects)
        for r in recents:
            path_obj = Path(r)
            if r not in all_paths and path_obj.exists():
                projects.append(Project(name=path_obj.name, path=path_obj, is_git=False))
        
        if filter_text:
            projects = [
                p for p in projects 
                if filter_text.lower() in p.name.lower() or filter_text.lower() in str(p.path).lower()
            ]

        self.app.call_from_thread(self._update_list, projects)

    def _update_list(self, projects: list[Project]) -> None:
        """Updates the ListView with results.

        Args:
            projects: The list of project models to display.
        """
        list_view = self.query_one("#project-list", ListView)
        list_view.clear()
        
        empty_label = self.query_one("#projects-empty", Label)
        
        if not projects:
            empty_label.remove_class("hidden")
            list_view.display = False
        else:
            empty_label.add_class("hidden")
            list_view.display = True
            for project in sorted(projects, key=lambda p: p.name.lower()):
                item = ListItem(Label(f" {project.name} [dim]({project.path})[/]"))
                # Use a custom attribute to store the path string
                setattr(item, "project_path", str(project.path))
                list_view.append(item)

    @on(Input.Changed, "#project-search")
    def on_search_changed(self, event: Input.Changed) -> None:
        self.refresh_projects(event.value)

    @on(ListView.Selected, "#project-list")
    def on_project_selected(self, event: ListView.Selected) -> None:
        # Find the path from the item
        path = getattr(event.item, "project_path", None)
        if path:
            self._handle_project_selection(path)

    @on(Button.Pressed, "#btn-browse")
    def action_browse(self) -> None:
        """Opens the advanced filesystem browser modal."""
        self.app.push_screen(AdvancedBrowseModal(), callback=self._handle_project_selection)

    @on(Button.Pressed, "#btn-create")
    def action_create(self) -> None:
        """Opens the project creation modal."""
        from nexus.screens.create_project import CreateProject
        from nexus.app import NexusApp
        
        if isinstance(self.app, NexusApp):
            root = self.app.container.config_manager.get_project_root()
            self.app.push_screen(CreateProject(root), callback=self._handle_project_selection)

    def _handle_project_selection(self, path: Path | str | None) -> None:
        """Processes the final project selection and launches the tool.

        Args:
            path: The selected directory path.
        """
        if not path:
            return

        final_path = Path(path)
        from nexus.container import get_container
        get_container().state_manager.add_recent(str(final_path))
        
        # Pop back to tool selector and execute
        from nexus.screens.tool_selector import ToolSelector
        
        # We need to find the ToolSelector in the stack
        for stack_screen in self.app.screen_stack:
            if isinstance(stack_screen, ToolSelector):
                # Pop the ProjectPicker and any other modals on top
                self.app.pop_screen()
                stack_screen.execute_tool_command(self.tool, project_path=final_path)
                break

    def action_back(self) -> None:
        """Go back to the previous screen."""
        self.app.pop_screen()

    def action_select(self) -> None:
        """Selects the currently highlighted project."""
        list_view = self.query_one("#project-list", ListView)
        if list_view.has_focus and list_view.index is not None:
            # We trigger the list view's internal selection mechanism
            list_view.action_select_cursor()
