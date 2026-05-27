# KLSU - Keychain Language Somewhat Understandable

A beginner-friendly programming language with a Tkinter-based IDE.

## Features

- **Simple Syntax**: Readable, natural language-like code
- **Colour-Coded IDE**: Full syntax highlighting
- **GUI Support**: Built-in window, button, label, and textbox creation
- **Sample Games**: Pre-loaded games to explore
- **Interactive Console**: Real-time output and input

## Installation

```bash
git clone https://github.com/tjtjklra529/klsu.git
cd klsu
pip install -r requirements.txt
```

## Running the IDE

```bash
python main.py
```

## Creating Your First Program

Here's a simple "Hello World" in KLSU:

```klsu
print:Hello_World
```

Or with variables:

```klsu
+name is Alice
print:Hello_v;name
```

## Language Basics

### Variables

```klsu
+variableName is value
```

### Integers

```klsu
+age is i;25
```

### Input

```klsu
input:username]]]Enter_your_username
print:Hello_v;username
```

### Conditionals

```klsu
if v;age > i;18 then expect'
+-> print:You_are_an_adult
```

### Loops

```klsu
|||5
+-> print:This_repeats_5_times
```

### Functions

```klsu
definition of greet is'
+-> print:Welcome_to_KLSU

run:greet
```

## File Association (Windows)

To associate `.klsu` files with the IDE:

1. Run the included `setup.reg` file
2. Or manually create registry entry:
   - `HKEY_CLASSES_ROOT\.klsu` = `klsu_file`
   - `HKEY_CLASSES_ROOT\klsu_file\shell\open\command` = `path/to/klsu_ide.exe "%1"`

## Packaging as .exe

```bash
pip install pyinstaller
pyinstaller --onefile --windowed --add-data "games:games" main.py
```

Your executable will be in the `dist/` folder.

## Keyboard Shortcuts

- `Ctrl+N`: New File
- `Ctrl+O`: Open File
- `Ctrl+S`: Save
- `Ctrl+Shift+S`: Save As
- `Ctrl+W`: Close Tab
- `Ctrl+Z`: Undo
- `Ctrl+Shift+Z`: Redo
- `Ctrl+Alt+R`: Run
- `Ctrl+R`: Debug

## License

MIT License
