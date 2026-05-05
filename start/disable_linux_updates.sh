#!/bin/bash
set -e

echo "========== 禁用 Linux 自動更新與更新彈窗 =========="

echo "[1/6] 停止 unattended-upgrades..."
sudo systemctl stop unattended-upgrades 2>/dev/null || true
sudo systemctl disable unattended-upgrades 2>/dev/null || true
sudo systemctl mask unattended-upgrades 2>/dev/null || true

echo "[2/6] 停止 apt-daily 自動檢查更新..."
sudo systemctl stop apt-daily.timer apt-daily-upgrade.timer 2>/dev/null || true
sudo systemctl disable apt-daily.timer apt-daily-upgrade.timer 2>/dev/null || true
sudo systemctl mask apt-daily.timer apt-daily-upgrade.timer 2>/dev/null || true

sudo systemctl stop apt-daily.service apt-daily-upgrade.service 2>/dev/null || true
sudo systemctl disable apt-daily.service apt-daily-upgrade.service 2>/dev/null || true
sudo systemctl mask apt-daily.service apt-daily-upgrade.service 2>/dev/null || true

echo "[3/6] 停止 PackageKit 後台更新檢查..."
sudo systemctl stop packagekit 2>/dev/null || true
sudo systemctl disable packagekit 2>/dev/null || true
sudo systemctl mask packagekit 2>/dev/null || true

echo "[4/6] 寫入 apt 自動更新禁用配置..."

sudo tee /etc/apt/apt.conf.d/20auto-upgrades >/dev/null <<APT_EOF
APT::Periodic::Update-Package-Lists "0";
APT::Periodic::Unattended-Upgrade "0";
APT::Periodic::Download-Upgradeable-Packages "0";
APT::Periodic::AutocleanInterval "0";
APT_EOF

sudo tee /etc/apt/apt.conf.d/10periodic >/dev/null <<APT_EOF
APT::Periodic::Enable "0";
APT::Periodic::Update-Package-Lists "0";
APT::Periodic::Download-Upgradeable-Packages "0";
APT::Periodic::AutocleanInterval "0";
APT::Periodic::Unattended-Upgrade "0";
APT_EOF

echo "[5/6] 禁用桌面更新彈窗..."

mkdir -p "$HOME/.config/autostart"

cat > "$HOME/.config/autostart/update-manager.desktop" <<DESKTOP_EOF
[Desktop Entry]
Type=Application
Name=Update Manager
Hidden=true
DESKTOP_EOF

cat > "$HOME/.config/autostart/update-notifier.desktop" <<DESKTOP_EOF
[Desktop Entry]
Type=Application
Name=Update Notifier
Hidden=true
DESKTOP_EOF

cat > "$HOME/.config/autostart/org.gnome.Software.desktop" <<DESKTOP_EOF
[Desktop Entry]
Type=Application
Name=GNOME Software
Hidden=true
DESKTOP_EOF

echo "[6/6] 嘗試禁用 update-manager / update-notifier 可執行入口..."

sudo chmod -x /usr/bin/update-notifier 2>/dev/null || true
sudo chmod -x /usr/bin/update-manager 2>/dev/null || true

echo
echo "========== 完成 =========="
echo "已禁用："
echo "1. unattended-upgrades 自動更新"
echo "2. apt-daily 自動檢查更新"
echo "3. apt-daily-upgrade 自動升級"
echo "4. PackageKit 後台更新檢查"
echo "5. 桌面更新彈窗"
echo
echo "建議現在重啟："
echo "sudo reboot"
echo
echo "如需檢查狀態，可執行："
echo "systemctl status unattended-upgrades"
echo "systemctl list-timers | grep apt"
