# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

libdir='/opt/miniconda3/envs/cq/lib'

a = Analysis(['cq-bolt'],
             pathex=['/home/wink/prgs/CadQuery/projects/thread-experiments'],
             binaries=[
                 (os.path.join(libdir, 'python3.8/site-packages/OCP.cpython-38-x86_64-linux-gnu.so'), '.')
	     ],
	     datas=[(libdir, '.')],
             hiddenimports=[],
             hookspath=[],
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
          a.binaries,
          a.zipfiles,
          a.datas,
          [],
          name='cq-bolt',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          upx_exclude=[],
          runtime_tmpdir=None,
          console=True )
