import asyncio
import os
import pty
import fcntl
import struct
import termios
import sys
from textual.app import ComposeResult
from textual.widgets import Static, Label, TabbedContent, TabPane, RichLog, Input
from textual.containers import Vertical, Horizontal
from textual import on, work
from textual.reactive import reactive

class TerminalWidget(Static):
    """
    A simple PTY-based terminal emulator widget.
    It spawns a bash/zsh shell and pipes output to a RichLog.
    Input extends textual Input but forwards keys to the PTY.
    """
    def __init__(self):
        super().__init__(classes="term-widget")
        self.master_fd = None
        self.slave_fd = None
        self.proc = None
        self.buffer = ""

    def compose(self) -> ComposeResult:
        with Vertical():
            yield RichLog(id="term-out", markup=False, auto_scroll=True)
            yield Input(placeholder="Command...", id="term-in")

    def on_mount(self):
        self.master_fd, self.slave_fd = pty.openpty()
        
        fl = fcntl.fcntl(self.master_fd, fcntl.F_GETFL)
        fcntl.fcntl(self.master_fd, fcntl.F_SETFL, fl | os.O_NONBLOCK)
        
        shell = os.environ.get("SHELL", "/bin/sh")
        
        try:
            self.proc = asyncio.create_subprocess_exec(
                shell,
                stdin=self.slave_fd,
                stdout=self.slave_fd,
                stderr=self.slave_fd,
                preexec_fn=os.setsid
            )
            self.read_output()
            asyncio.create_task(self.proc)
        except Exception as e:
            self.query_one("#term-out").write(f"Failed to spawn shell: {e}")

    @work(exclusive=True)
    async def read_output(self):
        while True:
            await asyncio.sleep(0.05) 
            try:
                data = os.read(self.master_fd, 1024)
                if data:
                    text = data.decode(errors="replace")
                    self.query_one("#term-out").write(text)
            except BlockingIOError:
                pass
            except Exception:
                break

    @on(Input.Submitted, "#term-in")
    def on_command(self, event: Input.Submitted):
        if self.master_fd:
            cmd = event.value + "\n"
            os.write(self.master_fd, cmd.encode())
            event.input.value = ""

from textual.widgets import DataTable

class DockerWidget(Static):
    def compose(self) -> ComposeResult:
        yield Label("Docker Containers", classes="h2")
        yield DataTable(id="docker-table")

    def on_mount(self):
        table = self.query_one("#docker-table")
        table.add_columns("ID", "Image", "Name", "Status")
        self.refresh_containers()
        self.set_interval(5, self.refresh_containers)

    @work(exclusive=True)
    async def refresh_containers(self):
        import docker
        try:
            client = docker.from_env()
            containers = client.containers.list()
            
            table = self.query_one("#docker-table")
            table.clear()
            
            for c in containers:
                table.add_row(
                    c.short_id,
                    c.image.tags[0] if c.image.tags else "none",
                    c.name,
                    c.status
                )
        except Exception as e:
            pass

class DevOpsView(Horizontal):
    def compose(self) -> ComposeResult:
        with TabbedContent():
            with TabPane("Terminal"):
                yield TerminalWidget()
            with TabPane("Docker"):
                yield DockerWidget()
