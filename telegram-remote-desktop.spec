# -*- mode: python ; coding: utf-8 -*-

a = Analysis(
    ['telegram-remote-desktop.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('auth.json', '.'),
    ],
    hiddenimports=[
        'telegram',
        'telegram.ext',
        'telegram._bot',
        'telegram.ext._application',
        'telegram.ext._updater',
        'httpx',
        'anyio',
        'anyio._backends._asyncio',
        'mss',
        'mss.windows',
        'psutil',
        'pyperclip',
        'ctypes',
        'webbrowser',
    ],
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
    name='telegram-remote-desktop',
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
