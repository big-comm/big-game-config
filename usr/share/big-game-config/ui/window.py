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

        # Current view tracking
        self.current_view = "launchers"
        self.last_active_view = "launchers" # Armazena a última view real visitada

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
        # Get view_id from the row
        view_id = getattr(row, 'view_id', None)

        if view_id:
            # Se não estivermos no modo de busca, salvamos onde o usuário clicou
            # e limpamos a busca se houver texto
            self.current_view = view_id
            self.last_active_view = view_id
            
            # Se houver texto na busca e o usuário clicar na sidebar, limpamos a busca
            if hasattr(self, 'search_entry') and self.search_entry.get_text():
                self.search_entry.set_text("")
                # O set_text("") disparará _on_search_changed, que fará a troca de view
            else:
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

        # Search Results View (Hidden by default, used when searching)
        self.search_results_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=20)
        self.search_results_box.set_margin_top(30)
        self.search_results_box.set_margin_bottom(30)
        self.search_results_box.set_margin_start(40)
        self.search_results_box.set_margin_end(40)
        self.view_stack.add_titled(self.search_results_box, "search_results", _("Search Results"))

        # Set initial visible child
        self.view_stack.set_visible_child_name("launchers")

    def _create_launchers_view(self):
        """Create launchers view with cards."""
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

        # FlowBox for cards (maintains size when children are hidden)
        flowbox = Gtk.FlowBox()
        flowbox.set_valign(Gtk.Align.START)
        flowbox.set_max_children_per_line(2)
        flowbox.set_min_children_per_line(2)
        flowbox.set_row_spacing(20)
        flowbox.set_column_spacing(20)
        flowbox.set_homogeneous(True)
        flowbox.set_selection_mode(Gtk.SelectionMode.NONE)

        # Get launcher packages
        packages_by_category = get_packages_by_category()
        launchers = []
        for cat_key, packages in packages_by_category.items():
            if "Launcher" in cat_key[1]:
                launchers = packages
                break

        # Add cards
        for package in launchers:
            card = self._create_large_card(package)
            flowbox.append(card)

        box.append(flowbox)

        return box

    def _create_list_view(self, tag, title, category_filter):
        """Create list view with large cards in grid layout."""
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
                # Category title
                category_title = Gtk.Label()
                category_title.set_markup(f"<span size='large' weight='bold'>{cat_key[1]}</span>")
                category_title.set_halign(Gtk.Align.START)
                category_title.set_margin_top(20)
                box.append(category_title)

                # FlowBox for cards (maintains size when children are hidden)
                flowbox = Gtk.FlowBox()
                flowbox.set_valign(Gtk.Align.START)
                flowbox.set_max_children_per_line(2)
                flowbox.set_min_children_per_line(2)
                flowbox.set_row_spacing(20)
                flowbox.set_column_spacing(20)
                flowbox.set_homogeneous(True)
                flowbox.set_selection_mode(Gtk.SelectionMode.NONE)
                flowbox.set_margin_top(10)

                # Add cards
                for package in packages:
                    card = self._create_large_card(package)
                    flowbox.append(card)

                box.append(flowbox)

        return box

    def _create_large_card(self, package):
        """Create large card for launchers."""
        card = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        card.add_css_class("card")
        card.set_size_request(320, 280)

        # Store package info for search
        card.package_name = package['name'].lower()
        card.package_desc = package['description'].lower()

        # Icon
        icon_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        icon_box.set_margin_top(24)

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
        name_label.set_markup(f"<span size='large' weight='bold'>{package['name']}</span>")
        name_label.set_wrap(True)
        name_label.set_justify(Gtk.Justification.CENTER)
        name_label.set_margin_top(4)
        card.append(name_label)

        # Description
        desc_label = Gtk.Label(label=package['description'])
        desc_label.set_wrap(True)
        desc_label.set_justify(Gtk.Justification.CENTER)
        desc_label.set_max_width_chars(35)
        desc_label.add_css_class("dim-label")
        desc_label.set_margin_start(16)
        desc_label.set_margin_end(16)
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
        button.set_margin_bottom(16)
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
        """Handle search text changes and display global results."""
        search_text = search_entry.get_text().lower().strip()

        if not search_text:
            # Se a busca foi limpa, volta para a última view selecionada
            self.current_view = self.last_active_view
            self.view_stack.set_visible_child_name(self.last_active_view)
            return

        # Limpa resultados anteriores
        child = self.search_results_box.get_first_child()
        while child:
            self.search_results_box.remove(child)
            child = self.search_results_box.get_first_child()

        # Define o título da busca
        title = Gtk.Label()
        title.set_markup(f"<span size='xx-large' weight='bold'>{_('Search Results')}</span>")
        title.set_halign(Gtk.Align.START)
        self.search_results_box.append(title)

        # Realiza a busca global
        packages_by_category = get_packages_by_category()
        found_any = False

        for category_key, packages in packages_by_category.items():
            category_matches = []
            
            # Pega o nome da categoria (tupla ou string)
            cat_name = category_key[1] if isinstance(category_key, tuple) else category_key
            
            # Verifica se o termo buscado está no nome da categoria
            is_cat_match = search_text in cat_name.lower()

            for package in packages:
                name_match = search_text in package["name"].lower()
                desc_match = search_text in package["description"].lower()
                
                # Se deu match no pacote OU na categoria, adiciona o pacote
                if name_match or desc_match or is_cat_match:
                    category_matches.append(package)

            if category_matches:
                found_any = True
                
                # Adiciona cabeçalho da categoria
                cat_label = Gtk.Label()
                cat_label.set_markup(f"<span size='large' weight='bold'>{cat_name}</span>")
                cat_label.set_halign(Gtk.Align.START)
                cat_label.set_margin_top(20)
                self.search_results_box.append(cat_label)

                # Cria grid para os resultados
                flowbox = Gtk.FlowBox()
                flowbox.set_valign(Gtk.Align.START)
                flowbox.set_max_children_per_line(2)
                flowbox.set_min_children_per_line(2)
                flowbox.set_row_spacing(20)
                flowbox.set_column_spacing(20)
                flowbox.set_homogeneous(True)
                flowbox.set_selection_mode(Gtk.SelectionMode.NONE)
                flowbox.set_margin_top(10)

                for package in category_matches:
                    card = self._create_large_card(package)
                    flowbox.append(card)

                self.search_results_box.append(flowbox)

        if not found_any:
            no_results = Gtk.Label(label=_("No packages found."))
            no_results.add_css_class("dim-label")
            no_results.set_margin_top(40)
            self.search_results_box.append(no_results)

        # Atualiza o estado para view de busca
        self.current_view = "search_results"
        self.view_stack.set_visible_child_name("search_results")


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
