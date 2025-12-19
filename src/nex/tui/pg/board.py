from textual.app import ComposeResult
from textual.screen import ModalScreen, Screen
from textual.widgets import Static, Label, Header, Footer, Button, Input, TextArea
from textual.containers import VerticalScroll, Horizontal, Vertical
from textual.message import Message
from textual.binding import Binding
from textual import on

from nex.db.conn import get_db
from nex.db.repo.task import TaskRepo
from datetime import datetime

class TaskForm(ModalScreen):
    
    def __init__(self, task=None, title="New Task"):
        super().__init__()
        self.task_data = task
        self.form_title = title
        
    def compose(self) -> ComposeResult:
        with Vertical(id="form-container"):
            yield Label(self.form_title, id="header", classes="h1")
            
            yield Label("Title:", id="title-label")
            yield Input(
                value=self.task_data.title if self.task_data else "", 
                placeholder="Task Title", 
                id="title_input"
            )
            
            yield Label("Description:", id="desc-label")
            yield TextArea(
                self.task_data.desc if self.task_data and self.task_data.desc else "", 
                id="desc_input",
                show_line_numbers=False,
            )

            yield Label("Start Date (YYYY-MM-DD):")
            s_val = str(self.task_data.start_date.date()) if self.task_data and self.task_data.start_date else ""
            yield Input(s_val, id="start_input", placeholder="YYYY-MM-DD")
            
            yield Label("Due Date (YYYY-MM-DD):")
            d_val = str(self.task_data.due_date.date()) if self.task_data and self.task_data.due_date else ""
            yield Input(d_val, id="due_input", placeholder="YYYY-MM-DD")
            
            with Horizontal(classes="buttons"):
                yield Button("Cancel", variant="error", id="cancel")
                yield Button("Save", variant="primary", id="save")

    def on_mount(self):
        self.query_one("#title_input").focus()

    @on(Button.Pressed, "#save")
    def action_save(self):
        title = self.query_one("#title_input").value
        desc = self.query_one("#desc_input").text
        start_str = self.query_one("#start_input").value
        due_str = self.query_one("#due_input").value
        
        start_date = None
        due_date = None
        
        try:
            if start_str.strip():
                start_date = datetime.strptime(start_str.strip(), "%Y-%m-%d")
            if due_str.strip():
                due_date = datetime.strptime(due_str.strip(), "%Y-%m-%d")
        except ValueError:
            self.notify("Invalid date format. Use YYYY-MM-DD", severity="error")
            return
        
        if not title.strip():
            self.notify("Title is required!", severity="error")
            return
            
        self.dismiss({
            "action": "save", 
            "title": title, 
            "desc": desc, 
            "start_date": start_date,
            "due_date": due_date,
            "task": self.task_data
        })

    @on(Button.Pressed, "#cancel")
    def action_cancel(self):
        self.dismiss(None)

class TaskCard(Static):
    
    class StatusChanged(Message):
        def __init__(self, card, new_status):
            self.card = card
            self.new_status = new_status
            super().__init__()

    class DeleteRequested(Message):
        def __init__(self, card):
            self.card = card
            super().__init__()
            
    class EditRequested(Message):
        def __init__(self, card):
            self.card = card
            super().__init__()

    BINDINGS = [
        Binding("space", "toggle_status", "Next Status"),
        Binding("e", "edit", "Edit"),
        Binding("d", "delete", "Delete"),
    ]

    def __init__(self, task):
        super().__init__(classes="task-card")
        self.db_task = task
        self.task_id = task.id
        self.task_title = task.title
        self.task_desc = task.desc
        self.status = task.status
        self.can_focus = True
        
        self._blockers = []
        try:
             self._blockers = [{"title": b.title, "status": b.status} for b in task.blockers]
        except Exception:
             pass 
             
        self._children = []
        try:
            self._children = [{"title": c.title, "status": c.status} for c in task.children]
        except Exception:
            pass

    def compose(self) -> ComposeResult:
        with Vertical():
            yield Label(self.task_title, classes="task-title")
            
            if self._blockers:
                blocked_names = ", ".join([b['title'] for b in self._blockers if b['status'] != 'done'])
                if blocked_names:
                    yield Label(f"⛔ Blocked by: {blocked_names}", classes="task-blocked")
                    self.add_class("-blocked")
            
            if self.task_desc:
                yield Label(self.task_desc, classes="task-desc")
            
            if self._children:
                yield Label("Subtasks:", classes="subtask-header")
                for child in self._children:
                    status_icon = "✓" if child['status'] == 'done' else "○"
                    yield Label(f"  {status_icon} {child['title']}", classes="subtask-item")

    def on_mount(self):
        self.update_appearance()

    def update_appearance(self):
        self.remove_class("-done")
        self.remove_class("-doing")
        self.remove_class("-blocked")
        
        if self.status == "done":
            self.add_class("-done")
        elif self.status == "doing":
            self.add_class("-doing")
            
        if any(b['status'] != 'done' for b in self._blockers):
             self.add_class("-blocked")

    def action_toggle_status(self):
        if self.status == "todo":
            unfinished_blockers = [b for b in self._blockers if b['status'] != 'done']
            if unfinished_blockers:
                self.notify(f"Blocked by {len(unfinished_blockers)} tasks!", severity="error")
                return

        next_status = {
            "todo": "doing",
            "doing": "done",
            "done": "todo" 
        }.get(self.status, "todo")
        self.post_message(self.StatusChanged(self, next_status))
        
    def action_edit(self):
        self.post_message(self.EditRequested(self))
        
    def action_delete(self):
        self.post_message(self.DeleteRequested(self))
        
    def on_click(self):
        self.focus()

