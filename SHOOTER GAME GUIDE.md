# Shooter Game Guide

This project is a 2D side-scrolling shooter made with Python and Pygame. The game loads its world from CSV level files, uses image/audio assets from the project folders, and includes a separate level editor for making or changing levels.

## Project Structure

```text
SHOOTER/
  shooter_game_my.py       Main playable game file
  shooter_game.py          Alternate/modified game file
  level_editor.py          Level editor
  requirements.txt         Python build requirements
  build_windows.ps1        Windows packaging script
  build_android_wsl.sh     Android build command helper for WSL/Linux
  buildozer.spec           Android Buildozer configuration
  level*_data.csv          Level map data files
  img/                     Images, tiles, player/enemy animations, buttons
  audio/                   Music and sound effects
```

## How The Game Works

The game uses Pygame to create a window, draw sprites, play audio, handle keyboard input, and update the game loop.

Main controls:

```text
Left Arrow     Move left
Right Arrow    Move right
W / Up Arrow   Jump
Space          Shoot
Q              Throw grenade
Esc            Quit
```

The player, enemies, bullets, grenades, pickups, water, decorations, and exits are all represented as Pygame sprites or tile objects.

The game scrolls horizontally. When the player moves near the right side of the screen, the world scrolls instead of the player moving off-screen.

## Level System

Levels are stored as CSV files:

```text
level1_data.csv
level2_data.csv
level3_data.csv
...
```

Each CSV is a grid:

```text
16 rows x 150 columns
```

Each number in the CSV represents a tile or object.

Important tile IDs:

```text
-1  Empty space
0-8 Ground/obstacle tiles
9-10 Water
11-14 Decorations
15  Player start
16  Enemy
17  Ammo box
18  Grenade box
19  Health box
20  Exit
```

Every playable level should have:

```text
1 player start tile: 15
1 exit tile: 20
safe ground under/near the player
```

## Level Editor

The editor file is:

```text
level_editor.py
```

It lets you place tiles and save levels.

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

The editor automatically makes sure the level has a player and exit when saving. If the player is placed too close to the edge, it moves the player to a safer start position.

## Recommended Desktop App Option

For this game, the best packaging option is:

```text
PyInstaller --onedir
```

This creates a folder app instead of one single file. It is more reliable for Pygame games because the game needs images, audio, CSV levels, and saved custom levels.

Recommended shared folder:

```text
ShooterGame/
  shooter_game_my.exe
  level_editor.exe
  img/
  audio/
  level1_data.csv
  level2_data.csv
  ...
  level10_data.csv
```

You can zip this folder and send it to someone. They unzip it and run the `.exe`.

## Windows Build

Install PyInstaller:

```powershell
pip install pyinstaller
```

Build the game:

```powershell
pyinstaller --onedir --windowed ^
  --add-data "img;img" ^
  --add-data "audio;audio" ^
  --add-data "level1_data.csv;." ^
  --add-data "level2_data.csv;." ^
  --add-data "level3_data.csv;." ^
  --add-data "level4_data.csv;." ^
  --add-data "level5_data.csv;." ^
  --add-data "level6_data.csv;." ^
  --add-data "level7_data.csv;." ^
  --add-data "level8_data.csv;." ^
  --add-data "level9_data.csv;." ^
  --add-data "level10_data.csv;." ^
  shooter_game_my.py
```

Build the editor:

```powershell
pyinstaller --onedir --windowed ^
  --add-data "img;img" ^
  --add-data "audio;audio" ^
  --add-data "level1_data.csv;." ^
  --add-data "level2_data.csv;." ^
  --add-data "level3_data.csv;." ^
  --add-data "level4_data.csv;." ^
  --add-data "level5_data.csv;." ^
  --add-data "level6_data.csv;." ^
  --add-data "level7_data.csv;." ^
  --add-data "level8_data.csv;." ^
  --add-data "level9_data.csv;." ^
  --add-data "level10_data.csv;." ^
  level_editor.py
```

The output will be inside:

```text
dist/
```

This project also includes a ready script:

```powershell
powershell -ExecutionPolicy Bypass -File .\build_windows.ps1
```

