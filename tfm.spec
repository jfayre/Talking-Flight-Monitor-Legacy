# -*- mode: python ; coding: utf-8 -*-

block_cipher = None


a = Analysis(['tfm.pyw'],
             pathex=['C:\\Users\\jfayr\\projects\\talking-flight-monitor'],
             binaries=[],
             hookspath=[],
             datas=[('sounds/*.wav', 'sounds'), ('tfm.defaults', '.'), ('*.lua', '.'), ],
             hiddenimports=['babel.numbers'],

             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          [],
          exclude_binaries=True,
          name='tfm',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          console=False )
coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas,
               strip=False,
               upx=True,
               upx_exclude=[],
               name='tfm')
