"""
Módulos de configuração para Big Game Config
Converte scripts shell para Python para aplicar configurações de gaming
"""

import subprocess
import os
import shutil
from pathlib import Path
from typing import Tuple, Optional, List
import pwd
import stat

class ConfigurationManager:
    """Gerenciador centralizado de configurações de gaming"""
    
    def __init__(self):
        self.color_codes = {
            'red': '\033[0;31m',
            'green': '\033[0;32m',
            'blue': '\033[0;34m',
            'yellow': '\033[1;33m',
            'cyan': '\033[1;36m',
            'reset': '\033[0m'
        }
    
    def _print_status(self, message: str, color: str = 'cyan'):
        """Imprime mensagem de status com cores"""
        c = self.color_codes.get(color, self.color_codes['reset'])
        reset = self.color_codes['reset']
        print(f"{c}→{reset} {message}")
    
    def _run_command(self, cmd: List[str], check: bool = True, 
                     capture_output: bool = False) -> Tuple[int, str, str]:
        """Executa comando com tratamento de erro"""
        try:
            result = subprocess.run(
                cmd,
                check=False,
                capture_output=capture_output,
                text=True
            )
            return result.returncode, result.stdout, result.stderr
        except Exception as e:
            if check:
                raise RuntimeError(f"Erro ao executar comando: {' '.join(cmd)} - {str(e)}")
            return 1, "", str(e)
    
    def _get_real_users(self) -> List[Tuple[str, str]]:
        """Retorna lista de usuários reais (UID >= 1000)
        Retorna lista de tuplas (username, home_dir)
        """
        users = []
        try:
            with open('/etc/passwd', 'r') as f:
                for line in f:
                    parts = line.strip().split(':')
                    if len(parts) >= 6:
                        username, _, uid, _, _, homedir = parts[:6]
                        try:
                            uid_int = int(uid)
                            if 1000 <= uid_int < 65534:
                                users.append((username, homedir))
                        except ValueError:
                            continue
        except Exception as e:
            self._print_status(f"Erro ao ler /etc/passwd: {str(e)}", 'red')
        return users


class SteamConfigurer(ConfigurationManager):
    """Configuração e instalação do Steam com dependências"""
    
    def install_steam_with_dependencies(self) -> bool:
        """
        Instala Steam com as dependências necessárias:
        - linux-steam-integration
        - python-steam
        """
        self._print_status("Iniciando instalação do Steam com dependências...", 'blue')
        
        packages = ['steam', 'linux-steam-integration', 'python-steam']
        
        try:
            # Construir comando pacman
            cmd = ['sudo', 'pacman', '-S', '--noconfirm'] + packages
            
            returncode, stdout, stderr = self._run_command(cmd)
            
            if returncode == 0:
                self._print_status(f"✓ Steam e dependências instalados com sucesso!", 'green')
                return True
            else:
                self._print_status(f"Erro na instalação: {stderr}", 'red')
                return False
                
        except Exception as e:
            self._print_status(f"Erro ao instalar Steam: {str(e)}", 'red')
            return False


class MangoHudConfigurer(ConfigurationManager):
    """Configuração do MangoHud para todos os usuários"""
    
    MANGOHUD_CONFIG_SOURCE = '/etc/skel/.config/MangoHud/MangoHud.conf'
    
    def configure_mangohud(self) -> bool:
        """
        Aplica configuração do MangoHud para todos os usuários
        Copia arquivo de config de /etc/skel/.config/MangoHud/
        """
        self._print_status("Configurando MangoHud para todos os usuários...", 'yellow')
        
        try:
            # Verificar se o arquivo de config existe
            if not os.path.exists(self.MANGOHUD_CONFIG_SOURCE):
                self._print_status(
                    f"Arquivo de config não encontrado em {self.MANGOHUD_CONFIG_SOURCE}",
                    'red'
                )
                return False
            
            users = self._get_real_users()
            success_count = 0
            
            for username, home_dir in users:
                if self._configure_user_mangohud(username, home_dir):
                    success_count += 1
            
            self._print_status(
                f"✓ MangoHud configurado para {success_count}/{len(users)} usuários",
                'green'
            )
            return success_count > 0
            
        except Exception as e:
            self._print_status(f"Erro ao configurar MangoHud: {str(e)}", 'red')
            return False
    
    def _configure_user_mangohud(self, username: str, home_dir: str) -> bool:
        """Configura MangoHud para um usuário específico"""
        try:
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
            
            # Alterar proprietário do diretório
            try:
                uid = pwd.getpwnam(username).pw_uid
                gid = pwd.getpwnam(username).pw_gid
                os.chown(str(user_mangohud_dir), uid, gid)
                os.chown(str(config_file), uid, gid)
            except KeyError:
                self._print_status(f"Usuário {username} não encontrado", 'yellow')
                return False
            
            self._print_status(f"  ✓ {username}: configurado", 'green')
            return True
            
        except Exception as e:
            self._print_status(f"  ✗ {username}: {str(e)}", 'red')
            return False


