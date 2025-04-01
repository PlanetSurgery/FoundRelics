@echo off
mode con: cols=44 lines=25
color 0A

title FoundRelics - Loot Tracker Tool

echo.
echo  [ FoundRelics - Loot Tracker Initialized ] 
ping localhost -n 2 >nul

setlocal EnableDelayedExpansion

set "PYTHON_EXE=C:\Users\%USERNAME%\AppData\Local\Programs\Python\Python310\python.exe"
set "mainLaunched=0"
set "lastStatus=Offline"

:loop
tasklist /FI "IMAGENAME eq LostRelics.exe" 2>NUL | find /I "LostRelics.exe" >nul
if !ERRORLEVEL! equ 0 (
    set "status=Active"
) else (
    set "status=Offline"
)

if not "!status!"=="!lastStatus!" (
    cls
    echo ===========================================
    echo +          FoundRelics Tracker            +
    echo ===========================================
    echo ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
	echo.
    echo    * Status: Game !status!
    echo    * Version 0.02_1
    echo.
    if "!status!"=="Active" (
         echo -------------------------------------------
         echo            Game has been found.
         echo -------------------------------------------
		 echo.
		 echo Console: Incoming game logs will now be displayed.
		 echo.
		 echo --
		 echo.
         if "!mainLaunched!"=="0" (
              start /B "" "%PYTHON_EXE%" "%~dp0\Scripts\Main.py"
              set "mainLaunched=1"
         )
    ) else (
         echo -------------------------------------------
         echo          Start game to continue...
         echo -------------------------------------------
		 echo.
    )
    set "lastStatus=!status!"
)

timeout /t 1 >nul
goto loop
