# -*- mode: python ; coding: utf-8 -*-
from pathlib import Path

project = Path(SPECPATH).resolve().parents[1]
a = Analysis(
    [str(project / '03_SERVER' / 'server.py')],
    pathex=[], binaries=[],
    datas=[
        (str(project / '02_WEB_UI'), '02_WEB_UI'),
        (str(project / '04_CONFIG'), '04_CONFIG'),
        (str(project / '09_RETRO'), '09_RETRO'),
    ],
    hiddenimports=[], hookspath=[], hooksconfig={}, runtime_hooks=[],
    excludes=[], noarchive=False,
)
pyz = PYZ(a.pure)
exe = EXE(
    pyz, a.scripts, a.binaries, a.datas, [],
    name='HESPERIA_PS4_Control_Center_v21',
    debug=False, bootloader_ignore_signals=False, strip=False, upx=True,
    upx_exclude=[], runtime_tmpdir=None, console=False,
    disable_windowed_traceback=False, argv_emulation=False, target_arch=None,
    codesign_identity=None, entitlements_file=None,
    icon=str(project / '01_START' / 'HESPERIA_PS4_Control_Center_icon.ico'),
)
