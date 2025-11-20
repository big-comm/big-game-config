"""
Package definitions organized by categories.
Each package contains metadata for display and installation.
"""

from utils.i18n import _


def get_packages_by_category():
    """
    Returns a dictionary of package categories with their respective packages.

    Returns:
        dict: Dictionary with category names as keys and lists of package dicts as values.
              Each category key is a tuple: (icon_name, translated_title)
    """
    return {
        ("applications-games-symbolic", _("Game Launchers")): [
            {
                "name": "Steam",
                "description": _("Main PC game store and launcher."),
                "package_name": "steam",
                "icon": "steam"
            },
            {
                "name": "Heroic Games Launcher",
                "description": _("Launcher for Epic Games, GOG and Prime Gaming."),
                "package_name": "heroic-games-launcher",
                "icon": "heroic"
            },
            {
                "name": "Steam Acolyte",
                "description": _("Allows logging into multiple Steam accounts simultaneously."),
                "package_name": "steam-acolyte",
                "icon": "acolyte"
            },
            # TODO: Add Lutris icon
            # {
            #     "name": "Lutris",
            #     "description": _("Open-source game manager."),
            #     "package_name": "lutris",
            #     "icon": "lutris"
            # },
        ],
        ("speedometer-symbolic", _("Performance Tools")): [
            {
                "name": "MangoHud",
                "description": _("Displays a HUD to monitor FPS, temperatures and hardware usage."),
                "package_name": "mangohud",
                "icon": "mangohud"
            },
            {
                "name": "GOverlay",
                "description": _("Graphical interface to manage and configure MangoHud."),
                "package_name": "goverlay",
                "icon": "goverlay"
            },
            {
                "name": "MangoJuice",
                "description": _("Tool for Vulkan layer injection, used with MangoHud."),
                "package_name": "mangojuice-bin",
                "icon": "mangojuice"
            },
            {
                "name": "ProtonPlus",
                "description": _("Manager for custom Proton versions (Proton-GE)."),
                "package_name": "protonplus",
                "icon": "protonplus"
            },
        ],
        ("computer-symbolic", _("Hardware and Overclock")): [
            {
                "name": "CoreCtrl",
                "description": _("Software for controlling AMD graphics card hardware."),
                "package_name": "corectrl",
                "icon": "corectrl"
            },
            {
                "name": "LACT",
                "description": _("Tool to monitor and control AMD GPUs."),
                "package_name": "lact",
                "icon": "lact"
            },
            {
                "name": "GreenWithEnvy (GWE)",
                "description": _("Interface to monitor and overclock NVIDIA graphics cards."),
                "package_name": "gwe",
                "icon": "gwe"
            },
        ],
        ("input-gaming-symbolic", _("Emulators")): [
            {
                "name": "RetroArch",
                "description": _("Frontend for emulators, allowing games from various consoles."),
                "package_name": "retroarch",
                "icon": "Retroarch"
            },
            {
                "name": "PCSX2",
                "description": _("PlayStation 2 emulator."),
                "package_name": "pcsx2",
                "icon": "PCSX2"
            },
            {
                "name": "RPCS3",
                "description": _("PlayStation 3 emulator."),
                "package_name": "rpcs3-bin",
                "icon": "rpcs3"
            },
        ]
    }


def get_all_packages():
    """
    Returns a flat list of all packages across all categories.

    Returns:
        list: List of all package dictionaries
    """
    packages = []
    for category_packages in get_packages_by_category().values():
        packages.extend(category_packages)
    return packages


def search_packages(query):
    """
    Search packages by name, description, or category.

    Args:
        query (str): Search query string

    Returns:
        dict: Dictionary with matching categories and packages
    """
    if not query or query.strip() == "":
        return get_packages_by_category()

    query_lower = query.lower().strip()
    results = {}

    categories = get_packages_by_category()
    for category_name, packages in categories.items():
        matching_packages = []

        # Check if category name matches
        category_matches = query_lower in category_name.lower()

        for package in packages:
            # Check if package name or description matches
            name_matches = query_lower in package["name"].lower()
            desc_matches = query_lower in package["description"].lower()

            if name_matches or desc_matches or category_matches:
                matching_packages.append(package)

        if matching_packages:
            results[category_name] = matching_packages

    return results
