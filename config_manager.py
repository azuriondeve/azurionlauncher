import os
import json

APPDATA = os.getenv('APPDATA')
LAUNCHER_DIR = os.path.join(APPDATA, ".azurionlauncher")
MINECRAFT_DIR = os.path.join(APPDATA, ".minecraft")
CONFIG_FILE = os.path.join(LAUNCHER_DIR, "config.json")

os.makedirs(LAUNCHER_DIR, exist_ok=True)
os.makedirs(MINECRAFT_DIR, exist_ok=True)

def load_config():
    """Carrega as configurações do arquivo JSON ou retorna o padrão."""
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r") as f:
                config_data = json.load(f)
                # Garantia de chaves padrões para versões antigas
                defaults = {
                    "theme_color": "#7b2cbf",
                    "accounts": [],
                    "current_account": "",
                    "ram": "2G",
                    "demo_mode": False,
                    "gpu_preference": "Auto"
                }
                for key, value in defaults.items():
                    if key not in config_data:
                        config_data[key] = value
                return config_data
        except:
            pass
    return {
        "theme_color": "#7b2cbf",
        "accounts": [], 
        "current_account": "",
        "ram": "2G",
        "demo_mode": False,
        "gpu_preference": "Auto"
    }

def save_config(data):
    """Salva as configurações no diretório da AppData."""
    with open(CONFIG_FILE, "w") as f:
        json.dump(data, f, indent=4)

def get_available_gpus():
    """Tenta detectar GPUs no sistema via Windows (WMIC)."""
    try:
        output = subprocess.check_output("wmic path win32_VideoController get name", shell=True).decode()
        lines = [line.strip() for line in output.split('\n') if line.strip() and "Name" not in line]
        return ["Auto"] + lines
    except:
        return ["Auto", "High Performance", "Power Saving"]
