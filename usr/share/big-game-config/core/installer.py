"""
Package installer module with pkexec privilege escalation.
Handles installation and removal of packages using pacman.
"""

import subprocess
import shlex
from typing import Tuple, Optional


class PackageInstaller:
    """Handles package installation and removal operations."""

    @staticmethod
    def install_package(package_name: str) -> Tuple[bool, str]:
        """
        Install a package using pacman with pkexec for privilege escalation.

        Args:
            package_name (str): Name of the package to install

        Returns:
            Tuple[bool, str]: (success, error_message)
                success: True if installation succeeded, False otherwise
                error_message: Error message if failed, empty string if succeeded
        """
        try:
            # Build command with pkexec for privilege escalation
            command = [
                "pkexec",
                "pacman",
                "-S",
                "--noconfirm",
                package_name
            ]

            # Execute command
            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                timeout=300  # 5 minute timeout
            )

            if result.returncode == 0:
                return True, ""
            else:
                error_msg = result.stderr if result.stderr else result.stdout
                return False, error_msg

        except subprocess.TimeoutExpired:
            return False, "Installation timed out after 5 minutes"
        except subprocess.CalledProcessError as e:
            return False, f"Installation failed: {e.stderr}"
        except FileNotFoundError:
            return False, "pkexec or pacman not found. Are you running on Arch Linux?"
        except Exception as e:
            return False, f"Unexpected error: {str(e)}"

    @staticmethod
    def remove_package(package_name: str) -> Tuple[bool, str]:
        """
        Remove a package using pacman with pkexec for privilege escalation.

        Args:
            package_name (str): Name of the package to remove

        Returns:
            Tuple[bool, str]: (success, error_message)
                success: True if removal succeeded, False otherwise
                error_message: Error message if failed, empty string if succeeded
        """
        try:
            # Build command with pkexec for privilege escalation
            command = [
                "pkexec",
                "pacman",
                "-R",
                "--noconfirm",
                package_name
            ]

            # Execute command
            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                timeout=300  # 5 minute timeout
            )

            if result.returncode == 0:
                return True, ""
            else:
                error_msg = result.stderr if result.stderr else result.stdout
                return False, error_msg

        except subprocess.TimeoutExpired:
            return False, "Removal timed out after 5 minutes"
        except subprocess.CalledProcessError as e:
            return False, f"Removal failed: {e.stderr}"
        except FileNotFoundError:
            return False, "pkexec or pacman not found. Are you running on Arch Linux?"
        except Exception as e:
            return False, f"Unexpected error: {str(e)}"

    @staticmethod
    def get_install_command(package_name: str) -> str:
        """
        Get the install command string for display purposes.

        Args:
            package_name (str): Name of the package

        Returns:
            str: Command string
        """
        return f"pkexec pacman -S --noconfirm {shlex.quote(package_name)}"

    @staticmethod
    def get_remove_command(package_name: str) -> str:
        """
        Get the remove command string for display purposes.

        Args:
            package_name (str): Name of the package

        Returns:
            str: Command string
        """
        return f"pkexec pacman -R --noconfirm {shlex.quote(package_name)}"
