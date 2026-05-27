"""
KLSU Lexer - Tokenizes KLSU source code
"""
import re
from enum import Enum, auto
from dataclasses import dataclass
from typing import List, Optional

class TokenType(Enum):
    # Literals
    INTEGER = auto()
    STRING = auto()
    VARIABLE = auto()
    
    # Keywords
    PRINT = auto()
    INPUT = auto()
    IF = auto()
    THEN = auto()
    DEFINITION = auto()
    OF = auto()
    IS = auto()
    RUN = auto()
    EXPECT = auto()
    OPENWINDOW = auto()
    BUTTON = auto()
    LABEL = auto()
    TEXTBOX = auto()
    WINDOW_ELEMENT = auto()
    THREE_D_ELEMENT = auto()
    TRUE = auto()
    FALSE = auto()
    
    # Operators
    EQUAL = auto()
    NOT_EQUAL = auto()
    GREATER = auto()
    LESS = auto()
    GREATER_EQUAL = auto()
    LESS_EQUAL = auto()
    
    # Delimiters
    INDENT = auto()  # +->
    SEPARATOR = auto()  # ]]]
    LOOP = auto()  # |||
    COLON = auto()  # :
    BY = auto()  # by
    AND = auto()  # and
    AT = auto()  # at
    COMMA = auto()  # ,
    
    # Special
    EOF = auto()
    NEWLINE = auto()
    COMMENT = auto()

@dataclass
class Token:
    type: TokenType
    value: any
    line: int
    column: int

