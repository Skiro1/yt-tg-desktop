@echo off
chcp 65001 >nul
setlocal
pushd "%~dp0" || goto :error
if exist ".venv\Scripts\python.exe" (
    ".venv\Scripts\python.exe" main.py
) else (
    python main.py
)
if errorlevel 1 goto :error
popd
pause
exit /b 0

:error
echo.
echo ========================================
echo  Start failed!
echo ========================================
echo.
popd
pause
exit /b 1
