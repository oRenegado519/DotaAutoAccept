import customtkinter as ctk
import pyautogui
import time
import threading
import sys
import os
import json

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("green") 

pyautogui.FAILSAFE = True 
ARQUIVO_CONFIG = "dota_config.json"

try:
    import winsound
    def bip_aviso(): winsound.Beep(500, 200)
    def bip_sucesso(): winsound.Beep(1000, 500)
except:
    def bip_aviso(): print('\a')
    def bip_sucesso(): print('\a')
def detectar_padrao_texto(x, y):
    """
    Busca pela 'assinatura' visual da palavra ACEITAR.
    Retorna: (Achou?, Num_Transicoes, Num_Verdes)
    """
    try:
        width = 120  
        height = 15
        
        x = int(x)
        y = int(y)
        
        img = pyautogui.screenshot(region=(int(x - width/2), int(y - height/2), width, height))
        
        transicoes = 0
        pixels_verdes = 0
        
        linha_y = int(height / 2)
        ultimo_foi_claro = False
        
        for i in range(width):
            r, g, b = img.getpixel((i, linha_y))
            brilho = r + g + b
            
            eh_claro = brilho > 600 
            
            eh_verde = (g > r + 10) and (g > b + 10) and (brilho < 500)
            
            if eh_verde:
                pixels_verdes += 1

            if eh_claro != ultimo_foi_claro:
                transicoes += 1
                ultimo_foi_claro = eh_claro

        tem_texto = transicoes > 6 
        tem_fundo = pixels_verdes > 15
        
        return (tem_texto and tem_fundo), transicoes, pixels_verdes
        
    except Exception as e:
        print(f"Erro scan: {e}")
        return False, 0, 0

class DotaAcceptApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Auto Aceitar Dota 2 - Pro")
        self.geometry("500x450")
        self.resizable(False, False)

        self.monitorando = False
        self.x_alvo = None
        self.y_alvo = None
        self.cor_fundo_safe = None
        self.criar_interface()
        self.carregar_config()
        self.thread_monitor = threading.Thread(target=self.loop_monitoramento, daemon=True)
        self.thread_monitor.start()

    def criar_interface(self):
        self.lbl_titulo = ctk.CTkLabel(self, text="🛡️ DOTA 2 ACCEPTOR", font=("Roboto", 24, "bold"), text_color="#00E676")
        self.lbl_titulo.pack(pady=(20, 5))
        
        self.lbl_subtitulo = ctk.CTkLabel(self, text="AFK Mode Activated", font=("Roboto", 12), text_color="gray")
        self.lbl_subtitulo.pack(pady=(0, 20))
        self.frame_status = ctk.CTkFrame(self, fg_color="#1b1b1b")
        self.frame_status.pack(fill="x", padx=20, pady=5)
        
        self.lbl_coords = ctk.CTkLabel(self.frame_status, text="Mira: Não configurada", font=("Consolas", 12))
        self.lbl_coords.pack(pady=10)
        
        self.lbl_status = ctk.CTkLabel(self.frame_status, text="STATUS: AGUARDANDO", font=("Roboto", 14, "bold"), text_color="#FF9800")
        self.lbl_status.pack(pady=(0, 10))
        self.frame_btns = ctk.CTkFrame(self, fg_color="transparent")
        self.frame_btns.pack(pady=20)
        
        self.btn_calibrar = ctk.CTkButton(self.frame_btns, text="📍 Recalibrar", command=self.iniciar_calibracao, 
                                          fg_color="#455A64", hover_color="#37474F", width=140)
        self.btn_calibrar.pack(side="left", padx=10)
        
        self.btn_start = ctk.CTkButton(self.frame_btns, text="▶️ INICIAR", command=self.toggle_monitoramento, 
                                       state="disabled", width=140, font=("Roboto", 14, "bold"))
        self.btn_start.pack(side="left", padx=10)

        self.txt_log = ctk.CTkTextbox(self, height=120, font=("Consolas", 11))
        self.txt_log.pack(fill="x", padx=20, pady=10)
        self.log("Sistema iniciado.")

    def log(self, msg):
        timestamp = time.strftime("%H:%M:%S")
        self.txt_log.insert("end", f"[{timestamp}] {msg}\n")
        self.txt_log.see("end")

    def salvar_config(self):
        dados = {"x": self.x_alvo, "y": self.y_alvo}
        try:
            with open(ARQUIVO_CONFIG, "w") as f:
                json.dump(dados, f)
            self.log("Configuração salva com sucesso!")
        except Exception as e:
            self.log(f"Erro ao salvar: {e}")

    def carregar_config(self):
        if os.path.exists(ARQUIVO_CONFIG):
            try:
                with open(ARQUIVO_CONFIG, "r") as f:
                    dados = json.load(f)
                    self.x_alvo = dados["x"]
                    self.y_alvo = dados["y"]
                    
                    self.log(f"Config carregada: {self.x_alvo}, {self.y_alvo}")
                    self.lbl_coords.configure(text=f"Mira Salva: X={self.x_alvo}, Y={self.y_alvo}")
                    self.btn_start.configure(state="normal")
                    self.lbl_status.configure(text="STATUS: PRONTO", text_color="#2196F3")
            except Exception as e:
                self.log("Erro ao ler config salva. Recalibre.")

    def iniciar_calibracao(self):
        self.btn_calibrar.configure(state="disabled")
        self.btn_start.configure(state="disabled")
        threading.Thread(target=self._rotina_calibracao, daemon=True).start()

    def _rotina_calibracao(self):
        w, h = pyautogui.size()
        cx = int(w / 2)
        
        self.log("⚠️ CALIBRAÇÃO EM 5 SEGUNDOS...")
        self.log(f"O Script vai usar o CENTRO DA TELA (X={cx}).")
        self.log("Apenas ajuste a ALTURA do mouse para onde fica o botão.")
        
        for i in range(5, 0, -1):
            self.lbl_status.configure(text=f"CALIBRANDO EM {i}...", text_color="#FF9800")
            time.sleep(1)
            
        _, my = pyautogui.position()
        self.x_alvo = cx
        self.y_alvo = int(my)
        
        bip_aviso()
        self.salvar_config() 
        
        self.lbl_coords.configure(text=f"Mira: X={self.x_alvo}, Y={self.y_alvo}")
        
        achou, tr, vd = detectar_padrao_texto(self.x_alvo, self.y_alvo)
        self.log(f"Teste de Mira -> Texto visível? {achou}")
        
        self.btn_calibrar.configure(state="normal")
        self.btn_start.configure(state="normal")
        self.lbl_status.configure(text="STATUS: PRONTO", text_color="#2196F3")

    def toggle_monitoramento(self):
        if not self.monitorando:
            self.monitorando = True
            self.btn_start.configure(text="⏸️ PAUSAR", fg_color="#C62828", hover_color="#B71C1C")
            self.btn_calibrar.configure(state="disabled")
            self.lbl_status.configure(text="VIGILÂNCIA ATIVA", text_color="#00E676")
            self.cor_fundo_safe = pyautogui.pixel(self.x_alvo, self.y_alvo)
            self.log("Monitoramento INICIADO. Pode dar Alt-Tab.")
        else:
            self.monitorando = False
            self.btn_start.configure(text="▶️ INICIAR", fg_color="#1f6aa5", hover_color="#144870")
            self.btn_calibrar.configure(state="normal")
            self.lbl_status.configure(text="STATUS: PAUSADO", text_color="gray")
            self.log("Monitoramento PAUSADO.")

    def loop_monitoramento(self):
        while True:
            if self.monitorando and self.x_alvo:
                try:
                    cor_atual = pyautogui.pixel(self.x_alvo, self.y_alvo)
                    if self.cor_fundo_safe is None:
                         self.cor_fundo_safe = cor_atual
                         
                    mudanca = sum([abs(c1 - c2) for c1, c2 in zip(self.cor_fundo_safe, cor_atual)])
                    if mudanca > 15:
                        tem_texto, tr, vd = detectar_padrao_texto(self.x_alvo, self.y_alvo)
                        
                        if tem_texto:
                            self.log(f"🔥 PARTIDA ENCONTRADA! (Tr:{tr} Vd:{vd})")
                            bip_sucesso()
                            pyautogui.moveTo(self.x_alvo, self.y_alvo)
                            time.sleep(0.1)
                            pyautogui.click()
                            time.sleep(0.1)
                            pyautogui.press('enter')
                            
                            self.log("✅ Aceito! Pausa de 20s...")
                            time.sleep(20)
                            self.cor_fundo_safe = pyautogui.pixel(self.x_alvo, self.y_alvo)
                            self.log("Voltando a vigiar...")
                            
                except Exception as e:
                    print(f"Erro loop: {e}")
            
            time.sleep(0.2)

if __name__ == "__main__":
    app = DotaAcceptApp()
    app.mainloop()