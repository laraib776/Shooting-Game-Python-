# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['level_editor.py'],
    pathex=[],
    binaries=[],
    datas=[('img', 'img'), ('audio', 'audio'), ('level1_data.csv', '.'), ('level2_data.csv', '.'), ('level3_data.csv', '.'), ('level4_data.csv', '.'), ('level5_data.csv', '.'), ('level6_data.csv', '.')],
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
    [],
    exclude_binaries=True,
    name='level_editor',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='level_editor',
)
