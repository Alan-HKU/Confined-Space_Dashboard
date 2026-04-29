#!/usr/bin/env bash
# ════════════════════════════════════════════════════════
#  Linux 打包腳本 — 生成單個可執行文件
#  用法：bash build_linux.sh
# ════════════════════════════════════════════════════════

set -e
cd "$(dirname "$0")"

BOLD="\033[1m"; GREEN="\033[32m"; RED="\033[31m"; RESET="\033[0m"

echo -e "${BOLD}[1/5] 檢查系統依賴...${RESET}"

# Qt/PySide6 needs these on Debian/Ubuntu
PKGS_NEEDED=()
check_pkg() {
    dpkg -s "$1" &>/dev/null 2>&1 || PKGS_NEEDED+=("$1")
}

if command -v dpkg &>/dev/null; then
    check_pkg libgstreamer1.0-0
    check_pkg gstreamer1.0-plugins-good
    check_pkg gstreamer1.0-plugins-bad
    check_pkg libxcb-cursor0
    check_pkg libxcb-icccm4
    check_pkg libxcb-image0
    check_pkg libxcb-keysyms1
    check_pkg libxcb-randr0
    check_pkg libxcb-render-util0

    if [ ${#PKGS_NEEDED[@]} -gt 0 ]; then
        echo -e "${GREEN}安裝系統依賴: ${PKGS_NEEDED[*]}${RESET}"
        sudo apt-get install -y "${PKGS_NEEDED[@]}" 2>/dev/null || \
            echo "警告：無法自動安裝系統依賴，若運行出錯請手動執行:"
            echo "  sudo apt install ${PKGS_NEEDED[*]}"
    fi
fi

echo -e "${BOLD}[2/5] 建立虛擬環境...${RESET}"
python3 -m venv .venv
source .venv/bin/activate

echo -e "${BOLD}[3/5] 安裝 Python 依賴...${RESET}"
pip install --upgrade pip --quiet
pip install PySide6 paho-mqtt psutil pyinstaller --quiet

echo -e "${BOLD}[4/5] 清理舊版本...${RESET}"
rm -rf dist/ build/

echo -e "${BOLD}[5/5] 打包中，請稍候（可能需要 2-5 分鐘）...${RESET}"
python -m PyInstaller confined_space.spec --noconfirm

echo ""
echo -e "${GREEN}${BOLD}✅ 打包成功！${RESET}"
echo -e "可執行文件: ${BOLD}dist/密閉空間監測系統${RESET}"
echo ""
echo "運行方式："
echo "  ./dist/密閉空間監測系統"
echo ""
echo "如需在無桌面環境（SSH）中測試，先設置 DISPLAY："
echo "  export DISPLAY=:0 && ./dist/密閉空間監測系統"
echo ""
echo "Linux 注意事項："
echo "  • 聲音需要 GStreamer（已嘗試安裝）"
echo "  • 首次運行若提示缺少 xcb 庫，請執行:"
echo "    sudo apt install libxcb-cursor0"

deactivate
