# -*- mode: python ; coding: utf-8 -*-
import os
from pathlib import Path

block_cipher = None

a = Analysis(
    ['gui_launcher.py'],
    pathex=['.'],
    binaries=[],
    datas=[
        ('checks/*', 'checks'),
        ('discontinuations/*', 'discontinuations'),
        ('version.txt', '.'),
        ('br_icon.ico', '.'),
        ('as4_to_as6_analyzer.py', '.'),
        ('helpers/*', 'helpers'),
    ],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
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
    [],
    exclude_binaries=True,
    name='as6-migration-tools',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    icon='br_icon.ico'
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='as6-migration-tools',
    distpath='dist',
    workpath='build',
)
