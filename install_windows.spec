# -*- mode: python ; coding: utf-8 -*-

import os
import tempfile

TEMPLATE_PARAMETER: str = "%code%"

added_files = [
    ( 'sbin/settings_windows.ini', '.' ),
    ( 'conf/urllist', '.' )
]

data = None
template = None
with open('template/windows_template.py', 'r', encoding='utf8') as file:
    template = file.read()

with open('sbin/networkd-resolver.py', 'r', encoding='utf8') as file:
    code = file.read()
    data = template.replace(TEMPLATE_PARAMETER, code)

fp = tempfile.NamedTemporaryFile(delete_on_close=False)
fp.close()
with open(fp.name, 'w', encoding='utf-8') as f:
    f.write(data)
filename = fp.name

a = Analysis(
    [filename],
    pathex=[],
    binaries=[],
    datas=added_files,
    hiddenimports=['win32timezone'],
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
    a.binaries,
    a.datas,
    [],
    name='webhost',
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
    icon='icon/program.ico',
)

os.remove(filename)