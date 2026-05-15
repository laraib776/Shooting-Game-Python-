# Converting This Game To One EXE

This guide explains how this project was converted into one downloadable Windows app file:

```text
Downloadable Exe game File/shooter_game.exe
```

This exe is built from:

```text
shooter_game.py
```

It includes:

```text
the playable game
the level editor code
all image assets
all audio assets
all level CSV files
```

## Important Result

The final file to share is:

```text
Downloadable Exe game File/shooter_game.exe
```

You can send only this one file to someone on Windows. They can run it and play the game.

On GitHub, this file is stored with Git LFS because it is too large for normal Git storage.

## Files Used

Important files:

```text
shooter_game.py        Main game file used for the exe
level_editor.py        Embedded level editor
shooter_assets/img/    Images and animations
shooter_assets/audio/  Music and sound effects
levels/                Levels 1-10
requirements.txt       Python package requirements
scripts/build_single_exe.ps1
```

## How The Editor Works In One EXE

The level editor is included inside the same exe.

In the game menu, clicking `Edit Levels` relaunches the same exe in editor mode.

Internally, this works by running:

```text
shooter_game.exe --editor
```

So there is no separate `level_editor.exe` needed.

## Level Editing Rule

The editor can edit existing levels only.

It does not create:

```text
level11_data.csv
level12_data.csv
...
```

If someone edits a level and saves it, the exe writes one file next to itself:

```text
edited_levels.json
```

That file stores changes to existing levels. The original built-in levels are still inside the exe.

## Install Requirements

Run this in PowerShell:

```powershell
pip install -r requirements.txt
```

The important packages are:

```text
pygame
pyinstaller
```

## Build Command

The easiest way is to run:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\build_single_exe.ps1
```

This script builds:

```text
dist/shooter_game.exe
```

## What The Script Does

The script:

1. Installs requirements.
2. Finds all `levels/level*_data.csv` files.
3. Adds `shooter_assets/img/` into the exe.
4. Adds `shooter_assets/audio/` into the exe.
5. Adds `level_editor.py` into the exe.
6. Adds all level CSV files into the exe.
7. Builds one file named `shooter_game.exe`.

## Manual PyInstaller Command

The script is preferred, but the manual command looks like this:

```powershell
pyinstaller --noconfirm --onefile --windowed --name shooter_game ^
  --add-data "shooter_assets;shooter_assets" ^
  --add-data "level_editor.py;." ^
  --add-data "levels\level1_data.csv;levels" ^
  --add-data "levels\level2_data.csv;levels" ^
  --add-data "levels\level3_data.csv;levels" ^
  --add-data "levels\level4_data.csv;levels" ^
  --add-data "levels\level5_data.csv;levels" ^
  --add-data "levels\level6_data.csv;levels" ^
  --add-data "levels\level7_data.csv;levels" ^
  --add-data "levels\level8_data.csv;levels" ^
  --add-data "levels\level9_data.csv;levels" ^
  --add-data "levels\level10_data.csv;levels" ^
  shooter_game.py
```

On Windows, PyInstaller uses semicolons in `--add-data`:

```text
source;destination
```

## Packaging-Safe Paths

The code uses helper functions so files work both in normal Python and inside PyInstaller:

```python
APP_DIR = os.path.dirname(sys.executable) if getattr(sys, "frozen", False) else os.path.dirname(os.path.abspath(__file__))
RESOURCE_DIR = getattr(sys, "_MEIPASS", APP_DIR)

def resource_path(relative_path):
    return os.path.join(RESOURCE_DIR, relative_path)

def writable_path(relative_path):
    return os.path.join(APP_DIR, relative_path)
```

Use `resource_path()` for built-in files:

```python
pygame.image.load(resource_path("img/start_btn.png"))
pygame.mixer.Sound(resource_path("audio/shot.wav"))
```

Use `writable_path()` for files the app may save:

```python
writable_path("edited_levels.json")
```

## Where The EXE Appears

After building, check:

```text
dist/shooter_game.exe
```

That is the newly built file. Copy it into `Downloadable Exe game File/` if you want the GitHub downloadable folder to use the newest build.

## Sharing The Game

Send this file:

```text
shooter_game.exe
```

The other person does not need:

```text
Python
Pygame
img/
audio/
CSV files
source code
```

Everything needed to start playing is inside the exe.

## Notes

The exe is large because it contains:

```text
Python runtime
Pygame
images
audio
levels
editor code
```

That is normal for a one-file PyInstaller game.

If Windows Defender warns about it, that can happen with unsigned PyInstaller apps. It does not automatically mean the file is dangerous. For official distribution, the app should eventually be code-signed.