It creates:

```text
dist/ShooterGame/
dist/ShooterGame-Windows.zip
```

The `ShooterGame` folder includes the game exe, level editor exe, runtime files, assets, audio, and level CSV files.

## One EXE Option

You can also make one `.exe`. This project includes a ready script:

```powershell
powershell -ExecutionPolicy Bypass -File .\build_single_exe.ps1
```

It creates:

```text
dist/shooter_game.exe
```

This single file includes the game, level editor launcher mode, image assets, audio assets, and level CSV files. In the game menu, the `Editor` button opens the level editor by relaunching the same exe in editor mode.

Important: if someone edits/saves levels, the app may create `level*_data.csv` files next to the exe so their changes can be remembered. The original built-in levels are still inside the exe.

Manual command:

```powershell
pyinstaller --onefile --windowed ^
  --add-data "img;img" ^
  --add-data "audio;audio" ^
  --add-data "level_editor.py;." ^
  --add-data "level1_data.csv;." ^
  --add-data "level2_data.csv;." ^
  --add-data "level3_data.csv;." ^
  --add-data "level4_data.csv;." ^
  --add-data "level5_data.csv;." ^
  shooter_game_my.py
```

The folder app is still easier to debug, but the single exe is best when you only want to send one file.

## macOS Build

To make a macOS app, build on a Mac:

```bash
pip install pyinstaller
pyinstaller --onedir --windowed \
  --add-data "img:img" \
  --add-data "audio:audio" \
  --add-data "level1_data.csv:." \
  --add-data "level2_data.csv:." \
  --add-data "level3_data.csv:." \
  --add-data "level4_data.csv:." \
  --add-data "level5_data.csv:." \
  shooter_game_my.py
```

Important difference:

```text
Windows uses ; in --add-data
macOS/Linux use :
```

## Linux Build

Build on Linux:

```bash
pip install pyinstaller
pyinstaller --onedir --windowed \
  --add-data "img:img" \
  --add-data "audio:audio" \
  --add-data "level1_data.csv:." \
  --add-data "level2_data.csv:." \
  --add-data "level3_data.csv:." \
  --add-data "level4_data.csv:." \
  --add-data "level5_data.csv:." \
  shooter_game_my.py
```

Linux builds should usually be made on Linux.

## Can One File Work On Every Laptop?

No. You usually need separate builds:

```text
Windows -> .exe
macOS   -> .app or macOS executable
Linux   -> Linux executable
```

A Windows `.exe` will not run normally on Mac or Linux.

## Mobile Apps

Pygame is not ideal for mobile packaging, but this project includes starter Android build files:

```text
buildozer.spec
build_android_wsl.sh
```

Possible but harder:

```text
Android -> possible with extra tools, but not simple for normal Pygame
iPhone  -> much harder, usually needs macOS/Xcode and a different app workflow
```

If you want a real mobile game later, a better path may be:

```text
Godot
Unity
Kivy
```

For this current project, desktop packaging is the best target.

## Can Other People Edit The Code?

If you share only the built app folder, people will not casually edit your Python code.

However:

```text
CSV levels can be edited if included outside the exe
advanced users may reverse-engineer packaged Python apps
do not include .py source files if you do not want easy code editing
```

For normal sharing with friends/class, PyInstaller is fine.

## Recommended Next Steps

1. Keep developing and testing with Python first.
2. Make sure all levels are playable.
3. Add a menu button to open the level editor from the game if desired.
4. Make asset paths packaging-safe.
5. Build with PyInstaller `--onedir`.
6. Zip the output folder.
7. Share the zip file.

## Notes Before Packaging

The code currently loads files using paths like:

```python
pygame.image.load("img/start_btn.png")
open("level1_data.csv")
```

Before final packaging, it is better to add a path helper so files work both in normal Python and in a packaged PyInstaller app.

Example idea:

```python
def resource_path(relative_path):
    base_path = getattr(sys, "_MEIPASS", os.path.abspath("."))
    return os.path.join(base_path, relative_path)
```

Then load files like:

```python
pygame.image.load(resource_path("img/start_btn.png"))
```

This makes the app more reliable after packaging.
