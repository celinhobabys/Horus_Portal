import os
import sys
import shutil
import tkinter as tk
from tkinter import ttk
import pygame
from datetime import datetime

global sound_state
sound_state = False

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

def start_audio():
    global sound_state
    try:
        pygame.mixer.init()
        sound_state = True
    except:
        pass

def stop_audio():
    global sound_state
    try:
        pygame.mixer.quit()
        sound_state = False
    except:
        pass

def play_music(path):
    global sound_state
    if sound_state:
        try:
            sound = pygame.mixer.music.load(resource_path(path))
            pygame.mixer.music.play()
        except:
            pass

def play_sound(path):
    global sound_state
    if sound_state:
        try:
            sound = pygame.mixer.Sound(resource_path(path))
            pygame.mixer.Sound.play(sound)
        except:
            pass

def on_Enter_Sidebar(event):
    play_sound("resources/audio/sound/Hover.mp3")
    event.widget.config(bg="#3bdb42")

def on_Enter_Dominar(event):
    play_sound("resources/audio/sound/Hover.mp3")
    event.widget.config(bg="#db2a16")

def on_Leave_Sidebar(event):
    event.widget.config(bg="#4CAF50")

def on_Leave_Dominar(event):
    event.widget.config(bg="#a1392d")

def on_Click():
    play_sound("resources/audio/sound/Click.mp3")

def on_Click_Dom_On():
    play_sound("resources/audio/sound/DominationIn.mp3")

def on_Click_Dom_Off():
    play_sound("resources/audio/sound/DominationOut.mp3")

def error_sound():
    play_sound("resources/audio/sound/error.mp3")

def response_sound():
    play_sound("resources/audio/sound/response.mp3")


def make_draggable(widget):
    # Create a Frame inside the Toplevel window
    frame = tk.Frame(widget, bg='#3a3a3a')
    frame.pack(expand=True, fill='both')

    def start_drag(event):
        widget.x = event.x
        widget.y = event.y

    def do_drag(event):
        x = widget.winfo_x() - widget.x + event.x
        y = widget.winfo_y() - widget.y + event.y
        widget.geometry(f"+{x}+{y}")

    # Bind mouse events for dragging to the Frame
    frame.bind("<Button-1>", start_drag)
    frame.bind("<B1-Motion>", do_drag)

class ScrollableFrame(tk.Frame):
    def __init__(self, container, width=400, height=400, *args, **kwargs):
        super().__init__(container, *args, **kwargs, bd=0, highlightthickness=0)
        
        self.canvas = tk.Canvas(self, width=width, height=height, bd=0, highlightthickness=0, bg="#242323")
        self.canvas.pack(side="left", fill="both", expand=True)
        
        # Customiza a barra de rolagem
        style = ttk.Style()
        style.theme_use("clam")  # Escolha um tema que permita personalização
        style.configure(
            "Vertical.TScrollbar",
            troughcolor="#000000",  # Cor do fundo (área de rolagem)
            background="#4CAF50",  # Cor da barrinha
            arrowcolor="#4CAF50",  # Cor das setas
            bordercolor="#242323",  # Cor da borda
            relief="flat",  # Estilo da borda
        )
        
        self.scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.canvas.yview, style="Vertical.TScrollbar")
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

class ScrollableText(tk.Frame):
    def __init__(self, container, width=400, height=400, *args, **kwargs):
        super().__init__(container, *args, **kwargs, bd=0, highlightthickness=0)
        
        # Canvas to host the Text widget
        self.canvas = tk.Canvas(self, width=width, height=height, bd=0, highlightthickness=0, bg="#242323")
        self.canvas.pack(side="left", fill="both", expand=True)
        
        # Custom scrollbar style
        style = ttk.Style()
        style.theme_use("clam")
        style.configure(
            "Vertical.TScrollbar",
            troughcolor="#000000",
            background="#4CAF50",
            arrowcolor="#4CAF50",
            bordercolor="#242323",
            relief="flat",
        )
        
        self.scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.canvas.yview, style="Vertical.TScrollbar")
        self.scrollbar.pack(side="right", fill="y")
        
        # Configuring the scrollbar and canvas
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        
        # Creating a Text widget
        self.text = tk.Text(
            self.canvas,
            wrap="word",  # Allows word wrapping
            bd=0,
            highlightthickness=0,
            bg="#242323",
            fg="#ffffff",  # Text color
            insertbackground="#ffffff",  # Caret color
        )
        self.text_window = self.canvas.create_window((0, 0), window=self.text, anchor="nw")

        # Bind events for scrolling behavior
        self.text.bind("<Configure>", self.on_text_configure)
        self.canvas.bind("<Configure>", self.on_canvas_configure)

        # Search state
        self.search_results = []  # List of all match positions
        self.current_index = -1  # Current position in search results

    def on_text_configure(self, event=None):
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))
    
    def on_canvas_configure(self, event):
        canvas_width = event.width
        self.canvas.itemconfig(self.text_window, width=canvas_width)

    # Wrapper methods for the Text widget
    def insert(self, index, text, *args):
        self.text.insert(index, text, *args)

    def delete(self, start, end=None):
        self.text.delete(start, end)

    def config(self, **kwargs):
        self.text.config(**kwargs)

    # Search functionality
    def search_text(self, target):
        self.text.tag_remove("highlight", "1.0", tk.END)  # Clear previous highlights
        self.search_results = []  # Clear previous search results
        self.current_index = -1  # Reset current index

        if target:  # Search only if there's text
            start_pos = "1.0"
            while True:
                start_pos = self.text.search(target, start_pos, stopindex=tk.END)
                if not start_pos:
                    break  # Exit if no more matches
                end_pos = f"{start_pos}+{len(target)}c"
                self.text.tag_add("highlight", start_pos, end_pos)  # Highlight match
                self.search_results.append((start_pos, end_pos))  # Store match positions
                start_pos = end_pos  # Move past the match

        # Configure the highlight tag
        self.text.tag_config("highlight", background="yellow", foreground="black")
        if self.search_results:
            self.current_index = 0
            self.text.see(self.search_results[0][0])  # Show the first match

    def go_next(self):
        if self.search_results:
            self.current_index = (self.current_index + 1) % len(self.search_results)
            self.text.see(self.search_results[self.current_index][0])

    def go_back(self):
        if self.search_results:
            self.current_index = (self.current_index - 1) % len(self.search_results)
            self.text.see(self.search_results[self.current_index][0])

    def get(self, start="1.0", end=tk.END):
        """Get text from the internal Text widget."""
        return self.text.get(start, end).strip()