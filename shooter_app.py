import os
import runpy
import sys

import pygame  # Keeps pygame bundled when PyInstaller analyzes this launcher.


def resource_path(relative_path):
    base_path = getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_path, relative_path)


if "--editor" in sys.argv:
    runpy.run_path(resource_path("level_editor.py"), run_name="__main__")
else:
    runpy.run_path(resource_path("shooter_game_my.py"), run_name="__main__")
