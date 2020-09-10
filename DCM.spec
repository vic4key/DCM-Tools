# -*- mode: python ; coding: utf-8 -*-

# No module named 'pkg_resources.py2_warn'
# Failed to execute script pyi_rth_pkgres
# https://stackoverflow.com/questions/37815371/pyinstaller-failed-to-execute-script-pyi-rth-pkgres-and-missing-packages
# https://github.com/pypa/setuptools/issues/1963
# hiddenimports=['pkg_resources.py2_warn'], # add hidden import and this line to your code `import pkg_resources.py2_warn`

block_cipher = None

a = Analysis(['DCM.py'],
             pathex=['.'],
             binaries=[],
             datas=[],
             hiddenimports=['pkg_resources.py2_warn'],
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)
pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          [],
          name='DCM',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          upx_exclude=['vcruntime140.dll'],
          runtime_tmpdir=None,
          console=True , uac_admin=False, resources=['DCM.exe.manifest,1'])
