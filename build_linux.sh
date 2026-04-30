#!/usr/bin/env bash
# ════════════════════════════════════════════════════════
#  Linux 打包腳本 — 生成單個可執行文件 + .desktop 快捷方式
#  用法：bash build_linux.sh
# ════════════════════════════════════════════════════════

set -e
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

BOLD="\033[1m"; GREEN="\033[32m"; RED="\033[31m"; RESET="\033[0m"
APP_NAME="密閉空間監測系統"
EXE_NAME="confined_space_monitor"   # ASCII name for the binary (desktop safe)

echo -e "${BOLD}[1/6] 檢查系統依賴...${RESET}"

if command -v dpkg &>/dev/null; then
    PKGS_NEEDED=()
    for pkg in libgstreamer1.0-0 gstreamer1.0-plugins-good gstreamer1.0-plugins-bad \
               libxcb-cursor0 libxcb-icccm4 libxcb-image0 libxcb-keysyms1 \
               libxcb-randr0 libxcb-render-util0; do
        dpkg -s "$pkg" &>/dev/null 2>&1 || PKGS_NEEDED+=("$pkg")
    done
    if [ ${#PKGS_NEEDED[@]} -gt 0 ]; then
        echo "安裝系統依賴: ${PKGS_NEEDED[*]}"
        sudo apt-get install -y "${PKGS_NEEDED[@]}" 2>/dev/null || true
    fi
fi

echo -e "${BOLD}[2/6] 建立虛擬環境...${RESET}"
python3 -m venv .venv
source .venv/bin/activate

echo -e "${BOLD}[3/6] 安裝 Python 依賴...${RESET}"
pip install --upgrade pip --quiet
pip install PySide6 paho-mqtt psutil Pillow pyinstaller --quiet

echo -e "${BOLD}[4/6] 清理舊版本...${RESET}"
rm -rf dist/ build/

echo -e "${BOLD}[5/6] 打包中（約 2-5 分鐘）...${RESET}"
python -m PyInstaller confined_space.spec \
    --noconfirm \
    --name "$EXE_NAME"

deactivate

EXE_PATH="$(pwd)/dist/$EXE_NAME"
ICON_PATH="$(pwd)/assets/Picture1.png"

echo -e "${BOLD}[6/6] 生成 .desktop 快捷方式...${RESET}"

# ── Create .desktop file ───────────────────────────────────────────────────
DESKTOP_FILE="$SCRIPT_DIR/dist/${APP_NAME}.desktop"

cat > "$DESKTOP_FILE" << DESKTOP
[Desktop Entry]
Version=1.0
Type=Application
Name=${APP_NAME}
Comment=Confined Space Monitoring Dashboard
Exec=${EXE_PATH}
Icon=${ICON_PATH}
WorkingDirectory=$(dirname "$EXE_PATH")
Terminal=false
StartupNotify=true
Categories=Science;Monitor;
DESKTOP

chmod +x "$DESKTOP_FILE"

# Make the binary executable
chmod +x "$EXE_PATH"

echo ""
echo -e "${GREEN}${BOLD}✅ 打包成功！${RESET}"
echo ""
echo "可執行文件:  dist/$EXE_NAME"
echo ".desktop:    dist/${APP_NAME}.desktop"
echo ""
echo -e "${BOLD}桌面雙擊方式：${RESET}"
echo "  1. 把 dist/ 目錄下的所有文件複製到目標位置（例如桌面）："
echo "     cp dist/$EXE_NAME          ~/Desktop/"
echo "     cp dist/${APP_NAME}.desktop ~/Desktop/"
echo "     # 如果要修改配置，也需要 config.ini 在同目錄："
echo "     cp config.ini               ~/Desktop/"
echo ""
echo "  2. 右鍵 .desktop 文件 → 允許執行 / Allow Launching"
echo "     （不同桌面環境操作不同）"
echo ""
echo "  3. 雙擊 .desktop 即可從桌面直接啟動"
echo ""
echo -e "${BOLD}終端啓動方式（無需 .desktop）：${RESET}"
echo "  cd dist && ./$EXE_NAME"
