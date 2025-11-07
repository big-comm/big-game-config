import gi

gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")

from gi.repository import Gtk, Adw
from core.packages import get_packages

class BigGameConfigWindow(Gtk.ApplicationWindow):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.set_title("BigLinux Game Config")
        self.set_default_size(800, 600)

        header = Gtk.HeaderBar()
        self.set_titlebar(header)

        main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        main_box.set_margin_top(12)
        main_box.set_margin_bottom(12)
        main_box.set_margin_start(12)
        main_box.set_margin_end(12)
        self.set_child(main_box)

        title = Gtk.Label()
        title.set_markup("<span size='xx-large' weight='bold'>BigLinux Game Config</span>")
        main_box.append(title)

        flowbox = Gtk.FlowBox()
        flowbox.set_valign(Gtk.Align.START)
        flowbox.set_max_children_per_line(4)
        flowbox.set_selection_mode(Gtk.SelectionMode.NONE)

        packages = get_packages()
        for pkg in packages:
            flowbox.append(self.create_package_card(pkg))

        main_box.append(flowbox)

    def create_package_card(self, package_info):
        card = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        card.set_size_request(150, 200)
        card.set_margin_top(12)
        card.set_margin_bottom(12)
        card.set_margin_start(12)
        card.set_margin_end(12)
        card.get_style_context().add_class("card")

        # Adicionar ícone do pacote (a ser implementado)
        # icon = Gtk.Image.new_from_icon_name(package_info["icon"], Gtk.IconSize.LARGE)
        # card.append(icon)

        name = Gtk.Label()
        name.set_markup(f"<span weight='bold'>{package_info['name']}</span>")
        card.append(name)

        description = Gtk.Label(label=package_info["description"])
        description.set_wrap(True)
        card.append(description)

        button = Gtk.Button(label="Instalar")
        button.connect("clicked", self.on_install_clicked, package_info["package_name"])
        card.append(button)

        return card

    def on_install_clicked(self, button, package_name):
        print(f"Instalando {package_name}...")
        # Aqui você chamará o comando de instalação, por exemplo, via subprocess
