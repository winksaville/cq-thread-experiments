# -*- mode: python ; coding: utf-8 -*-
import sys, site, os
from path import Path

block_cipher = None
print("Path: " + Path(sys.prefix))
if sys.platform == 'linux':
    occt_dir = Path(sys.prefix) / 'share' / 'opencascade'
else:
    occt_dir = Path(sys.prefix) / 'Library' / 'share' / 'opencascade'

a = Analysis(['cq-bolt.py'],
             pathex=['/home/wink/prgs/CadQuery/projects/thread-experiments'],
             binaries=[
                 ('/opt/miniconda3/envs/cq-dev/lib/python3.8/site-packages/OCP.cpython-38-x86_64-linux-gnu.so', '.')
	     ],
	     datas=[('/opt/miniconda3/envs/cq-dev/lib', '.')],
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
          [],
          exclude_binaries=True,
          name='cq-bolt',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          console=True )

exclude = ('libGL','libEGL','libbsd')
a.binaries = TOC([x for x in a.binaries if not x[0].startswith(exclude)])

coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas,
               strip=False,
               upx=True,
               upx_exclude=[],
               name='cq-bolt')
