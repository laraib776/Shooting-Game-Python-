# Shooter Game Guide

This project is a 2D side-scrolling shooter made with Python and Pygame. It includes the main game, a level editor, image/audio assets, and CSV-based levels.

## Current Project Structure

```text
SHOOTER/
  shooter_game.py              Main playable game
  shooter_app.py               Launcher used for one-file packaging
  level_editor.py              Level editor
  requirements.txt             Python dependencies
  README.md                    GitHub project overview
  SHOOTER GAME GUIDE.md        Detailed game/build guide

  shooter_assets/
    img/                       Images, tiles, buttons, animations
    audio/                     Music and sound effects

  levels/
    level1_data.csv            Level data files
    ...
    level10_data.csv

  scripts/
    build_windows.ps1          Windows folder-app build
    build_single_exe.ps1       Single EXE build from shooter_game.py
    build_onefile_windows.ps1  Single EXE launcher build
    build_android_wsl.sh       Android/Buildozer helper

  packaging/
    *.spec                     PyInstaller/Buildozer config files
```

The old duplicate root `level*_data.csv` files were removed. The correct level files now live in `levels/`.

## How To Run From Source

Install Python 3.10 or newer, then run these commands from the project folder:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python shooter_game.py
```

To open the level editor directly:

```powershell
python level_editor.py
```

## Game Controls

```text
Left Arrow       Move left
Right Arrow      Move right
W / Up Arrow     Jump
Space            Shoot
Q                Throw grenade
Esc              Quit
```

## Level System

Levels are stored as CSV files inside `levels/`.

```text
levels/level1_data.csv
levels/level2_data.csv
...
levels/level10_data.csv
```

Each CSV is a grid of tile IDs:

```text
-1     Empty space
0-8    Ground and obstacle tiles
9-10   Water
11-14  Decorations
15     Player start
16     Enemy
17     Ammo box
18     Grenade box
19     Health box
20     Exit
```

Every playable level should have one player start tile and one exit tile.

## Level Editor

The editor is in:

```text
level_editor.py
```

Editor controls:

```text
Left click        Place selected tile
Right click       Erase tile
Double click      Erase one tile
A / D             Scroll level left/right
Arrow keys        Scroll level left/right
Mouse wheel       Scroll level
SAVE              Save current level
LOAD              Open level dropdown
CLEAR             Clear the level
DONE              Save and close editor
```

Saved edits are stored in `edited_levels.json` next to the app/exe. This keeps original CSV levels clean.

## Build Scripts

Build scripts now live in `scripts/`.

Windows folder-app build:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\build_windows.ps1
```

Single EXE build:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\build_single_exe.ps1
```

Launcher-style single EXE build:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\build_onefile_windows.ps1
```

Build output goes into `dist/`. Build output is ignored by Git.

## Packaging Files

Packaging config files live in:

```text
packaging/
```

These are kept separate from game source files so the root folder stays clean.

## GitHub Safety

These should not be committed:

```text
.venv/
.vscode/
__pycache__/
build/
dist/
.env
```

The `.gitignore` file protects those local files from being uploaded to GitHub.
