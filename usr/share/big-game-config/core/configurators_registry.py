"""
Registro centralizado de configuradores para cada pacote.
Mapeia package_name → classe configuradora + método de configuração

Uso:
    from core.configurators_registry import ConfiguratorsRegistry
    
    # Verificar se existe configurador
    if ConfiguratorsRegistry.has_configurator('steam'):
        # Obter método configurador
        config_fn = ConfiguratorsRegistry.get_configurator_method('steam')
        # Executar
        config_fn()
"""

from typing import Callable, Optional, Dict, Tuple


class ConfiguratorsRegistry:
    """Registro centralizado de configuradores pós-instalação"""
    
    # Mapeamento: package_name -> (Classe, método)
    # Formato: 'package_name': (ClasseConfiguradora, 'nome_do_metodo')
    CONFIGURATORS: Dict[str, Tuple[type, str]] = {}
    
    @classmethod
    def register(cls, package_name: str, configurator_class: type, method_name: str):
        """
        Registra um novo configurador para um pacote.
        
        Args:
            package_name: Nome do pacote (ex: 'steam')
            configurator_class: Classe do configurador
            method_name: Nome do método na classe
        """
        cls.CONFIGURATORS[package_name] = (configurator_class, method_name)
    
    @staticmethod
    def get_configurator_method(package_name: str) -> Optional[Callable]:
        """
        Retorna o método configurador para um pacote.
        
        Args:
            package_name: Nome do pacote (ex: 'steam', 'mangohud')
            
        Returns:
            Callable configurador ou None se não existir
            
        Example:
            config_fn = ConfiguratorsRegistry.get_configurator_method('steam')
            if config_fn:
                success = config_fn()  # Executa configuração
        """
        if package_name not in ConfiguratorsRegistry.CONFIGURATORS:
            return None
        
        try:
            configurator_class, method_name = ConfiguratorsRegistry.CONFIGURATORS[package_name]
            instance = configurator_class()
            return getattr(instance, method_name)
        except Exception:
            return None
    
    @staticmethod
    def has_configurator(package_name: str) -> bool:
        """
        Verifica se existe configurador para o pacote.
        
        Args:
            package_name: Nome do pacote
            
        Returns:
            True se existe configurador
        """
        return package_name in ConfiguratorsRegistry.CONFIGURATORS
    
    @staticmethod
    def get_configurable_packages() -> list:
        """
        Retorna lista de pacotes que têm configuradores.
        
        Returns:
            Lista de package_names com configuradores disponíveis
        """
        return list(ConfiguratorsRegistry.CONFIGURATORS.keys())


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# REGISTRO DE CONFIGURADORES
# Importar e registrar configuradores ao inicializar o módulo
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

try:
    from core.steam_configurer import SteamConfigurer
    ConfiguratorsRegistry.register('steam', SteamConfigurer, 'install_steam_with_dependencies')
except ImportError:
    pass

try:
    from core.mangohud_configurer import MangoHudConfigurer
    ConfiguratorsRegistry.register('mangohud', MangoHudConfigurer, 'configure_mangohud')
except ImportError:
    pass

try:
    from core.corectrl_configurer import CorectrlConfigurer
    ConfiguratorsRegistry.register('corectrl', CorectrlConfigurer, 'configure_corectrl')
except ImportError:
    pass
