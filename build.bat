@echo off
chcp 65001 >nul
cd /d D:\NEW_AI\YT_TG_DESKTOP

echo ========================================
echo  Building YT_TG_Desktop.exe
echo ========================================
echo.

:: Activate venv
call .venv\Scripts\activate.bat

:: Build exe
echo [INFO] Building with PyInstaller...
.venv\Scripts\pyinstaller.exe ^
    --name "YT_TG_Desktop" ^
    --onedir ^
    --paths "D:\NEW_AI\YT_TG_DESKTOP\.venv\Lib\site-packages" ^
    --hidden-import pyrogram ^
    --hidden-import pyrogram.raw.all ^
    --hidden-import pyrogram.raw.core ^
    --collect-all pyrogram ^
    --collect-all PyQt6 ^
    --collect-all yt_dlp ^
    --add-data "downloads;downloads" ^
    --clean ^
    main.py

echo.
echo ========================================
echo  Build complete!
echo ========================================
echo.
echo Output: dist\YT_TG_Desktop\
echo Run:    dist\YT_TG_Desktop\YT_TG_Desktop.exe
echo.
pause