class KanbanColumn(VerticalScroll):
    def __init__(self, title, id):
        self.title = title
        super().__init__(id=id, classes="column")

    def compose(self) -> ComposeResult:
        yield Label(self.title, classes="col-header")
        
class KanbanView(Vertical):
    BINDINGS = [
        ("n", "new_task", "New Task"),
        ("l", "refresh", "Refresh"),
    ]

    def compose(self) -> ComposeResult:
        with Horizontal(id="board"):
            yield KanbanColumn("To Do", id="todo")
            yield KanbanColumn("Doing", id="doing")
            yield KanbanColumn("Done", id="done")

    async def on_mount(self):
        await self.load_tasks()

    async def load_tasks(self):
        for col_id in ["#todo", "#doing", "#done"]:
            col = self.query_one(col_id)
            for child in col.query("TaskCard"):
                child.remove()
                
        async for session in get_db():
            repo = TaskRepo(session)
            tasks = await repo.get_all()
            
            cols = {
                "todo": self.query_one("#todo"),
                "doing": self.query_one("#doing"),
                "done": self.query_one("#done"),
            }
            
            for task in tasks:
                target_col = cols.get(task.status, cols["todo"])
                target_col.mount(TaskCard(task))
            break

    def action_new_task(self):
        self.app.push_screen(TaskForm(title="Add New Task"), self.on_task_form_close)

    async def on_task_form_close(self, result):
        if result and result.get("action") == "save":
            title = result["title"]
            desc = result["desc"]
            start_date = result.get("start_date")
            due_date = result.get("due_date")
            
            async for session in get_db():
                repo = TaskRepo(session)
                new_task = await repo.create(title, desc, start_date=start_date, due_date=due_date)
                
                self.query_one("#todo").mount(TaskCard(new_task))
                self.notify(f"Created task '{title}'")
                break

    async def on_task_card_edit_requested(self, event: TaskCard.EditRequested):
        self.app.push_screen(
            TaskForm(task=event.card.db_task, title="Edit Task"), 
            lambda res: self.on_edit_form_close(res, event.card)
        )

    async def on_edit_form_close(self, result, card: TaskCard):
        if result and result.get("action") == "save":
            async for session in get_db():
                repo = TaskRepo(session)
                await repo.update(
                    card.db_task.id, 
                    result["title"], 
                    result["desc"],
                    start_date=result.get("start_date"),
                    due_date=result.get("due_date")
                )
                break
            
            card.db_task.title = result["title"]
            card.db_task.desc = result["desc"]
            card.db_task.start_date = result.get("start_date")
            card.db_task.due_date = result.get("due_date")
            card.task_title = result["title"]
            card.task_desc = result["desc"]
            
            card.remove_children()
            card.mount(Label(card.task_title, classes="task-title"))
            if card.task_desc:
                card.mount(Label(card.task_desc, classes="task-desc"))
                
            self.notify(f"Updated task '{result['title']}'")

    async def on_task_card_status_changed(self, event: TaskCard.StatusChanged):
        async for session in get_db():
            repo = TaskRepo(session)
            await repo.update_status(event.card.task_id, event.new_status)
            break 
        
        event.card.status = event.new_status
        event.card.update_appearance()
        
        event.card.remove()
        col_id = f"#{event.new_status}"
        col = self.query_one(col_id)
        col.mount(event.card)
        event.card.focus()

    async def on_task_card_delete_requested(self, event: TaskCard.DeleteRequested):
       async for session in get_db():
           repo = TaskRepo(session)
           await repo.delete(event.card.task_id)
           break
       
       event.card.remove()
       self.notify("Task deleted")

    def action_refresh(self):
        self.run_worker(self.load_tasks())
