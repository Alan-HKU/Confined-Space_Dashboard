# -*- mode: python ; coding: utf-8 -*-
#
# PyInstaller spec for 密閉空間監測系統
#
# Windows:  pyinstaller confined_space.spec   → dist/密閉空間監測系統.exe  (single file)
# Linux:    pyinstaller confined_space.spec   → dist/密閉空間監測系統      (single file)
#
# Prerequisites:
#   pip install pyinstaller PySide6 paho-mqtt psutil
#
# If Qt multimedia (alarm sound) fails on Linux, install:
#   sudo apt install gstreamer1.0-plugins-good gstreamer1.0-plugins-bad libgstreamer1.0-0

import sys
from pathlib import Path

PROJECT = Path(SPECPATH)   # noqa: F821  (SPECPATH is injected by PyInstaller)

block_cipher = None

# ── Collect all data files that must be bundled ──────────────────────────────
added_files = [
    # (source_path,  dest_folder_inside_bundle)
    (str(PROJECT / "config.ini"),          "."),
    (str(PROJECT / "assets" / "alarm.wav"), "assets"),
    (str(PROJECT / "assets" / "Picture1.png"), "assets"),
]

# ── Hidden imports that PyInstaller's static analyser misses ─────────────────
hidden = [
    "paho.mqtt.client",
    "paho.mqtt.publish",
    "psutil",
    # PySide6 multimedia backend
    "PySide6.QtMultimedia",
    "PySide6.QtMultimediaWidgets",
    # PySide6 platform plugins (bundled automatically, but list for clarity)
    "PySide6.QtCore",
    "PySide6.QtGui",
    "PySide6.QtWidgets",
]

a = Analysis(
    [str(PROJECT / "main.py")],
    pathex=[str(PROJECT)],
    binaries=[],
    datas=added_files,
    hiddenimports=hidden,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        # Trim unused heavy packages
        "tkinter", "matplotlib", "numpy", "scipy",
        "IPython", "notebook", "PIL",
        "PySide6.Qt3DCore", "PySide6.Qt3DRender",
        "PySide6.QtDataVisualization", "PySide6.QtCharts",
        "PySide6.QtWebEngineWidgets", "PySide6.QtWebEngineCore",
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)  # noqa: F821

exe = EXE(  # noqa: F821
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name="密閉空間監測系統",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,           # compress with UPX if available (reduces size ~30%)
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,      # no black console window on Windows
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    # Windows icon (comment out on Linux)
    icon=str(PROJECT / "assets" / "Picture1.png") if sys.platform == "win32" else None,
    onefile=True,       # single executable
)
