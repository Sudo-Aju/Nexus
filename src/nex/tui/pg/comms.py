from textual.app import ComposeResult
from textual.widgets import Static, DataTable, Label, TextArea, Button
from textual.containers import Vertical, Horizontal
from textual import on, work
from nex.svc.comms import CommsService

class CommsView(Vertical):
    def compose(self) -> ComposeResult:
        yield Label("Unified Inbox", classes="h2")
        yield DataTable(id="inbox-table")
        
        with Vertical(id="reply-box", classes="hidden"):
            yield Label("Quick Reply:", classes="h3")
            yield TextArea(id="reply-input")
            yield Button("Send", id="send-reply", variant="primary")

    def on_mount(self):
        table = self.query_one("#inbox-table")
        table.cursor_type = "row"
        table.add_columns("Source", "Sender", "Subject", "Time")
        self.load_messages()

    @work
    async def load_messages(self):
        svc = CommsService()
        msgs = await svc.fetch_recent()
        
        table = self.query_one("#inbox-table")
        table.clear()
        
        for m in msgs:
            table.add_row(
                m.source,
                m.sender,
                m.snippet,
                str(m.timestamp.time().strftime("%H:%M")),
                key=m.id
            )

    @on(DataTable.RowSelected, "#inbox-table")
    def on_msg_select(self, event: DataTable.RowSelected):
        self.query_one("#reply-box").remove_class("hidden")
        self.query_one("#reply-input").focus()
        
    @on(Button.Pressed, "#send-reply")
    async def on_send(self):
        content = self.query_one("#reply-input").text
        self.query_one("#reply-box").add_class("hidden")
        self.query_one("#reply-input").text = ""
        self.notify("Reply sent!")
