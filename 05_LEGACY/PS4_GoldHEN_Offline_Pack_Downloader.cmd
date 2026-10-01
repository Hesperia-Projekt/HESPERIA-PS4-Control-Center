@echo off
setlocal EnableExtensions
title PS4 GoldHEN Offline Pack Downloader
set "OUT=%~dp0PS4_GoldHEN_Offline_Pack"
if not exist "%OUT%" mkdir "%OUT%"

echo [1/3] Lade neueste PS4 Cheats Manager PKG...
powershell -NoProfile -ExecutionPolicy Bypass -Command "$ErrorActionPreference='Stop'; $r=Invoke-RestMethod 'https://api.github.com/repos/bucanero/PS4CheatsManager/releases/latest'; $a=$r.assets ^| Where-Object {$_.name -match '\.pkg$'} ^| Select-Object -First 1; if(-not $a){throw 'Keine PKG gefunden'}; Invoke-WebRequest $a.browser_download_url -OutFile (Join-Path '%OUT%' $a.name)"

echo [2/3] Lade offizielle GoldHEN Cheat-Datenbank...
powershell -NoProfile -ExecutionPolicy Bypass -Command "Invoke-WebRequest 'https://github.com/GoldHEN/GoldHEN_Cheat_Repository/archive/refs/heads/main.zip' -OutFile '%OUT%\GoldHEN_Cheats_latest.zip'"

echo [3/3] Lade aktuelle Game-Patch-Datenbank...
powershell -NoProfile -ExecutionPolicy Bypass -Command "Invoke-WebRequest 'https://github.com/illusionyy/ps-game-patch/archive/refs/heads/main.zip' -OutFile '%OUT%\GoldHEN_Game_Patches_latest.zip'"

echo PS4 GoldHEN Offline Pack> "%OUT%\README.txt"
echo Die CMD laedt bei jedem Start die aktuell verfuegbaren Dateien neu.>> "%OUT%\README.txt"
echo Cheats/Patches muessen zur CUSA-ID und Spielversion passen.>> "%OUT%\README.txt"
echo PS4 Cheats Manager installieren und die Datenbanken bevorzugt ueber dessen Update-Funktion einspielen.>> "%OUT%\README.txt"
echo Die ZIP-Dateien dienen zusaetzlich als Offline-Kopie.>> "%OUT%\README.txt"

echo.
echo Fertig. Oeffne Download-Ordner...
start "" "%OUT%"
pause
