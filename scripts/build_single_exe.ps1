$ErrorActionPreference = "Stop"

python -m pip install -r requirements.txt

$levels = Get-ChildItem -Path "levels" -Filter "level*_data.csv" | Sort-Object Name
$addData = @(
  "--add-data", "shooter_assets;shooter_assets",
  "--add-data", "level_editor.py;."
)

foreach ($level in $levels) {
  $addData += "--add-data"
  $addData += "$($level.FullName);levels"
}

python -m PyInstaller --noconfirm --onefile --windowed --name shooter_game @addData shooter_game.py

Write-Host ""
Write-Host "Single EXE build complete:"
Write-Host "  dist\shooter_game.exe"
Write-Host ""
Write-Host "Share only this file. The editor can change existing levels only; saved edits go to edited_levels.json next to the exe."
