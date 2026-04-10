# -*- mode: python ; coding: utf-8 -*-
"""PyInstaller spec for building donghua.exe on Windows."""

import os

block_cipher = None
src_path = os.path.abspath(os.path.join(SPECPATH, '..', '..', 'src'))

a = Analysis(
    [os.path.join(src_path, 'donghua_cli', '__main__.py')],
    pathex=[src_path],
    binaries=[],
    datas=[
        (os.path.join(src_path, 'donghua_cli', 'banner_frames.json.gz'), 'donghua_cli'),
    ],
    hiddenimports=[
        'donghua_cli',
        'donghua_cli.cli',
        'donghua_cli.app',
        'donghua_cli.ui',
        'donghua_cli.tui',
        'donghua_cli.theme',
        'donghua_cli.scraper',
        'donghua_cli.extractor',
        'donghua_cli.player',
        'donghua_cli.cache',
        'donghua_cli.config',
        'donghua_cli.utils',
        'donghua_cli.sources',
        'donghua_cli.sources.base',
        'donghua_cli.sources.luciferdonghua',
        'donghua_cli.sources.animexin',
        'donghua_cli.sources.misterdonghua',
        'donghua_cli.sources.hdonghua',
        'donghua_cli.sources.lmanime',
        'httpx',
        'selectolax',
        'rich',
        'textual',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['tkinter', 'PIL', 'matplotlib', 'numpy'],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='donghua',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,
)
