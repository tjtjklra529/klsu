"""
KLSU Parser - Builds AST from tokens
"""
from dataclasses import dataclass
from typing import List, Optional, Union
from enum import Enum, auto
from src.lexer import Token, TokenType, Lexer

class ASTNodeType(Enum):
    PROGRAM = auto()
    VARIABLE_DECL = auto()
    PRINT = auto()
    INPUT = auto()
    IF = auto()
    LOOP = auto()
    FUNCTION_DEF = auto()
    FUNCTION_CALL = auto()
    WINDOW_OPEN = auto()
    BUTTON = auto()
    LABEL = auto()
    TEXTBOX = auto()
    WINDOW_ELEMENT = auto()
    THREE_D_ELEMENT = auto()
    BINARY_OP = auto()
    LITERAL = auto()
    VARIABLE_REF = auto()

@dataclass
class ASTNode:
    type: ASTNodeType
    value: any
    children: List['ASTNode'] = None
    metadata: dict = None
    
    def __post_init__(self):
        if self.children is None:
            self.children = []
        if self.metadata is None:
            self.metadata = {}

class Parser:
    def __init__(self, tokens: List[Token]):
        self.tokens = tokens
        self.position = 0
    
    def parse(self) -> ASTNode:
        """Parse tokens into AST"""
        statements = []
        
        while not self._is_at_end():
            stmt = self._parse_statement()
            if stmt:
                statements.append(stmt)
        
        return ASTNode(ASTNodeType.PROGRAM, None, statements)
    
    def _parse_statement(self) -> Optional[ASTNode]:
        """Parse a single statement"""
        token = self._peek()
        
        if token.type == TokenType.VARIABLE:
            # Variable declaration
            var_name = token.value
            self._advance()  # consume variable
            
            if self._peek().type == TokenType.IS:
                self._advance()  # consume 'is'
                value = self._parse_expression()
                return ASTNode(ASTNodeType.VARIABLE_DECL, var_name, [value] if value else [])
        
        elif token.type == TokenType.PRINT:
            self._advance()
            if self._peek().type == TokenType.COLON:
                self._advance()
                content = self._parse_expression()
                return ASTNode(ASTNodeType.PRINT, None, [content] if content else [])
        
        elif token.type == TokenType.INPUT:
            self._advance()
            if self._peek().type == TokenType.COLON:
                self._advance()
                var_name = self._parse_expression()
                if self._peek().type == TokenType.SEPARATOR:
                    self._advance()
                    prompt = self._parse_expression()
                    return ASTNode(ASTNodeType.INPUT, None, [var_name, prompt] if var_name and prompt else [])
        
        elif token.type == TokenType.IF:
            return self._parse_if()
        
        elif token.type == TokenType.LOOP:
            return self._parse_loop()
        
        elif token.type == TokenType.DEFINITION:
            return self._parse_function_def()
        
        elif token.type == TokenType.RUN:
            self._advance()
            if self._peek().type == TokenType.COLON:
                self._advance()
                func_name = self._parse_expression()
                return ASTNode(ASTNodeType.FUNCTION_CALL, None, [func_name] if func_name else [])
        
        elif token.type == TokenType.OPENWINDOW:
            return self._parse_window_open()
        
        elif token.type == TokenType.BUTTON:
            return self._parse_button()
        
        elif token.type == TokenType.LABEL:
            return self._parse_label()
        
        elif token.type == TokenType.TEXTBOX:
            return self._parse_textbox()
        
        self._advance()
        return None
    
    def _parse_if(self) -> ASTNode:
        """Parse if statement"""
        self._advance()  # consume 'if'
        
        condition = self._parse_condition()
        
        if self._peek().type == TokenType.THEN:
            self._advance()
            if self._peek().type == TokenType.EXPECT:
                self._advance()
                # Parse block
                block = self._parse_block()
                return ASTNode(ASTNodeType.IF, None, [condition] + block)
        
        return None
    
    def _parse_condition(self) -> Optional[ASTNode]:
        """Parse conditional expression"""
        left = self._parse_expression()
        
        op_token = self._peek()
        if op_token.type in (TokenType.EQUAL, TokenType.NOT_EQUAL, TokenType.GREATER, TokenType.LESS, TokenType.GREATER_EQUAL, TokenType.LESS_EQUAL):
            self._advance()
            right = self._parse_expression()
            return ASTNode(ASTNodeType.BINARY_OP, op_token.value, [left, right] if left and right else [])
        
        return left
    
    def _parse_loop(self) -> ASTNode:
        """Parse loop statement"""
        self._advance()  # consume '|||'
        
        # Get loop count
        count_token = self._peek()
        count = 0
        if count_token.type == TokenType.INTEGER:
            count = count_token.value
            self._advance()
        
        # Parse block
        block = self._parse_block()
        
        return ASTNode(ASTNodeType.LOOP, count, block)
    
    def _parse_function_def(self) -> ASTNode:
        """Parse function definition"""
        self._advance()  # consume 'definition'
        
        if self._peek().type == TokenType.OF:
            self._advance()
            func_name_token = self._peek()
            func_name = func_name_token.value if func_name_token.type == TokenType.STRING else ''
            self._advance()
            
            if self._peek().type == TokenType.IS:
                self._advance()
                if self._peek().type == TokenType.EXPECT:
                    self._advance()
                    block = self._parse_block()
                    return ASTNode(ASTNodeType.FUNCTION_DEF, func_name, block)
        
        return None
    
    def _parse_window_open(self) -> ASTNode:
        """Parse openWindow statement"""
        self._advance()  # consume 'openWindow'
        
        if self._peek().type == TokenType.COLON:
            self._advance()
            # Parse dimensions
            width = self._parse_expression()
            
            if self._peek().type == TokenType.BY:
                self._advance()
                height = self._parse_expression()
                
                title = ''
                if self._peek().type == TokenType.AND:
                    self._advance()
                    title_node = self._parse_expression()
                    title = title_node.value if title_node else ''
                
                return ASTNode(ASTNodeType.WINDOW_OPEN, None, [width, height], {'title': title})
        
        return None
    
    def _parse_button(self) -> ASTNode:
        """Parse button creation"""
        self._advance()
        if self._peek().type == TokenType.COLON:
            self._advance()
            # Parse width
            width = self._parse_expression()
            if self._peek().type == TokenType.BY:
                self._advance()
                height = self._parse_expression()
                if self._peek().type == TokenType.AT:
                    self._advance()
                    x = self._parse_expression()
                    if self._peek().type == TokenType.COMMA:
                        self._advance()
                        y = self._parse_expression()
                        return ASTNode(ASTNodeType.BUTTON, None, [width, height, x, y])
        return None
    
    def _parse_label(self) -> ASTNode:
        """Parse label creation"""
        self._advance()
        if self._peek().type == TokenType.COLON:
            self._advance()
            font = self._parse_expression()
            if self._peek().type == TokenType.AND:
                self._advance()
                size = self._parse_expression()
                if self._peek().type == TokenType.AND:
                    self._advance()
                    color = self._parse_expression()
                    if self._peek().type == TokenType.AND:
                        self._advance()
                        text = self._parse_expression()
                        return ASTNode(ASTNodeType.LABEL, None, [font, size, color, text])
        return None
    
    def _parse_textbox(self) -> ASTNode:
        """Parse textbox creation"""
        self._advance()
        if self._peek().type == TokenType.COLON:
            self._advance()
            elements = []
            while not self._is_at_end() and self._peek().type == TokenType.AND:
                self._advance()
                elem = self._parse_expression()
                if elem:
                    elements.append(elem)
            return ASTNode(ASTNodeType.TEXTBOX, None, elements)
        return None
    
    def _parse_block(self) -> List[ASTNode]:
        """Parse indented block"""
        block = []
        
        while not self._is_at_end() and self._peek().type == TokenType.INDENT:
            self._advance()  # consume '+->' 
            stmt = self._parse_statement()
            if stmt:
                block.append(stmt)
        
        return block
    
    def _parse_expression(self) -> Optional[ASTNode]:
        """Parse expression"""
        token = self._peek()
        
        if token.type == TokenType.INTEGER:
            self._advance()
            return ASTNode(ASTNodeType.LITERAL, token.value)
        
        elif token.type == TokenType.VARIABLE:
            self._advance()
            return ASTNode(ASTNodeType.VARIABLE_REF, token.value)
        
        elif token.type == TokenType.STRING:
            self._advance()
            # Handle underscore to space conversion
            value = token.value.replace('_', ' ')
            return ASTNode(ASTNodeType.LITERAL, value)
        
        elif token.type == TokenType.TRUE:
            self._advance()
            return ASTNode(ASTNodeType.LITERAL, True)
        
        elif token.type == TokenType.FALSE:
            self._advance()
            return ASTNode(ASTNodeType.LITERAL, False)
        
        return None
    
    def _peek(self, offset=0) -> Token:
        """Look at token without consuming"""
        pos = self.position + offset
        if pos < len(self.tokens):
            return self.tokens[pos]
        return self.tokens[-1]  # Return EOF
    
    def _advance(self):
        """Move position forward"""
        if self.position < len(self.tokens) - 1:
            self.position += 1
    
    def _is_at_end(self) -> bool:
        """Check if at end of tokens"""
        return self._peek().type == TokenType.EOF
