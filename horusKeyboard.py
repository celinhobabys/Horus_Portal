import tkinter as tk
from datetime import datetime

class QWERTYKeyboard:
    # Constants for key sizes and spacing
    KEY_WIDTH = 50
    KEY_HEIGHT = 50
    KEY_SPACING = 5

    # QWERTY keyboard layout with numbers row added
    keyboard_layout = [
        ["1", "2", "3", "4", "5", "6", "7", "8", "9", "0"],
        ["Q", "W", "E", "R", "T", "Y", "U", "I", "O", "P"],
        ["A", "S", "D", "F", "G", "H", "J", "K", "L", "Ç"],
        ["Z", "X", "C", "V", "B", "N", "M", ",", ".", ";"]
    ]

    # Special widths for certain keys
    special_keys = {
        "Esc": KEY_WIDTH + KEY_SPACING,
        "Backspace": 2 * KEY_WIDTH + KEY_SPACING,
        "Tab": 1.5 * KEY_WIDTH + KEY_SPACING,
        "Caps": 1.75 * KEY_WIDTH + KEY_SPACING,
        "Enter": 1.75 * KEY_WIDTH + KEY_SPACING,
        "Shift": 2.25 * KEY_WIDTH + KEY_SPACING,
        "Space": 5 * KEY_WIDTH + 4 * KEY_SPACING,
        "Ctrl": 1.5 * KEY_WIDTH + KEY_SPACING,
        "Win": 1.25 * KEY_WIDTH + KEY_SPACING,
        "Alt": 1.25 * KEY_WIDTH + KEY_SPACING,
    }

    key_mappings = {
        "ESCAPE": "Esc",
        "BACKSPACE": "Backspace",
        "TAB": "Tab",
        "CAPS_LOCK": "Caps",
        "SHIFT_L": "Shift",
        "SPACE": "Space",
        "COMMA": ",",
        "ALT_L": "Alt",
        "ALT_R": "Alt",
        "PERIOD": ".",
        "RETURN": "Enter",
        "CONTROL_L": "Ctrl",
        "CONTROL_R": "Ctrl",
        "SHIFT_R": "Shift"
    }

    mqtt_mappings = {
        "TAB": "Tab",
        "CAPS_LOCK": "Caps_lock",
        "CONTROL_R": "Ctrl",
        "CONTROL_L": "Ctrl",
        "ALT_L": "Alt",
        "ALT_R": "Alt",
        "BACKSPACE": "Backspace",
        "SPACE": "Space_key",
        "ESCAPE": "Esc"
    }

    inverse_mqtt_mappings = {
        'Tab': ['TAB'],
        'Caps_lock': ['CAPS_LOCK'],
        'Ctrl': ['CONTROL_R', 'CONTROL_L'],
        'Alt': ['ALT_L', 'ALT_R'],
        'Backspace': ['BACKSPACE'],
        'Space_key': ['SPACE'],
        'Esc': ['ESCAPE']
    }


    # Key type buffer for routine recording
    last_action_timestamp = -1
    mode = "listen"

    caps_pressed = False

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
        self.draw_row(self.keyboard_layout[0], (self.x_start - 1.75 * (self.KEY_WIDTH + self.KEY_SPACING)) + self.special_keys["Esc"] + self.KEY_SPACING, self.y_start)
        self.draw_row(self.keyboard_layout[1], (self.x_start - 1.75 * (self.KEY_WIDTH + self.KEY_SPACING)) + self.special_keys["Tab"] + self.KEY_SPACING, 
                      self.y_start + self.KEY_HEIGHT + self.KEY_SPACING)
        self.draw_row(self.keyboard_layout[2], (self.x_start - 1.75 * (self.KEY_WIDTH + self.KEY_SPACING)) + self.special_keys["Caps"] + self.KEY_SPACING, 
                      self.y_start + 2 * (self.KEY_HEIGHT + self.KEY_SPACING))
        self.draw_row(self.keyboard_layout[3], (self.x_start - 1.75 * (self.KEY_WIDTH + self.KEY_SPACING)) + self.special_keys["Shift"] + self.KEY_SPACING,
                      self.y_start + 3 * (self.KEY_HEIGHT + self.KEY_SPACING))
        

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
            "Esc": (self.x_start - 1.75 * (self.KEY_WIDTH + self.KEY_SPACING), self.y_start),
            "Backspace": (self.x_start + 10 * (self.KEY_WIDTH + self.KEY_SPACING), self.y_start),
            "Tab": (self.x_start - 1.75 * (self.KEY_WIDTH + self.KEY_SPACING), 
                    self.y_start + self.KEY_HEIGHT + self.KEY_SPACING),
            "Caps": (self.x_start - 1.75 * (self.KEY_WIDTH + self.KEY_SPACING), 
                     self.y_start + 2 * (self.KEY_HEIGHT + self.KEY_SPACING)),
            "Enter": (self.x_start + 11 * (self.KEY_WIDTH + self.KEY_SPACING), 
                      self.y_start + 2 * (self.KEY_HEIGHT + self.KEY_SPACING)),
            "Shift": (self.x_start - 1.75 * (self.KEY_WIDTH + self.KEY_SPACING), 
                      self.y_start + 3 * (self.KEY_HEIGHT + self.KEY_SPACING)),
            "Space": (self.x_start + 2.5 * (self.KEY_WIDTH + self.KEY_SPACING), 
                      self.y_start + 4 * (self.KEY_HEIGHT + self.KEY_SPACING)),
            "Ctrl": (self.x_start - 1.75 * (self.KEY_WIDTH + self.KEY_SPACING),
                      self.y_start + 4 * (self.KEY_HEIGHT + self.KEY_SPACING)),
            "Win": ((self.x_start - 1.75 * (self.KEY_WIDTH + self.KEY_SPACING)) + self.special_keys["Ctrl"] + 1 * self.KEY_SPACING,
                      self.y_start + 4 * (self.KEY_HEIGHT + self.KEY_SPACING)),
            "Alt": ((self.x_start - 1.75 * (self.KEY_WIDTH + self.KEY_SPACING)) + self.special_keys["Ctrl"] + self.special_keys["Win"] + 2 * self.KEY_SPACING,
                      self.y_start + 4 * (self.KEY_HEIGHT + self.KEY_SPACING))
        }

        for key, (x, y) in special_key_positions.items():
            width = self.special_keys[key]
            self.draw_key(x, y, width, self.KEY_HEIGHT, key)

    def highlight_key(self, label):
        # Change the color of the rectangle associated with the given label to red
        if label in self.inverse_mqtt_mappings:
            label = self.inverse_mqtt_mappings[label]
        elif label in self.key_mappings:
            label = self.key_mappings[label]

        if label in self.key_rects:
            rect_id = self.key_rects[label]
            self.canvas.itemconfig(rect_id, fill="green")

    def reset_key(self, label):
        # Reset the color of the key to lightgrey
        if label in self.inverse_mqtt_mappings:
            label = self.inverse_mqtt_mappings[label]
        elif label in self.key_mappings:
            label = self.key_mappings[label]
        
        if label in self.key_rects:
            rect_id = self.key_rects[label]
            self.canvas.itemconfig(rect_id, fill="lightgrey")
    
    def bind_keys(self):
        self.root.bind("<KeyPress>", self.on_key_press)
        self.root.bind("<Tab>", self.on_key_press)
        self.root.bind("<Control-KeyPress>", self.on_key_press)
        self.root.bind("<Alt-KeyPress>", self.on_key_press)
        self.root.bind("<Shift-KeyPress>", self.on_key_press)
        self.root.bind("<Control-KeyRelease>", self.on_key_release)
        self.root.bind("<Alt-KeyRelease>", self.on_key_release)
        self.root.bind("<Shift-KeyRelease>", self.on_key_release)
        self.root.bind("<KeyRelease>", self.on_key_release)

    def unbind_keys(self):
        self.root.unbind("<KeyPress>", self.on_key_press)
        self.root.unbind("<Tab>", self.on_key_press)
        self.root.unbind("<Control-KeyPress>", self.on_key_press)
        self.root.unbind("<Alt-KeyPress>", self.on_key_press)
        self.root.unbind("<Shift-KeyPress>", self.on_key_press)
        self.root.unbind("<Control-KeyRelease>", self.on_key_release)
        self.root.unbind("<Alt-KeyRelease>", self.on_key_release)
        self.root.unbind("<Shift-KeyRelease>", self.on_key_release)
        self.root.unbind("<KeyRelease>", self.on_key_release)

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

        action_label = label
        if label in self.mqtt_mappings:
            action_label = self.mqtt_mappings[label]

        action = (elapsed_time, action_label, mode)
        formatted = label

        if len(label) == 1 and label >= 'A' and label <= 'Z':
            formatted = formatted if ("SHIFT_L" in self.current_pressed or "SHIFT_R" in self.current_pressed or self.caps_pressed) else formatted.lower()

        if label in self.key_mappings and self.key_mappings[label] in self.special_keys:
            formatted = ""

            if label == "SPACE":
                formatted = " "
            elif label == "RETURN":
                formatted = "\n"
            elif label == "BACKSPACE":
                formatted = None
            elif label == "PERIOD":
                formatted = "."
            elif label == "COMMA":
                formatted = ","

        self.action_registered[label] = (mode, now)
        if self.handler_func != None:
            self.handler_func(action, formatted)

        self.last_action_timestamp = now

    def press_key(self, label):
        self.register_action(label, "p")

    def release_key(self, label):
        self.reset_key(label)
        self.register_action(label, "r")
        self.current_pressed.remove(label)

    def on_key_press(self, event):
        label = event.keysym.upper()
        self.label_pressed(label)

    def on_key_release(self, event):
        label = event.keysym.upper()
        self.label_released(label)

    def label_pressed(self, label):
        print("CURRENT_PRESSED: ", self.current_pressed)

        if label in self.key_timers:
            self.root.after_cancel(self.key_timers[label])
            del self.key_timers[label]
        if label not in self.current_pressed:
            self.highlight_key(label)
            self.current_pressed.append(label)
            if label == "CAPS_LOCK":
                self.caps_pressed = not self.caps_pressed
        self.press_key(label)

    def label_released(self, label):
        if label not in self.current_pressed:
            return
        self.key_timers[label] = self.root.after(50, lambda: self.release_key(label))
    
    def get_mapped(self, label):
        if label in self.key_mappings:
            label = self.key_mappings
        return label
