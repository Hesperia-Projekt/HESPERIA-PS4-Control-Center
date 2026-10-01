@echo off
setlocal EnableExtensions EnableDelayedExpansion
title HESPERIA PS4 GoldHEN Toolkit
color 0A
set "ROOT=%~dp0HESPERIA_PS4_TOOLKIT"
set "DL=%ROOT%\Downloads"
set "USBROOT=PS4_GoldHEN_Toolkit"
for %%D in ("%ROOT%" "%DL%" "%DL%\Cheats" "%DL%\Patches" "%DL%\Plugins" "%DL%\Itemzflow" "%ROOT%\CUSTOM\WALLPAPER" "%ROOT%\CUSTOM\MUSIC" "%ROOT%\CUSTOM\FONT") do if not exist "%%~D" mkdir "%%~D" >nul 2>&1

:menu
cls
echo ================================================================
echo        H E S P E R I A   -   PS4  G O L D H E N  TOOLKIT
echo ================================================================
echo.
echo   [1] Basis-Pack / PS4 Cheats Manager
echo   [2] GoldHEN Cheat-Datenbank
echo   [3] Game-Patch-Datenbank
echo   [4] Itemzflow Game Manager
echo   [5] GoldHEN Plugins
echo   [6] ALLES herunterladen / aktualisieren
echo   [7] USB-Stick vorbereiten
echo   [8] Custom-Ordner oeffnen (Wallpaper / Musik / Font)
echo   [9] Download-Ordner oeffnen
echo   [0] Beenden
echo.
set /p "SEL=Auswahl: "
if "%SEL%"=="1" call :cheatmanager & goto menu
if "%SEL%"=="2" call :cheatdb & goto menu
if "%SEL%"=="3" call :patchdb & goto menu
if "%SEL%"=="4" call :itemzflow & goto menu
if "%SEL%"=="5" call :plugins & goto menu
if "%SEL%"=="6" call :all & goto menu
if "%SEL%"=="7" call :usb & goto menu
if "%SEL%"=="8" explorer "%ROOT%\CUSTOM" & goto menu
if "%SEL%"=="9" explorer "%DL%" & goto menu
if "%SEL%"=="0" goto finish
echo Ungueltige Auswahl.
call :wait
goto menu

:cheatmanager
cls
echo [Cheats Manager] Ermittle neuestes Release...
powershell -NoProfile -ExecutionPolicy Bypass -Command "$ErrorActionPreference='Stop'; try {$r=Invoke-RestMethod -Headers @{'User-Agent'='Hesperia-PS4-Toolkit'} 'https://api.github.com/repos/bucanero/PS4CheatsManager/releases/latest'; $a=$r.assets|?{$_.name -match '\.pkg$'}|select -First 1; if(!$a){throw 'Keine PKG im Release gefunden'}; Invoke-WebRequest -Headers @{'User-Agent'='Hesperia-PS4-Toolkit'} $a.browser_download_url -OutFile (Join-Path '%DL%' $a.name); Write-Host ('OK: '+$a.name)} catch {Write-Host ('FEHLER: '+$_.Exception.Message); exit 1}"
call :result
exit /b

:cheatdb
cls
echo [Cheats] Lade aktuelle GoldHEN Cheat-Datenbank...
powershell -NoProfile -ExecutionPolicy Bypass -Command "$ErrorActionPreference='Stop'; try {Invoke-WebRequest -Headers @{'User-Agent'='Hesperia-PS4-Toolkit'} 'https://github.com/GoldHEN/GoldHEN_Cheat_Repository/archive/refs/heads/main.zip' -OutFile '%DL%\Cheats\GoldHEN_Cheats_latest.zip'; Write-Host 'OK'} catch {Write-Host ('FEHLER: '+$_.Exception.Message); exit 1}"
call :result
exit /b

:patchdb
cls
echo [Patches] Lade aktuelle PS-Game-Patch-Datenbank...
powershell -NoProfile -ExecutionPolicy Bypass -Command "$ErrorActionPreference='Stop'; try {Invoke-WebRequest -Headers @{'User-Agent'='Hesperia-PS4-Toolkit'} 'https://github.com/illusionyy/ps-game-patch/archive/refs/heads/main.zip' -OutFile '%DL%\Patches\Game_Patches_latest.zip'; Write-Host 'OK'} catch {Write-Host ('FEHLER: '+$_.Exception.Message); exit 1}"
call :result
exit /b

