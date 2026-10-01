@echo off
setlocal EnableExtensions EnableDelayedExpansion
title PS4 GoldHEN Offline Pack + optional USB Vorbereitung

set "OUT=%~dp0PS4_GoldHEN_Offline_Pack"
if not exist "%OUT%" mkdir "%OUT%"

echo ============================================================
echo   PS4 GoldHEN Offline Pack Downloader
echo ============================================================
echo.
echo [1/3] Lade neueste PS4 Cheats Manager PKG...
powershell -NoProfile -ExecutionPolicy Bypass -Command "$ErrorActionPreference='Stop'; $r=Invoke-RestMethod 'https://api.github.com/repos/bucanero/PS4CheatsManager/releases/latest'; $a=$r.assets | Where-Object {$_.name -match '\.pkg$'} | Select-Object -First 1; if(-not $a){throw 'Keine PKG gefunden'}; Invoke-WebRequest $a.browser_download_url -OutFile (Join-Path '%OUT%' $a.name)"
if errorlevel 1 goto :downloaderror

echo.
echo [2/3] Lade aktuelle GoldHEN Cheat-Datenbank...
powershell -NoProfile -ExecutionPolicy Bypass -Command "$ErrorActionPreference='Stop'; Invoke-WebRequest 'https://github.com/GoldHEN/GoldHEN_Cheat_Repository/archive/refs/heads/main.zip' -OutFile '%OUT%\GoldHEN_Cheats_latest.zip'"
if errorlevel 1 goto :downloaderror

echo.
echo [3/3] Lade aktuelle Game-Patch-Datenbank...
powershell -NoProfile -ExecutionPolicy Bypass -Command "$ErrorActionPreference='Stop'; Invoke-WebRequest 'https://github.com/illusionyy/ps-game-patch/archive/refs/heads/main.zip' -OutFile '%OUT%\GoldHEN_Game_Patches_latest.zip'"
if errorlevel 1 goto :downloaderror

(
echo PS4 GoldHEN Offline Pack
echo ========================
echo Die CMD laedt bei jedem Start den aktuellen Stand neu.
echo Cheats und Patches muessen zur CUSA-ID UND Spielversion passen.
echo Vor Cheat-Nutzung Spielstaende sichern.
echo.
echo Die ZIP-Dateien sind Offline-Kopien der Datenbanken.
echo Der PS4 Cheats Manager kann Datenbanken auch selbst online aktualisieren.
) > "%OUT%\README.txt"

echo.
echo Downloads abgeschlossen.
echo.
choice /C JN /N /M "Optional einen USB-Stick fuer die PS4 vorbereiten? [J/N]: "
if errorlevel 2 goto :done

echo.
echo Angeschlossene Wechseldatentraeger:
powershell -NoProfile -Command "Get-CimInstance Win32_LogicalDisk | Where-Object {$_.DriveType -eq 2} | ForEach-Object { Write-Host ('  ' + $_.DeviceID + '  ' + $_.VolumeName + '  ' + [math]::Round($_.FreeSpace/1GB,1) + ' GB frei') }"
echo.
set /p "USB=Bitte Laufwerksbuchstaben eingeben (z.B. E): "
set "USB=%USB::=%"
if not exist "%USB%:\" (
    echo.
    echo Laufwerk %USB%: wurde nicht gefunden.
    goto :done
)

echo.
echo ACHTUNG: Es wird NICHT formatiert und NICHTS geloescht.
echo Dateien werden nur auf %USB%: kopiert.
choice /C JN /N /M "Ist %USB%: wirklich dein PS4-USB-Stick? [J/N]: "
if errorlevel 2 goto :done

set "USBROOT=%USB%:\PS4_GoldHEN_Offline_Pack"
if not exist "%USBROOT%" mkdir "%USBROOT%"
if not exist "%USBROOT%\PKG" mkdir "%USBROOT%\PKG"
if not exist "%USBROOT%\DATABASES" mkdir "%USBROOT%\DATABASES"

echo.
echo Kopiere Cheats Manager PKG...
for %%F in ("%OUT%\*.pkg") do copy /Y "%%~fF" "%USBROOT%\PKG\" >nul

echo Kopiere Datenbank-Backups...
copy /Y "%OUT%\GoldHEN_Cheats_latest.zip" "%USBROOT%\DATABASES\" >nul
copy /Y "%OUT%\GoldHEN_Game_Patches_latest.zip" "%USBROOT%\DATABASES\" >nul
copy /Y "%OUT%\README.txt" "%USBROOT%\" >nul

(
echo PS4 USB - Kurzablauf
echo ===================
echo 1. GoldHEN auf der PS4 aktivieren.
echo 2. USB-Stick anschliessen.
echo 3. Cheats Manager PKG aus dem PKG-Ordner installieren.
echo 4. Cheats Manager starten.
echo 5. Cheat/Patch-Datenbank bevorzugt ueber dessen Update-/Download-Funktion aktualisieren.
echo 6. Offline-ZIPs liegen als Backup im Ordner DATABASES.
echo.
echo Hinweis: CUSA-ID und installierte Spielversion muessen zum jeweiligen Cheat/Patch passen.
echo Die CMD formatiert den USB-Stick absichtlich NICHT.
) > "%USBROOT%\INSTALLATION.txt"

echo.
echo USB-Vorbereitung abgeschlossen:
echo %USBROOT%
explorer "%USBROOT%"
goto :end

:downloaderror
echo.
echo FEHLER: Mindestens ein Download ist fehlgeschlagen.
echo Bitte Internetverbindung pruefen und die CMD erneut starten.
goto :end

:done
echo.
echo Fertig. Lokaler Pack-Ordner:
echo %OUT%
explorer "%OUT%"

:end
echo.
pause
endlocal
