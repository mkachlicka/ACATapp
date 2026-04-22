# build.spec  –  PyInstaller build configuration for ACAT
# Usage:  pyinstaller build.spec
#
# Produces:
#   dist/ACAT          (Linux / Windows exe)
#   dist/ACAT.app      (macOS bundle)

import sys
from PyInstaller.utils.hooks import collect_data_files, collect_dynamic_libs

block_cipher = None

# ── data files ──────────────────────────────────────────────────────────────
datas = [
    # Praat scripts shipped with the package
    ("acat/backend/support/functions/*.praat", "praat"),
]
datas += collect_data_files("customtkinter")   # CTk themes & assets
datas += collect_data_files("parselmouth")

# ── hidden imports ───────────────────────────────────────────────────────────
hidden = [
    "customtkinter",
    "parselmouth",
    "praatio",
    "pandas",
    "numpy",
    "pydub",
    "scipy",
    "PIL",
    "packaging",
    "darkdetect",
]

# ── analysis ─────────────────────────────────────────────────────────────────
a = Analysis(
    ["acat/__main__.py"],
    pathex=["."],
    binaries=collect_dynamic_libs("parselmouth"),
    datas=datas,
    hiddenimports=hidden,
    hookspath=[],
    runtime_hooks=[],
    excludes=["PyQt6", "PyQt5", "PySide6", "PySide2", "wx"],
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
    name="ACAT",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,              # no terminal window on Windows
    disable_windowed_traceback=False,
    argv_emulation=True,        # required on macOS
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

# macOS .app bundle
app = BUNDLE(
    exe,
    name="ACAT.app",
    icon="icon.icns",                  # None, replace with "icon.icns" if you have one
    bundle_identifier="com.acat.app",
    info_plist={
        "NSHighResolutionCapable": True,
        "NSMicrophoneUsageDescription": "ACAT needs microphone access for audio analysis.",
    },
)
