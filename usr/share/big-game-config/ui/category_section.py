"""
Category section component for grouping packages by category.
"""

import gi

gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")

from gi.repository import Gtk, Adw, GLib
from ui.package_card import PackageCard


class CategorySection(Gtk.Box):
    """
    A section widget that displays a category title and a grid of package cards.
    Uses Adwaita PreferencesGroup style for elegant category grouping.
    """

    def __init__(self, category_key, packages, base_dir, on_install, on_remove):
        """
        Initialize the category section.

        Args:
            category_key (tuple): Tuple of (icon_name, category_title)
            packages (list): List of package dictionaries in this category
            base_dir (str): Base directory for finding resources
            on_install (callable): Callback function for install button clicks
            on_remove (callable): Callback function for remove button clicks
        """
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=12)

        # Extract icon and name from tuple
        if isinstance(category_key, tuple):
            self.category_icon = category_key[0]
            self.category_name = category_key[1]
        else:
            # Fallback for old format (string only)
            self.category_icon = "folder-symbolic"
            self.category_name = category_key

        self.packages = packages
        self.base_dir = base_dir
        self.on_install = on_install
        self.on_remove = on_remove

        # Build the section
        self._build_section()

    def _build_section(self):
        """Build the category section with title and package grid."""
        # Category header
        header_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)
        header_box.set_margin_top(16)
        header_box.set_margin_bottom(8)
        header_box.set_margin_start(12)

        # Category icon
        icon = Gtk.Image.new_from_icon_name(self.category_icon)
        icon.set_pixel_size(24)
        icon.add_css_class("accent")
        header_box.append(icon)

        # Category title
        title_label = Gtk.Label()
        # Escape special characters like & for markup
        escaped_name = GLib.markup_escape_text(self.category_name)
        title_label.set_markup(f"<span size='large' weight='bold'>{escaped_name}</span>")
        title_label.set_halign(Gtk.Align.START)
        header_box.append(title_label)

        self.append(header_box)

        # Separator line
        separator = Gtk.Separator(orientation=Gtk.Orientation.HORIZONTAL)
        separator.set_margin_start(12)
        separator.set_margin_end(12)
        separator.set_margin_bottom(12)
        self.append(separator)

        # Package grid - FlowBox for 2-column responsive layout
        self.flowbox = Gtk.FlowBox()
        self.flowbox.set_max_children_per_line(2)
        self.flowbox.set_min_children_per_line(1)
        self.flowbox.set_selection_mode(Gtk.SelectionMode.NONE)
        self.flowbox.set_row_spacing(16)
        self.flowbox.set_column_spacing(16)
        self.flowbox.set_homogeneous(True)
        self.flowbox.set_margin_start(12)
        self.flowbox.set_margin_end(12)

        # Add package cards
        for package in self.packages:
            card = PackageCard(package, self.base_dir)
            card.connect("install-clicked", self._on_card_install)
            card.connect("remove-clicked", self._on_card_remove)
            self.flowbox.append(card)

        self.append(self.flowbox)

    def _on_card_install(self, card, package_name):
        """Handle install signal from package card."""
        if self.on_install:
            self.on_install(package_name, card)

    def _on_card_remove(self, card, package_name):
        """Handle remove signal from package card."""
        if self.on_remove:
            self.on_remove(package_name, card)

    def refresh_all_cards(self):
        """Refresh installation status for all cards in this category."""
        child = self.flowbox.get_first_child()
        while child is not None:
            card_widget = child.get_child()
            if isinstance(card_widget, PackageCard):
                card_widget.refresh_status()
            child = child.get_next_sibling()
