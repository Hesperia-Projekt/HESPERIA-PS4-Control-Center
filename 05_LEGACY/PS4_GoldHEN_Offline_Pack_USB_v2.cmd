@echo off
setlocal EnableExtensions EnableDelayedExpansion
title PS4 GoldHEN Offline Pack - Downloader + USB
color 0A

rem ============================================================
rem Fehlerbehandlung: Dieses Fenster soll sich NIE selbst schliessen.
rem ============================================================

cls
echo.
echo   ==============================================================
echo       ____   ____  _  _      ____       _     _     _   _ 
echo      ^|  _ \ / ___^|^| ^^ ^|    / ___^| ___ ^| ^| __^| ^| ^| ^|^| ^|
echo      ^| ^|_) ^\___ \^| ^|_^|   ^| ^|  _ / _ \^| ^|/ _` ^| ^| ^|^| ^|
echo      ^|  __/ ___) ^|  _    ^| ^|_^| ^| (_) ^| ^| (_^| ^| ^|_^|^| ^|
echo      ^|_^|   ^|____/^|_^| ^|_^|   \____^|\___/^|_^|\__,_^|\___/ ^|_^|
echo.
echo             G O L D H E N   O F F L I N E   P A C K
echo   ==============================================================
echo.
echo      Cheats Manager  -  Cheat DB  -  Game Patches  -  USB
echo.
echo   ==============================================================

set "OUT=%~dp0PS4_GoldHEN_Offline_Pack"
if not exist "%OUT%" mkdir "%OUT%" 2>nul
if errorlevel 1 (
    set "ERRMSG=Lokaler Zielordner konnte nicht erstellt werden: %OUT%"
    goto :fatal
)

echo.
echo [1/3] Lade neueste PS4 Cheats Manager PKG...
powershell -NoProfile -ExecutionPolicy Bypass -Command ^
 "$ErrorActionPreference='Stop'; try { $r=Invoke-RestMethod -Headers @{'User-Agent'='PS4-GoldHEN-Pack'} 'https://api.github.com/repos/bucanero/PS4CheatsManager/releases/latest'; $a=$r.assets | Where-Object {$_.name -match '\.pkg$'} | Select-Object -First 1; if(-not $a){throw 'Keine PKG im neuesten Release gefunden.'}; Invoke-WebRequest -Headers @{'User-Agent'='PS4-GoldHEN-Pack'} $a.browser_download_url -OutFile (Join-Path '%OUT%' $a.name); Write-Host ('OK: ' + $a.name) } catch { Write-Host ('FEHLER: ' + $_.Exception.Message); exit 1 }"
if errorlevel 1 (
    set "ERRMSG=Download des PS4 Cheats Managers fehlgeschlagen."
    goto :fatal
)

echo.
echo [2/3] Lade aktuelle GoldHEN Cheat-Datenbank...
powershell -NoProfile -ExecutionPolicy Bypass -Command ^
 "$ErrorActionPreference='Stop'; try { Invoke-WebRequest -Headers @{'User-Agent'='PS4-GoldHEN-Pack'} 'https://github.com/GoldHEN/GoldHEN_Cheat_Repository/archive/refs/heads/main.zip' -OutFile '%OUT%\GoldHEN_Cheats_latest.zip'; Write-Host 'OK: GoldHEN Cheat DB' } catch { Write-Host ('FEHLER: ' + $_.Exception.Message); exit 1 }"
if errorlevel 1 (
    set "ERRMSG=Download der GoldHEN Cheat-Datenbank fehlgeschlagen."
    goto :fatal
)

echo.
echo [3/3] Lade aktuelle Game-Patch-Datenbank...
powershell -NoProfile -ExecutionPolicy Bypass -Command ^
 "$ErrorActionPreference='Stop'; try { Invoke-WebRequest -Headers @{'User-Agent'='PS4-GoldHEN-Pack'} 'https://github.com/illusionyy/ps-game-patch/archive/refs/heads/main.zip' -OutFile '%OUT%\GoldHEN_Game_Patches_latest.zip'; Write-Host 'OK: Game Patch DB' } catch { Write-Host ('FEHLER: ' + $_.Exception.Message); exit 1 }"
if errorlevel 1 (
    set "ERRMSG=Download der Game-Patch-Datenbank fehlgeschlagen."
    goto :fatal
)

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
echo ============================================================
echo  DOWNLOADS ERFOLGREICH ABGESCHLOSSEN
echo ============================================================
echo.
choice /C JN /N /M "Optional einen USB-Stick fuer die PS4 vorbereiten? [J/N]: "
if errorlevel 2 goto :success

echo.
echo Angeschlossene Wechseldatentraeger:
powershell -NoProfile -Command ^
 "Get-CimInstance Win32_LogicalDisk | Where-Object {$_.DriveType -eq 2} | ForEach-Object { Write-Host ('  ' + $_.DeviceID + '  ' + $_.VolumeName + '  ' + [math]::Round($_.FreeSpace/1GB,1) + ' GB frei') }"
echo.
set /p "USB=Bitte Laufwerksbuchstaben eingeben (z.B. E): "
set "USB=%USB::=%"

if "%USB%"=="" (
    set "ERRMSG=Kein Laufwerksbuchstabe eingegeben."
    goto :fatal
)

if not exist "%USB%:\" (
    set "ERRMSG=Laufwerk %USB%: wurde nicht gefunden."
    goto :fatal
)

echo.
echo ACHTUNG: Es wird NICHT formatiert und NICHTS geloescht.
echo Dateien werden nur auf %USB%: kopiert.
choice /C JN /N /M "Ist %USB%: wirklich dein PS4-USB-Stick? [J/N]: "
if errorlevel 2 goto :success

set "USBROOT=%USB%:\PS4_GoldHEN_Offline_Pack"
if not exist "%USBROOT%" mkdir "%USBROOT%" 2>nul
if errorlevel 1 (
    set "ERRMSG=Ordner auf dem USB-Stick konnte nicht erstellt werden."
    goto :fatal
)
if not exist "%USBROOT%\PKG" mkdir "%USBROOT%\PKG" 2>nul
if not exist "%USBROOT%\DATABASES" mkdir "%USBROOT%\DATABASES" 2>nul

echo.
echo Kopiere Cheats Manager PKG...
set "PKGFOUND=0"
for %%F in ("%OUT%\*.pkg") do (
    if exist "%%~fF" (
        set "PKGFOUND=1"
        copy /Y "%%~fF" "%USBROOT%\PKG\" >nul
        if errorlevel 1 (
            set "ERRMSG=PKG konnte nicht auf den USB-Stick kopiert werden."
            goto :fatal
        )
    )
)
if "!PKGFOUND!"=="0" (
    set "ERRMSG=Keine heruntergeladene PKG-Datei gefunden."
    goto :fatal
)

echo Kopiere Datenbank-Backups...
copy /Y "%OUT%\GoldHEN_Cheats_latest.zip" "%USBROOT%\DATABASES\" >nul
if errorlevel 1 (
    set "ERRMSG=Cheat-Datenbank konnte nicht auf USB kopiert werden."
    goto :fatal
)
copy /Y "%OUT%\GoldHEN_Game_Patches_latest.zip" "%USBROOT%\DATABASES\" >nul
if errorlevel 1 (
    set "ERRMSG=Patch-Datenbank konnte nicht auf USB kopiert werden."
    goto :fatal
)
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
echo ============================================================
echo  USB-VORBEREITUNG ERFOLGREICH
echo ============================================================
echo  %USBROOT%
echo ============================================================
explorer "%USBROOT%"
goto :hold

:success
echo.
echo ============================================================
echo  FERTIG
echo ============================================================
echo  Lokaler Pack-Ordner:
echo  %OUT%
echo ============================================================
explorer "%OUT%"
goto :hold

:fatal
echo.
echo ============================================================
echo  FEHLER
echo ============================================================
echo.
echo  !ERRMSG!
echo.
echo  Das Fenster bleibt absichtlich geoeffnet.
echo  So kannst du die Fehlermeldung lesen oder fotografieren.
echo.
echo ============================================================
goto :hold

:hold
echo.
echo Druecke eine beliebige Taste, um das Fenster zu schliessen.
pause >nul
endlocal
exit /b
