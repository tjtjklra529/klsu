"""
KLSU IDE - Main GUI Application
"""
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from pathlib import Path
import os
from typing import Dict, List

from src.lexer import Lexer
from src.parser import Parser
from src.interpreter import Interpreter, KLSUError
from src.syntax_highlighter import SyntaxHighlighter

class KLSUIDEApplication:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Keychain Language Somewhat Understandable Full Colour Coded - KLSU")
        self.root.geometry("1200x700")
        self.root.minsize(800, 500)
        
        self.open_files: Dict[str, str] = {}  # filename -> content
        self.current_file = None
        self.output_lines: List[str] = []
        
        self.setup_ui()
        self.setup_menu()
        self.setup_keybindings()
    
    def setup_ui(self):
        """Setup main UI layout"""
        # Main container
        main_container = ttk.PanedWindow(self.root, orient=tk.HORIZONTAL)
        main_container.pack(fill=tk.BOTH, expand=True)
        
        # Left pane - Editor
        left_pane = ttk.Frame(main_container)
        main_container.add(left_pane, weight=3)
        
        # Tabs for open files
        self.notebook = ttk.Notebook(left_pane)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Right pane - Panels
        right_container = ttk.PanedWindow(self.root, orient=tk.VERTICAL)
        main_container.add(right_container, weight=1)
        
        # Interactables Panel
        interactables_frame = ttk.LabelFrame(right_container, text="Interactables", padding=5)
        right_container.add(interactables_frame, weight=1)
        
        self.interactables_text = tk.Text(interactables_frame, height=10, width=30, bg='#1e1e1e', fg='#00ffff')
        self.interactables_text.pack(fill=tk.BOTH, expand=True)
        
        # Output Panel
        output_frame = ttk.LabelFrame(right_container, text="Output", padding=5)
        right_container.add(output_frame, weight=1)
        
        self.output_text = tk.Text(output_frame, height=10, width=30, bg='#000000', fg='#00ff00')
        self.output_text.pack(fill=tk.BOTH, expand=True)
        
        # Status bar
        self.status_var = tk.StringVar(value="Ready")
        status_bar = ttk.Label(self.root, textvariable=self.status_var, relief=tk.SUNKEN)
        status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        
        self.create_new_tab()
    
    def setup_menu(self):
        """Setup menu bar"""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # File Menu
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="New File (Ctrl+N)", command=self.new_file)
        file_menu.add_command(label="Open (Ctrl+O)", command=self.open_file)
        file_menu.add_command(label="Save (Ctrl+S)", command=self.save_file)
        file_menu.add_command(label="Save As (Ctrl+Shift+S)", command=self.save_file_as)
        file_menu.add_command(label="Close Tab (Ctrl+W)", command=self.close_tab)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)
        
        # Edit Menu
        edit_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Edit", menu=edit_menu)
        edit_menu.add_command(label="Undo (Ctrl+Z)", command=self.undo)
        edit_menu.add_command(label="Redo (Ctrl+Shift+Z)", command=self.redo)
        
        # Run Menu
        run_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Run", menu=run_menu)
        run_menu.add_command(label="Run Current Tab (Ctrl+Alt+R)", command=self.run_current)
        run_menu.add_command(label="Debug (Ctrl+R)", command=self.debug)
        run_menu.add_command(label="Run and Debug (Ctrl+Fn+R)", command=self.run_and_debug)
        
        # View Menu
        view_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="View", menu=view_menu)
        view_menu.add_command(label="Toggle Interactables (Ctrl+Alt+V I)", command=self.toggle_interactables)
        view_menu.add_command(label="Toggle Output (Ctrl+Alt+V O)", command=self.toggle_output)
        view_menu.add_command(label="Toggle Tabs Bar (Ctrl+Alt+V T)", command=self.toggle_tabs)
        view_menu.add_command(label="Toggle Colour Coding (Ctrl+Alt+V C)", command=self.toggle_syntax)
    
    def setup_keybindings(self):
        """Setup keyboard shortcuts"""
        self.root.bind('<Control-n>', lambda e: self.new_file())
        self.root.bind('<Control-o>', lambda e: self.open_file())
        self.root.bind('<Control-s>', lambda e: self.save_file())
        self.root.bind('<Control-Shift-S>', lambda e: self.save_file_as())
        self.root.bind('<Control-w>', lambda e: self.close_tab())
        self.root.bind('<Control-z>', lambda e: self.undo())
        self.root.bind('<Control-Shift-Z>', lambda e: self.redo())
        self.root.bind('<Control-Alt-r>', lambda e: self.run_current())
        self.root.bind('<Control-r>', lambda e: self.debug())
    
    def create_new_tab(self, filename: str = None):
        """Create a new editor tab"""
        tab_frame = ttk.Frame(self.notebook)
        
        # Text editor with scrollbar
        scrollbar = ttk.Scrollbar(tab_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        text_widget = tk.Text(tab_frame, yscrollcommand=scrollbar.set, font=('Consolas', 11), 
                             bg='#1e1e1e', fg='#e0e0e0', insertbackground='white')
        text_widget.pack(fill=tk.BOTH, expand=True)
        scrollbar.config(command=text_widget.yview)
        
        # Syntax highlighting
        highlighter = SyntaxHighlighter(text_widget)
        text_widget.bind('<<Change>>', highlighter.highlight)
        text_widget.bind('<KeyRelease>', highlighter.highlight)
        
        tab_label = filename or f"Untitled-{len(self.open_files) + 1}.klsu"
        self.notebook.add(tab_frame, text=tab_label)
        
        self.open_files[tab_label] = ""
        self.current_file = tab_label
        
        return text_widget
    
    def get_current_editor(self) -> tk.Text:
        """Get current editor widget"""
        current_tab = self.notebook.select()
        if current_tab:
            tab_frame = self.notebook.nametowidget(current_tab)
            for child in tab_frame.winfo_children():
                if isinstance(child, tk.Text):
                    return child
        return None
    
    def new_file(self):
        """Create new file"""
        self.create_new_tab()
    
    def open_file(self):
        """Open KLSU file"""
        filepath = filedialog.askopenfilename(filetypes=[("KLSU files", "*.klsu"), ("All files", "*.*")])
        if filepath:
            try:
                with open(filepath, 'r') as f:
                    content = f.read()
                
                filename = Path(filepath).name
                editor = self.create_new_tab(filename)
                editor.insert('1.0', content)
                self.open_files[filename] = filepath
                self.status_var.set(f"Opened: {filename}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to open file: {e}")
    
    def save_file(self):
        """Save current file"""
        editor = self.get_current_editor()
        if editor and self.current_file:
            content = editor.get('1.0', tk.END)
            filepath = self.open_files.get(self.current_file)
            
            if filepath:
                try:
                    with open(filepath, 'w') as f:
                        f.write(content)
                    self.status_var.set(f"Saved: {self.current_file}")
                except Exception as e:
                    messagebox.showerror("Error", f"Failed to save file: {e}")
            else:
                self.save_file_as()
    
    def save_file_as(self):
        """Save file with new name"""
        editor = self.get_current_editor()
        if editor:
            filepath = filedialog.asksaveasfilename(defaultextension=".klsu", filetypes=[("KLSU files", "*.klsu"), ("All files", "*.*")])
            if filepath:
                content = editor.get('1.0', tk.END)
                try:
                    with open(filepath, 'w') as f:
                        f.write(content)
                    
                    old_name = self.current_file
                    new_name = Path(filepath).name
                    self.open_files[new_name] = filepath
                    del self.open_files[old_name]
                    self.current_file = new_name
                    
                    current_tab = self.notebook.select()
                    self.notebook.tab(current_tab, text=new_name)
                    
                    self.status_var.set(f"Saved as: {new_name}")
                except Exception as e:
                    messagebox.showerror("Error", f"Failed to save file: {e}")
    
    def close_tab(self):
        """Close current tab"""
        if self.notebook.tabs():
            current_tab = self.notebook.select()
            tab_name = self.notebook.tab(current_tab, 'text')
            self.notebook.forget(current_tab)
            
            if tab_name in self.open_files:
                del self.open_files[tab_name]
            
            if self.notebook.tabs():
                self.current_file = self.notebook.tab(self.notebook.select(), 'text')
    
    def run_current(self):
        """Run current tab"""
        editor = self.get_current_editor()
        if editor:
            code = editor.get('1.0', tk.END)
            self.output_text.config(state=tk.NORMAL)
            self.output_text.delete('1.0', tk.END)
            
            try:
                self.execute_klsu(code)
                self.status_var.set("Execution completed")
            except KLSUError as e:
                self.output_text.insert(tk.END, f"KLSU Error: {e}\n")
                self.status_var.set(f"Error: {e}")
            except Exception as e:
                self.output_text.insert(tk.END, f"Error: {e}\n")
                self.status_var.set(f"Error: {e}")
    
    def debug(self):
        """Debug mode"""
        self.status_var.set("Debug mode (not yet implemented)")
    
    def run_and_debug(self):
        """Run and debug"""
        self.status_var.set("Run and Debug (not yet implemented)")
    
    def execute_klsu(self, code: str):
        """Execute KLSU code"""
        # Lex
        lexer = Lexer(code)
        tokens = lexer.tokenize()
        
        # Parse
        parser = Parser(tokens)
        ast = parser.parse()
        
        # Interpret
        def output_callback(text):
            self.output_text.config(state=tk.NORMAL)
            self.output_text.insert(tk.END, str(text) + '\n')
            self.output_text.see(tk.END)
        
        def input_callback(prompt):
            # For now, use messagebox
            return tk.simpledialog.askstring("Input", prompt)
        
        interpreter = Interpreter(output_callback=output_callback, input_callback=input_callback)
        interpreter.execute(ast)
    
    def undo(self):
        """Undo action"""
        editor = self.get_current_editor()
        if editor:
            try:
                editor.edit_undo()
            except:
                pass
    
    def redo(self):
        """Redo action"""
        editor = self.get_current_editor()
        if editor:
            try:
                editor.edit_redo()
            except:
                pass
    
    def toggle_interactables(self):
        """Toggle interactables panel visibility"""
        pass
    
    def toggle_output(self):
        """Toggle output panel visibility"""
        pass
    
    def toggle_tabs(self):
        """Toggle tabs visibility"""
        pass
    
    def toggle_syntax(self):
        """Toggle syntax highlighting"""
        pass
    
    def run(self):
        """Start the application"""
        self.root.mainloop()
