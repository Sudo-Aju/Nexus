import psutil
import plotext as plt
from textual.app import ComposeResult
from textual.widgets import Static, Label, DataTable
from textual.containers import Vertical, Horizontal
from textual import work

class ProcessTable(Static):
    def compose(self) -> ComposeResult:
        yield Label("Process Monitor (Top CPU)", classes="h2")
        yield DataTable(id="proc-table")

    def on_mount(self):
        table = self.query_one("#proc-table")
        table.add_columns("PID", "Name", "User", "CPU%", "MEM%")
        self.update_procs()
        self.set_interval(3, self.update_procs)

    @work(exclusive=True)
    async def update_procs(self):
        procs = []
        for p in psutil.process_iter(['pid', 'name', 'username', 'cpu_percent', 'memory_percent']):
            try:
                procs.append(p.info)
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass
        
        procs.sort(key=lambda x: x['cpu_percent'] or 0, reverse=True)
        top = procs[:15]
        
        table = self.query_one("#proc-table")
        table.clear()
        for p in top:
            table.add_row(
                p['pid'],
                p['name'][:20],
                p['username'][:10] if p['username'] else "?",
                f"{(p['cpu_percent'] or 0):.1f}",
                f"{(p['memory_percent'] or 0):.1f}"
            )

class SystemGraph(Static):
    def __init__(self):
        super().__init__(classes="sys-graph")
        self.cpu_history = []
        self.mem_history = []
    
    def on_mount(self):
        self.update_graph()
        self.set_interval(2, self.update_graph)
    
    def update_graph(self):
        cpu = psutil.cpu_percent()
        mem = psutil.virtual_memory().percent
        
        self.cpu_history.append(cpu)
        self.mem_history.append(mem)
        
        if len(self.cpu_history) > 40:
            self.cpu_history.pop(0)
            self.mem_history.pop(0)
            
        plt.clear_figure()
        plt.theme('dark')
        plt.plot(self.cpu_history, label="CPU %")
        plt.plot(self.mem_history, label="MEM %")
        plt.ylim(0, 100)
        plt.frame(False)
        plt.plotsize(60, 15)
        
        graph_str = plt.build()
        self.update(graph_str)

class SystemView(Horizontal):
    def compose(self) -> ComposeResult:
        with Vertical(classes="proc-col"):
            yield ProcessTable()
        with Vertical(classes="graph-col"):
            yield Label("Telemetry", classes="h2")
            yield SystemGraph()
