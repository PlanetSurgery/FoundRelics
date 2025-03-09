@echo off
REM Check if Python is available in the environment PATH
where python >nul 2>&1
if errorlevel 1 (
    echo Python is not in your PATH.
    REM Define a default installation path; change this if needed
    set "PYTHON_DEFAULT_PATH=C:\Users\%USERNAME%\AppData\Local\Programs\Python\Python39"
    if exist "%PYTHON_DEFAULT_PATH%\python.exe" (
        echo Found Python at %PYTHON_DEFAULT_PATH%.
        echo Adding it to your user PATH...
        REM Append the default path to the current PATH and set it permanently.
        setx /M PATH "%PATH%;%PYTHON_DEFAULT_PATH%"
        echo The PATH has been updated. Please restart your command prompt to use Python.
    ) else (
        echo Could not find Python at the default location.
        echo Please install Python and ensure it is added to your PATH.
        pause
        exit /b 1
    )
) else (
    echo Python is already in your PATH.
)

REM Upgrade pip
echo Upgrading pip...
python -m pip install --upgrade pip

REM Install required modules: requests and PyQt5
echo Installing required modules: requests and PyQt5...
python -m pip install requests PyQt5

echo.
echo Installation complete.
pause
