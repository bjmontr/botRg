import tkinter as tk
from tkinter import scrolledtext
import pyautogui
import cv2
import numpy as np
import pytesseract
import keyboard
from PIL import ImageGrab

pytesseract.pytesseract.tesseract_cmd = r'C:\Users\gyan.monteiro\AppData\Local\Programs\Tesseract-OCR\tesseract.exe'

class BotApp:
    def __init__(self, root):
        self.root = root
        self.root.title("BotRg")

        # Área de texto para exibir as ações do bot
        self.text_area = scrolledtext.ScrolledText(root, width=40, height=10)
        self.text_area.pack()

        # Lista de inimigos e suas variáveis de seleção
        self.enemies = ["isilla.png", "inimigo2.png", "inimigo3.png", "inimigo4.png", "inimigo5.png"]
        self.check_vars = [tk.IntVar() for _ in self.enemies]  # Variáveis para os checkboxes

        # Criação dos checkboxes
        for i, enemy in enumerate(self.enemies):
            cb = tk.Checkbutton(root, text=enemy, variable=self.check_vars[i])
            cb.pack(anchor='w')

        # Campo de entrada para a tecla de ataque
        self.attack_key_label = tk.Label(root, text="Tecla de Ataque:")
        self.attack_key_label.pack()
        self.attack_key_entry = tk.Entry(root)
        self.attack_key_entry.pack()

        # Mensagem para exibir a tecla de ataque
        self.attack_key_message = tk.Label(root, text="")
        self.attack_key_message.pack()

        # Botão para capturar a tecla de ataque
        self.capture_attack_key_button = tk.Button(root, text="Capturar Tecla de Ataque", command=self.capture_attack_key)
        self.capture_attack_key_button.pack()

        # Campo de entrada para a tecla de teletransporte
        self.teleport_key_label = tk.Label(root, text="Tecla de Teletransporte:")
        self.teleport_key_label.pack()
        self.teleport_key_entry = tk.Entry(root)
        self.teleport_key_entry.pack()

        # Mensagem para exibir a tecla de teletransporte
        self.teleport_key_message = tk.Label(root, text="")
        self.teleport_key_message.pack()

        # Botão para capturar a tecla de teletransporte
        self.capture_teleport_key_button = tk.Button(root, text="Capturar Tecla de Teletransporte", command=self.capture_teleport_key)
        self.capture_teleport_key_button.pack()

        # Botão para iniciar o bot
        self.start_button = tk.Button(root, text="Iniciar", command=self.run_bot)
        self.start_button.pack()

        self.stop_key_button = tk.Button(root, text="Definir Tecla de Parada", command=self.get_stop_key)
        self.stop_key_button.pack()

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
        """Função para identificar o inimigo na tela"""
        screenshot = np.array(pyautogui.screenshot())  # Usa pyautogui para capturar a tela
        screenshot_gray = cv2.cvtColor(screenshot, cv2.COLOR_BGR2GRAY)
        template = cv2.imread(template_path, 0)
        result = cv2.matchTemplate(screenshot_gray, template, cv2.TM_CCOEFF_NORMED)
        threshold = 0.8
        loc = np.where(result >= threshold)

        if loc[0].size > 0:
            # Retorna a posição média do inimigo encontrado
            y, x = loc[0][0], loc[1][0]
            return (x, y)  # Retorna as coordenadas (x, y) do inimigo
        return None  # Retorna None se o inimigo não for encontrado

    def attack_enemy(self, enemy_position=None):
        """Simula o ataque e teleportação do mouse para o inimigo"""
        self.log_action("Ataque iniciado.")
        
        # Obtém a tecla de ataque a partir do campo de entrada
        attack_key = self.attack_key_entry.get() or 'space'  # Default para 'space' se vazio
        pyautogui.press(attack_key)

        # Se a posição do inimigo for fornecida, move o mouse para lá instantaneamente
        if enemy_position:
            x, y = enemy_position
            self.log_action(f"Teleportando o mouse para a posição do inimigo em ({x}, {y}).")
            
            # Teleporta o mouse para a posição do inimigo instantaneamente
            pyautogui.moveTo(x, y, duration=0)  # Duração de 0 para movimento instantâneo
            pyautogui.click()  # Simula um clique no inimigo
        else:
            self.log_action("Posição do inimigo não encontrada.")

    def use_teleport(self):
        """Usa o item de teletransporte"""
        self.log_action("Usando teletransporte.")
        
        # Obtém a tecla de teletransporte a partir do campo de entrada
        teleport_key = self.teleport_key_entry.get() or 'f1'  # Default para 'f1' se vazio
        pyautogui.press(teleport_key)  # Simula a tecla de teletransporte

    def check_for_verification(self):
        """Verifica a presença de mensagens de verificação"""
        screenshot = pyautogui.screenshot()
        text = pytesseract.image_to_string(screenshot)
        if "verificação" in text or "sala de teste" in text:
            self.log_action("Verificação detectada. Parando o bot.")
            self.stop_bot()
            return True
        return False

    def capture_attack_key(self):
        """Captura a tecla de ataque pressionada"""
        self.log_action("Pressione a tecla para atacar...")
        self.attack_key_message.config(text="Pressione a tecla para atacar...")  # Mensagem de captura
        self.root.after(100, self.get_attack_key)

    def get_attack_key(self):
        """Obtém a tecla pressionada"""
        # Verifica se houve uma tecla pressionada
        if keyboard.read_event().event_type == keyboard.KEY_DOWN:
            key = keyboard.read_event().name
            self.attack_key_entry.delete(0, tk.END)  # Limpa o campo
            self.attack_key_entry.insert(0, key)  # Insere a tecla pressionada
            self.attack_key_message.config(text=f"Tecla definida como: {key}")  # Atualiza a mensagem
            self.log_action(f"Tecla de Ataque capturada: {key}")
            return  # Retorna após capturar a tecla

        self.root.after(100, self.get_attack_key)  # Continua verificando

    def capture_teleport_key(self):
        """Captura a tecla de teletransporte pressionada"""
        self.log_action("Pressione a tecla para teletransportar...")
        self.teleport_key_message.config(text="Pressione a tecla para teletransportar...")  # Mensagem de captura
        self.root.after(100, self.get_teleport_key)

    def get_teleport_key(self):
        """Obtém a tecla pressionada"""
        # Verifica se houve uma tecla pressionada
        if keyboard.read_event().event_type == keyboard.KEY_DOWN:
            key = keyboard.read_event().name
            self.teleport_key_entry.delete(0, tk.END)  # Limpa o campo
            self.teleport_key_entry.insert(0, key)  # Insere a tecla pressionada
            self.teleport_key_message.config(text=f"Tecla definida como: {key}")  # Atualiza a mensagem
            self.log_action(f"Tecla de Teletransporte capturada: {key}")
            return  # Retorna após capturar a tecla

        self.root.after(100, self.get_teleport_key)  # Continua verificando

    def get_stop_key(self):
        self.log_action("Pressione a tecla para parar o bot...")
        while True:
            event = keyboard.read_event()
            if event.event_type == keyboard.KEY_DOWN:
                self.stop_key = event.name
                self.log_action(f"Tecla de parada definida como: {self.stop_key}")
                break

    def run_bot(self):
        """Loop principal do bot"""
        self.running = True
        self.log_action("Bot iniciado.")
        while self.running:
            if self.check_for_verification():
                break

            # Verifica se a tecla de parada foi pressionada
            if self.stop_key and keyboard.is_pressed(self.stop_key):
                self.log_action("Tecla de parada pressionada. Parando o bot.")
                self.stop_bot()
                break

            self.log_action("Varredura iniciada.")
            enemy_position = self.find_enemy('isilla.png')

            if enemy_position:
                self.log_action("Inimigo encontrado.")
                self.attack_enemy(enemy_position)
                self.use_teleport()
            else:
                self.log_action("Inimigo não encontrado.")

            self.root.update()  # Atualiza a interface


if __name__ == "__main__":
    root = tk.Tk()
    app = BotApp(root)
    root.mainloop()
