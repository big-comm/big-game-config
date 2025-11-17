def get_packages():
    """
    Retorna uma lista de dicionários, cada um contendo as informações
    de um pacote de jogo ou ferramenta para ser exibido na interface.
    """
    return [
        {
            "name": "Steam",
            "description": "Principal loja e lançador de jogos para PC.",
            "package_name": "steam",
            "icon": "steam"
        },
        {
            "name": "Steam Acolyte",
            "description": "Permite o login em múltiplas contas da Steam simultaneamente.",
            "package_name": "steam-acolyte",
            "icon": "acolyte"  # Alterado para corresponder a acolyte.svg
        },
        {
            "name": "Heroic Games Launcher",
            "description": "Lançador para jogos da Epic Games, GOG e Prime Gaming.",
            "package_name": "heroic-games-launcher",
            "icon": "heroic" # Alterado para corresponder a heroic.svg
        },
        {
            "name": "MangoHud",
            "description": "Exibe um HUD para monitorar FPS, temperaturas e uso de hardware.",
            "package_name": "mangohud",
            "icon": "mangohud"
        },
        {
            "name": "GOverlay",
            "description": "Interface gráfica para gerenciar e configurar o MangoHud.",
            "package_name": "goverlay",
            "icon": "goverlay"
        },
        {
            "name": "MangoJuice",
            "description": "Ferramenta para injeção de camadas Vulkan, usada com MangoHud.",
            "package_name": "mangojuice-bin",
            "icon": "mangojuice"
        },
        {
            "name": "ProtonPlus",
            "description": "Gerenciador para versões customizadas do Proton (Proton-GE).",
            "package_name": "protonplus",
            "icon": "protonplus" # Ícone sugestivo (sem arquivo .svg correspondente ainda)
        },
        {
            "name": "CoreCtrl",
            "description": "Software para controle de hardware de placas de vídeo AMD.",
            "package_name": "corectrl",
            "icon": "corectrl"
        },
        {
            "name": "LACT",
            "description": "Ferramenta para monitorar e controlar GPUs AMD.",
            "package_name": "lact",
            "icon": "lact"
        },
        {
            "name": "GreenWithEnvy (GWE)",
            "description": "Interface para monitorar e fazer overclock em placas de vídeo NVIDIA.",
            "package_name": "gwe",
            "icon": "gwe"
        },
        {
            "name": "RetroArch",
            "description": "Frontend para emuladores, permitindo jogar games de diversos consoles.",
            "package_name": "retroarch",
            "icon": "retroarch" # Sem arquivo .svg correspondente ainda
        },
        {
            "name": "PCSX2",
            "description": "Emulador de PlayStation 2.",
            "package_name": "pcsx2",
            "icon": "PCSX2" # Alterado para corresponder a PCSX2.svg (maiúsculas)
        },
        {
            "name": "RPCS3",
            "description": "Emulador de PlayStation 3.",
            "package_name": "rpcs3-bin",
            "icon": "rpcs3"
        }
    ]
