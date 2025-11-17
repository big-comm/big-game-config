import gi
import os

gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")

from gi.repository import Gtk, Adw
from core.packages import get_packages
from core.pacman import is_package_installed

class BigGameConfigWindow(Gtk.ApplicationWindow):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Determina o diretório base para encontrar recursos como ícones
        # Se o programa estiver instalado, usará /usr/share/big-game-config
        # Se estiver rodando localmente, usará o diretório atual
        self.base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        if self.base_dir == "/usr/share":
             self.base_dir = "/usr/share/big-game-config"


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

        scrolled_window = Gtk.ScrolledWindow()
        scrolled_window.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        scrolled_window.set_vexpand(True)

        self.flowbox = Gtk.FlowBox()
        self.flowbox.set_max_children_per_line(4)
        self.flowbox.set_selection_mode(Gtk.SelectionMode.NONE)
        self.flowbox.set_row_spacing(12)
        self.flowbox.set_column_spacing(12)

        self.load_packages()

        scrolled_window.set_child(self.flowbox)
        main_box.append(scrolled_window)

    def load_packages(self):
        """Carrega ou recarrega todos os cards de pacotes."""
        while child := self.flowbox.get_child_at_index(0):
            self.flowbox.remove(child)

        packages = get_packages()
        for pkg in packages:
            self.flowbox.append(self.create_package_card(pkg))

    def create_package_card(self, package_info):
        card = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        card.set_size_request(150, 200)
        card.get_style_context().add_class("card")
        card.set_margin_top(12)
        card.set_margin_bottom(12)
        card.set_margin_start(12)
        card.set_margin_end(12)

        # --- Bloco ÚNICO e CORRIGIDO para ícone e título ---
        title_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        title_box.set_halign(Gtk.Align.CENTER)

        # Usa o base_dir para montar o caminho do ícone
        icon_path = os.path.join(self.base_dir, "icons", f"{package_info['icon']}.svg")
        if os.path.exists(icon_path):
            icon = Gtk.Image.new_from_file(icon_path)
            icon.set_pixel_size(32)
            title_box.append(icon)

        name = Gtk.Label()
        name.set_markup(f"<span weight='bold'>{package_info['name']}</span>")
        title_box.append(name)

        card.append(title_box)
        # --- Fim do bloco corrigido ---

        description = Gtk.Label(label=package_info["description"])
        description.set_wrap(True)
        card.append(description)

        package_name = package_info["package_name"]
        if is_package_installed(package_name):
            button = Gtk.Button(label="Remover")
            button.get_style_context().add_class("destructive-action")
            button.connect("clicked", self.on_remove_clicked, package_name)
        else:
            button = Gtk.Button(label="Instalar")
            button.get_style_context().add_class("suggested-action")
            button.connect("clicked", self.on_install_clicked, package_name)

        button.set_vexpand(True)
        button.set_valign(Gtk.Align.END)
        card.append(button)

        return card

    def on_install_clicked(self, button, package_name):
        print(f"Instalando {package_name}...")
        # Lógica de instalação...

    def on_remove_clicked(self, button, package_name):
        print(f"Removendo {package_name}...")
        # Lógica de remoção...
