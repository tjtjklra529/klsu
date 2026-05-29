"""
KLSU Window Manager - Handles GUI window creation and elements
"""
import tkinter as tk
from tkinter import ttk
from typing import Dict, List, Optional, Callable

class WindowManager:
    def __init__(self):
        self.windows: Dict[str, tk.Toplevel] = {}
        self.active_window: Optional[tk.Toplevel] = None
        self.window_counter = 0
        self.elements: Dict[str, List] = {}
    
    def create_window(self, width: int, height: int, title: str = None) -> str:
        """Create a new window"""
        if title is None:
            title = f'NewWindow{self.window_counter:02d}'
        
        window = tk.Toplevel()
        window.geometry(f"{width}x{height}")
        window.title(title)
        
        window_id = f"window_{self.window_counter}"
        self.window_counter += 1
        
        self.windows[window_id] = window
        self.active_window = window
        self.elements[window_id] = []
        
        return window_id
    
    def add_button(self, window_id: str, x: int, y: int, width: int, height: int, text: str = "Button", command: Callable = None) -> tk.Button:
        """Add button to window"""
        if window_id not in self.windows:
            raise ValueError(f"Window {window_id} not found")
        
        window = self.windows[window_id]
        button = tk.Button(window, text=text, command=command, bg='#0078d4', fg='white', font=('Arial', 10))
        button.place(x=x, y=y, width=width, height=height)
        self.elements[window_id].append(('button', button))
        return button
    
    def add_label(self, window_id: str, x: int, y: int, text: str = "", font: str = "Arial", size: int = 12, color: str = "black") -> tk.Label:
        """Add label to window"""
        if window_id not in self.windows:
            raise ValueError(f"Window {window_id} not found")
        
        window = self.windows[window_id]
        label = tk.Label(window, text=text, font=(font, size), fg=color, bg='#f0f0f0')
        label.place(x=x, y=y)
        self.elements[window_id].append(('label', label))
        return label
    
    def add_textbox(self, window_id: str, x: int, y: int, width: int, height: int, font: str = "Consolas", font_size: int = 10, text_color: str = "black", highlight_color: str = "#0078d4", syntax_mode: str = "plaintext") -> tk.Text:
        """Add textbox to window"""
        if window_id not in self.windows:
            raise ValueError(f"Window {window_id} not found")
        
        window = self.windows[window_id]
        frame = tk.Frame(window, bg='#f0f0f0', highlightbackground=highlight_color, highlightthickness=2)
        frame.place(x=x, y=y, width=width, height=height)
        
        scrollbar = ttk.Scrollbar(frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        textbox = tk.Text(frame, font=(font, font_size), fg=text_color, bg='white', yscrollcommand=scrollbar.set)
        textbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=textbox.yview)
        textbox.syntax_mode = syntax_mode
        
        self.elements[window_id].append(('textbox', textbox))
        return textbox
    
    def add_window_element(self, window_id: str, element_type: str, x: int, y: int, width: int, height: int) -> tk.Frame:
        """Add predefined window element"""
        if window_id not in self.windows:
            raise ValueError(f"Window {window_id} not found")
        
        window = self.windows[window_id]
        element_configs = {
            'sidebar': {'bg': '#2d2d2d'},
            'toolbar': {'bg': '#e0e0e0'},
            'mainPanel': {'bg': '#ffffff'},
            'editorPanel': {'bg': '#1e1e1e'},
            'statusBar': {'bg': '#0078d4'},
            'terminalPanel': {'bg': '#000000'},
            'dashboardPanel': {'bg': '#f5f5f5'},
        }
        
        config = element_configs.get(element_type, {'bg': '#ffffff'})
        frame = tk.Frame(window, **config)
        frame.place(x=x, y=y, width=width, height=height)
        self.elements[window_id].append(('windowElement', frame))
        return frame
    
    def add_3d_element(self, window_id: str, element_type: str, x: int, y: int, width: int, height: int) -> tk.Canvas:
        """Add 3D element"""
        if window_id not in self.windows:
            raise ValueError(f"Window {window_id} not found")
        
        window = self.windows[window_id]
        canvas = tk.Canvas(window, width=width, height=height, bg='#000033')
        canvas.place(x=x, y=y)
        self._draw_3d_object(canvas, element_type, width, height)
        self.elements[window_id].append(('3dElement', canvas))
        return canvas
    
    def _draw_3d_object(self, canvas: tk.Canvas, obj_type: str, width: int, height: int):
        """Draw 3D objects"""
        center_x = width // 2
        center_y = height // 2
        
        if obj_type == 'cube':
            self._draw_cube(canvas, center_x, center_y, 50)
        elif obj_type == 'sphere':
            self._draw_sphere(canvas, center_x, center_y, 50)
        elif obj_type == 'spaceship':
            self._draw_spaceship(canvas, center_x, center_y)
        elif obj_type == 'robot':
            self._draw_robot(canvas, center_x, center_y)
        elif obj_type == 'banana':
            self._draw_banana(canvas, center_x, center_y)
        else:
            canvas.create_text(center_x, center_y, text=f"3D: {obj_type}", fill='#00ff00', font=('Arial', 12))
    
    def _draw_cube(self, canvas: tk.Canvas, x: int, y: int, size: int):
        s = size
        canvas.create_rectangle(x-s, y-s, x+s, y+s, outline='#00ff00', width=2)
        canvas.create_rectangle(x-s+20, y-s+20, x+s+20, y+s+20, outline='#00ff00', width=2)
        canvas.create_line(x-s, y-s, x-s+20, y-s+20, fill='#00ff00', width=2)
        canvas.create_line(x+s, y-s, x+s+20, y-s+20, fill='#00ff00', width=2)
        canvas.create_line(x-s, y+s, x-s+20, y+s+20, fill='#00ff00', width=2)
        canvas.create_line(x+s, y+s, x+s+20, y+s+20, fill='#00ff00', width=2)
    
    def _draw_sphere(self, canvas: tk.Canvas, x: int, y: int, radius: int):
        canvas.create_oval(x-radius, y-radius, x+radius, y+radius, outline='#00ff00', width=2)
        for i in range(-radius, radius+1, radius//4):
            canvas.create_line(x+i, y-radius, x+i, y+radius, fill='#00ff00', width=1, dash=(2, 2))
    
    def _draw_spaceship(self, canvas: tk.Canvas, x: int, y: int):
        canvas.create_polygon([x, y-40, x+30, y+40, x-30, y+40], outline='#00ff00', fill='', width=2)
        canvas.create_oval(x-10, y-20, x+10, y, outline='#00ffff', width=2)
    
    def _draw_robot(self, canvas: tk.Canvas, x: int, y: int):
        canvas.create_rectangle(x-20, y-40, x+20, y-10, outline='#00ff00', width=2)
        canvas.create_oval(x-10, y-30, x-5, y-25, fill='#ffff00')
        canvas.create_oval(x+5, y-30, x+10, y-25, fill='#ffff00')
        canvas.create_rectangle(x-25, y-10, x+25, y+30, outline='#00ff00', width=2)
    
    def _draw_banana(self, canvas: tk.Canvas, x: int, y: int):
        canvas.create_arc(x-40, y-30, x+40, y+30, start=0, extent=180, outline='#ffff00', width=8)
