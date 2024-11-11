import os
import sys
import shutil
import winreg
import tkinter as tk
import pygame

pygame.mixer.init()

def centralize_Window(root,width = None,height = None):
    
    if width is None:
        width = 1280
    if height is None:
        height = 720

    widthW = root.winfo_screenwidth()
    heightW = root.winfo_screenheight()
    
    pos_x = (widthW - width) // 2
    pos_y = (heightW - height) // 2
    
    root.geometry(f"{width}x{height}+{pos_x}+{pos_y}")

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

def install_font(font_path):
    font_name = os.path.basename(font_path)
    try:
        # Check if the font file exists
        if not os.path.isfile(font_path):
            print("Font file not found.")
            return False
        font_dir = os.path.join(os.environ["WINDIR"], "Fonts")
        destination = os.path.join(font_dir, font_name)
        shutil.copy(font_path, destination)
        font_name_no_ext = os.path.splitext(font_name)[0]
        with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows NT\CurrentVersion\Fonts", 0, winreg.KEY_SET_VALUE) as key:
            winreg.SetValueEx(key, font_name_no_ext, 0, winreg.REG_SZ, font_name)
        return True
    except Exception as e:
        print(f"Failed to install font: {e}")
        return False

def home_Page():
    
    return

def on_Enter_Sidebar(event):
    sound = pygame.mixer.Sound(resource_path("resources/Hover.mp3"))
    pygame.mixer.Sound.play(sound)
    event.widget.config(bg="#3bdb42")

def on_Enter_Dominar(event):
    sound = pygame.mixer.Sound(resource_path("resources/Hover.mp3"))
    pygame.mixer.Sound.play(sound)
    event.widget.config(bg="#db2a16")

def on_Leave_Sidebar(event):
    event.widget.config(bg="#4CAF50")

def on_Leave_Dominar(event):
    event.widget.config(bg="#a1392d")

def on_Click():
    sound = pygame.mixer.Sound(resource_path("resources/Click.mp3"))
    pygame.mixer.Sound.play(sound)

def on_Click_Dom_On():
    sound = pygame.mixer.Sound(resource_path("resources/DominationIn.mp3"))
    pygame.mixer.Sound.play(sound)

def on_Click_Dom_Off():
    sound = pygame.mixer.Sound(resource_path("resources/DominationOut.mp3"))
    pygame.mixer.Sound.play(sound)

class ScrollableFrame(tk.Frame):
    def __init__(self, container, width=400, height=400, *args, **kwargs):
        super().__init__(container, *args, **kwargs, bd=0, highlightthickness=0)
        
        self.canvas = tk.Canvas(self, width=width, height=height, bd=0, highlightthickness=0, bg="#242323")
        self.canvas.pack(side="left", fill="both", expand=True)
        
        self.scrollbar = tk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.scrollbar.pack(side="right", fill="y")
        
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        
        self.scrollable_frame = tk.Frame(self.canvas, bg="#242323")
        
        self.canvas_window = self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        
        self.scrollable_frame.bind("<Configure>", self.on_frame_configure)
        self.canvas.bind("<Configure>", self.on_canvas_configure)
    
    def on_frame_configure(self, event=None):
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))
    
    def on_canvas_configure(self, event):
        canvas_width = event.width
        self.canvas.itemconfig(self.canvas_window, width=canvas_width)
