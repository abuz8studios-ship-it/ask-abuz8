@echo off
REM Ask ABUZ8 — one-command judge/demo run (Windows).
REM   Double-click, or:  Start-Ask-ABUZ8.bat [--fresh]
REM --fresh deletes data\feed.runtime.json first for a pristine demo ledger.
setlocal EnableDelayedExpansion
cd /d "%~dp0"
if "%PORT%"=="" set PORT=8377

if "%~1"=="--fresh" (
  if exist "data\feed.runtime.json" (
    del /q "data\feed.runtime.json"
    echo [fresh] demo ledger reset.
  )
)

where py >nul 2>nul
if %ERRORLEVEL%==0 ( set PY=py ) else ( set PY=python )
if not exist ".venv\Scripts\python.exe" (
  echo [setup] creating virtualenv...
  %PY% -m venv .venv >nul 2>nul
  if not exist ".venv\Scripts\python.exe" (
    echo [setup] %PY% failed, retrying with python...
    if exist ".venv" rmdir /s /q .venv
    python -m venv .venv >nul 2>nul
  )
  if not exist ".venv\Scripts\python.exe" ( echo [setup] FAILED to create .venv & pause & exit /b 1 )
)
echo [setup] installing dependencies...
".venv\Scripts\python.exe" -m pip install -q -r requirements.txt || ( echo [setup] pip install FAILED & pause & exit /b 1 )

echo [run] starting MCP server on 127.0.0.1:%PORT%...
start "Ask ABUZ8 MCP server" /min ".venv\Scripts\python.exe" mcp_server\server.py

echo [run] waiting for health check...
for /L %%i in (1,1,60) do (
  curl.exe -s -m 2 http://127.0.0.1:%PORT%/health >nul 2>nul
  if !ERRORLEVEL!==0 goto :healthy
  timeout /t 1 /nobreak >nul
)
echo [run] server did not answer on port %PORT% after 60s. See the server window.
pause & exit /b 1

:healthy
echo [run] server is UP. Opening the console...
if not "%ASK_ABUZ8_NO_BROWSER%"=="1" start "" http://127.0.0.1:%PORT%/
echo.
echo Ask ABUZ8 is running:  http://127.0.0.1:%PORT%/
echo MCP endpoint:          http://127.0.0.1:%PORT%/mcp
echo Close the "Ask ABUZ8 MCP server" window to stop it.
echo.
pause