:itemzflow
cls
echo [Itemzflow]
echo Das offizielle GitHub-Release verweist fuer die PS4-PKG auf pkg-zone.com.
echo Die Download-Seite wird deshalb geoeffnet, statt eine PKG-URL zu erraten.
start "" "https://pkg-zone.com/details/ITEM00001"
echo.
echo GitHub Releases: https://github.com/LightningMods/Itemzflow/releases
call :wait
exit /b

:plugins
cls
echo [Plugins] Lade neuestes offizielles GoldHEN Plugin-Release...
powershell -NoProfile -ExecutionPolicy Bypass -Command "$ErrorActionPreference='Stop'; try {$r=Invoke-RestMethod -Headers @{'User-Agent'='Hesperia-PS4-Toolkit'} 'https://api.github.com/repos/GoldHEN/GoldHEN_Plugins_Repository/releases/latest'; if(!$r.assets){throw 'Release enthaelt keine Download-Dateien'}; foreach($a in $r.assets){Invoke-WebRequest -Headers @{'User-Agent'='Hesperia-PS4-Toolkit'} $a.browser_download_url -OutFile (Join-Path '%DL%\Plugins' $a.name); Write-Host ('OK: '+$a.name)}} catch {Write-Host ('FEHLER: '+$_.Exception.Message); exit 1}"
call :result
exit /b

:all
call :cheatmanager
call :cheatdb
call :patchdb
call :plugins
echo.
echo Itemzflow wird aus Sicherheitsgruenden nicht von einer geratenen Direkt-URL geladen.
echo Nutze Menuepunkt 4 fuer die offizielle Download-Seite.
call :wait
exit /b

:usb
cls
echo ================================================================
echo USB-VORBEREITUNG - ES WIRD NICHT FORMATIERT ODER GELOESCHT
echo ================================================================
echo.
powershell -NoProfile -Command "Get-CimInstance Win32_LogicalDisk|?{$_.DriveType -eq 2}|%%{Write-Host ('  '+$_.DeviceID+'  '+$_.VolumeName+'  '+[math]::Round($_.FreeSpace/1GB,1)+' GB frei')}"
echo.
set /p "U=Laufwerksbuchstabe (z.B. E): "
set "U=!U::=!"
if "!U!"=="" echo FEHLER: Keine Eingabe.&call :wait&exit /b
if not exist "!U!:\" echo FEHLER: Laufwerk nicht gefunden.&call :wait&exit /b
echo.
choice /C JN /N /M "Wirklich nach !U!: kopieren? [J/N]: "
if errorlevel 2 exit /b
set "DEST=!U!:\%USBROOT%"
if not exist "!DEST!" mkdir "!DEST!" >nul 2>&1
echo Kopiere Toolkit-Dateien...
xcopy "%DL%\*" "!DEST!\Downloads\" /E /I /Y >nul
xcopy "%ROOT%\CUSTOM\*" "!DEST!\CUSTOM\" /E /I /Y >nul
(
 echo HESPERIA PS4 GoldHEN Toolkit
 echo ============================
 echo 1. GoldHEN aktivieren.
 echo 2. Cheats Manager PKG installieren.
 echo 3. Cheats/Patches bevorzugt mit Cheats Manager aktualisieren.
 echo 4. GoldHEN Plugins nach /data/GoldHEN/plugins/ kopieren und nur benoetigte Plugins aktivieren.
 echo 5. Itemzflow separat ueber die offizielle Download-Seite beziehen.
 echo.
 echo WICHTIG: Cheats/Patches muessen zu CUSA und Spielversion passen.
 echo Vor Aenderungen Spielstaende sichern.
) > "!DEST!\INSTALLATION.txt"
echo.
echo FERTIG: !DEST!
explorer "!DEST!"
call :wait
exit /b

:result
if errorlevel 1 (
 echo.
 echo ================================================================
 echo FEHLER - Fenster bleibt offen.
 echo Bitte Meldung oben lesen oder fotografieren.
 echo ================================================================
) else (
 echo.
 echo Download erfolgreich.
)
call :wait
exit /b

:wait
echo.
echo Taste druecken, um zum Menue zurueckzukehren...
pause >nul
exit /b

:finish
echo.
echo Toolkit beendet. Taste druecken, um das Fenster zu schliessen.
pause >nul
endlocal
exit /b
