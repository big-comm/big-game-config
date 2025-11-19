import sys
import os
import gi

gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")

from gi.repository import Gtk, Gio, Adw
from ui.window import BigGameConfigWindow
from utils.i18n import _


class BigGameConfigApplication(Adw.Application):
    def __init__(self):
        super().__init__(application_id="org.communitybig.big-game-config",
                         flags=Gio.ApplicationFlags.FLAGS_NONE)

        # Create actions
        self.create_action("about", self.on_about_action)
        self.create_action("quit", self.on_quit_action)

    def do_activate(self):
        win = self.props.active_window
        if not win:
            win = BigGameConfigWindow(application=self)
        win.present()

    def create_action(self, name, callback):
        """Create an action and add it to the app."""
        action = Gio.SimpleAction.new(name, None)
        action.connect("activate", callback)
        self.add_action(action)

    def on_about_action(self, action, param):
        """Show the about dialog."""
        about = Adw.AboutDialog(
            application_name=_("BigLinux Game Config"),
            application_icon="org.communitybig.big-game-config",
            developer_name="BigLinux Community",
            version="1.0.0",
            developers=[
                "BigLinux Team",
                "Community Contributors"
            ],
            copyright="© 2024 BigLinux Community",
            license_type=Gtk.License.GPL_3_0,
            website="https://www.biglinux.com.br",
            issue_url="https://github.com/biglinux/big-game-config/issues",
            support_url="https://github.com/biglinux/big-game-config",
            translator_credits=_("translator-credits"),
            comments=_(
                "Install and manage your gaming applications and tools.\n"
                "Supports game launchers, performance tools, hardware utilities, and emulators."
            )
        )
        about.present(self.props.active_window)

    def on_quit_action(self, action, param):
        """Quit the application."""
        self.quit()


def main():
    # Setup icon theme to include local icons when running from source
    base_dir = os.path.dirname(os.path.abspath(__file__))
    # Go up two levels: from /usr/share/big-game-config to /usr/share
    share_dir = os.path.dirname(base_dir)
    local_icon_dir = os.path.join(share_dir, "icons", "hicolor")

    # Add to XDG_DATA_DIRS if running from source
    if os.path.exists(local_icon_dir):
        xdg_data_dirs = os.environ.get("XDG_DATA_DIRS", "/usr/local/share:/usr/share")
        if share_dir not in xdg_data_dirs:
            os.environ["XDG_DATA_DIRS"] = f"{share_dir}:{xdg_data_dirs}"

    app = BigGameConfigApplication()
    return app.run(sys.argv)


if __name__ == "__main__":
    sys.exit(main())
