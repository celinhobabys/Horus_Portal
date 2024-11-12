import tkinter as tk
from datetime import datetime

class QWERTYKeyboard:
    # Constants for key sizes and spacing
    KEY_WIDTH = 50
    KEY_HEIGHT = 50
    KEY_SPACING = 5

    # QWERTY keyboard layout
    keyboard_layout = [
        ["Q", "W", "E", "R", "T", "Y", "U", "I", "O", "P"],
        ["A", "S", "D", "F", "G", "H", "J", "K", "L"],
        ["Z", "X", "C", "V", "B", "N", "M"]
    ]

    # Special widths for certain keys
    special_keys = {
        "Backspace": 2 * KEY_WIDTH + KEY_SPACING,
        "Tab": 1.5 * KEY_WIDTH + KEY_SPACING,
        "Caps": 1.5 * KEY_WIDTH + KEY_SPACING,
        "Enter": 1.75 * KEY_WIDTH + KEY_SPACING,
        "Shift": 2.25 * KEY_WIDTH + KEY_SPACING,
        "Space": 5 * KEY_WIDTH + 4 * KEY_SPACING
    }

    # Key type buffer for routine recording
    last_action_timestamp = -1
    mode = "listen"

    def __init__(self, root, parent, x_start, y_start):
        self.root = root
        self.parent = parent
        self.canvas = tk.Canvas(self.parent, width=800, height=300, bg="#242323", bd=0, highlightthickness=0)
        self.canvas.pack()
        
        # Starting position for the keyboard layout
        self.x_start, self.y_start = x_start, y_start

        # Dictionary to keep track of rectangles by label
        self.key_rects = {}

        # Dictionary to keep track of key release timers
        self.key_timers = {}

        self.action_registered = {}
        self.current_pressed = []
        self.handler_func = None
        self.last_action_timestamp = datetime.now()

        # Draw the keyboard
        self.draw_keyboard()

    def draw_keyboard(self):
        # Draw keys for each row
        self.draw_row(self.keyboard_layout[0], self.x_start, self.y_start)
        self.draw_row(self.keyboard_layout[1], self.x_start + 0.75 * (self.KEY_WIDTH + self.KEY_SPACING), 
                      self.y_start + self.KEY_HEIGHT + self.KEY_SPACING)
        self.draw_row(self.keyboard_layout[2], self.x_start + 1.5 * (self.KEY_WIDTH + self.KEY_SPACING), 
                      self.y_start + 2 * (self.KEY_HEIGHT + self.KEY_SPACING))

        # Add special keys
        self.draw_special_keys()

    def draw_row(self, row, x_start, y):
        x = x_start
        for key in row:
            self.draw_key(x, y, self.KEY_WIDTH, self.KEY_HEIGHT, key)
            x += self.KEY_WIDTH + self.KEY_SPACING

    def draw_key(self, x, y, width, height, label):
        rect = self.canvas.create_rectangle(x, y, x + width, y + height, fill="lightgrey")
        self.canvas.create_text(x + width / 2, y + height / 2, text=label, font=("Arial", 16))
        
        # Store the rectangle ID with the label for easy lookup
        self.key_rects[label] = rect

    def draw_special_keys(self):
        # Special key positions relative to x_start, y_start
        special_key_positions = {
            "Backspace": (self.x_start + 10 * (self.KEY_WIDTH + self.KEY_SPACING), self.y_start),
            "Tab": (self.x_start - 0.75 * (self.KEY_WIDTH + self.KEY_SPACING), 
                    self.y_start + self.KEY_HEIGHT + self.KEY_SPACING),
            "Caps": (self.x_start - 1.5 * (self.KEY_WIDTH + self.KEY_SPACING), 
                     self.y_start + 2 * (self.KEY_HEIGHT + self.KEY_SPACING)),
            "Enter": (self.x_start + 9 * (self.KEY_WIDTH + self.KEY_SPACING), 
                      self.y_start + 2 * (self.KEY_HEIGHT + self.KEY_SPACING)),
            "Shift": (self.x_start - 1.75 * (self.KEY_WIDTH + self.KEY_SPACING), 
                      self.y_start + 3 * (self.KEY_HEIGHT + self.KEY_SPACING)),
            "Space": (self.x_start + 2.5 * (self.KEY_WIDTH + self.KEY_SPACING), 
                      self.y_start + 4 * (self.KEY_HEIGHT + self.KEY_SPACING))
        }

        for key, (x, y) in special_key_positions.items():
            width = self.special_keys[key]
            self.draw_key(x, y, width, self.KEY_HEIGHT, key)

    def highlight_key(self, label):
        # Change the color of the rectangle associated with the given label to red
        if label in self.key_rects:
            rect_id = self.key_rects[label]
            self.canvas.itemconfig(rect_id, fill="green")

    def reset_key(self, label):
        # Reset the color of the key to lightgrey
        if label in self.key_rects:
            rect_id = self.key_rects[label]
            self.canvas.itemconfig(rect_id, fill="lightgrey")
    
    def bind_keys(self):
        self.root.bind("<KeyPress>", self.on_key_press)
        self.root.bind("<KeyRelease>", self.on_key_release)

    def set_mode(self, new_mode, param=None):
        if new_mode in ["listen", "recording", "typing"]:
            self.mode = new_mode
            print("new_mode", new_mode)
        else:
            print("invalid_mode", new_mode)
        
        if self.mode == "typing":
            self.handler_func = param
            self.last_action_timestamp = None
    
    def bind_action_handler(self, handler_func):
        self.handler_func = handler_func

    def register_action(self, label, mode):
        
        now = datetime.now()

        if self.last_action_timestamp == None:
            self.last_action_timestamp = now

        elapsed_time = "%.2f" % ((now - self.last_action_timestamp).total_seconds() * 1000)

        action = (label, mode, elapsed_time)

        self.action_registered[label] = (mode, now)
        if self.handler_func != None:
            self.handler_func(action)

        self.last_action_timestamp = now

    def press_key(self, label):
        self.register_action(label, "PRESSED")
        self.current_pressed.append(label)

    def release_key(self, label):
        self.reset_key(label)
        self.register_action(label, "RELEASED")
        self.current_pressed.remove(label)

    def on_key_press(self, event):
        label = event.keysym.upper()

        if label in self.key_timers:
            self.root.after_cancel(self.key_timers[label])
            del self.key_timers[label]
        if label not in self.current_pressed:
            self.highlight_key(label)
        self.press_key(label)

    def on_key_release(self, event):
        label = event.keysym.upper()
        self.key_timers[label] = self.root.after(50, lambda: self.release_key(label))
