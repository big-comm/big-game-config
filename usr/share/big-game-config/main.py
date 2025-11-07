import sys
import gi

gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")

from gi.repository import Gtk, Gio
from ui.window import BigGameConfigWindow

class BigGameConfigApplication(Gtk.Application):
    def __init__(self):
        super().__init__(application_id="org.communitybig.big-game-config",
                         flags=Gio.ApplicationFlags.FLAGS_NONE)

    def do_activate(self):
        win = self.props.active_window
        if not win:
            win = BigGameConfigWindow(application=self)
        win.present()

def main():
    app = BigGameConfigApplication()
    return app.run(sys.argv)
