@echo off
chcp 65001 >nul
setlocal
pushd "%~dp0" || goto :error

echo ========================================
echo  Building YT_TG_Desktop.exe
echo ========================================
echo.

if not exist "main.py" (
    echo [ERROR] main.py was not found.
    goto :error
)

if not exist ".venv\Scripts\python.exe" (
    echo [INFO] Creating virtual environment...
    where py >nul 2>nul
    if not errorlevel 1 (
        py -3 -m venv .venv
    ) else (
        python -m venv .venv
    )
    if errorlevel 1 goto :error
)

echo [INFO] Installing requirements...
".venv\Scripts\python.exe" -m pip install -r requirements.txt
if errorlevel 1 goto :error

if not exist "downloads" mkdir "downloads"
if errorlevel 1 goto :error

echo [INFO] Building with PyInstaller...
".venv\Scripts\python.exe" -m PyInstaller ^
    --name "YT_TG_Desktop" ^
    --onefile ^
    --hidden-import pyrogram ^
    --hidden-import pyrogram.raw.all ^
    --hidden-import pyrogram.raw.core ^
    --collect-all pyrogram ^
    --collect-all PyQt6 ^
    --collect-all yt_dlp ^
    --add-data "downloads;downloads" ^
    --clean ^
    main.py
if errorlevel 1 goto :error

echo.
echo ========================================
echo  Build complete!
echo ========================================
echo.
echo Output: dist\YT_TG_Desktop.exe
echo Run:    dist\YT_TG_Desktop.exe
echo.
popd
pause
exit /b 0

:error
echo.
echo ========================================
echo  Build failed!
echo ========================================
echo.
popd
pause
exit /b 1
