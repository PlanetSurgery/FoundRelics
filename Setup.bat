@echo off
REM Check for administrative privileges.
net session >nul 2>&1
if %errorlevel% neq 0 (
    echo This script requires administrative privileges.
    pause
    exit /b 1
)

REM Define a default installation path; change this if needed.
set "PYTHON_DEFAULT_PATH=C:\Users\%USERNAME%\AppData\Local\Programs\Python\Python39"
set "PYTHON_EXE="

REM Check if Python is available in the environment PATH.
where python >nul 2>&1
if errorlevel 1 (
    echo Python is not in your PATH.
    if exist "%PYTHON_DEFAULT_PATH%\python.exe" (
        echo Found Python at %PYTHON_DEFAULT_PATH%.
        set "PYTHON_EXE=%PYTHON_DEFAULT_PATH%\python.exe"
    ) else (
        echo Could not find Python at the default location.
        echo Please install Python and ensure it is added to your PATH.
        pause
        exit /b 1
    )
) else (
    echo Python is already in your PATH.
    set "PYTHON_EXE=python"
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
