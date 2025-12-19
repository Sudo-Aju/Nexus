from textual.app import ComposeResult
from textual.screen import Screen
from textual.widgets import Header, Footer, TabbedContent, TabPane, Placeholder
from nex.tui.pg.board import KanbanView


from nex.tui.pg.dev import DevOpsView
from nex.tui.pg.comms import CommsView
from nex.tui.pg.system import SystemView
from nex.tui.pg.assistant import AssistantView

class MainScreen(Screen):
    BINDINGS = [
        ("q", "quit", "Quit"),
        ("s", "scratchpad", "Scratchpad"),
    ]

    def compose(self) -> ComposeResult:
        yield Header()
        with TabbedContent(initial="projects"):
            with TabPane("Projects", id="projects"):
                yield KanbanView()
            

            

            
            with TabPane("DevOps", id="devops"):
                yield DevOpsView()
            
            with TabPane("Comms", id="comms"):
                yield CommsView()

            with TabPane("System", id="system"):
                yield SystemView()

            with TabPane("Assistant", id="assistant"):
                yield AssistantView()

        yield Footer()

    def action_scratchpad(self):
        from nex.tui.pg.edit import EditorScreen
        # We could load persistent scratchpad content here if we had it.
        # For now, it's a transient buffer.
        self.app.push_screen(EditorScreen(title="Scratchpad"), self.on_scratchpad_close)

    def on_scratchpad_close(self, result):
        if result and result.get("action") == "save":
             # In a real app, save to a file or DB
             self.notify("Scratchpad content saved (in memory only).")
