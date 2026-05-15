$ErrorActionPreference = "Stop"

python -m pip install -r requirements.txt

$levels = Get-ChildItem -Path "levels" -Filter "level*_data.csv" | Sort-Object Name
$addData = @(
  "--add-data", "shooter_assets;shooter_assets"
)

foreach ($level in $levels) {
  $addData += "--add-data"
  $addData += "$($level.FullName);levels"
}

python -m PyInstaller --noconfirm --onedir --windowed @addData shooter_game.py
python -m PyInstaller --noconfirm --onedir --windowed @addData level_editor.py

$release = "dist\ShooterGame"
if (Test-Path $release) {
  Remove-Item $release -Recurse -Force
}
New-Item -ItemType Directory -Path $release | Out-Null

Copy-Item "dist\shooter_game\*" $release -Recurse
Copy-Item "dist\level_editor\level_editor.exe" $release
Copy-Item "dist\level_editor\_internal\*" "$release\_internal" -Recurse -Force
Copy-Item "shooter_assets" $release -Recurse
Copy-Item "levels" $release -Recurse

Compress-Archive -Path "$release\*" -DestinationPath "dist\ShooterGame-Windows.zip" -Force

Write-Host ""
Write-Host "Windows build complete:"
Write-Host "  $release"
Write-Host "  dist\ShooterGame-Windows.zip"
