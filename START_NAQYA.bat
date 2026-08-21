@echo off
set PORT=8765
start "NAQYA" http://127.0.0.1:%PORT%
where py >nul 2>nul
if %errorlevel%==0 (
  py -3 -m http.server %PORT% --bind 127.0.0.1
) else (
  python -m http.server %PORT% --bind 127.0.0.1
)
pause
