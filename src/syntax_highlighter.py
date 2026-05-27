"""
KLSU Syntax Highlighter for Tkinter Text widget
"""
import tkinter as tk
from typing import Dict, Tuple
import re

class SyntaxHighlighter:
    def __init__(self, text_widget: tk.Text):
        self.text = text_widget
        self.setup_tags()
    
    def setup_tags(self):
        """Configure syntax highlighting colors"""
        # Keywords - brown
        self.text.tag_config('keyword', foreground='#8B4513', font=('Consolas', 11, 'bold'))
        
        # System words - pink
        self.text.tag_config('system', foreground='#FF69B4', font=('Consolas', 11, 'bold'))
        
        # Variables - yellow
        self.text.tag_config('variable', foreground='#FFD700', font=('Consolas', 11))
        
        # Strings - light green
        self.text.tag_config('string', foreground='#90EE90', font=('Consolas', 11))
        
        # Numbers - orange
        self.text.tag_config('number', foreground='#FFA500', font=('Consolas', 11))
        
        # Comments - gray
        self.text.tag_config('comment', foreground='#808080', font=('Consolas', 11, 'italic'))
    
    def highlight(self, event=None):
        """Highlight entire text"""
        # Remove previous highlighting
        for tag in ('keyword', 'system', 'variable', 'string', 'number', 'comment'):
            self.text.tag_remove(tag, '1.0', tk.END)
        
        content = self.text.get('1.0', tk.END)
        
        # Comment highlighting
        for match in re.finditer(r'~~[^~]*~~', content):
            start_idx = self._offset_to_index(match.start())
            end_idx = self._offset_to_index(match.end())
            self.text.tag_add('comment', start_idx, end_idx)
        
        # Keywords
        keywords = ['print', 'input', 'if', 'then', 'definition', 'of', 'is', 'run', 'expect', 'true', 'false']
        for keyword in keywords:
            for match in re.finditer(r'\b' + keyword + r'\b', content):
                start_idx = self._offset_to_index(match.start())
                end_idx = self._offset_to_index(match.end())
                self.text.tag_add('keyword', start_idx, end_idx)
        
        # System words
        system_words = ['openWindow', 'button', 'label', 'textbox', 'windowElement', '3dElement']
        for word in system_words:
            for match in re.finditer(r'\b' + word + r'\b', content):
                start_idx = self._offset_to_index(match.start())
                end_idx = self._offset_to_index(match.end())
                self.text.tag_add('system', start_idx, end_idx)
        
        # Variables (starting with + or v;)
        for match in re.finditer(r'(\+[a-zA-Z_][a-zA-Z0-9_]*|v;[a-zA-Z_][a-zA-Z0-9_]*)', content):
            start_idx = self._offset_to_index(match.start())
            end_idx = self._offset_to_index(match.end())
            self.text.tag_add('variable', start_idx, end_idx)
        
        # Numbers (i;123)
        for match in re.finditer(r'i;\d+', content):
            start_idx = self._offset_to_index(match.start())
            end_idx = self._offset_to_index(match.end())
            self.text.tag_add('number', start_idx, end_idx)
    
    def _offset_to_index(self, offset: int) -> str:
        """Convert character offset to tk index"""
        content = self.text.get('1.0', tk.END)
        line = 1
        col = 0
        
        for i, char in enumerate(content):
            if i == offset:
                return f"{line}.{col}"
            if char == '\n':
                line += 1
                col = 0
            else:
                col += 1
        
        return f"{line}.{col}"
