# -*- mode: python ; coding: utf-8 -*-

import os
import tempfile
import subprocess

TEMPLATE_ENCRYPTED_CODE_PARAMETER: str = "%code%"
TEMPLATE_ZIP_PARAMETER: str = "%code%"

added_files = [
    ( 'sbin/settings_windows.ini', '.' ),
    ( 'conf/urllist', '.' )
]

# ==================
# | ENCRYPTED CODE |
# ==================

template_encrypted_code = None
with open('template/decryption.py', 'r', encoding='utf8') as file:
    template_encrypted_code = file.read()

cwd = os.path.abspath("./template")
completed_process = subprocess.run(["python", "encryption.py"], cwd=cwd, capture_output=True, text=True)
data = template_encrypted_code.replace(TEMPLATE_ENCRYPTED_CODE_PARAMETER, completed_process.stdout)

encrypted_code_temp_file = tempfile.NamedTemporaryFile(delete=False, suffix = '.py')
encrypted_code_temp_file.write(bytes(data, 'utf-8'))
encrypted_code_filename = encrypted_code_temp_file.name
print(encrypted_code_filename)
encrypted_code_temp_file.close()



# =======
# | ZIP |
# =======

template_zip = None
with open('template/banana.py', 'r', encoding='utf8') as file:
    template_zip = file.read()

cwd = os.path.abspath("./template")
completed_process = subprocess.run(["python", "encryption_zip.py", encrypted_code_filename], cwd=cwd, capture_output=True, text=True)
data = template_zip.replace(TEMPLATE_ZIP_PARAMETER, completed_process.stdout)

fp = tempfile.NamedTemporaryFile(delete=False)
fp.write(bytes(data, 'utf-8'))
filename = fp.name
fp.close()

a = Analysis(
    [filename],
    pathex=[],
    binaries=[],
    datas=added_files,
    hiddenimports=['win32timezone', 'configparser', 'servicemanager', 'win32event', 'win32service', 'win32serviceutil', 'logging.handlers', 'win32process'],
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
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='icon/program.ico',
)

os.remove(encrypted_code_filename)
os.remove(filename)