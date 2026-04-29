# 密閉空間監測系統 v2.0

## 目錄結構

```
confined_space/
├── main.py                  ← 入口點
├── config.ini               ← 配置文件（可在程式內修改）
├── requirements.txt         ← Python 依賴
├── confined_space.spec      ← PyInstaller 打包配置
├── build_windows.bat        ← Windows 一鍵打包
├── build_linux.sh           ← Linux 一鍵打包
├── assets/
│   ├── alarm.wav            ← 報警音頻
│   └── Picture1.png         ← 程式圖標
├── core/                    ← 業務邏輯（無 Qt 依賴）
│   ├── config.py
│   ├── data_model.py
│   ├── mqtt_client.py
│   └── logger_setup.py      ← 日誌（跨平台 ANSI 顏色）
└── ui/                      ← 界面層
    ├── styles.py             ← QSS（字體跨平台自適應）
    └── ...
```

---

## 直接運行（開發 / 測試）

```bash
pip install -r requirements.txt
python main.py          # Windows
python3 main.py         # Linux
```

Linux 需要先安裝 xcb 和 GStreamer（見下方）。

---

## 打包成獨立可執行文件

### Windows → .exe

```bat
REM 方法一：雙擊腳本
build_windows.bat

REM 方法二：手動
pip install pyinstaller
pyinstaller confined_space.spec --noconfirm
```

輸出：`dist\密閉空間監測系統.exe`（單文件，無需安裝 Python）

### Linux → 單文件可執行

```bash
# 方法一：腳本（自動安裝系統依賴）
bash build_linux.sh

# 方法二：手動
pip install pyinstaller
pyinstaller confined_space.spec --noconfirm
chmod +x "dist/密閉空間監測系統"
"./dist/密閉空間監測系統"
```

---

## Linux 系統依賴

### 界面（必須）
```bash
sudo apt install libxcb-cursor0 libxcb-icccm4 libxcb-image0 \
    libxcb-keysyms1 libxcb-randr0 libxcb-render-util0
```

### 報警音頻（GStreamer）
```bash
sudo apt install gstreamer1.0-plugins-good gstreamer1.0-plugins-bad \
    libgstreamer1.0-0 gstreamer1.0-alsa
```

---

## 平台差異

| 功能 | Windows | Linux |
|------|---------|-------|
| 字體 | Segoe UI + Microsoft JhengHei | Noto Sans + WenQuanYi |
| 控制台顏色 | Win10+ / Windows Terminal | 所有終端 |
| 報警音頻 | DirectSound（內建） | 需要 GStreamer |
| 本機電量 | psutil（筆記本） | psutil（筆記本） |

---

## MQTT Payload 格式

```json
{"device_id": 1, "gas_h2s": 3.5, "air_humidity": 67.2, "Battery": 80}
{"status": "bind"}
{"status": "unbind"}
```
