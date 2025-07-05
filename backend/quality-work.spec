# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['quality-work.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('media/audio_settings.json','media'),
        ('fixture.json','.'),
        ('frontend/*','frontend/'),
        ('frontend/static/css/*','frontend/static/css'),
        ('frontend/static/js/*','frontend/static/js'),
        ('frontend/static/media/*','frontend/static/media'),
        ('templates/index.html','templates'),
        ('.venv/lib/python3.11/site-packages/janome/sysdic/entries_compact*.py','janome/sysdic'),
        ('.venv/lib/python3.11/site-packages/janome/sysdic/entries_extra*.py','janome/sysdic'),
    ],
    hiddenimports=['activities.apps','activities.urls','rest_framework.parsers','rest_framework.negotiation','rest_framework.metadata'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='quality-work',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='QTicon_S.ico',
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='quality-work',
)
