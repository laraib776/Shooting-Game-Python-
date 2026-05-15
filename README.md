# Shooting Game Python

![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Pygame](https://img.shields.io/badge/Pygame-2.6.1-2E7D32?style=for-the-badge)
![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20Python-lightgrey?style=for-the-badge)

```text
============================================================
                 2D PYTHON SHOOTER GAME
        Play levels, fight enemies, and edit maps
============================================================
```

A 2D side-scrolling shooter built with Python and Pygame. The project includes the playable game, a level editor, image/audio assets, and CSV-based levels.

## Features

- Playable side-scrolling shooter made with Pygame
- 10 CSV-based levels stored in `levels/`
- Built-in level editor for editing existing levels
- Image and audio assets stored in `shooter_assets/`
- Windows build scripts for folder-app and single-EXE builds
- Clean GitHub setup with `.venv/`, `.vscode/`, build output, and cache files ignored

## Project Layout

```text
Shooting-Game-Python-/
  shooter_game.py              Main game
  shooter_app.py               Launcher for packaging
  level_editor.py              Level editor
  requirements.txt             Python dependencies
  SHOOTER GAME GUIDE.md        Detailed guide

  Downloadable Exe game File/
    shooter_game.exe           Ready-to-run Windows game
    Convert Py file to exe.md  EXE build notes

  shooter_assets/
    img/                       Game images and animations
    audio/                     Music and sound effects

  levels/
    level1_data.csv
    ...
    level10_data.csv

  scripts/
    build_windows.ps1
    build_single_exe.ps1
    build_onefile_windows.ps1
    build_android_wsl.sh

  packaging/
    *.spec
```

## Download The Code

Open the GitHub repo page and choose:

```text
Code -> Download ZIP
```

Then unzip the folder on your computer.

You can also use Git:

```bash
git clone https://github.com/laraib776/Shooting-Game-Python-.git
cd Shooting-Game-Python-
```

## Download And Play On Windows

If you only want to play the game on Windows, open:

```text
Downloadable Exe game File/shooter_game.exe
```

Download that file and run it. You do not need to install Python, Pygame, or any extra packages for the EXE version.

If Windows shows a warning, choose the option to run anyway only if you downloaded it from this repository. Unsigned PyInstaller apps can show warnings on some computers.

## Run The Game From Source

Install Python 3.10 or newer first.

On Windows PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python shooter_game.py
```

To run the level editor:

```powershell
python level_editor.py
```

## Controls

```text
Left Arrow       Move left
Right Arrow      Move right
W / Up Arrow     Jump
Space            Shoot
Q                Throw grenade
Esc              Quit
```

## Build A Downloadable Windows Game

A prebuilt Windows EXE is included in:

```text
Downloadable Exe game File/
```

To rebuild it yourself, use the scripts below.

To create a Windows build folder and ZIP:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\build_windows.ps1
```

To create one single `.exe` file:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\build_single_exe.ps1
```

The output will be created inside:

```text
dist/
```

Share the generated ZIP or EXE with Windows users. They do not need to install Python when using the built EXE version.

## Level Editing

The project includes a level editor:

```powershell
python level_editor.py
```

The original level CSV files are stored in `levels/`. Edited level changes are saved separately in `edited_levels.json`, so the original levels stay clean.

## What Not To Upload

The repo is set up so local/private files stay off GitHub:

```text
.venv/
.vscode/
__pycache__/
build/
dist/
.env
```

These are ignored by `.gitignore`.

## Notes

- Use `shooter_game.py` for the main game.
- Keep assets inside `shooter_assets/`.
- Keep level CSV files inside `levels/`.
- Build scripts belong in `scripts/`.
- Packaging config files belong in `packaging/`.

```text
============================================================
                  Have fun playing!
============================================================
```
