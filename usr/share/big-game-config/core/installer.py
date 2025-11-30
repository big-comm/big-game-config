"""
Package installer module with post-installation configuration support.
Handles installation and removal of packages using pacman.

Suporta callbacks pós-instalação para aplicação automática de configurações.
"""

import subprocess
import shlex
from typing import Tuple, Optional, Callable


class PackageInstaller:
    """Handles package installation and removal operations."""
    
    @staticmethod
    def install_package(
        package_name: str,
        post_install_callback: Optional[Callable] = None,
        apply_configuration: bool = True
    ) -> Tuple[bool, str]:
        """
        Install a package using pacman with pkexec for privilege escalation.
        
        Opcionalmente executa callback pós-instalação para configuração automática.
        
        Args:
            package_name (str): Name of the package to install
            post_install_callback (Optional[Callable]): Função de callback para executar após instalação.
                                                        Se None e apply_configuration=True,
                                                        tenta usar configurador automático
            apply_configuration (bool): Se True, tenta aplicar configuração automaticamente
            
        Returns:
            Tuple[bool, str]: (success, error_message)
            - success: True if installation succeeded, False otherwise
            - error_message: Error message if failed, empty string if succeeded
            
        Example:
            # Instalação simples
            success, msg = PackageInstaller.install_package('steam')
            
            # Com callback customizado
            def custom_config():
                print("Configurando...")
                return True
            
            success, msg = PackageInstaller.install_package(
                'steam',
                post_install_callback=custom_config
            )
        """
        try:
            # ╔════════════════════════════════════════════════════════╗
            # ║ ETAPA 1: Instalar Pacote                              ║
            # ╚════════════════════════════════════════════════════════╝
            
            print(f"🚀 Instalando {package_name}...")
            
            command = [
                "pkexec",
                "pacman",
                "-S",
                "--noconfirm",
                package_name
            ]
            
            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                timeout=300  # 5 minute timeout
            )
            
            if result.returncode != 0:
                error_msg = result.stderr if result.stderr else result.stdout
                print(f"❌ Erro na instalação: {error_msg}")
                return False, f"Instalação falhou: {error_msg}"
            
            print(f"✅ {package_name} instalado com sucesso!")
            
            # ╔════════════════════════════════════════════════════════╗
            # ║ ETAPA 2: Aplicar Configuração (Opcional)              ║
            # ╚════════════════════════════════════════════════════════╝
            
            if apply_configuration:
                # Se não forneceu callback, tenta usar configurador automático
                if post_install_callback is None:
                    try:
                        from core.configurators_registry import ConfiguratorsRegistry
                        
                        if ConfiguratorsRegistry.has_configurator(package_name):
                            post_install_callback = ConfiguratorsRegistry.get_configurator_method(
                                package_name
                            )
                            print(f"🔍 Configurador automático encontrado para {package_name}")
                    except ImportError:
                        print(f"⚠️ Não foi possível carregar registry de configuradores")
                        post_install_callback = None
                
                # Executar callback se disponível
                if post_install_callback is not None:
                    print(f"⚙️ Aplicando configurações para {package_name}...")
                    try:
                        config_result = post_install_callback()
                        
                        if config_result:
                            print(f"✅ Configuração de {package_name} concluída!")
                        else:
                            # Não falha se configuração falhar, pacote já foi instalado
                            print(f"⚠️ Configuração de {package_name} não foi totalmente bem-sucedida")
                            print("   (Pacote instalado, mas configuração parcial)")
                    
                    except Exception as e:
                        # Não falha se configuração explodir
                        print(f"⚠️ Erro ao configurar {package_name}: {str(e)}")
                        print("   (Pacote instalado, mas configuração falhou)")
            
            return True, ""
        
        except subprocess.TimeoutExpired:
            print(f"❌ Timeout na instalação de {package_name}")
            return False, "Installation timed out after 5 minutes"
        
        except subprocess.CalledProcessError as e:
            print(f"❌ Erro ao executar pacman: {e.stderr}")
            return False, f"Installation failed: {e.stderr}"
        
        except FileNotFoundError:
            print(f"❌ pkexec ou pacman não encontrado")
            return False, "pkexec or pacman not found. Are you running on Arch Linux?"
        
        except Exception as e:
            print(f"❌ Erro inesperado: {str(e)}")
            return False, f"Unexpected error: {str(e)}"
    
    @staticmethod
    def remove_package(package_name: str) -> Tuple[bool, str]:
        """
        Remove a package using pacman with pkexec for privilege escalation.
        
        Args:
            package_name (str): Name of the package to remove
            
        Returns:
            Tuple[bool, str]: (success, error_message)
            - success: True if removal succeeded, False otherwise
            - error_message: Error message if failed, empty string if succeeded
            
        Example:
            success, msg = PackageInstaller.remove_package('steam')
            if success:
                print("Pacote removido!")
        """
        try:
            print(f"🗑️ Removendo {package_name}...")
            
            command = [
                "pkexec",
                "pacman",
                "-R",
                "--noconfirm",
                package_name
            ]
            
            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                timeout=300  # 5 minute timeout
            )
            
            if result.returncode == 0:
                print(f"✅ {package_name} removido com sucesso!")
                return True, ""
            else:
                error_msg = result.stderr if result.stderr else result.stdout
                print(f"❌ Erro ao remover: {error_msg}")
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
            str: Command string (para exibição/debug)
        """
        return f"pkexec pacman -S --noconfirm {shlex.quote(package_name)}"
    
    @staticmethod
    def get_remove_command(package_name: str) -> str:
        """
        Get the remove command string for display purposes.
        
        Args:
            package_name (str): Name of the package
            
        Returns:
            str: Command string (para exibição/debug)
        """
        return f"pkexec pacman -R --noconfirm {shlex.quote(package_name)}"
