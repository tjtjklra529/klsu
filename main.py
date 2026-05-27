"""
KLSU IDE - Keychain Language Somewhat Understandable
Main Application Entry Point
"""
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from ide_gui import KLSUIDEApplication

if __name__ == '__main__':
    app = KLSUIDEApplication()
    app.run()
