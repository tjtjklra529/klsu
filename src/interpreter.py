"""
KLSU Interpreter - Executes AST
"""
from typing import Dict, Any, List, Optional, Callable
from src.parser import ASTNode, ASTNodeType
import sys

class KLSUError(Exception):
    """Base KLSU runtime error"""
    pass

class TypeError(KLSUError):
    """Type error"""
    pass

class WindowError(KLSUError):
    """Window-related error"""
    pass

class Interpreter:
    def __init__(self, output_callback: Callable = None, input_callback: Callable = None):
        self.variables: Dict[str, Any] = {}
        self.functions: Dict[str, ASTNode] = {}
        self.output_callback = output_callback or print
        self.input_callback = input_callback or input
        self.active_window = None
        self.window_counter = 0
        self.window_lock = True  # openWindow is locked until definition is made
    
    def execute(self, ast: ASTNode) -> Any:
        """Execute AST"""
        if ast.type == ASTNodeType.PROGRAM:
            result = None
            for child in ast.children:
                result = self.execute(child)
            return result
        
        elif ast.type == ASTNodeType.VARIABLE_DECL:
            var_name = ast.value
            if var_name.startswith('+'):
                var_name = var_name[1:]  # Remove +
            
            value = None
            if ast.children:
                value = self.execute(ast.children[0])
            
            self.variables[var_name] = value
            return value
        
        elif ast.type == ASTNodeType.PRINT:
            output = ''
            if ast.children:
                output = str(self.execute(ast.children[0]))
            self.output_callback(output)
            return output
        
        elif ast.type == ASTNodeType.INPUT:
            if len(ast.children) >= 2:
                var_info = self.execute(ast.children[0])
                prompt = str(self.execute(ast.children[1]))
                
                # Check if input should be integer
                is_integer = isinstance(var_info, str) and var_info.startswith('i;')
                
                try:
                    user_input = self.input_callback(prompt + ' ')
                    
                    if is_integer:
                        try:
                            value = int(user_input)
                        except ValueError:
                            raise TypeError(f"Expected integer input, got '{user_input}'")
                    else:
                        value = user_input
                    
                    # Store in variable
                    var_name = str(ast.children[0].value).replace('v;', '').replace('+', '')
                    self.variables[var_name] = value
                    return value
                except KeyboardInterrupt:
                    return None
        
        elif ast.type == ASTNodeType.IF:
            if len(ast.children) >= 2:
                condition_result = self.execute(ast.children[0])
                
                if self._is_truthy(condition_result):
                    # Execute block
                    for stmt in ast.children[1:]:
                        self.execute(stmt)
        
        elif ast.type == ASTNodeType.LOOP:
            count = ast.value
            if not isinstance(count, int):
                raise TypeError(f"Loop count must be integer, got {type(count).__name__}")
            
            for _ in range(count):
                for stmt in ast.children:
                    self.execute(stmt)
        
        elif ast.type == ASTNodeType.FUNCTION_DEF:
            func_name = ast.value
            self.functions[func_name] = ast
            
            # Special case: openWindow definition
            if func_name == 'openWindow':
                self.window_lock = False
        
        elif ast.type == ASTNodeType.FUNCTION_CALL:
            if ast.children:
                func_name = str(self.execute(ast.children[0]))
                if func_name in self.functions:
                    func_node = self.functions[func_name]
                    for stmt in func_node.children:
                        self.execute(stmt)
        
        elif ast.type == ASTNodeType.WINDOW_OPEN:
            if self.window_lock:
                raise WindowError("Cannot open window without proper initialization")
            
            if len(ast.children) >= 2:
                width = int(self.execute(ast.children[0]))
                height = int(self.execute(ast.children[1]))
                title = ast.metadata.get('title', f'NewWindow{self.window_counter:02d}')
                
                self.window_counter += 1
                self.active_window = {
                    'width': width,
                    'height': height,
                    'title': title,
                    'elements': []
                }
                return self.active_window
        
        elif ast.type == ASTNodeType.BUTTON:
            if not self.active_window:
                raise WindowError("No active window exists")
            
            if len(ast.children) >= 4:
                width = int(self.execute(ast.children[0]))
                height = int(self.execute(ast.children[1]))
                x = int(self.execute(ast.children[2]))
                y = int(self.execute(ast.children[3]))
                
                button = {
                    'type': 'button',
                    'width': width,
                    'height': height,
                    'x': x,
                    'y': y
                }
                self.active_window['elements'].append(button)
                return button
        
        elif ast.type == ASTNodeType.LABEL:
            if not self.active_window:
                raise WindowError("No active window exists")
            
            if len(ast.children) >= 4:
                font = str(self.execute(ast.children[0]))
                size = int(self.execute(ast.children[1]))
                color = str(self.execute(ast.children[2]))
                text = str(self.execute(ast.children[3]))
                
                label = {
                    'type': 'label',
                    'font': font,
                    'size': size,
                    'color': color,
                    'text': text
                }
                self.active_window['elements'].append(label)
                return label
        
        elif ast.type == ASTNodeType.LITERAL:
            return ast.value
        
        elif ast.type == ASTNodeType.VARIABLE_REF:
            var_name = str(ast.value).replace('v;', '').replace('+', '')
            if var_name in self.variables:
                return self.variables[var_name]
            raise NameError(f"Variable '{var_name}' not defined")
        
        elif ast.type == ASTNodeType.BINARY_OP:
            if len(ast.children) >= 2:
                left = self.execute(ast.children[0])
                right = self.execute(ast.children[1])
                op = ast.value
                
                if op == '==':
                    return left == right
                elif op == '¦¦':
                    return left != right
                elif op == '>':
                    return left > right
                elif op == '<':
                    return left < right
                elif op == '/\\/':
                    return left >= right
                elif op == '//\\':
                    return left <= right
        
        return None
    
    def _is_truthy(self, value: Any) -> bool:
        """Determine if value is truthy"""
        if isinstance(value, bool):
            return value
        if isinstance(value, int):
            return value != 0
        if isinstance(value, str):
            return len(value) > 0
        return bool(value)
