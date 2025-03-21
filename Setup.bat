@echo off
mode con: cols=54 lines=55
color 0A

title FoundRelics - Loot Tracker Tool

echo.
echo  [ FoundRelics - Loot Tracker Initialized ]
ping localhost -n 2 >nul

setlocal EnableDelayedExpansion

cls
echo =====================================================
echo +               FoundRelics Tracker                 +
echo =====================================================
echo ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
echo.
echo    * Name: FoundRelics
echo    * Description: Loot Tracker
echo    * Status: Installing Requirements
echo.
echo -----------------------------------------------------
echo               Installing requirements...
echo -----------------------------------------------------
echo.

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

echo.
echo Upgrading pip...
"%PYTHON_EXE%" -m pip install --upgrade pip

echo.
echo Installing required modules: requests and PyQt5...
"%PYTHON_EXE%" -m pip install requests PyQt5

echo.
echo -----------------------------------------------------
echo             Modules installed succesfully.
echo -----------------------------------------------------
echo.
echo Console: Installation complete.
echo.
pause
