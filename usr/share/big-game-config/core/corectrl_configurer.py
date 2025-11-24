"""
Módulo de configuração do Corectrl
Configura GRUB e Polkit para acesso ao Corectrl com privilégios administrativos
"""

import os
import shutil
from pathlib import Path
from core.config_manager import ConfigurationManager


class CorectrlConfigurer(ConfigurationManager):
    """Configuração do Corectrl com GRUB e Polkit"""
    
    # Caminhos de configuração
    GRUB_CONFIG_PATH = '/etc/default/grub'
    POLKIT_RULES_DIR = '/etc/polkit-1/rules.d'
    POLKIT_RULES_FILE = 'corectrl.rules'
    
    # Parâmetro AMD GPU para GRUB
    AMD_GPU_PARAM = 'amdgpu.ppfeaturemask=0xffffffff'
    
    def configure_corectrl(self) -> bool:
        """
        Aplica configuração completa do Corectrl:
        1. Adiciona parâmetro AMD GPU ao GRUB (permite overdrive)
        2. Cria regra Polkit para acesso do Corectrl sem senha
        
        Requer reinicialização para aplicar as alterações de GRUB
        
        Returns:
            bool: True se configuração foi bem-sucedida
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
            failed = [k for k, v in results.items() if not v]
            self._print_status(
                f"Falha na configuração de: {', '.join(failed)}. Verifique os erros acima.",
                'red'
            )
            return False
    
    def _setup_grub_parameter(self) -> bool:
        """
        Adiciona parâmetro AMD GPU ao GRUB
        
        Este parâmetro permite overdrive e outras funcionalidades de GPU
        no Corectrl. Requer reinicialização para aplicar.
        
        Returns:
            bool: True se configuração foi bem-sucedida
        """
        try:
            # Verificar se GRUB config existe
            if not os.path.exists(self.GRUB_CONFIG_PATH):
                self._print_status(
                    f"Arquivo GRUB não encontrado: {self.GRUB_CONFIG_PATH}",
                    'red'
                )
                return False
            
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
                try:
                    shutil.copy2(self.GRUB_CONFIG_PATH, backup_path)
                    self._print_status(f"Backup criado: {backup_path}", 'cyan')
                except Exception as e:
                    self._print_status(f"Erro ao fazer backup: {str(e)}", 'red')
                    return False
            
            # Ler o arquivo GRUB
            try:
                with open(self.GRUB_CONFIG_PATH, 'r') as f:
                    grub_content = f.read()
            except Exception as e:
                self._print_status(f"Erro ao ler GRUB config: {str(e)}", 'red')
                return False
            
            # Adicionar o parâmetro se não existir
            if self.AMD_GPU_PARAM not in grub_content:
                # Procurar por GRUB_CMDLINE_LINUX_DEFAULT e adicionar o parâmetro
                if 'GRUB_CMDLINE_LINUX_DEFAULT=' in grub_content:
                    # Substituir mantendo o resto das opções
                    old_pattern = 'GRUB_CMDLINE_LINUX_DEFAULT="'
                    new_pattern = f'GRUB_CMDLINE_LINUX_DEFAULT="{self.AMD_GPU_PARAM} '
                    
                    if old_pattern in grub_content:
                        grub_content = grub_content.replace(
                            old_pattern,
                            new_pattern,
                            1  # Substituir apenas primeira ocorrência
                        )
                    else:
                        self._print_status(
                            "Não foi possível localizar GRUB_CMDLINE_LINUX_DEFAULT",
                            'red'
                        )
                        return False
                else:
                    self._print_status(
                        "Arquivo GRUB não contém GRUB_CMDLINE_LINUX_DEFAULT",
                        'red'
                    )
                    return False
                
                # Escrever arquivo modificado
                try:
                    with open(self.GRUB_CONFIG_PATH, 'w') as f:
                        f.write(grub_content)
                    self._print_status(
                        f"Parâmetro adicionado ao {self.GRUB_CONFIG_PATH}",
                        'cyan'
                    )
                except Exception as e:
                    self._print_status(f"Erro ao escrever GRUB config: {str(e)}", 'red')
                    return False
            
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
                self._print_status(
                    f"Erro ao regenerar GRUB: {stderr}",
                    'red'
                )
                return False
                
        except Exception as e:
            self._print_status(f"Erro ao configurar GRUB: {str(e)}", 'red')
            return False
    
    def _setup_polkit_rule(self) -> bool:
        """
        Cria regra Polkit para Corectrl
        
        Permite que usuários reais executem comandos administrativos
        do Corectrl sem necessidade de senha.
        
        Returns:
            bool: True se configuração foi bem-sucedida
        """
        try:
            # Criar diretório de regras Polkit se não existir
            os.makedirs(self.POLKIT_RULES_DIR, exist_ok=True)
            self._print_status(
                f"Diretório Polkit garantido: {self.POLKIT_RULES_DIR}",
                'cyan'
            )
            
            polkit_file_path = os.path.join(
                self.POLKIT_RULES_DIR,
                self.POLKIT_RULES_FILE
            )
            
            # Obter usuários reais
            users = self._get_real_users()
            
            if not users:
                self._print_status("Nenhum usuário real encontrado", 'yellow')
                return False
            
            self._print_status(f"Criando regra Polkit para {len(users)} usuário(s)", 'cyan')
            
            # Criar conteúdo das regras Polkit
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
            try:
                with open(polkit_file_path, 'w') as f:
                    f.write(polkit_content)
                self._print_status(
                    f"Arquivo Polkit criado: {polkit_file_path}",
                    'cyan'
                )
            except Exception as e:
                self._print_status(f"Erro ao escrever arquivo Polkit: {str(e)}", 'red')
                return False
            
            # Definir permissões (664 para Polkit rules)
            try:
                os.chmod(polkit_file_path, 0o664)
                self._print_status("Permissões de Polkit definidas corretamente", 'cyan')
            except Exception as e:
                self._print_status(f"Erro ao definir permissões: {str(e)}", 'red')
                return False
            
            self._print_status(
                f"✓ Regra Polkit configurada para {len(users)} usuário(s)",
                'green'
            )
            return True
            
        except Exception as e:
            self._print_status(f"Erro ao configurar Polkit: {str(e)}", 'red')
            return False
    
    def is_corectrl_installed(self) -> bool:
        """
        Verifica se Corectrl está instalado
        
        Returns:
            bool: True se Corectrl está instalado
        """
        from core.pacman import is_package_installed
        return is_package_installed('corectrl')
    
    def reset_configuration(self) -> bool:
        """
        Remove as configurações do Corectrl
        (Útil para troubleshooting ou remoção)
        
        Returns:
            bool: True se remoção foi bem-sucedida
        """
        try:
            polkit_file_path = os.path.join(
                self.POLKIT_RULES_DIR,
                self.POLKIT_RULES_FILE
            )
            
            # Remover arquivo Polkit se existir
            if os.path.exists(polkit_file_path):
                os.remove(polkit_file_path)
                self._print_status("Regra Polkit removida", 'cyan')
            
            # Restaurar GRUB se houver backup
            backup_path = f"{self.GRUB_CONFIG_PATH}.bak"
            if os.path.exists(backup_path):
                shutil.copy2(backup_path, self.GRUB_CONFIG_PATH)
                self._print_status("Configuração GRUB restaurada do backup", 'cyan')
                
                # Regenerar GRUB
                returncode, _, _ = self._run_command(
                    ['sudo', 'grub-mkconfig', '-o', '/boot/grub/grub.cfg'],
                    check=False
                )
                if returncode == 0:
                    self._print_status("GRUB regenerado", 'cyan')
            
            self._print_status(
                "✓ Configurações do Corectrl removidas. Reinicie o sistema.",
                'green'
            )
            return True
            
        except Exception as e:
            self._print_status(f"Erro ao remover configurações: {str(e)}", 'red')
            return False
