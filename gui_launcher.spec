# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['gui_launcher.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('discontinuations/*.json', 'discontinuations'),
        ('version.txt', '.'),
        ('gui_icon.ico', '.'),
        ('helpers/*.py', 'helpers'),
        ('as4_to_as6_analyzer.py', '.'),
        ('checks/*.py', 'checks'),
        ('utils/*.py', 'utils'),
    ],
    hiddenimports=[],
    hookspath=[],
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    name='as6-migration-tools',
    debug=False,
    strip=False,
    upx=True,
    console=False,
    icon='gui_icon.ico',
    bootloader_ignore_signals=False,
)
