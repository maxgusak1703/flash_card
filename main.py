# main.py

import sys
import os

try:
    import gi
    gi.require_version('Gtk', '4.0')
    gi.require_version('Adw', '1')
    from gi.repository import Gtk, Adw, Gio, Gdk 
except ImportError:
    print("Помилка: Не знайдено PyGObject. Перевірте встановлення.")
    sys.exit(1)

project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.append(project_root)

from ui.windows import App

if __name__ == "__main__":
    app = App()
    app.run(sys.argv)