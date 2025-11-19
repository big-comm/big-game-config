"""
Installation dialog with progress bar and expandable VTE terminal.
Shows real-time installation progress with beautiful terminal output.
"""

import gi

gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
gi.require_version("Vte", "3.91")

from gi.repository import Gtk, Adw, Vte, GLib
from core.terminal_colors import apply_theme_to_terminal
from utils.i18n import _


class InstallDialog(Adw.Window):
    """
    Dialog window for package installation/removal with progress indicator
    and expandable terminal output.
    """

    def __init__(self, parent, package_name, operation="install"):
        """
        Initialize the installation dialog.

        Args:
            parent: Parent window
            package_name (str): Name of the package to install/remove
            operation (str): Operation type - "install" or "remove"
        """
        super().__init__()

        self.package_name = package_name
        self.operation = operation
        self.is_complete = False
        self.success = False
        self.child_pid = None

        # Set up dialog properties
        self.set_transient_for(parent)
        self.set_modal(True)
        self.set_default_size(700, 500)

        operation_text = _("Installing") if operation == "install" else _("Removing")
        title = f"{operation_text} {package_name}"
        self.set_title(title)

        # Build UI
        self._build_ui()

        # Start operation
        GLib.idle_add(self._run_operation)

    def _build_ui(self):
        """Build the dialog user interface."""
        # Main container
        main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        self.set_content(main_box)

        # Header area with title and progress
        header_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        header_box.set_margin_top(24)
        header_box.set_margin_bottom(12)
        header_box.set_margin_start(24)
        header_box.set_margin_end(24)

        # Status label
        self.status_label = Gtk.Label()
        operation_text = _("Installing") if self.operation == "install" else _("Removing")
        status_text = f"{operation_text} {self.package_name}..."
        self.status_label.set_markup(f"<span size='large' weight='bold'>{status_text}</span>")
        self.status_label.set_halign(Gtk.Align.START)
        header_box.append(self.status_label)

        # Progress bar
        self.progress_bar = Gtk.ProgressBar()
        self.progress_bar.set_show_text(False)
        self.progress_bar.pulse()
        header_box.append(self.progress_bar)

        # Start progress pulse animation
        GLib.timeout_add(100, self._pulse_progress)

        main_box.append(header_box)

        # Expander for terminal output
        expander_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        expander_box.set_margin_start(24)
        expander_box.set_margin_end(24)
        expander_box.set_margin_bottom(12)

        # Expander header button
        expander_header = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        expander_header.add_css_class("toolbar")

        self.expander_label = Gtk.Label(label=_("Installation details"))
        self.expander_label.set_halign(Gtk.Align.START)
        self.expander_label.set_hexpand(True)
        expander_header.append(self.expander_label)

        self.expander_icon = Gtk.Image.new_from_icon_name("pan-down-symbolic")
        expander_header.append(self.expander_icon)

        expander_button = Gtk.Button()
        expander_button.set_child(expander_header)
        expander_button.add_css_class("flat")
        expander_button.connect("clicked", self._toggle_terminal)
        expander_box.append(expander_button)

        # Revealer for terminal (hidden by default)
        self.revealer = Gtk.Revealer()
        self.revealer.set_transition_type(Gtk.RevealerTransitionType.SLIDE_DOWN)
        self.revealer.set_transition_duration(200)

        # Terminal widget
        terminal_frame = Gtk.Frame()
        terminal_frame.set_margin_top(8)

        scrolled_window = Gtk.ScrolledWindow()
        scrolled_window.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        scrolled_window.set_min_content_height(300)

        self.terminal = Vte.Terminal()
        self.terminal.set_scrollback_lines(1000)
        self.terminal.set_scroll_on_output(True)

        # Apply Nord color theme
        apply_theme_to_terminal(self.terminal, "nord")

        # Set terminal font
        from gi.repository import Pango
        font_desc = Pango.FontDescription.from_string("Monospace 10")
        self.terminal.set_font(font_desc)

        # Connect child-exited signal
        self.terminal.connect("child-exited", self._on_child_exited)

        scrolled_window.set_child(self.terminal)
        terminal_frame.set_child(scrolled_window)
        self.revealer.set_child(terminal_frame)

        expander_box.append(self.revealer)
        main_box.append(expander_box)

        # Spacer
        spacer = Gtk.Box()
        spacer.set_vexpand(True)
        main_box.append(spacer)

        # Bottom button bar
        button_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        button_box.set_halign(Gtk.Align.END)
        button_box.set_margin_top(12)
        button_box.set_margin_bottom(24)
        button_box.set_margin_start(24)
        button_box.set_margin_end(24)

        self.cancel_button = Gtk.Button(label=_("Cancel"))
        self.cancel_button.connect("clicked", self._on_cancel)
        button_box.append(self.cancel_button)

        self.close_button = Gtk.Button(label=_("Close"))
        self.close_button.add_css_class("suggested-action")
        self.close_button.connect("clicked", self._on_close)
        self.close_button.set_sensitive(False)
        button_box.append(self.close_button)

        main_box.append(button_box)

    def _toggle_terminal(self, button):
        """Toggle terminal visibility."""
        is_revealed = self.revealer.get_reveal_child()
        self.revealer.set_reveal_child(not is_revealed)

        # Update icon
        icon_name = "pan-up-symbolic" if not is_revealed else "pan-down-symbolic"
        self.expander_icon.set_from_icon_name(icon_name)

    def _pulse_progress(self):
        """Pulse the progress bar animation."""
        if not self.is_complete:
            self.progress_bar.pulse()
            return True  # Continue animation
        return False  # Stop animation

    def _write_to_terminal(self, text):
        """
        Write text to terminal in the main thread.

        Args:
            text (str): Text to write
        """
        self.terminal.feed(text.encode('utf-8'))

    def _run_operation(self):
        """Run the installation/removal operation."""
        try:
            # Build command
            if self.operation == "install":
                argv = ["pkexec", "pacman", "-S", "--noconfirm", self.package_name]
                command_display = f"pkexec pacman -S --noconfirm {self.package_name}"
            else:
                argv = ["pkexec", "pacman", "-R", "--noconfirm", self.package_name]
                command_display = f"pkexec pacman -R --noconfirm {self.package_name}"

            self._write_to_terminal(f"$ {command_display}\n\n")

            # Spawn process in terminal
            self.terminal.spawn_async(
                Vte.PtyFlags.DEFAULT,
                None,  # working directory
                argv,
                None,  # environment
                GLib.SpawnFlags.DO_NOT_REAP_CHILD,
                None,  # child setup
                None,  # child setup data
                -1,    # timeout
                None,  # cancellable
                self._on_spawn_complete,
                None   # user data
            )

        except Exception as e:
            self._write_to_terminal(f"\n{_('Error')}: {str(e)}\n")
            self._on_operation_complete(False)

        return False  # Remove idle source

    def _on_spawn_complete(self, terminal, pid, error, user_data):
        """Called when spawn completes."""
        if error:
            self._write_to_terminal(f"\n{_('Error')}: {error.message}\n")
            self._on_operation_complete(False)
        else:
            self.child_pid = pid
            # Process will exit and trigger child-exited signal

    def _on_child_exited(self, terminal, status):
        """Handle child process exit."""
        # Check if already completed to avoid double-trigger
        if self.is_complete:
            return

        success = status == 0
        self._on_operation_complete(success)

    def _on_operation_complete(self, success):
        """
        Handle operation completion.

        Args:
            success (bool): Whether the operation succeeded
        """
        if self.is_complete:
            return  # Avoid double completion

        self.is_complete = True
        self.success = success

        # Update desktop database if installation was successful
        if success and self.operation == "install":
            GLib.timeout_add(500, self._update_desktop_database)

        # Update status label
        if success:
            operation_text = _("installed") if self.operation == "install" else _("removed")
            status_text = f"✓ {self.package_name} {operation_text} {_('successfully')}!"
            self.status_label.set_markup(f"<span size='large' weight='bold' foreground='#26A269'>{status_text}</span>")
        else:
            operation_text = _("install") if self.operation == "install" else _("remove")
            status_text = f"✗ {_('Failed to')} {operation_text} {self.package_name}"
            self.status_label.set_markup(f"<span size='large' weight='bold' foreground='#C01C28'>{status_text}</span>")

        # Update progress bar
        self.progress_bar.set_fraction(1.0 if success else 0.0)

        # Enable close button, disable cancel
        self.close_button.set_sensitive(True)
        self.cancel_button.set_sensitive(False)

        # Auto-expand terminal on error
        if not success and not self.revealer.get_reveal_child():
            self._toggle_terminal(None)

    def _update_desktop_database(self):
        """Update desktop database and icon cache after installation."""
        try:
            import subprocess
            # Update desktop database
            subprocess.run(
                ["update-desktop-database", "-q"],
                capture_output=True,
                timeout=10
            )
            # Update icon cache
            subprocess.run(
                ["gtk-update-icon-cache", "-f", "-t", "/usr/share/icons/hicolor"],
                capture_output=True,
                timeout=10
            )
        except Exception as e:
            print(f"Warning: Could not update desktop database: {e}")

        return False  # Remove timeout source

    def _on_cancel(self, button):
        """Handle cancel button click."""
        if self.child_pid and not self.is_complete:
            try:
                import os
                import signal
                os.kill(self.child_pid, signal.SIGTERM)
            except:
                pass
        self.close()

    def _on_close(self, button):
        """Handle close button click."""
        self.close()

    def get_result(self):
        """
        Get the operation result.

        Returns:
            bool: True if operation succeeded, False otherwise
        """
        return self.success
