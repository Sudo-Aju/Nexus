from textual.app import App
from nex.tui.main_screen import MainScreen

class NexusApp(App):
    CSS_PATH = "tui/css/main.tcss"

    def on_mount(self):
        self.push_screen(MainScreen())
        from nex.tui.pg.auth import AuthScreen
        self.push_screen(AuthScreen())