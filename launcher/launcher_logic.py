import minecraft_launcher_lib
import subprocess
import uuid
import threading
import os
from config_manager import MINECRAFT_DIR

class MinecraftHandler:
    def __init__(self, update_status_callback):
        self.minecraft_dir = MINECRAFT_DIR
        self.update_status = update_status_callback
        self.process = None

    def get_versions(self):
        """Retorna as versões disponíveis e instaladas."""
        try:
            available = minecraft_launcher_lib.utils.get_version_list()
            installed = [v["id"] for v in minecraft_launcher_lib.utils.get_installed_versions(self.minecraft_dir)]
            data = []
            for v in available:
                if v["type"] == "release":
                    data.append({
                        "id": v["id"], 
                        "status": "Instalada" if v["id"] in installed else "Nuvem"
                    })
            return data
        except:
            return []

    def launch(self, version_id, username, ram, demo_mode, gpu_pref):
        """Instala e executa o jogo."""
        try:
            self.update_status(f"Baixando arquivos de {version_id}...", 0.2)
            minecraft_launcher_lib.install.install_minecraft_version(version_id, self.minecraft_dir)

            options = {
                "username": username,
                "uuid": str(uuid.uuid5(uuid.NAMESPACE_DNS, username)),
                "token": "",
                "jvmArguments": [f"-Xmx{ram}", f"-Xms{ram}"],
                "demo": demo_mode
            }

            # Configuração de GPU (Variáveis de ambiente comuns para Java/OpenGL)
            env = os.environ.copy()
            if gpu_pref != "Auto":
                # Nota: A seleção real de GPU muitas vezes depende do Painel de Controle da Nvidia/AMD
                # mas podemos tentar forçar via variáveis de ambiente para certas implementações
                env["_JAVA_OPTIONS"] = f"-Dsun.java2d.opengl=true"

            self.update_status("Iniciando motor gráfico...", 0.95)
            command = minecraft_launcher_lib.command.get_minecraft_command(version_id, self.minecraft_dir, options)
            
            self.process = subprocess.Popen(command, env=env)
            self.update_status("Jogo em execução!", 1.0)
            self.process.wait()
            self.update_status("Pronto para jogar.", 0)
            
        except Exception as e:
            self.update_status(f"Erro: {str(e)[:30]}", 0)

    def stop(self):
        """Encerra o processo do jogo se estiver rodando."""
        if self.process:
            try:
                self.process.terminate()
            except:
                pass