import subprocess

def is_package_installed(package_name):
    """
    Verifica se um pacote está instalado usando 'pacman -Q'.
    Retorna True se o pacote estiver instalado, False caso contrário.
    """
    try:
        # Executa 'pacman -Q' para consultar o pacote
        # stdout e stderr são descartados para não poluir o console
        result = subprocess.run(
            ['pacman', '-Q', package_name],
            check=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        # Se o comando foi bem-sucedido (returncode 0), o pacote está instalado
        return result.returncode == 0
    except (subprocess.CalledProcessError, FileNotFoundError):
        # CalledProcessError ocorre se o pacote não for encontrado (pacman retorna 1)
        # FileNotFoundError ocorre se o comando 'pacman' não for encontrado
        return False
