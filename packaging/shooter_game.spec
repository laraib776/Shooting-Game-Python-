# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['shooter_game.py'],
    pathex=[],
    binaries=[],
    datas=[('img', 'img'), ('audio', 'audio'), ('level_editor.py', '.'), ('level1_data.csv', '.'), ('level10_data.csv', '.'), ('level2_data.csv', '.'), ('level3_data.csv', '.'), ('level4_data.csv', '.'), ('level5_data.csv', '.'), ('level6_data.csv', '.'), ('level7_data.csv', '.'), ('level8_data.csv', '.'), ('level9_data.csv', '.')],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='shooter_game',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
