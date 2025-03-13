@echo off
REM Check for administrative privileges.
net session >nul 2>&1
if %errorlevel% neq 0 (
    echo This script requires administrative privileges.
    pause
    exit /b 1
)

REM Define the default installation path for Python.
set "PYTHON_DEFAULT_PATH=C:\Users\%USERNAME%\AppData\Local\Programs\Python\Python310"

REM Check if Python exists at the default location.
if exist "%PYTHON_DEFAULT_PATH%\python.exe" (
    echo Found Python at %PYTHON_DEFAULT_PATH%.
    set "PYTHON_EXE=%PYTHON_DEFAULT_PATH%\python.exe"
) else (
    echo Could not find Python at the default location: %PYTHON_DEFAULT_PATH%.
    echo Please install Python at this location.
    pause
    exit /b 1
)

REM Upgrade pip.
echo Upgrading pip...
"%PYTHON_EXE%" -m pip install --upgrade pip

REM Install required modules: requests and PyQt5.
echo Installing required modules: requests and PyQt5...
"%PYTHON_EXE%" -m pip install requests PyQt5

echo.
echo Installation complete.
pause
