from textual.app import ComposeResult
from textual.widgets import Static, Label, Input, RichLog
from textual.containers import Vertical
from textual import on, work
from nex.svc.ai import AIService

class AssistantView(Vertical):
    def compose(self) -> ComposeResult:
        yield Label("NEXUS Assistant", classes="h2")
        yield RichLog(id="chat-history", highlight=True, markup=True)
        yield Input(placeholder="Ask me anything...", id="chat-input")

    def on_mount(self):
        log = self.query_one("#chat-history")
        log.write("[bold green]System:[/bold green] AI Module Online. Connected to OpenAI (gpt-5.1).")

    @on(Input.Submitted, "#chat-input")
    async def on_chat(self, event: Input.Submitted):
        query = event.value
        if not query: return
        
        log = self.query_one("#chat-history")
        log.write(f"[bold blue]User:[/bold blue] {query}")
        event.input.value = ""
        
        self.run_query(query)

    @work
    async def run_query(self, query: str):
        log = self.query_one("#chat-history")
        svc = AIService(
            provider="openai", 
            api_key="sk-hc-v1-e9c67e1d665c4e62863d251f1a17c78b6b6112edf6094198bece31b509ec6e80",
            model="openai/gpt-4o",
            base_url="https://ai.hackclub.com/proxy/v1"
        )
        
        log.write("[italic dimmer]Thinking...[/italic dimmer]")
        response = await svc.chat(query)
        
        log.write(f"[bold purple]NEXUS:[/bold purple] {response}")
        log.write("---")
