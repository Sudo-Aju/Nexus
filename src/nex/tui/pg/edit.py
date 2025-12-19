from textual.screen import ModalScreen
from textual.app import ComposeResult
from textual.widgets import TextArea, Button, Label
from textual.containers import Vertical, Horizontal
from textual import on

class EditorScreen(ModalScreen):
    """Generic full-screen editor modal."""
    
    CSS = """
    EditorScreen {
        align: center middle;
        padding: 4;
        background: $background 80%;
    }
    
    #editor-container {
        width: 100%;
        height: 100%;
        background: $surface;
        border: thick $primary;
        padding: 1;
    }
    
    #editor-title {
        text-align: center;
        background: $primary;
        color: $text;
        text-style: bold;
        margin-bottom: 1;
        width: 100%;
    }
    
    #main-editor {
        height: 1fr;
        margin-bottom: 1;
        border: tall $accent;
    }
    
    #editor-buttons {
        height: auto;
        align: right bottom;
        dock: bottom;
    }
    
    #editor-buttons Button {
        margin-left: 2;
    }
    """

    def __init__(self, content="", title="Editor"):
        super().__init__()
        self.initial_content = content
        self.editor_title = title

    def compose(self) -> ComposeResult:
        with Vertical(id="editor-container"):
            yield Label(self.editor_title, id="editor-title")
            yield TextArea(self.initial_content, id="main-editor", show_line_numbers=True)
            with Horizontal(id="editor-buttons"):
                yield Button("Cancel", id="cancel", variant="error")
                yield Button("Save", id="save", variant="success")

    def on_mount(self):
        self.query_one("#main-editor").focus()

    @on(Button.Pressed, "#save")
    def action_save(self):
        content = self.query_one("#main-editor").text
        self.dismiss({"action": "save", "content": content})

    @on(Button.Pressed, "#cancel")
    def action_cancel(self):
        self.dismiss(None)
