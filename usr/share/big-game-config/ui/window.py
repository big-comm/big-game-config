"""
Main application window with sidebar navigation and adaptive views.
Modern GTK4 + Adwaita design following GNOME HIG.
"""

import gi
import os

gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")

from gi.repository import Gtk, Adw, GLib, Gio, GdkPixbuf, Gdk
from core.packages import get_packages_by_category
from core.pacman import is_package_installed
from ui.install_dialog import InstallDialog
from utils.i18n import _


class BigGameConfigWindow(Adw.ApplicationWindow):
    """Main application window with sidebar navigation."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Determine base directory for resources
        self.base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        if self.base_dir == "/usr/share":
            self.base_dir = "/usr/share/big-game-config"

        # Configure window
        self.set_title(_("BigLinux Game Config"))
        self.set_default_size(1100, 700)

        # Current view
        self.current_view = "launchers"

        # Build UI
        self._build_ui()

    def _build_ui(self):
        """Build the main window UI with modern Adwaita components."""
        # Breakpoint for mobile/desktop
        breakpoint = Adw.Breakpoint.new(Adw.BreakpointCondition.parse("max-width: 500sp"))

        # Navigation split view
        self.split_view = Adw.NavigationSplitView()
        breakpoint.add_setter(self.split_view, "collapsed", True)
        self.add_breakpoint(breakpoint)

        # Sidebar
        sidebar_page = self._create_sidebar()
        self.split_view.set_sidebar(sidebar_page)

        # Content
        content_page = self._create_content()
        self.split_view.set_content(content_page)

        self.set_content(self.split_view)

    def _create_sidebar(self):
        """Create sidebar with navigation."""
        # Sidebar navigation page
        sidebar_page = Adw.NavigationPage()
        sidebar_page.set_title(_("Navigation"))

        # Toolbar view for sidebar
        toolbar_view = Adw.ToolbarView()

        # Header bar for sidebar
        header = Adw.HeaderBar()
        header.set_show_end_title_buttons(False)
        toolbar_view.add_top_bar(header)

        # Navigation list
        list_box = Gtk.ListBox()
        list_box.set_selection_mode(Gtk.SelectionMode.SINGLE)
        list_box.add_css_class("navigation-sidebar")

        # Navigation items
        nav_items = [
            ("launchers", _("Launchers"), "applications-games-symbolic"),
            ("emulators", _("Emulators"), "input-gaming-symbolic"),
            ("tools", _("Tools"), "applications-system-symbolic"),
            ("hardware", _("Hardware"), "computer-symbolic"),
        ]

        for view_id, label, icon_name in nav_items:
            row = Adw.ActionRow()
            row.set_title(label)
            row.set_activatable(True)

            icon = Gtk.Image.new_from_icon_name(icon_name)
            icon.set_pixel_size(20)
            row.add_prefix(icon)

            # Store view_id
            row.view_id = view_id

            list_box.append(row)

        # Connect row activation
        list_box.connect("row-activated", self._on_nav_activated)

        # Select first row
        list_box.select_row(list_box.get_row_at_index(0))

        toolbar_view.set_content(list_box)
        sidebar_page.set_child(toolbar_view)

        return sidebar_page

    def _on_nav_activated(self, list_box, row):
        """Handle navigation row activation."""
        # Get view_id from the row (ActionRow is passed directly, not wrapped in ListBoxRow)
        view_id = getattr(row, 'view_id', None)

        if view_id:
            self.current_view = view_id
            self.view_stack.set_visible_child_name(view_id)

    def _create_content(self):
        """Create content area with navigation view."""
        # Content navigation page
        content_page = Adw.NavigationPage()
        content_page.set_title(_("BigLinux Game Config"))

        # Toolbar view
        toolbar_view = Adw.ToolbarView()

        # Header bar
        header = Adw.HeaderBar()

        # Search entry
        self.search_entry = Gtk.SearchEntry()
        self.search_entry.set_placeholder_text(_("Search packages..."))
        self.search_entry.set_hexpand(True)
        self.search_entry.set_max_width_chars(50)
        self.search_entry.connect("search-changed", self._on_search_changed)
        header.set_title_widget(self.search_entry)

        # Menu button
        menu_button = Gtk.MenuButton()
        menu_button.set_icon_name("open-menu-symbolic")
        menu = Gio.Menu()
        menu.append(_("About"), "app.about")
        menu.append(_("Quit"), "app.quit")
        menu_button.set_menu_model(menu)
        header.pack_end(menu_button)

        toolbar_view.add_top_bar(header)

        # View stack for content pages (not NavigationView - that's for hierarchical navigation)
        self.view_stack = Adw.ViewStack()

        # Create all view pages
        self._create_all_view_pages()

        # Wrap in scrolled window
        scrolled = Gtk.ScrolledWindow()
        scrolled.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        scrolled.set_child(self.view_stack)

        toolbar_view.set_content(scrolled)
        content_page.set_child(toolbar_view)

        return content_page

    def _create_all_view_pages(self):
        """Create all view pages."""
        # Launchers
        launchers_view = self._create_launchers_view()
        self.view_stack.add_titled(launchers_view, "launchers", _("Launchers"))

        # Emulators
        emulators_view = self._create_list_view("emulators", _("Emulators"), "Emulator")
        self.view_stack.add_titled(emulators_view, "emulators", _("Emulators"))

        # Tools
        tools_view = self._create_list_view("tools", _("Tools"), "Performance")
        self.view_stack.add_titled(tools_view, "tools", _("Tools"))

        # Hardware
        hardware_view = self._create_list_view("hardware", _("Hardware"), "Hardware")
        self.view_stack.add_titled(hardware_view, "hardware", _("Hardware"))

        # Set initial visible child
        self.view_stack.set_visible_child_name("launchers")

    def _create_launchers_view(self):
        """Create launchers view with cards."""
        # Scrolled window
        scrolled = Gtk.ScrolledWindow()
        scrolled.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)

        # Content box
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=20)
        box.set_margin_top(30)
        box.set_margin_bottom(30)
        box.set_margin_start(40)
        box.set_margin_end(40)

        # Title
        title = Gtk.Label()
        title.set_markup(f"<span size='xx-large' weight='bold'>{_('Launchers')}</span>")
        title.set_halign(Gtk.Align.START)
        box.append(title)

        # Grid for cards
        grid = Gtk.Grid()
        grid.set_row_spacing(20)
        grid.set_column_spacing(20)
        grid.set_column_homogeneous(True)

        # Get launcher packages
        packages_by_category = get_packages_by_category()
        launchers = []
        for cat_key, packages in packages_by_category.items():
            if "Launcher" in cat_key[1]:
                launchers = packages
                break

        # Add cards
        row, col = 0, 0
        for package in launchers:
            card = self._create_large_card(package)
            grid.attach(card, col, row, 1, 1)
            col += 1
            if col >= 2:
                col = 0
                row += 1

        box.append(grid)
        scrolled.set_child(box)

        return scrolled

    def _create_list_view(self, tag, title, category_filter):
        """Create list view with AdwActionRow."""
        # Scrolled window
        scrolled = Gtk.ScrolledWindow()
        scrolled.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)

        # Content box
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=20)
        box.set_margin_top(30)
        box.set_margin_bottom(30)
        box.set_margin_start(40)
        box.set_margin_end(40)

        # Title
        title_label = Gtk.Label()
        title_label.set_markup(f"<span size='xx-large' weight='bold'>{title}</span>")
        title_label.set_halign(Gtk.Align.START)
        box.append(title_label)

        # Get packages
        packages_by_category = get_packages_by_category()

        for cat_key, packages in packages_by_category.items():
            if category_filter in cat_key[1]:
                # Category group
                group = Adw.PreferencesGroup()
                group.set_title(cat_key[1])
                group.set_margin_top(10)

                for package in packages:
                    row = self._create_package_row(package)
                    group.add(row)

                box.append(group)

        scrolled.set_child(box)

        return scrolled

    def _create_large_card(self, package):
        """Create large card for launchers."""
        card = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=16)
        card.add_css_class("card")
        card.set_size_request(300, 320)

        # Store package info for search
        card.package_name = package['name'].lower()
        card.package_desc = package['description'].lower()

        # Icon
        icon_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        icon_box.set_margin_top(30)

        icon_path = os.path.join(self.base_dir, "icons", f"{package['icon']}.svg")
        if os.path.exists(icon_path):
            try:
                pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_scale(icon_path, 160, 160, True)
                texture = Gdk.Texture.new_for_pixbuf(pixbuf)
                icon = Gtk.Image.new_from_paintable(texture)
                icon.set_pixel_size(80)
                icon_box.append(icon)
            except:
                pass

        card.append(icon_box)

        # Name
        name_label = Gtk.Label()
        name_label.set_markup(f"<span size='x-large' weight='bold'>{package['name']}</span>")
        name_label.set_wrap(True)
        name_label.set_justify(Gtk.Justification.CENTER)
        card.append(name_label)

        # Description
        desc_label = Gtk.Label(label=package['description'])
        desc_label.set_wrap(True)
        desc_label.set_justify(Gtk.Justification.CENTER)
        desc_label.set_max_width_chars(35)
        desc_label.add_css_class("dim-label")
        desc_label.set_margin_start(20)
        desc_label.set_margin_end(20)
        card.append(desc_label)

        # Spacer
        spacer = Gtk.Box()
        spacer.set_vexpand(True)
        card.append(spacer)

        # Button
        is_installed = is_package_installed(package['package_name'])
        button = Gtk.Button(label=_("Remove") if is_installed else _("Install"))

        if is_installed:
            button.add_css_class("destructive-action")
        else:
            button.add_css_class("suggested-action")

        button.set_halign(Gtk.Align.CENTER)
        button.set_size_request(140, -1)
        button.set_margin_bottom(20)
        button.connect("clicked", self._on_package_action, package['package_name'])
        card.append(button)

        return card

    def _create_package_row(self, package):
        """Create AdwActionRow for package."""
        row = Adw.ActionRow()
        row.set_title(package['name'])
        row.set_subtitle(package['description'])

        # Store package info for search
        row.package_name = package['name'].lower()
        row.package_desc = package['description'].lower()

        # Icon
        icon_path = os.path.join(self.base_dir, "icons", f"{package['icon']}.svg")
        if os.path.exists(icon_path):
            try:
                pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_scale(icon_path, 96, 96, True)
                texture = Gdk.Texture.new_for_pixbuf(pixbuf)
                icon = Gtk.Image.new_from_paintable(texture)
                icon.set_pixel_size(48)
                row.add_prefix(icon)
            except:
                pass

        # Button
        is_installed = is_package_installed(package['package_name'])
        button = Gtk.Button(label=_("Remove") if is_installed else _("Install"))

        if is_installed:
            button.add_css_class("destructive-action")
        else:
            button.add_css_class("suggested-action")

        button.set_valign(Gtk.Align.CENTER)
        button.set_size_request(100, -1)
        button.connect("clicked", self._on_package_action, package['package_name'])
        row.add_suffix(button)

        return row

    def _on_search_changed(self, search_entry):
        """Handle search text changes."""
        search_text = search_entry.get_text().lower().strip()

        # Get current visible view
        visible_view = self.view_stack.get_visible_child()
        if not visible_view:
            return

        # Get the scrolled window and its child (the content box)
        content_box = visible_view.get_child()
        if not content_box:
            return

        # For launchers view: search in grid cards
        if self.current_view == "launchers":
            self._filter_launchers_view(content_box, search_text)
        else:
            # For list views: search in preference groups
            self._filter_list_view(content_box, search_text)

    def _filter_launchers_view(self, content_box, search_text):
        """Filter launcher cards based on search text."""
        # content_box is a Gtk.Box, find the grid inside it
        child = content_box.get_first_child()
        while child:
            if isinstance(child, Gtk.Grid):
                # Iterate through grid children (cards)
                card = child.get_first_child()
                while card:
                    # Check if card matches search
                    if search_text:
                        name = getattr(card, 'package_name', '')
                        desc = getattr(card, 'package_desc', '')
                        visible = search_text in name or search_text in desc
                    else:
                        visible = True

                    card.set_visible(visible)
                    card = card.get_next_sibling()
                break
            child = child.get_next_sibling()

    def _filter_list_view(self, content_box, search_text):
        """Filter list rows based on search text."""
        # content_box is a Gtk.Box, iterate through PreferencesGroups
        child = content_box.get_first_child()
        while child:
            if isinstance(child, Adw.PreferencesGroup):
                # Check each row in the group
                has_visible_rows = False
                row_widget = child.get_first_child()
                while row_widget:
                    if isinstance(row_widget, Adw.ActionRow):
                        # Check if row matches search
                        if search_text:
                            name = getattr(row_widget, 'package_name', '')
                            desc = getattr(row_widget, 'package_desc', '')
                            visible = search_text in name or search_text in desc
                        else:
                            visible = True

                        row_widget.set_visible(visible)
                        if visible:
                            has_visible_rows = True

                    row_widget = row_widget.get_next_sibling()

                # Hide group if no visible rows
                child.set_visible(has_visible_rows or not search_text)

            child = child.get_next_sibling()

    def _on_package_action(self, button, package_name):
        """Handle install/remove."""
        is_installed = is_package_installed(package_name)
        operation = "remove" if is_installed else "install"

        dialog = InstallDialog(self, package_name, operation)
        dialog.present()
        dialog.connect("close-request", lambda d: self._refresh_view())

    def _refresh_view(self):
        """Refresh current view after install/remove."""
        GLib.timeout_add(500, self._do_refresh)

    def _do_refresh(self):
        """Rebuild current view."""
        current = self.current_view

        # Remove current view from stack
        old_child = self.view_stack.get_child_by_name(current)
        if old_child:
            self.view_stack.remove(old_child)

        # Recreate view
        if current == "launchers":
            view = self._create_launchers_view()
            self.view_stack.add_titled(view, "launchers", _("Launchers"))
        elif current == "emulators":
            view = self._create_list_view("emulators", _("Emulators"), "Emulator")
            self.view_stack.add_titled(view, "emulators", _("Emulators"))
        elif current == "tools":
            view = self._create_list_view("tools", _("Tools"), "Performance")
            self.view_stack.add_titled(view, "tools", _("Tools"))
        elif current == "hardware":
            view = self._create_list_view("hardware", _("Hardware"), "Hardware")
            self.view_stack.add_titled(view, "hardware", _("Hardware"))
        else:
            return False

        # Set it as visible
        self.view_stack.set_visible_child_name(current)

        return False
