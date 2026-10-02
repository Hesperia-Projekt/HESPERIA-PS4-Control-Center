@echo off
setlocal
cd /d "%~dp0.."
title HESPERIA PS4 Control Center v28
if exist "HESPERIA_PS4_Control_Center_v28.exe" (
  start "HESPERIA PS4 Control Center" "HESPERIA_PS4_Control_Center_v28.exe"
  goto :eof
)
if exist "HESPERIA_PS4_Control_Center_v27.exe" (
  start "HESPERIA PS4 Control Center" "HESPERIA_PS4_Control_Center_v27.exe"
  goto :eof
)
if exist "HESPERIA_PS4_Control_Center_v26.exe" (
  start "HESPERIA PS4 Control Center" "HESPERIA_PS4_Control_Center_v26.exe"
  goto :eof
)
if exist "HESPERIA_PS4_Control_Center_v25.exe" (
  start "HESPERIA PS4 Control Center" "HESPERIA_PS4_Control_Center_v25.exe"
  goto :eof
)
if exist "HESPERIA_PS4_Control_Center_v24.exe" (
  start "HESPERIA PS4 Control Center" "HESPERIA_PS4_Control_Center_v24.exe"
  goto :eof
)
if exist "HESPERIA_PS4_Control_Center_v23.exe" (
  start "HESPERIA PS4 Control Center" "HESPERIA_PS4_Control_Center_v23.exe"
  goto :eof
)
if exist "HESPERIA_PS4_Control_Center_v22.exe" (
  start "HESPERIA PS4 Control Center" "HESPERIA_PS4_Control_Center_v22.exe"
  goto :eof
)
if exist "HESPERIA_PS4_Control_Center_v21.exe" (
  start "HESPERIA PS4 Control Center" "HESPERIA_PS4_Control_Center_v21.exe"
  goto :eof
)
if exist "HESPERIA_PS4_Control_Center_v20.exe" (
  start "HESPERIA PS4 Control Center" "HESPERIA_PS4_Control_Center_v20.exe"
  goto :eof
)
where py >nul 2>&1 && (py -3 "03_SERVER\server.py" & goto :eof)
where python >nul 2>&1 && (python "03_SERVER\server.py" & goto :eof)
echo Python 3 wurde nicht gefunden.
echo Installiere Python 3 fuer Windows und starte diese Datei erneut.
echo Beim ersten Start Zugriff in der Windows-Firewall fuer private Netzwerke erlauben.
pause
