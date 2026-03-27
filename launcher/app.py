import customtkinter as ctk
import threading
import config_manager as cfg
from launcher_logic import MinecraftHandler

# Carrega as configurações globais
config = cfg.load_config()

ctk.set_appearance_mode("dark")

class AzurionApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Azurion Launcher v3.0")
        self.geometry("1000x620")
        self.attributes("-alpha", 0.95)
        
        self.handler = MinecraftHandler(self.update_status)
        self.selected_version = None
        self.is_installing = False

        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.setup_ui()
        
        # Carregar versões em segundo plano
        threading.Thread(target=self.load_versions_list, daemon=True).start()

    def update_status(self, msg, progress=None):
        self.status_label.configure(text=msg)
        if progress is not None:
            self.progress_bar.set(progress)

    def setup_ui(self):
        # --- Sidebar ---
        self.sidebar = ctk.CTkFrame(self, width=220, corner_radius=0, fg_color="#0f0a17")
        self.sidebar.grid(row=0, column=0, sticky="nsew")

        self.logo_frame = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        self.logo_frame.pack(pady=(30, 40))
        ctk.CTkLabel(self.logo_frame, text="✦", font=("Arial", 32), text_color=config["theme_color"]).pack(side="left", padx=5)
        ctk.CTkLabel(self.logo_frame, text="AZURION", font=("Arial Black", 22)).pack(side="left")

        self.create_nav_button("Início", "🏠", self.go_home)
        self.create_nav_button("Gerenciar Contas", "👤", self.open_accounts_manager)
        self.create_nav_button("Configurações", "⚙", self.open_options)

        # --- Main Content ---
        self.main_content = ctk.CTkFrame(self, fg_color="#140f1f", corner_radius=0)
        self.main_content.grid(row=0, column=1, sticky="nsew")
        
        # Card Central
        self.center_card = ctk.CTkFrame(self.main_content, fg_color="#1d162b", corner_radius=20, border_width=1, border_color="#2d2242")
        self.center_card.place(relx=0.5, rely=0.45, anchor="center", relwidth=0.5, relheight=0.6)

        ctk.CTkLabel(self.center_card, text="Azurion Launcher", font=("Segoe UI", 24, "bold")).pack(pady=(40, 5))
        
        ctk.CTkLabel(self.center_card, text="Perfil Ativo:", font=("Segoe UI", 12), text_color="#888").pack(pady=(15, 0))
        self.profile_btn = ctk.CTkButton(
            self.center_card, text=config.get("current_account", "Nenhuma conta"),
            width=280, height=45, fg_color="#2d2242", hover_color="#3d2b52", command=self.open_profile_selector
        )
        self.profile_btn.pack(pady=10)

        self.version_btn = ctk.CTkButton(
            self.center_card, text="Selecionar Versão", width=280, height=45, 
            fg_color="transparent", border_width=1, border_color=config["theme_color"], command=self.open_versions
        )
        self.version_btn.pack(pady=10)

        self.play_btn = ctk.CTkButton(
            self.center_card, text="JOGAR AGORA", width=280, height=55, font=("Segoe UI", 16, "bold"),
            fg_color=config["theme_color"], hover_color="#9d4edd", command=self.start_game
        )
        self.play_btn.pack(pady=(30, 0))

        # Status & Progress
        self.status_label = ctk.CTkLabel(self.main_content, text="Sistema pronto.", font=("Segoe UI", 11), text_color="#666")
        self.status_label.place(relx=0.5, rely=0.88, anchor="center")
        self.progress_bar = ctk.CTkProgressBar(self.main_content, height=6, progress_color=config["theme_color"], width=400)
        self.progress_bar.set(0)
        self.progress_bar.place(relx=0.5, rely=0.92, anchor="center")

    def create_nav_button(self, text, icon, command):
        btn = ctk.CTkButton(self.sidebar, text=f"  {icon}  {text}", font=("Segoe UI", 13), fg_color="transparent", 
                            text_color="#aaa", hover_color="#1d162b", anchor="w", height=45, command=command)
        btn.pack(fill="x", padx=15, pady=5)

    def go_home(self): pass

    def load_versions_list(self):
        self.versions_list = self.handler.get_versions()

    def open_profile_selector(self):
        win = ctk.CTkToplevel(self)
        win.title("Perfis")
        win.geometry("350x400")
        win.attributes("-topmost", True)
        
        scroll = ctk.CTkScrollableFrame(win, fg_color="transparent")
        scroll.pack(fill="both", expand=True, padx=20, pady=20)

        for acc in config["accounts"]:
            ctk.CTkButton(scroll, text=f"👤 {acc}", fg_color="#1d162b", height=45,
                         command=lambda a=acc: [self.set_active_account(a), win.destroy()]).pack(fill="x", pady=5)

    def set_active_account(self, name):
        config["current_account"] = name
        cfg.save_config(config)
        self.profile_btn.configure(text=name)

    def open_versions(self):
        win = ctk.CTkToplevel(self)
        win.title("Versões do Jogo")
        win.geometry("400x500")
        win.attributes("-topmost", True)
        
        scroll = ctk.CTkScrollableFrame(win, fg_color="transparent")
        scroll.pack(fill="both", expand=True, padx=20, pady=20)

        for v in self.versions_list:
            ctk.CTkButton(scroll, text=f"{v['id']} ({v['status']})", fg_color="transparent", border_width=1,
                         command=lambda n=v['id']: [setattr(self, 'selected_version', n), 
                                                   self.version_btn.configure(text=f"Versão: {n}"), 
                                                   win.destroy()]).pack(fill="x", pady=4)

    def open_accounts_manager(self):
        win = ctk.CTkToplevel(self)
        win.geometry("400x300")
        entry = ctk.CTkEntry(win, placeholder_text="Novo Nickname", width=250)
        entry.pack(pady=30)
        
        def add():
            name = entry.get().strip()
            if name and name not in config["accounts"]:
                config["accounts"].append(name)
                self.set_active_account(name)
                win.destroy()
        
        ctk.CTkButton(win, text="Criar Perfil", command=add, fg_color=config["theme_color"]).pack()

    def open_options(self):
        win = ctk.CTkToplevel(self)
        win.title("Configurações Avançadas")
        win.geometry("450x550")
        win.configure(fg_color="#140f1f")

        ctk.CTkLabel(win, text="Ajustes do Launcher", font=("Segoe UI", 18, "bold")).pack(pady=20)

        # Seleção de GPU (Novo!)
        ctk.CTkLabel(win, text="Placa de Vídeo (GPU):", font=("Segoe UI", 12)).pack(pady=(10,0))
        import subprocess # Necessário para detectar GPUs
        gpus = ["Auto", "NVIDIA High Performance", "AMD Radeon", "Integrated Graphics"]
        gpu_var = ctk.StringVar(value=config.get("gpu_preference", "Auto"))
        gpu_menu = ctk.CTkOptionMenu(win, values=gpus, variable=gpu_var, fg_color="#2d2242", button_color=config["theme_color"])
        gpu_menu.pack(pady=5)

        # RAM
        ctk.CTkLabel(win, text="Memória RAM (ex: 4G):").pack(pady=(20, 5))
        ram_entry = ctk.CTkEntry(win, width=200)
        ram_entry.insert(0, config["ram"])
        ram_entry.pack()

        # Demo Mode
        demo_var = ctk.BooleanVar(value=config["demo_mode"])
        ctk.CTkSwitch(win, text="Modo Demo (Trial)", variable=demo_var).pack(pady=20)

        def save():
            config["ram"] = ram_entry.get()
            config["demo_mode"] = demo_var.get()
            config["gpu_preference"] = gpu_var.get()
            cfg.save_config(config)
            win.destroy()

        ctk.CTkButton(win, text="Salvar e Sair", fg_color=config["theme_color"], command=save).pack(pady=30)

    def start_game(self):
        if not config["current_account"] or not self.selected_version:
            self.update_status("Erro: Escolha conta e versão!")
            return
        
        self.is_installing = True
        threading.Thread(target=lambda: self.handler.launch(
            self.selected_version, config["current_account"], config["ram"], 
            config["demo_mode"], config["gpu_preference"]
        ), daemon=True).start()

    def on_closing(self):
        self.handler.stop()
        self.destroy()

if __name__ == "__main__":
    app = AzurionApp()
    app.mainloop()