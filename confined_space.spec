# -*- mode: python ; coding: utf-8 -*-
#
# PyInstaller spec for 密閉空間監測系統
#
# Windows:  pyinstaller confined_space.spec   → dist/密閉空間監測系統.exe
# Linux:    pyinstaller confined_space.spec   → dist/密閉空間監測系統
#
# Prerequisites:
#   pip install pyinstaller PySide6 paho-mqtt psutil Pillow

import sys
from pathlib import Path

PROJECT = Path(SPECPATH)   # noqa: F821

block_cipher = None

# ── Resolve Windows icon (.ico required; auto-convert from PNG via Pillow) ────
def _get_win_icon() -> str | None:
    """
    Returns path to a .ico file for Windows.
    1. Use assets/app_icon.ico if it already exists.
    2. Try converting assets/Picture1.png → assets/app_icon.ico via Pillow.
    3. Fall back to None (PyInstaller uses its own default icon).
    """
    if sys.platform != "win32":
        return None

    ico_path = PROJECT / "assets" / "app_icon.ico"

    # Already have an .ico — use it directly
    if ico_path.exists():
        return str(ico_path)

    png_path = PROJECT / "assets" / "Picture1.png"
    if not png_path.exists():
        print("[spec] WARNING: assets/Picture1.png not found — skipping icon")
        return None

    try:
        from PIL import Image
        img = Image.open(png_path).convert("RGBA")

        # ICO supports multiple sizes; include common ones for best quality
        sizes = [(16,16), (24,24), (32,32), (48,48), (64,64), (128,128), (256,256)]
        imgs  = []
        for s in sizes:
            resized = img.resize(s, Image.LANCZOS)
            imgs.append(resized)

        imgs[0].save(
            str(ico_path),
            format="ICO",
            sizes=[(i.width, i.height) for i in imgs],
            append_images=imgs[1:],
        )
        print(f"[spec] Converted PNG → ICO: {ico_path}")
        return str(ico_path)

    except ImportError:
        print("[spec] Pillow not installed — run: pip install Pillow")
        print("[spec] Continuing without custom icon (exe will use default)")
        return None
    except Exception as exc:
        print(f"[spec] Icon conversion failed: {exc}")
        return None


WIN_ICON = _get_win_icon()

# ── Data files to bundle ──────────────────────────────────────────────────────
added_files = [
    (str(PROJECT / "config.ini"), "."),
]

# Bundle everything inside assets/
assets_dir = PROJECT / "assets"
if assets_dir.exists():
    for f in assets_dir.iterdir():
        if f.is_file():
            added_files.append((str(f), "assets"))

# ── Hidden imports ────────────────────────────────────────────────────────────
hidden = [
    "paho.mqtt.client",
    "paho.mqtt.publish",
    "psutil",
    "PySide6.QtMultimedia",
    "PySide6.QtMultimediaWidgets",
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
        "tkinter", "matplotlib", "numpy", "scipy",
        "IPython", "notebook",
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
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=WIN_ICON,    # None on Linux; .ico path on Windows
    onefile=True,
)
