@echo off
REM Ask ABUZ8 Portable Appliance launcher (Windows).
REM   Double-click, or:  Start-Ask-ABUZ8.bat [--fresh]
REM --fresh deletes data\feed.runtime.json first for a pristine demo ledger.
REM Owner feed: put the feed path on the first non-# line of config\feed.txt.
setlocal EnableDelayedExpansion
cd /d "%~dp0"
if "%PORT%"=="" set PORT=8377

if "%~1"=="--fresh" (
  if exist "data\feed.runtime.json" (
    del /q "data\feed.runtime.json"
    echo [fresh] demo ledger reset.
  )
)

if not exist "Ask-ABUZ8.exe" (
  echo [run] Ask-ABUZ8.exe is missing from this portable folder. Re-download the zip.
  pause & exit /b 1
)
if not exist "simulator\index.html" (
  echo [run] simulator\index.html is missing from this portable folder. Re-download the zip.
  pause & exit /b 1
)
if not exist "data\feed.json" (
  echo [run] data\feed.json is missing from this portable folder. Re-download the zip.
  pause & exit /b 1
)

if exist "config\feed.txt" (
  for /f "eol=# delims=" %%L in (config\feed.txt) do (
    set "ASK_ABUZ8_FEED=%%L"
    goto :gotfeed
  )
  :gotfeed
  if defined ASK_ABUZ8_FEED echo [run] owner feed: !ASK_ABUZ8_FEED!
)

echo [run] starting Ask ABUZ8 on 127.0.0.1:%PORT%...
start "Ask ABUZ8 Appliance" /min Ask-ABUZ8.exe

echo [run] waiting for health check...
for /L %%i in (1,1,60) do (
  curl.exe -s -m 2 http://127.0.0.1:%PORT%/health >nul 2>nul
  if !ERRORLEVEL!==0 goto :healthy
  timeout /t 1 /nobreak >nul
)
echo [run] server did not answer on port %PORT% after 60s. See the appliance window.
pause & exit /b 1

:healthy
echo [run] server is UP. Opening the console...
if not "%ASK_ABUZ8_NO_BROWSER%"=="1" start "" http://127.0.0.1:%PORT%/
echo.
echo Ask ABUZ8 is running:  http://127.0.0.1:%PORT%/
echo Close the "Ask ABUZ8 Appliance" window to stop it.
echo.
pause
