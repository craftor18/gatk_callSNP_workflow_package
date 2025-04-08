# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['gatk_snp_pipeline/main.py'],
    pathex=[],
    binaries=[],
    datas=[],
    hiddenimports=[
        'gatk_snp_pipeline',
        'gatk_snp_pipeline.cli',
        'gatk_snp_pipeline.config',
        'gatk_snp_pipeline.dependency_checker',
        'gatk_snp_pipeline.logger',
        'gatk_snp_pipeline.pipeline',
        'src',
        'src.steps',
        'src.utils'
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
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
    name='gatk-snp-pipeline',
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
) 