"""
Terminal color schemes for VTE widget.
Provides beautiful color palettes for terminal output.
"""

import gi

gi.require_version("Gdk", "4.0")
from gi.repository import Gdk


def parse_color(hex_color):
    """
    Parse hex color string to Gdk.RGBA.

    Args:
        hex_color (str): Hex color string (e.g., "#2E3440")

    Returns:
        Gdk.RGBA: Parsed color object
    """
    rgba = Gdk.RGBA()
    rgba.parse(hex_color)
    return rgba


class NordTheme:
    """
    Nord color scheme - a beautiful arctic, north-bluish color palette.
    https://www.nordtheme.com/
    """

    @staticmethod
    def get_colors():
        """
        Get Nord theme colors for VTE terminal.

        Returns:
            dict: Dictionary with foreground, background, cursor, and palette colors
        """
        return {
            "foreground": parse_color("#D8DEE9"),
            "background": parse_color("#2E3440"),
            "cursor": parse_color("#D8DEE9"),
            "palette": [
                parse_color("#3B4252"),  # Black
                parse_color("#BF616A"),  # Red
                parse_color("#A3BE8C"),  # Green
                parse_color("#EBCB8B"),  # Yellow
                parse_color("#81A1C1"),  # Blue
                parse_color("#B48EAD"),  # Magenta
                parse_color("#88C0D0"),  # Cyan
                parse_color("#E5E9F0"),  # White
                parse_color("#4C566A"),  # Bright Black
                parse_color("#BF616A"),  # Bright Red
                parse_color("#A3BE8C"),  # Bright Green
                parse_color("#EBCB8B"),  # Bright Yellow
                parse_color("#81A1C1"),  # Bright Blue
                parse_color("#B48EAD"),  # Bright Magenta
                parse_color("#8FBCBB"),  # Bright Cyan
                parse_color("#ECEFF4"),  # Bright White
            ]
        }


class DraculaTheme:
    """
    Dracula color scheme - a dark theme for terminal applications.
    https://draculatheme.com/
    """

    @staticmethod
    def get_colors():
        """
        Get Dracula theme colors for VTE terminal.

        Returns:
            dict: Dictionary with foreground, background, cursor, and palette colors
        """
        return {
            "foreground": parse_color("#F8F8F2"),
            "background": parse_color("#282A36"),
            "cursor": parse_color("#F8F8F2"),
            "palette": [
                parse_color("#21222C"),  # Black
                parse_color("#FF5555"),  # Red
                parse_color("#50FA7B"),  # Green
                parse_color("#F1FA8C"),  # Yellow
                parse_color("#BD93F9"),  # Blue
                parse_color("#FF79C6"),  # Magenta
                parse_color("#8BE9FD"),  # Cyan
                parse_color("#F8F8F2"),  # White
                parse_color("#6272A4"),  # Bright Black
                parse_color("#FF6E6E"),  # Bright Red
                parse_color("#69FF94"),  # Bright Green
                parse_color("#FFFFA5"),  # Bright Yellow
                parse_color("#D6ACFF"),  # Bright Blue
                parse_color("#FF92DF"),  # Bright Magenta
                parse_color("#A4FFFF"),  # Bright Cyan
                parse_color("#FFFFFF"),  # Bright White
            ]
        }


class GruvboxTheme:
    """
    Gruvbox Dark color scheme - retro groove theme with warm colors.
    https://github.com/morhetz/gruvbox
    """

    @staticmethod
    def get_colors():
        """
        Get Gruvbox Dark theme colors for VTE terminal.

        Returns:
            dict: Dictionary with foreground, background, cursor, and palette colors
        """
        return {
            "foreground": parse_color("#EBDBB2"),
            "background": parse_color("#282828"),
            "cursor": parse_color("#EBDBB2"),
            "palette": [
                parse_color("#282828"),  # Black
                parse_color("#CC241D"),  # Red
                parse_color("#98971A"),  # Green
                parse_color("#D79921"),  # Yellow
                parse_color("#458588"),  # Blue
                parse_color("#B16286"),  # Magenta
                parse_color("#689D6A"),  # Cyan
                parse_color("#A89984"),  # White
                parse_color("#928374"),  # Bright Black
                parse_color("#FB4934"),  # Bright Red
                parse_color("#B8BB26"),  # Bright Green
                parse_color("#FABD2F"),  # Bright Yellow
                parse_color("#83A598"),  # Bright Blue
                parse_color("#D3869B"),  # Bright Magenta
                parse_color("#8EC07C"),  # Bright Cyan
                parse_color("#EBDBB2"),  # Bright White
            ]
        }


def get_theme(theme_name="nord"):
    """
    Get a terminal color theme by name.

    Args:
        theme_name (str): Name of the theme ("nord", "dracula", "gruvbox")

    Returns:
        dict: Theme color dictionary
    """
    themes = {
        "nord": NordTheme.get_colors(),
        "dracula": DraculaTheme.get_colors(),
        "gruvbox": GruvboxTheme.get_colors(),
    }

    return themes.get(theme_name.lower(), NordTheme.get_colors())


def apply_theme_to_terminal(terminal, theme_name="nord"):
    """
    Apply a color theme to a VTE terminal widget.

    Args:
        terminal: VTE terminal widget
        theme_name (str): Name of the theme to apply
    """
    colors = get_theme(theme_name)

    terminal.set_colors(
        colors["foreground"],
        colors["background"],
        colors["palette"]
    )
    terminal.set_color_cursor(colors["cursor"])
