"""
Módulo de configuração do MangoHud
Aplica configurações do MangoHud para todos os usuários do sistema
"""

import os
import shutil
import pwd
from pathlib import Path
from core.config_manager import ConfigurationManager


class MangoHudConfigurer(ConfigurationManager):
    """Configuração do MangoHud para todos os usuários"""
    
    # Caminho onde a configuração padrão está armazenada
    MANGOHUD_CONFIG_SOURCE = '/etc/skel/.config/MangoHud/MangoHud.conf'
    
    def configure_mangohud(self) -> bool:
        """
        Aplica configuração do MangoHud para todos os usuários do sistema.
        Copia arquivo de config de /etc/skel/.config/MangoHud/ para cada usuário.
        
        Returns:
            bool: True se configuração foi bem-sucedida para pelo menos um usuário
        """
        self._print_status("Configurando MangoHud para todos os usuários...", 'yellow')
        
        try:
            # Verificar se o arquivo de config existe
            if not os.path.exists(self.MANGOHUD_CONFIG_SOURCE):
                self._print_status(
                    f"Arquivo de config não encontrado em {self.MANGOHUD_CONFIG_SOURCE}",
                    'red'
                )
                self._print_status(
                    "Certifique-se de que /etc/skel/.config/MangoHud/MangoHud.conf existe",
                    'yellow'
                )
                return False
            
            # Obter lista de usuários reais
            users = self._get_real_users()
            
            if not users:
                self._print_status("Nenhum usuário real encontrado no sistema", 'yellow')
                return False
            
            self._print_status(f"Encontrados {len(users)} usuário(s) para configurar", 'cyan')
            
            success_count = 0
            
            # Configurar para cada usuário
            for username, home_dir in users:
                if self._configure_user_mangohud(username, home_dir):
                    success_count += 1
            
            # Resultado final
            if success_count > 0:
                self._print_status(
                    f"✓ MangoHud configurado para {success_count}/{len(users)} usuário(s)",
                    'green'
                )
                self._print_status(
                    "As configurações de MangoHud serão aplicadas na próxima execução de jogos",
                    'cyan'
                )
                return True
            else:
                self._print_status("Nenhum usuário foi configurado com sucesso", 'red')
                return False
            
        except Exception as e:
            self._print_status(f"Erro ao configurar MangoHud: {str(e)}", 'red')
            return False
    
    def _configure_user_mangohud(self, username: str, home_dir: str) -> bool:
        """
        Configura MangoHud para um usuário específico
        
        Args:
            username: Nome do usuário
            home_dir: Diretório home do usuário
            
        Returns:
            bool: True se configuração foi bem-sucedida
        """
        try:
            # Caminho do diretório MangoHud do usuário
            user_mangohud_dir = Path(home_dir) / '.config' / 'MangoHud'
            config_file = user_mangohud_dir / 'MangoHud.conf'
            
            # Criar diretório se não existir
            user_mangohud_dir.mkdir(parents=True, exist_ok=True)
            
            # Copiar arquivo de config se não existir
            if not config_file.exists():
                shutil.copy2(
                    self.MANGOHUD_CONFIG_SOURCE,
                    str(config_file)
                )
                self._print_status(
                    f"  ✓ Config copiada para {username}",
                    'green'
                )
            else:
                self._print_status(
                    f"  ℹ Config já existe para {username}",
                    'cyan'
                )
            
            # Alterar proprietário do diretório e arquivo
            try:
                pwd_entry = pwd.getpwnam(username)
                uid = pwd_entry.pw_uid
                gid = pwd_entry.pw_gid
                
                # Recursive chown no diretório
                os.chown(str(user_mangohud_dir), uid, gid)
                os.chown(str(config_file), uid, gid)
                
                self._print_status(
                    f"  ✓ Proprietário definido para {username}",
                    'green'
                )
                
            except KeyError:
                self._print_status(
                    f"  ⚠ Usuário {username} não encontrado em pwd",
                    'yellow'
                )
                return False
            
            return True
            
        except Exception as e:
            self._print_status(
                f"  ✗ Erro configurando {username}: {str(e)}",
                'red'
            )
            return False
    
    def is_mangohud_installed(self) -> bool:
        """
        Verifica se MangoHud está instalado
        
        Returns:
            bool: True se MangoHud está instalado
        """
        from core.pacman import is_package_installed
        return is_package_installed('mangohud')
    
    def reset_user_config(self, username: str) -> bool:
        """
        Reseta a configuração de um usuário específico
        
        Args:
            username: Nome do usuário
            
        Returns:
            bool: True se reset foi bem-sucedido
        """
        try:
            pwd_entry = pwd.getpwnam(username)
            home_dir = pwd_entry.pw_dir
            
            user_mangohud_dir = Path(home_dir) / '.config' / 'MangoHud'
            config_file = user_mangohud_dir / 'MangoHud.conf'
            
            if config_file.exists():
                config_file.unlink()
                self._print_status(
                    f"Config de MangoHud removida para {username}",
                    'cyan'
                )
            
            return self._configure_user_mangohud(username, home_dir)
            
        except KeyError:
            self._print_status(f"Usuário {username} não encontrado", 'red')
            return False
        except Exception as e:
            self._print_status(f"Erro ao resetar config de {username}: {str(e)}", 'red')
            return False
