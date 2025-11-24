"""
Módulo de configuração do Steam
Instalação do Steam com dependências necessárias
"""

import subprocess
from typing import List
from core.config_manager import ConfigurationManager


class SteamConfigurer(ConfigurationManager):
    """Configuração e instalação do Steam com dependências"""
    
    # Pacotes que devem ser instalados junto com Steam
    STEAM_PACKAGES = ['steam', 'linux-steam-integration', 'python-steam']
    
    def install_steam_with_dependencies(self) -> bool:
        """
        Instala Steam com as dependências necessárias:
        - steam: Cliente Steam
        - linux-steam-integration: Integração com Steam no Linux
        - python-steam: Bindings Python para Steam
        
        Returns:
            bool: True se instalação foi bem-sucedida, False caso contrário
        """
        self._print_status("Iniciando instalação do Steam com dependências...", 'blue')
        
        try:
            # Construir comando pacman
            cmd = ['sudo', 'pacman', '-S', '--noconfirm'] + self.STEAM_PACKAGES
            
            self._print_status(f"Instalando pacotes: {', '.join(self.STEAM_PACKAGES)}", 'cyan')
            
            returncode, stdout, stderr = self._run_command(cmd)
            
            if returncode == 0:
                self._print_status(
                    f"✓ Steam e dependências instalados com sucesso!",
                    'green'
                )
                self._print_status("Steam está pronto para uso.", 'cyan')
                return True
            else:
                self._print_status(
                    f"Erro na instalação dos pacotes Steam: {stderr}",
                    'red'
                )
                return False
                
        except Exception as e:
            self._print_status(
                f"Erro ao instalar Steam: {str(e)}",
                'red'
            )
            return False
    
    def is_steam_installed(self) -> bool:
        """
        Verifica se Steam já está instalado
        
        Returns:
            bool: True se Steam está instalado
        """
        from core.pacman import is_package_installed
        return is_package_installed('steam')
    
    def check_dependencies(self) -> List[str]:
        """
        Verifica quais dependências do Steam estão faltando
        
        Returns:
            List[str]: Lista de pacotes não instalados
        """
        from core.pacman import is_package_installed
        
        missing = []
        for package in self.STEAM_PACKAGES:
            if not is_package_installed(package):
                missing.append(package)
        
        return missing