class CorectrlConfigurer(ConfigurationManager):
    """Configuração do Corectrl com GRUB e Polkit"""
    
    GRUB_CONFIG_PATH = '/etc/default/grub'
    POLKIT_RULES_DIR = '/etc/polkit-1/rules.d'
    POLKIT_RULES_FILE = 'corectrl.rules'
    AMD_GPU_PARAM = 'amdgpu.ppfeaturemask=0xffffffff'
    
    def configure_corectrl(self) -> bool:
        """
        Aplica configuração completa do Corectrl:
        1. Adiciona parâmetro AMD GPU ao GRUB
        2. Cria regra Polkit para acesso do Corectrl
        """
        self._print_status("Configurando Corectrl...", 'yellow')
        
        results = {
            'grub': self._setup_grub_parameter(),
            'polkit': self._setup_polkit_rule()
        }
        
        if results['grub'] and results['polkit']:
            self._print_status("═" * 45, 'blue')
            self._print_status("✓ Configuração do Corectrl Concluída!", 'green')
            self._print_status("═" * 45, 'blue')
            self._print_status(
                "Reinicie o sistema para aplicar todas as alterações.",
                'yellow'
            )
            return True
        else:
            self._print_status("Alguns passos falharam. Verifique os erros acima.", 'red')
            return False
    
    def _setup_grub_parameter(self) -> bool:
        """Adiciona parâmetro AMD GPU ao GRUB"""
        try:
            # Verificar se o parâmetro já está configurado
            returncode, output, _ = self._run_command(
                ['grep', '-q', self.AMD_GPU_PARAM, self.GRUB_CONFIG_PATH],
                check=False
            )
            
            if returncode == 0:
                self._print_status(
                    "✓ Parâmetro GPU já configurado no GRUB",
                    'green'
                )
                return True
            
            # Fazer backup do arquivo original
            backup_path = f"{self.GRUB_CONFIG_PATH}.bak"
            if not os.path.exists(backup_path):
                shutil.copy2(self.GRUB_CONFIG_PATH, backup_path)
                self._print_status(f"Backup criado: {backup_path}", 'cyan')
            
            # Ler o arquivo GRUB
            with open(self.GRUB_CONFIG_PATH, 'r') as f:
                grub_content = f.read()
            
            # Adicionar o parâmetro se não existir
            if self.AMD_GPU_PARAM not in grub_content:
                # Substituir GRUB_CMDLINE_LINUX_DEFAULT
                old_line = 'GRUB_CMDLINE_LINUX_DEFAULT='
                new_line = f'GRUB_CMDLINE_LINUX_DEFAULT="{self.AMD_GPU_PARAM} '
                
                grub_content = grub_content.replace(
                    f'{old_line}"',
                    new_line
                )
                
                with open(self.GRUB_CONFIG_PATH, 'w') as f:
                    f.write(grub_content)
            
            # Regenerar configuração GRUB
            returncode, _, stderr = self._run_command(
                ['sudo', 'grub-mkconfig', '-o', '/boot/grub/grub.cfg'],
                check=False
            )
            
            if returncode == 0:
                self._print_status(
                    "✓ Parâmetro AMD GPU adicionado e GRUB atualizado!",
                    'green'
                )
                return True
            else:
                self._print_status(f"Erro ao atualizar GRUB: {stderr}", 'red')
                return False
                
        except Exception as e:
            self._print_status(f"Erro ao configurar GRUB: {str(e)}", 'red')
            return False
    
    def _setup_polkit_rule(self) -> bool:
        """Cria regra Polkit para Corectrl"""
        try:
            # Criar diretório de regras Polkit se não existir
            os.makedirs(self.POLKIT_RULES_DIR, exist_ok=True)
            
            polkit_file_path = os.path.join(
                self.POLKIT_RULES_DIR,
                self.POLKIT_RULES_FILE
            )
            
            users = self._get_real_users()
            
            if not users:
                self._print_status("Nenhum usuário real encontrado", 'yellow')
                return False
            
            # Criar regra Polkit para cada usuário
            polkit_content = 'polkit.addRule(function(action, subject) {\n'
            
            for username, _ in users:
                polkit_content += (
                    f'    if ((action.id == "org.corectrl.helper.init" ||\n'
                    f'         action.id == "org.corectrl.helperkiller.init") &&\n'
                    f'        subject.local == true &&\n'
                    f'        subject.active == true &&\n'
                    f'        subject.isInGroup("{username}")) {{\n'
                    f'            return polkit.Result.YES;\n'
                    f'    }}\n'
                )
            
            polkit_content += '});\n'
            
            # Escrever arquivo de regras
            with open(polkit_file_path, 'w') as f:
                f.write(polkit_content)
            
            # Definir permissões
            os.chmod(polkit_file_path, 0o644)
            
            self._print_status(
                f"✓ Regra Polkit configurada para {len(users)} usuário(s)",
                'green'
            )
            return True
            
        except Exception as e:
            self._print_status(f"Erro ao configurar Polkit: {str(e)}", 'red')
            return False