class Lexer:
    def __init__(self, source: str):
        self.source = source
        self.position = 0
        self.line = 1
        self.column = 1
        self.tokens: List[Token] = []
        self.current_indent_level = 0
    
    def tokenize(self) -> List[Token]:
        """Convert source code into tokens"""
        while self.position < len(self.source):
            self._skip_whitespace_and_comments()
            
            if self.position >= len(self.source):
                break
            
            if self._peek() == '\n':
                self._advance()
                self.line += 1
                self.column = 1
                continue
            
            # Check for indentation (+->) 
            if self._check_sequence('+->'):
                self.tokens.append(Token(TokenType.INDENT, '+->', self.line, self.column))
                self._advance_by(3)
                continue
            
            # Check for loop (|||)
            if self._check_sequence('|||'):
                self.tokens.append(Token(TokenType.LOOP, '|||', self.line, self.column))
                self._advance_by(3)
                # Get the number after loop
                num = self._read_number()
                if num:
                    self.tokens.append(Token(TokenType.INTEGER, int(num), self.line, self.column))
                continue
            
            # Check for operators
            if self._check_sequence('/\\/'):
                self.tokens.append(Token(TokenType.GREATER_EQUAL, '/\\/', self.line, self.column))
                self._advance_by(3)
                continue
            
            if self._check_sequence('//\\'):
                self.tokens.append(Token(TokenType.LESS_EQUAL, '//\\', self.line, self.column))
                self._advance_by(3)
                continue
            
            if self._check_sequence('=='):
                self.tokens.append(Token(TokenType.EQUAL, '==', self.line, self.column))
                self._advance_by(2)
                continue
            
            if self._check_sequence('¦¦'):
                self.tokens.append(Token(TokenType.NOT_EQUAL, '¦¦', self.line, self.column))
                self._advance_by(2)
                continue
            
            if self._check_sequence(']]]'):
                self.tokens.append(Token(TokenType.SEPARATOR, ']]]', self.line, self.column))
                self._advance_by(3)
                continue
            
            # Single character tokens
            if self._peek() == '>':
                self.tokens.append(Token(TokenType.GREATER, '>', self.line, self.column))
                self._advance()
                continue
            
            if self._peek() == '<':
                self.tokens.append(Token(TokenType.LESS, '<', self.line, self.column))
                self._advance()
                continue
            
            if self._peek() == ':':
                self.tokens.append(Token(TokenType.COLON, ':', self.line, self.column))
                self._advance()
                continue
            
            if self._peek() == ',':
                self.tokens.append(Token(TokenType.COMMA, ',', self.line, self.column))
                self._advance()
                continue
            
            # Integer literal (i;42)
            if self._check_sequence('i;'):
                self._advance_by(2)
                num = self._read_number()
                if num:
                    self.tokens.append(Token(TokenType.INTEGER, int(num), self.line, self.column - len(num) - 2))
                continue
            
            # Variable reference (v;varname)
            if self._check_sequence('v;'):
                self._advance_by(2)
                varname = self._read_identifier()
                if varname:
                    self.tokens.append(Token(TokenType.VARIABLE, varname, self.line, self.column - len(varname) - 2))
                continue
            
            # Variable declaration (+varname)
            if self._peek() == '+' and self.position + 1 < len(self.source) and self.source[self.position + 1].isalpha():
                self._advance()
                varname = self._read_identifier()
                if varname:
                    self.tokens.append(Token(TokenType.VARIABLE, '+' + varname, self.line, self.column - len(varname) - 1))
                continue
            
            # Escape sequences (¬¬...¬¬)
            if self._check_sequence('¬¬'):
                self._advance_by(2)
                escaped = self._read_until('¬¬')
                if escaped:
                    self.tokens.append(Token(TokenType.STRING, escaped, self.line, self.column - len(escaped) - 4))
                continue
            
            # Keywords and identifiers
            if self._peek().isalpha() or self._peek() == '_':
                word = self._read_identifier()
                token_type = self._get_keyword_type(word)
                self.tokens.append(Token(token_type, word, self.line, self.column - len(word)))
                continue
            
            # String (default)
            if self._peek() not in ('\n', ' ', '\t'):
                string_val = self._read_string_until_special()
                if string_val:
                    self.tokens.append(Token(TokenType.STRING, string_val, self.line, self.column - len(string_val)))
                continue
            
            self._advance()
        
        self.tokens.append(Token(TokenType.EOF, None, self.line, self.column))
        return self.tokens
    
    def _peek(self, offset=0) -> Optional[str]:
        """Look at character without consuming"""
        pos = self.position + offset
        if pos < len(self.source):
            return self.source[pos]
        return None
    
    def _advance(self, count=1):
        """Move position forward"""
        for _ in range(count):
            if self.position < len(self.source):
                if self.source[self.position] == '\n':
                    self.line += 1
                    self.column = 1
                else:
                    self.column += 1
                self.position += 1
    
    def _advance_by(self, count: int):
        """Move position forward by count"""
        self._advance(count)
    
    def _check_sequence(self, seq: str) -> bool:
        """Check if sequence matches at current position"""
        return self.source[self.position:self.position+len(seq)] == seq
    
    def _read_number(self) -> Optional[str]:
        """Read integer from current position"""
        start = self.position
        while self.position < len(self.source) and self.source[self.position].isdigit():
            self._advance()
        return self.source[start:self.position]
    
    def _read_identifier(self) -> str:
        """Read identifier (variable name, keyword)"""
        start = self.position
        while self.position < len(self.source) and (self.source[self.position].isalnum() or self.source[self.position] == '_'):
            self._advance()
        return self.source[start:self.position]
    
    def _read_string_until_special(self) -> str:
        """Read string until special character or newline"""
        start = self.position
        while self.position < len(self.source):
            ch = self._peek()
            if ch in ('\n', ':', ',', ' ') or self._check_sequence(']]') or self._check_sequence('¬¬'):
                break
            self._advance()
        return self.source[start:self.position]
    
    def _read_until(self, delimiter: str) -> str:
        """Read until delimiter"""
        start = self.position
        while self.position < len(self.source) and not self._check_sequence(delimiter):
            self._advance()
        result = self.source[start:self.position]
        self._advance_by(len(delimiter))
        return result
    
    def _skip_whitespace_and_comments(self):
        """Skip whitespace and comments"""
        while self.position < len(self.source):
            if self.source[self.position] in (' ', '\t'):
                self._advance()
            elif self._check_sequence('~~'):
                # Comment - skip until end of line
                while self.position < len(self.source) and self._peek() != '\n':
                    self._advance()
            else:
                break
    
    def _get_keyword_type(self, word: str) -> TokenType:
        """Determine token type for keyword"""
        keywords = {
            'print': TokenType.PRINT,
            'input': TokenType.INPUT,
            'if': TokenType.IF,
            'then': TokenType.THEN,
            'expect': TokenType.EXPECT,
            'definition': TokenType.DEFINITION,
            'of': TokenType.OF,
            'is': TokenType.IS,
            'run': TokenType.RUN,
            'openWindow': TokenType.OPENWINDOW,
            'button': TokenType.BUTTON,
            'label': TokenType.LABEL,
            'textbox': TokenType.TEXTBOX,
            'windowElement': TokenType.WINDOW_ELEMENT,
            '3dElement': TokenType.THREE_D_ELEMENT,
            'true': TokenType.TRUE,
            'false': TokenType.FALSE,
            'by': TokenType.BY,
            'and': TokenType.AND,
            'at': TokenType.AT,
        }
        return keywords.get(word, TokenType.STRING)
