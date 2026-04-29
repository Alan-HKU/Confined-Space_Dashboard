@echo off
REM ════════════════════════════════════════════════════════
REM  Windows 打包腳本 — 生成 密閉空間監測系統.exe
REM  在 confined_space\ 目錄內雙擊執行即可
REM ════════════════════════════════════════════════════════

setlocal
cd /d "%~dp0"

echo [1/4] 檢查 Python...
python --version >nul 2>&1
if errorlevel 1 (
    echo 錯誤：找不到 Python，請安裝 Python 3.10+ 並加入 PATH
    pause
    exit /b 1
)

echo [2/4] 安裝依賴...
python -m pip install --upgrade pip --quiet
python -m pip install PySide6 paho-mqtt psutil pyinstaller --quiet
if errorlevel 1 (
    echo 錯誤：依賴安裝失敗
    pause
    exit /b 1
)

echo [3/4] 清理舊版本...
if exist dist rmdir /s /q dist
if exist build rmdir /s /q build

echo [4/4] 打包中，請稍候...
python -m PyInstaller confined_space.spec --noconfirm
if errorlevel 1 (
    echo 錯誤：打包失敗，請查看上方錯誤訊息
    pause
    exit /b 1
)

echo.
echo ✅ 打包成功！
echo 可執行文件位置: dist\密閉空間監測系統.exe
echo.
echo 注意：首次運行需要將以下文件放在 .exe 同目錄：
echo   - config.ini     （已自動打包）
echo   - assets\        （已自動打包）
echo   如需修改配置請在程式内配置頁面修改並保存。
echo.
pause
