from textual.screen import Screen
from textual.app import ComposeResult
from textual.widgets import Label, Input, Button
from textual.containers import Vertical
from textual import on, work
from textual.reactive import reactive
import hashlib
from nex.db.conn import get_db
from nex.db.repo.secret import SecretRepo

class AuthScreen(Screen):
    CSS = """
    AuthScreen {
        align: center middle;
        background: $background;
    }
    
    #login-box {
        width: 60;
        height: auto;
        background: $panel;
        border: thick $accent;
        padding: 4;
        align: center middle;
    }
    
    #login-header {
        text-align: center;
        text-style: bold;
        color: $accent;
        margin-bottom: 2;
        width: 100%;
        content-align: center middle;
    }
    
    #error-msg {
        color: $error;
        text-align: center;
        margin-top: 2;
        display: none;
    }
    
    #error-msg.visible {
        display: block;
    }
    
    Input {
        margin: 1 0;
    }
    
    Button {
        width: 100%;
        margin-top: 2;
    }
    
    .hidden {
        display: none;
    }
    """

    mode = reactive("loading")

    def compose(self) -> ComposeResult:
        with Vertical(id="login-box"):
            yield Label("NEXUS SYSTEM LOCK", id="login-header", classes="h2")
            

            with Vertical(id="setup_container", classes="hidden"):
                yield Label("System Setup Required")
                yield Input(placeholder="Set Username", id="setup_user")
                yield Input(placeholder="Set Password", password=True, id="setup_pass")
                yield Button("Initialize System", variant="primary", id="setup_btn")
            

            with Vertical(id="login_container", classes="hidden"):
                yield Label("Enter Passphrase:", id="login_label")
                yield Input(placeholder="Password", password=True, id="login_pass")
                yield Button("Unlock System", variant="primary", id="login_btn")
                
            yield Label("", id="error-msg")

    def on_mount(self):
        self.check_setup_status()

    def watch_mode(self, mode: str):
        self.query_one("#setup_container").set_class(mode == "setup", "-active")
        self.query_one("#setup_container").set_class(mode != "setup", "hidden")
        
        self.query_one("#login_container").set_class(mode == "login", "-active")
        self.query_one("#login_container").set_class(mode != "login", "hidden")
        
        if mode == "setup":
             self.query_one("#setup_user").focus()
        elif mode == "login":
             self.query_one("#login_pass").focus()

    @work
    async def check_setup_status(self):
        try:
            async for session in get_db():
                repo = SecretRepo(session)
                try:
                    user = await repo.get("auth_user")
                    if user:
                        self.stored_user = user
                        self.query_one("#login_label").update(f"Welcome, {user}. Enter Password:")
                        self.mode = "login"
                    else:
                        self.mode = "setup"
                except Exception as e:
                except Exception as e:
                    self.show_error(f"DB Error: {e}. Try running init_db.py")

                break
        except Exception as e:
             self.show_error(f"Connection Error: {e}")

    @on(Button.Pressed, "#setup_btn")
    async def action_setup(self):
        user = self.query_one("#setup_user").value.strip()
        pwd = self.query_one("#setup_pass").value.strip()
        
        if not user or not pwd:
            self.show_error("Username and Password required.")
            return


        hashed = hashlib.sha256(pwd.encode()).hexdigest()
        
        async for session in get_db():
            repo = SecretRepo(session)
            await repo.set("auth_user", user)
            await repo.set("auth_pass", hashed)
            self.notify("System Initialized.")
            
            self.app.pop_screen()
            self.notify("Access Granted")
            break

    @on(Button.Pressed, "#login_btn")
    def action_login(self):
        self.verify_login()

    @on(Input.Submitted, "#login_pass")
    def on_login_submit(self):
        self.verify_login()
        
    @work
    async def verify_login(self):
        pwd = self.query_one("#login_pass").value.strip()
        hashed = hashlib.sha256(pwd.encode()).hexdigest()
        
        async for session in get_db():
            repo = SecretRepo(session)
            stored_hash = await repo.get("auth_pass")
            
            if stored_hash == hashed:
                self.app.pop_screen()
                self.notify("Access Granted")
            else:
                self.show_error("Invalid Password")
                self.query_one("#login_pass").value = ""
            break

    def show_error(self, msg):
        err = self.query_one("#error-msg")
        err.update(msg)
        err.add_class("visible")
