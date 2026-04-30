#!/bin/bash

DESKTOP_DIR="$HOME/桌面"
APP_PATH="$DESKTOP_DIR/密閉空間監測系統"

# 等待桌面、顯示、聲音服務啟動
sleep 8

# 確保圖形環境變量存在
export DISPLAY=${DISPLAY:-:0}
export XAUTHORITY=${XAUTHORITY:-$HOME/.Xauthority}

# 1. 設置屏幕為橫向顯示
if command -v xrandr >/dev/null 2>&1; then
    xrandr -o normal >/dev/null 2>&1 || true

    PRIMARY_DISPLAY=$(xrandr --query 2>/dev/null | awk '/ connected primary/{print $1; exit}')
    if [ -z "$PRIMARY_DISPLAY" ]; then
        PRIMARY_DISPLAY=$(xrandr --query 2>/dev/null | awk '/ connected/{print $1; exit}')
    fi

    if [ -n "$PRIMARY_DISPLAY" ]; then
        xrandr --output "$PRIMARY_DISPLAY" --rotate normal >/dev/null 2>&1 || true
    fi
fi

# 2. 設置屏幕亮度為最大
if command -v xrandr >/dev/null 2>&1; then
    if [ -n "$PRIMARY_DISPLAY" ]; then
        xrandr --output "$PRIMARY_DISPLAY" --brightness 1.0 >/dev/null 2>&1 || true
    else
        xrandr --brightness 1.0 >/dev/null 2>&1 || true
    fi
fi

# 內屏 / 一體機背光亮度最大
if [ -d /sys/class/backlight ]; then
    for BL in /sys/class/backlight/*; do
        if [ -f "$BL/max_brightness" ] && [ -f "$BL/brightness" ]; then
            MAX_BRIGHTNESS=$(cat "$BL/max_brightness")
            echo "$MAX_BRIGHTNESS" | sudo -n tee "$BL/brightness" >/dev/null 2>&1 || true
        fi
    done
fi

# 3. 音量最大，取消靜音
if command -v pactl >/dev/null 2>&1; then
    pactl set-sink-mute @DEFAULT_SINK@ 0 >/dev/null 2>&1 || true
    pactl set-sink-volume @DEFAULT_SINK@ 100% >/dev/null 2>&1 || true
fi

# 4. 檢查程序是否存在
if [ ! -f "$APP_PATH" ]; then
    exit 1
fi

chmod +x "$APP_PATH"

# 5. 防止重複啟動
if ! pgrep -f "$APP_PATH" >/dev/null 2>&1; then
    nohup "$APP_PATH" >/dev/null 2>&1 &
fi

# 等待窗口出現
sleep 8

# 6. 最大化 / 全屏程序窗口
if command -v wmctrl >/dev/null 2>&1; then
    wmctrl -r :ACTIVE: -b add,maximized_vert,maximized_horz >/dev/null 2>&1 || true

    wmctrl -r "密閉空間監測系統" -b add,maximized_vert,maximized_horz >/dev/null 2>&1 || true
    wmctrl -r "密閉空間監測系統" -b add,fullscreen >/dev/null 2>&1 || true

    wmctrl -r "密閉空間监测系统" -b add,maximized_vert,maximized_horz >/dev/null 2>&1 || true
    wmctrl -r "密閉空間监测系统" -b add,fullscreen >/dev/null 2>&1 || true

    wmctrl -r "Confined Space" -b add,maximized_vert,maximized_horz >/dev/null 2>&1 || true
    wmctrl -r "Confined Space" -b add,fullscreen >/dev/null 2>&1 || true
fi

# 7. 用 xdotool 再嘗試 F11 全屏
if command -v xdotool >/dev/null 2>&1; then
    WINDOW_ID=$(xdotool search --onlyvisible --name "密閉空間" 2>/dev/null | head -n 1)
    if [ -n "$WINDOW_ID" ]; then
        xdotool windowactivate "$WINDOW_ID" >/dev/null 2>&1 || true
        xdotool key F11 >/dev/null 2>&1 || true
    fi
fi
