@echo off
title KV Systems Launcher

echo.
echo  =========================================
echo    KV Systems ^& Automations
echo    Social Agent Console v3.0-viral
echo  =========================================
echo.

:: Navigate to project folder
cd /d "C:\Users\First Cash Pawn\OneDrive\KVSystems-FB-Agent"

:: Check if server is already running on 7861
netstat -ano | findstr :7861 >nul 2>&1
if %errorlevel%==0 (
    echo  [!] Server already running on port 7861
) else (
    echo  [+] Starting server on port 7861...
    start "KV Agent Server" cmd /k "cd /d "C:\Users\First Cash Pawn\OneDrive\KVSystems-FB-Agent" && py -m uvicorn server:app --port 7861"
    timeout /t 3 /nobreak >nul
    echo  [+] Server started
)

:: Open dashboard in Chrome
echo  [+] Opening dashboard...
start chrome "file:///C:/Users/First%%20Cash%%20Pawn/OneDrive/KVSystems-FB-Agent/kv-console.html"

echo.
echo  [✓] KV Dashboard launched
echo  [✓] Server running in background window
echo.
echo  Close the "KV Agent Server" window to stop the server.
echo.
pause