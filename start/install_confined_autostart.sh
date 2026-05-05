#!/bin/bash
set -e

DESKTOP_DIR="$HOME/桌面"
START_SCRIPT="$DESKTOP_DIR/start_confined_space.sh"
APP_PATH="$DESKTOP_DIR/密閉空間監測系統"
AUTOSTART_DIR="$HOME/.config/autostart"
AUTOSTART_FILE="$AUTOSTART_DIR/confined-space-monitor.desktop"

echo "========== 安裝密閉空間監測系統自啟動 =========="

echo "[1/5] 安裝需要的工具..."
sudo apt update
sudo apt install -y wmctrl xdotool pulseaudio-utils x11-xserver-utils

echo "[2/5] 檢查程序本體..."
if [ ! -f "$APP_PATH" ]; then
    echo "錯誤：找不到程序本體：$APP_PATH"
    echo "請確認桌面上有：密閉空間監測系統"
    exit 1
fi

echo "[3/5] 添加可執行權限..."
chmod +x "$APP_PATH"
chmod +x "$START_SCRIPT"

echo "[4/5] 創建開機自啟動配置..."
mkdir -p "$AUTOSTART_DIR"

cat > "$AUTOSTART_FILE" <<DESKTOP_EOF
[Desktop Entry]
Type=Application
Name=Confined Space Monitor
Comment=Auto start 密閉空間監測系統
Exec=$START_SCRIPT
Terminal=false
X-GNOME-Autostart-enabled=true
DESKTOP_EOF

chmod +x "$AUTOSTART_FILE"

echo "[5/5] 完成"
echo
echo "現在請先手動測試："
echo "$START_SCRIPT"
echo
echo "如果程序能正常啟動、橫屏、音量最大、亮度最大、窗口最大化，就可以重啟測試："
echo "sudo reboot"
