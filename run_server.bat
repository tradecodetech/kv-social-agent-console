@echo off
cd /d "C:\Users\First Cash Pawn\OneDrive\KVSystems-FB-Agent"
echo.
echo  KV Systems Agent -- On-Demand Server
echo  =====================================
echo  API running at: http://localhost:7861
echo  Console UI:     Open kv-console.html in your browser
echo  Docs:           http://localhost:7861/docs
echo.
py -m uvicorn server:app --host 0.0.0.0 --port 7861 --reload
pause
