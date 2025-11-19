"""
Main application window with category-based package layout and search functionality.
"""

import gi
import os

gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")

from gi.repository import Gtk, Adw, GLib, Gio
from core.packages import get_packages_by_category, search_packages
from ui.category_section import CategorySection
from ui.install_dialog import InstallDialog
from utils.i18n import _


class BigGameConfigWindow(Adw.ApplicationWindow):
    """Main application window with modern Adwaita design."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Determine base directory for resources
        self.base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        if self.base_dir == "/usr/share":
            self.base_dir = "/usr/share/big-game-config"

        # Configure window
        self.set_title(_("BigLinux Game Config"))
        self.set_default_size(1000, 700)

        # Store category sections for refresh
        self.category_sections = []

        # Build UI
        self._build_ui()

        # Load custom CSS after UI is built
        self._load_css()

    def _load_css(self):
        """Load custom CSS styles for the application."""
        css_provider = Gtk.CssProvider()

        # Define CSS inline with higher specificity
        # Using !important to override Adwaita defaults
        css_data = """
        /* Compact buttons - 30% smaller */
        button.compact-button {
            padding: 4px 10px !important;
            min-height: 26px !important;
            min-width: 60px !important;
            font-size: 13px !important;
        }

        button.compact-button.suggested-action,
        button.compact-button.destructive-action {
            padding: 4px 10px !important;
            min-height: 26px !important;
        }
        """

        try:
            css_provider.load_from_data(css_data.encode('utf-8'))
            Gtk.StyleContext.add_provider_for_display(
                self.get_display(),
                css_provider,
                Gtk.STYLE_PROVIDER_PRIORITY_USER
            )
            print("✓ CSS loaded with USER priority")
        except Exception as e:
            print(f"Warning: Could not load CSS: {e}")

    def _build_ui(self):
        """Build the main window UI."""
        # Main container
        main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)

        # Header bar with search
        header = Adw.HeaderBar()

        # Search button and entry
        self.search_entry = Gtk.SearchEntry()
        self.search_entry.set_placeholder_text(_("Search packages..."))
        self.search_entry.set_size_request(300, -1)
        self.search_entry.connect("search-changed", self._on_search_changed)
        header.set_title_widget(self.search_entry)

        # Refresh button
        refresh_button = Gtk.Button()
        refresh_button.set_icon_name("view-refresh-symbolic")
        refresh_button.set_tooltip_text(_("Refresh package status"))
        refresh_button.connect("clicked", self._on_refresh_clicked)
        header.pack_end(refresh_button)

        # Menu button
        menu_button = Gtk.MenuButton()
        menu_button.set_icon_name("open-menu-symbolic")
        menu_button.set_tooltip_text(_("Menu"))

        # Create menu model
        menu = Gio.Menu()
        menu.append(_("About"), "app.about")
        menu.append(_("Quit"), "app.quit")
        menu_button.set_menu_model(menu)

        header.pack_end(menu_button)

        main_box.append(header)

        # Clamp for centered content with max width
        clamp = Adw.Clamp()
        clamp.set_maximum_size(1200)
        clamp.set_tightening_threshold(900)

        # Scrolled window for package categories
        scrolled_window = Gtk.ScrolledWindow()
        scrolled_window.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        scrolled_window.set_vexpand(True)

        # Container for category sections
        self.categories_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=24)
        self.categories_box.set_margin_top(24)
        self.categories_box.set_margin_bottom(24)
        self.categories_box.set_margin_start(12)
        self.categories_box.set_margin_end(12)

        # Load initial categories
        self._load_categories()

        scrolled_window.set_child(self.categories_box)
        clamp.set_child(scrolled_window)

        # Toast overlay for notifications
        self.toast_overlay = Adw.ToastOverlay()
        self.toast_overlay.set_child(clamp)
        main_box.append(self.toast_overlay)

        # Set main content
        self.set_content(main_box)

    def _load_categories(self, categories=None):
        """
        Load package categories into the UI.

        Args:
            categories (dict, optional): Dictionary of categories to display.
                                        If None, loads all categories.
        """
        # Clear existing category sections
        while child := self.categories_box.get_first_child():
            self.categories_box.remove(child)
        self.category_sections.clear()

        # Get categories to display
        if categories is None:
            categories = get_packages_by_category()

        # Check if we have any results
        if not categories:
            # Show empty state
            status_page = Adw.StatusPage()
            status_page.set_icon_name("system-search-symbolic")
            status_page.set_title(_("No packages found"))
            status_page.set_description(_("Try adjusting your search"))
            status_page.set_vexpand(True)
            self.categories_box.append(status_page)
            return

        # Create section for each category
        for category_key, packages in categories.items():
            if packages:  # Only show categories with packages
                section = CategorySection(
                    category_key,  # Pass the full tuple (icon, name)
                    packages,
                    self.base_dir,
                    self._on_install_package,
                    self._on_remove_package
                )
                self.category_sections.append(section)
                self.categories_box.append(section)

    def _on_search_changed(self, search_entry):
        """Handle search entry text change."""
        query = search_entry.get_text()

        # Debounce search to avoid too many updates
        if hasattr(self, '_search_timeout'):
            GLib.source_remove(self._search_timeout)

        self._search_timeout = GLib.timeout_add(300, self._perform_search, query)

    def _perform_search(self, query):
        """
        Perform the actual search and update UI.

        Args:
            query (str): Search query

        Returns:
            bool: False to remove the timeout source
        """
        results = search_packages(query)
        self._load_categories(results)
        return False  # Remove timeout source

    def _on_refresh_clicked(self, button):
        """Handle refresh button click."""
        # Refresh all category sections
        for section in self.category_sections:
            section.refresh_all_cards()

        # Show toast notification
        toast = Adw.Toast.new(_("Package status updated"))
        toast.set_timeout(2)
        self.toast_overlay.add_toast(toast)

    def _on_install_package(self, package_name, card):
        """
        Handle package installation request.

        Args:
            package_name (str): Name of the package to install
            card (PackageCard): The card widget that triggered the installation
        """
        # Show installation dialog
        dialog = InstallDialog(self, package_name, operation="install")
        dialog.present()

        # Connect to dialog close to refresh card status
        dialog.connect("close-request", lambda d: self._on_dialog_closed(card))

    def _on_remove_package(self, package_name, card):
        """
        Handle package removal request.

        Args:
            package_name (str): Name of the package to remove
            card (PackageCard): The card widget that triggered the removal
        """
        # Show removal dialog
        dialog = InstallDialog(self, package_name, operation="remove")
        dialog.present()

        # Connect to dialog close to refresh card status
        dialog.connect("close-request", lambda d: self._on_dialog_closed(card))

    def _on_dialog_closed(self, card):
        """
        Handle dialog close event and refresh card status.

        Args:
            card (PackageCard): The card widget to refresh

        Returns:
            bool: False (required by signal handler)
        """
        # Refresh the card status after dialog closes
        GLib.timeout_add(100, lambda: card.refresh_status())

        # Show toast notification
        toast = Adw.Toast.new(_("Operation completed"))
        toast.set_timeout(2)
        self.toast_overlay.add_toast(toast)

        return False  # Required by signal handler
