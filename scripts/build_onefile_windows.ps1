$ErrorActionPreference = "Stop"

python -m pip install -r requirements.txt

$levels = Get-ChildItem -Path "levels" -Filter "level*_data.csv" | Sort-Object Name
$addData = @(
  "--add-data", "shooter_game.py;.",
  "--add-data", "level_editor.py;.",
  "--add-data", "shooter_assets;shooter_assets"
)

foreach ($level in $levels) {
  $addData += "--add-data"
  $addData += "$($level.FullName);levels"
}

python -m PyInstaller --noconfirm --onefile --windowed --name ShooterGame @addData shooter_app.py

Write-Host ""
Write-Host "Single-file Windows build complete:"
Write-Host "  dist\ShooterGame.exe"
Write-Host ""
Write-Host "Send only this file if you want one-file sharing."
Write-Host "Edited/new levels will be saved next to ShooterGame.exe on the user's computer."
