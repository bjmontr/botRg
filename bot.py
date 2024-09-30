import tkinter as tk
from tkinter import scrolledtext, messagebox
import pyautogui
import cv2
import numpy as np
import pytesseract
import keyboard
from PIL import Image, ImageTk
import time

pytesseract.pytesseract.tesseract_cmd = r'C:\Users\gyan.monteiro\AppData\Local\Programs\Tesseract-OCR\tesseract.exe'

class BotApp:
    def __init__(self, root):
        self.root = root
        self.root.title("BotRg")

        # Área de texto para exibir as ações do bot
        self.text_area = scrolledtext.ScrolledText(root, width=40, height=10)
        self.text_area.pack()

        # Lista de inimigos com seus nomes e imagens
        self.enemies = [
            {"name": "Isilla", "image": "isilla.png"},
            {"name": "Hodremlin", "image": "hodremlin.png"},
            {"name": "Vanberk", "image": "vanberk.png"},
            {"name": "Majoruros", "image": "majoruros.png"},
            {"name": "Les", "image": "les.png"}
        ]

        # Frame para organizar os inimigos
        enemy_frame = tk.Frame(root)
        enemy_frame.pack()

        self.check_vars = {}
        self.enemy_buttons = {}

        for enemy in self.enemies:
            # Frame individual para cada inimigo (botão + imagem)
            frame = tk.Frame(enemy_frame)
            frame.pack(side=tk.LEFT, padx=10)

            # Variável de checkbox
            var = tk.IntVar()
            checkbox = tk.Checkbutton(frame, text=enemy["name"], variable=var)
            checkbox.pack()

            # Carregar a imagem do inimigo
            img = Image.open(enemy["image"]).resize((50, 50))
            img = ImageTk.PhotoImage(img)
            label = tk.Label(frame, image=img)
            label.image = img  # Manter a referência da imagem
            label.pack()

            # Armazenar checkbox e variável associada
            self.check_vars[enemy["name"]] = var
            self.enemy_buttons[enemy["name"]] = checkbox

        # Campos e botões para capturar as teclas de ataque e teletransporte
        self.attack_key_label = tk.Label(root, text="Tecla de Ataque:")
        self.attack_key_label.pack()
        self.attack_key_entry = tk.Entry(root)
        self.attack_key_entry.pack()

        self.teleport_key_label = tk.Label(root, text="Tecla de Teletransporte:")
        self.teleport_key_label.pack()
        self.teleport_key_entry = tk.Entry(root)
        self.teleport_key_entry.pack()

        self.capture_attack_key_button = tk.Button(root, text="Capturar Tecla de Ataque", command=self.capture_attack_key)
        self.capture_attack_key_button.pack()

        self.capture_teleport_key_button = tk.Button(root, text="Capturar Tecla de Teletransporte", command=self.capture_teleport_key)
        self.capture_teleport_key_button.pack()

        # Botões
        self.start_button = tk.Button(root, text="Iniciar", command=self.run_bot)
        self.start_button.pack()

        self.stop_key_button = tk.Button(root, text="Definir Tecla de Parada", command=self.get_stop_key)
        self.stop_key_button.pack()

        # Variáveis para armazenar as teclas
        self.attack_key = None
        self.teleport_key = None
        self.stop_key = None

        # Variável para controlar o loop do bot
        self.running = True

    def log_action(self, action):
        """Função para logar ações na interface"""
        self.text_area.insert(tk.END, f"{action}\n")
        self.text_area.see(tk.END)  # Scroll automático

    def stop_bot(self):
        """Função para parar o bot"""
        self.running = False
        self.log_action("Bot parado.")

    def find_enemy(self, template_path):
        """Função para identificar o inimigo na tela, ajustando para diferentes tamanhos"""
        screenshot = np.array(pyautogui.screenshot())  # Captura a tela usando pyautogui
        screenshot_gray = cv2.cvtColor(screenshot, cv2.COLOR_BGR2GRAY)

        # Carrega a imagem do template (inimigo ou captcha)
        template = cv2.imread(template_path, 0)
        template_height, template_width = template.shape[:2]

        # Inicializa a variável para armazenar o melhor resultado
        best_match = None
        best_val = 0

        # Faz a varredura em múltiplas escalas
        for scale in np.linspace(0.5, 1.5, 20):  # Escalas entre 50% e 150% do tamanho original
            resized_template = cv2.resize(template, (int(template_width * scale), int(template_height * scale)))

            # Ignora escalas que resultam em templates maiores que a imagem
            if resized_template.shape[0] > screenshot_gray.shape[0] or resized_template.shape[1] > screenshot_gray.shape[1]:
                continue

            # Faz a correspondência do template
            result = cv2.matchTemplate(screenshot_gray, resized_template, cv2.TM_CCOEFF_NORMED)
            _, max_val, _, max_loc = cv2.minMaxLoc(result)

            # Mantém o melhor resultado
            if max_val > best_val:
                best_val = max_val
                best_match = (max_loc, scale)

        if best_val >= 0.7:  # Define um threshold para correspondência
            self.log_action(f"Correspondência encontrada no template {template_path} com valor de confiança {best_val}.")
            return best_match[0]  # Retorna a posição do melhor match
        else:
            self.log_action(f"Nenhuma correspondência confiável encontrada para o template {template_path}.")
            return None

    def attack_enemy(self, enemy_position=None):
        """Simula o ataque e teletransporte do mouse para o inimigo"""
        self.log_action("Ataque iniciado.")
        attack_key = self.attack_key or 'space'
        pyautogui.press(attack_key)

        if enemy_position:
            x, y = enemy_position
            self.log_action(f"Teleportando o mouse para a posição do inimigo em ({x}, {y}).")
            pyautogui.moveTo(x, y, duration=0)  # Move o mouse instantaneamente
            pyautogui.click()

    def capture_attack_key(self):
        """Captura a tecla de ataque pressionada"""
        self.log_action("Pressione a tecla para atacar...")
        self.root.after(100, self.get_attack_key)

    def get_attack_key(self):
        """Obtém a tecla de ataque"""
        if keyboard.read_event().event_type == keyboard.KEY_DOWN:
            key = keyboard.read_event().name
            self.attack_key_entry.delete(0, tk.END)  # Limpa o campo
            self.attack_key_entry.insert(0, key)  # Insere a tecla pressionada
            self.attack_key = key
            self.log_action(f"Tecla de Ataque capturada: {key}")
            return  # Capturou a tecla, então sai da função

        self.root.after(100, self.get_attack_key)  # Continua verificando

    def capture_teleport_key(self):
        """Captura a tecla de teletransporte pressionada"""
        self.log_action("Pressione a tecla para teletransportar...")
        self.root.after(100, self.get_teleport_key)

    def get_teleport_key(self):
        """Obtém a tecla de teletransporte"""
        if keyboard.read_event().event_type == keyboard.KEY_DOWN:
            key = keyboard.read_event().name
            self.teleport_key_entry.delete(0, tk.END)  # Limpa o campo
            self.teleport_key_entry.insert(0, key)  # Insere a tecla pressionada
            self.teleport_key = key
            self.log_action(f"Tecla de Teletransporte capturada: {key}")
            return  # Capturou a tecla, então sai da função

        self.root.after(100, self.get_teleport_key)  # Continua verificando

    def get_stop_key(self):
        """Captura a tecla para parar o bot"""
        self.log_action("Pressione a tecla para parar o bot...")
        while True:
            event = keyboard.read_event()
            if event.event_type == keyboard.KEY_DOWN:
                self.stop_key = event.name
                self.log_action(f"Tecla de parada definida como: {self.stop_key}")
                break

    def check_for_verification(self):
        """Verifica a presença de mensagens de verificação ou CAPTCHA"""
        screenshot = pyautogui.screenshot()
        text = pytesseract.image_to_string(screenshot)
        if "checagem" in text or "automatica" in text or "anti-bot" in text:
            self.log_action("Verificação/CAPTCHA detectado! Parando o bot.")
            self.stop_bot()
            self.alert_verification()  # Exibe o alerta de CAPTCHA
            return True
        return False

    def alert_verification(self):
        """Mostra um alerta visual quando o CAPTCHA é detectado"""
        messagebox.showwarning("CAPTCHA Detectado", "O CAPTCHA foi detectado! O bot foi interrompido.")

    def use_teleport(self):
        """Simula o uso da habilidade de teletransporte"""
        if self.teleport_key:
            pyautogui.press(self.teleport_key)
            self.log_action(f"Usando teletransporte com a tecla {self.teleport_key}.")
            time.sleep(1)  # Espera 2 segundos após o uso do teletransporte

    def run_bot(self):
        """Inicia o loop principal do bot sem bloquear a interface"""
        self.running = True
        self.log_action("Bot iniciado.")
        self.bot_loop()

    def bot_loop(self):
        """Loop principal do bot usando after para não bloquear a interface"""
        if not self.running:
            return

        # Verifica o CAPTCHA logo no início do loop
        if self.check_for_verification():
            self.log_action("Captcha detectado! Bot parado.")
            self.stop_bot()
            return

        # Verifica se a tecla de parada foi pressionada
        if self.stop_key and keyboard.is_pressed(self.stop_key):
            self.log_action("Tecla de parada pressionada. Parando o bot.")
            self.stop_bot()
            return

        self.log_action("Varredura iniciada.")

        # Itera sobre todos os inimigos e verifica se estão selecionados
        for enemy in self.enemies:
            if self.check_vars[enemy["name"]].get():  # Se o checkbox estiver marcado
                self.log_action(f"Procurando por {enemy['name']}...")
                enemy_position = self.find_enemy(enemy["image"])  # Usa a imagem do inimigo selecionado

                if enemy_position:
                    self.log_action(f"Inimigo {enemy['name']} encontrado.")
                    self.attack_enemy(enemy_position)

                    # Verificação de CAPTCHA após atacar o inimigo
                    if self.check_for_verification():
                        self.log_action("Captcha detectado após ataque! Bot parado.")
                        self.stop_bot()
                        return

                    self.use_teleport()  # Usa teleporte com atraso e verificação
                    break  # Para o loop ao encontrar um inimigo
            else:
                self.log_action(f"{enemy['name']} não selecionado. Pulando...")

        else:
            self.log_action("Nenhum inimigo encontrado nesta varredura.")

        # Verifica o CAPTCHA ao final da varredura
        if self.check_for_verification():
            self.log_action("Captcha detectado após varredura! Bot parado.")
            self.stop_bot()
            return

        # Reagenda o próximo loop após 100ms
        self.root.after(100, self.bot_loop)

# Execução do programa
if __name__ == "__main__":
    root = tk.Tk()
    app = BotApp(root)
    root.mainloop()
