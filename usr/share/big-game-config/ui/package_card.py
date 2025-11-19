"""
Package card component for displaying individual packages.
"""

import gi
import os

gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
gi.require_version("GdkPixbuf", "2.0")

from gi.repository import Gtk, Adw, GObject, GdkPixbuf
from core.pacman import is_package_installed
from utils.i18n import _


class PackageCard(Gtk.Box):
    """
    A card widget that displays package information with icon, name, description,
    status badge, and action button.
    """

    __gtype_name__ = 'PackageCard'

    # Signals
    __gsignals__ = {
        'install-clicked': (GObject.SignalFlags.RUN_FIRST, None, (str,)),
        'remove-clicked': (GObject.SignalFlags.RUN_FIRST, None, (str,)),
    }

    def __init__(self, package_info, base_dir):
        """
        Initialize the package card.

        Args:
            package_info (dict): Package information containing name, description, package_name, and icon
            base_dir (str): Base directory for finding resources like icons
        """
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=12)

        self.package_info = package_info
        self.base_dir = base_dir
        self.package_name = package_info["package_name"]

        # Style the card
        self.add_css_class("card")
        self.set_size_request(280, 320)

        # Create card content
        self._build_card()

    def _build_card(self):
        """Build the card layout with all components."""
        # Icon container
        icon_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        icon_box.set_halign(Gtk.Align.CENTER)
        icon_box.set_margin_top(16)

        # Load and display icon with high quality rendering
        icon_path = os.path.join(self.base_dir, "icons", f"{self.package_info['icon']}.svg")
        if os.path.exists(icon_path):
            try:
                # Load SVG at high resolution (2x for crisp display)
                # Use scale factor for HiDPI displays
                scale_factor = 2
                pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_scale(
                    icon_path,
                    64 * scale_factor,  # width
                    64 * scale_factor,  # height
                    True  # preserve aspect ratio
                )

                # Create texture from pixbuf for GTK4
                from gi.repository import Gdk
                texture = Gdk.Texture.new_for_pixbuf(pixbuf)

                icon = Gtk.Image.new_from_paintable(texture)
                icon.set_pixel_size(64)
                icon_box.append(icon)
            except Exception as e:
                # Fallback to simple file loading if pixbuf fails
                print(f"Warning: Could not load high-res icon {icon_path}: {e}")
                icon = Gtk.Image.new_from_file(icon_path)
                icon.set_pixel_size(64)
                icon_box.append(icon)
        else:
            # Fallback icon if file not found
            icon = Gtk.Image.new_from_icon_name("application-x-executable")
            icon.set_pixel_size(64)
            icon.set_opacity(0.5)
            icon_box.append(icon)

        self.append(icon_box)

        # Package name
        name_label = Gtk.Label()
        name_label.set_markup(f"<span size='large' weight='bold'>{self.package_info['name']}</span>")
        name_label.set_wrap(True)
        name_label.set_justify(Gtk.Justification.CENTER)
        name_label.set_max_width_chars(30)
        name_label.set_margin_top(8)
        name_label.set_margin_start(12)
        name_label.set_margin_end(12)
        self.append(name_label)

        # Description
        desc_label = Gtk.Label(label=self.package_info["description"])
        desc_label.set_wrap(True)
        desc_label.set_justify(Gtk.Justification.CENTER)
        desc_label.set_max_width_chars(35)
        desc_label.set_lines(3)
        desc_label.set_ellipsize(3)  # PANGO_ELLIPSIZE_END
        desc_label.add_css_class("dim-label")
        desc_label.set_margin_start(12)
        desc_label.set_margin_end(12)
        self.append(desc_label)

        # Spacer to push status and button to bottom
        spacer = Gtk.Box()
        spacer.set_vexpand(True)
        self.append(spacer)

        # Status badge
        self.status_badge = self._create_status_badge()
        self.append(self.status_badge)

        # Action button
        self.action_button = self._create_action_button()
        self.append(self.action_button)

    def _create_status_badge(self):
        """
        Create status badge showing installation state.

        Returns:
            Gtk.Box: Status badge container
        """
        badge_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        badge_box.set_halign(Gtk.Align.CENTER)
        badge_box.set_margin_bottom(8)

        is_installed = is_package_installed(self.package_name)

        if is_installed:
            # Installed badge - green with checkmark
            badge_box.add_css_class("success")
            badge_box.set_margin_start(8)
            badge_box.set_margin_end(8)
            badge_box.set_margin_top(4)
            badge_box.set_margin_bottom(4)

            check_icon = Gtk.Image.new_from_icon_name("object-select-symbolic")
            check_icon.set_pixel_size(16)
            badge_box.append(check_icon)

            status_label = Gtk.Label(label=_("Installed"))
            status_label.add_css_class("caption")
            badge_box.append(status_label)
        else:
            # Not installed badge - subtle
            status_label = Gtk.Label(label=_("Not installed"))
            status_label.add_css_class("dim-label")
            status_label.add_css_class("caption")
            badge_box.append(status_label)

        return badge_box

    def _create_action_button(self):
        """
        Create action button (Install/Remove) based on installation state.

        Returns:
            Gtk.Button: Action button
        """
        is_installed = is_package_installed(self.package_name)

        if is_installed:
            button = Gtk.Button(label=_("Remove"))
            button.add_css_class("destructive-action")
            button.connect("clicked", self._on_remove_clicked)
        else:
            button = Gtk.Button(label=_("Install"))
            button.add_css_class("suggested-action")
            button.connect("clicked", self._on_install_clicked)

        button.set_margin_start(12)
        button.set_margin_end(12)
        button.set_margin_bottom(12)

        return button

    def _on_install_clicked(self, button):
        """Handle install button click."""
        self.emit("install-clicked", self.package_name)

    def _on_remove_clicked(self, button):
        """Handle remove button click."""
        self.emit("remove-clicked", self.package_name)

    def refresh_status(self):
        """Refresh the card's installation status and update UI accordingly."""
        # Remove old status badge and button
        self.remove(self.status_badge)
        self.remove(self.action_button)

        # Create new ones with updated status
        self.status_badge = self._create_status_badge()
        self.action_button = self._create_action_button()

        # Add them back
        self.append(self.status_badge)
        self.append(self.action_button)
