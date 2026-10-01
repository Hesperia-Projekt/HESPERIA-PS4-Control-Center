
## Version 9.0 – PS1 FIRST
- PS1 zur kritischen Kernfunktion hochgestuft.
- PS1-Dateierkennung erweitert: CUE/BIN, CHD, PBP, M3U, CCD, IMG, ISO, MDF, TOC, CBN.
- BIOS-Validierung per MD5 und bekannte Retail-PS1-BIOS-Prüfung ergänzt.
- Multi-Disc-Prüfung über M3U ergänzt.
- PS4 RetroBox/RetroArch mit mednafen_psx als optionaler, verifizierter PS1-Linux-Runtime-Provider hinterlegt.
- Nativer Orbis-PKG-Provider bleibt bewusst reserviert, bis eine belastbare Distribution verifiziert ist.
- API und USB-Export auf v9 aktualisiert.

# HESPERIA PS4 Control Center v7 – vollständige Paketdokumentation

Stand: 30.09.2026

## Ziel
Lokales, portables Steuer- und Vorbereitungspaket für eine eigene GoldHEN-PS4. Ein Windows-PC hostet eine kleine Website auf Port 8088; jedes Gerät im gleichen LAN/WLAN – auch Android – kann die Oberfläche öffnen. Downloads erfolgen auf dem Windows-PC. Das Tool verteilt keine Spiele, ROMs, BIOS-Dateien, Keys oder Lizenzen.

## Schnellstart
1. ZIP entpacken.
2. `01_START/START_HESPERIA_PS4.cmd` starten.
3. Auf dem PC öffnet sich `http://127.0.0.1:8088`.
4. Auf Android die im Konsolenfenster angezeigte LAN-Adresse `http://<PC-IP>:8088` öffnen.
5. Module/Preset auswählen und herunterladen.
6. `USB-Struktur erstellen` wählen; Ergebnis liegt in `08_USB_EXPORT`.
7. GoldHEN auf der eigenen PS4 starten und Homebrew-PKGs über den Package Installer installieren.

## Ordner
- `01_START` – Windows-Starter und GoldHEN-Offline-Startseite aus dem Vorgängerpaket.
- `02_WEB_UI` – responsive lokale Weboberfläche.
- `03_SERVER` – Python-3-HTTP/API-Server, nur Standardbibliothek.
- `04_CONFIG` – Quellenkatalog und Presets.
- `05_LEGACY` – ältere CMD-Werkzeuge als Fallback/Referenz.
- `06_DOCS` – Masterplan und diese vollständige Dokumentation.
- `07_DOWNLOADS` – vom Tool geladene Dateien.
- `08_USB_EXPORT` – automatisch erzeugte USB-Struktur samt SHA-256-Manifest.
- `09_RETRO` – Hinweise/Plan für Retro-Emulation bis zur PS1-Generation.
- `10_LOGS` – für spätere Diagnose-/Logfunktionen reserviert.

## Funktionen v7
### Lokale Website
Responsive UI für Windows, Android, Tablet und andere Browser im gleichen Netzwerk. Keine Cloud und kein Account erforderlich.

### Quellenprüfung und Download
GitHub-Releases werden zur Laufzeit über die GitHub-API geprüft. Bei pEMU werden Assets per Regex getrennt, damit nicht versehentlich das erste `.pkg` für alle Emulatoren geladen wird.

### Cheats und Patches
- PS4 Cheats Manager
- GoldHEN Cheat Repository
- Game Patch Repository
- GoldHEN Plugin Repository
Cheats/Patches müssen zur Title-ID/CUSA und Spielversion passen.

### Media Center
pPlay wird aus dem offiziellen Cpasjuste-Release bezogen. pPlay nutzt MPV/FFmpeg und unterstützt gängige Video-/Audioformate, Untertitel sowie HTTP/FTP-Streaming. 4K/HDR/exotische Codecs sind nicht garantiert.

### Retro bis PS1-Generation
Empfohlen und direkt auswählbar: pNES, pSNES, pGEN, pFBNeo. pGBA ist optional markiert, weil 2026 noch einzelne PS4-/PS4-Pro-Probleme gemeldet werden. PS1 ist als Zielgrenze dokumentiert, wird aber in v7 nicht über einen unklaren/unzuverlässigen nativen Build automatisiert. Keine ROMs/BIOS enthalten.

### Presets
- Essentials: Cheats Manager + pPlay
- Cheats: Manager + Cheat DB + Patch DB
- Media: pPlay
- Retro empfohlen: pNES + pSNES + pGEN + pFBNeo
- Alles empfohlen: alles oben plus Plugins, ohne das optional problematischere pGBA

### Automatische PS4-Erkennung
`PS4 automatisch suchen` scannt die lokalen `/24`-Subnetze des Windows-PCs auf typische Dienste: FTP 2121, BinLoader 9090 sowie RPI 12800/12801. Ein Treffer ist ein Kandidat, keine sichere Identifikation. Die Funktion verändert nichts auf gefundenen Geräten. Für die RPI-Ports gilt ein längeres Timeout als bei Neben-Diensten; eine erfolgreich bestätigte RPI-API überschreibt zusätzlich einen fehlgeschlagenen Kurztest in der angezeigten Portliste.

### USB-Export
Erzeugt `PKG`, `DATABASES`, `ROMS_OWN_DUMPS_ONLY`, `BIOS_OWN_DUMPS_ONLY`, `MEDIA`, `INSTALLATION.txt` und `MANIFEST.json`. Das Manifest enthält SHA-256 und Dateigröße jedes exportierten Downloads.

## Was bewusst NICHT automatisch passiert
- Keine kommerziellen Spiele/ROMs/Disc-Images/BIOS/Keys/Lizenzen.
- Keine automatische Installation fremder PKGs auf die PS4 ohne bestätigten Installationsweg.
- Kein Flashen, kein Firmware-Downgrade, kein automatisches Schreiben in Systembereiche.
- Keine Behauptung, dass ein offener Port zweifelsfrei eine PS4 ist.
- Keine dubiosen PS1-Builds nur um eine Checkbox mehr anbieten zu können.

## Technische Architektur
Browser -> lokaler Python-HTTP-Server -> `sources.json` -> offizielle Release-/Repository-Quellen -> lokaler Downloadordner -> USB-Export. Der Server bindet an `0.0.0.0:8088`, damit Android im selben Netz zugreifen kann. Es wird kein Internet-Port geöffnet; Windows-Firewall kann beim ersten Start eine Freigabe für private Netze verlangen.

## Quellenstrategie
Bevorzugt werden Original-Repositories der jeweiligen Projekte. Der Downloader löst `releases/latest` zur Laufzeit auf, damit das Paket nicht an eine bestimmte Versionsnummer gebunden ist. Datenbank-Repositories werden als aktuelle Branch-ZIPs geladen.

## Sicherheit
Nur im vertrauenswürdigen Heimnetz betreiben. Port 8088 nicht im Router ins Internet weiterleiten. Downloads werden mit SHA-256 im Exportmanifest dokumentiert. Vor Installation kann die Quelle in `04_CONFIG/sources.json` nachvollzogen werden.

## Bekannte Grenzen
- GitHub kann API-Ratelimits anwenden.
- Manche Homebrew-Projekte ändern Asset-Namen; dann muss der Regex im Quellenkatalog angepasst werden.
- PS4-Firmware/GoldHEN-Version und einzelne Homebrew-Versionen können sich gegenseitig beeinflussen.
- pGBA ist auf PS4 Pro nicht in allen 2026-Berichten zuverlässig.
- Native PS1-Emulation ist noch nicht als „ein Klick und sehr gut“ in den empfohlenen Provider aufgenommen.

## Changelog v7 gegenüber v6
- Retro-Bereich bis PS1-Generation ergänzt.
- pNES, pSNES, pGEN, pFBNeo und optional pGBA integriert.
- pEMU-Asset-Auswahl repariert/robust per Regex.
- automatische LAN-Kandidatensuche für PS4 ergänzt.
- Presets ergänzt.
- SHA-256-Manifest beim USB-Export ergänzt.
- getrennte ROM-/BIOS-Eigen-Dump-Ordner ergänzt.
- Web-UI erweitert und mobilfreundlich gehalten.
- Dokumentation vollständig aktualisiert.

## Nächste sinnvolle Ausbaustufe
Eine spätere v8 kann – nach verifizierter Kompatibilität – einen bestätigten Remote-Package-Installer-Workflow, Gerätepaarung/gespeicherte PS4-IP, echten Health-Check, Download-Cache, Updatevergleich, Backup/Restore von Homebrew-Konfigurationen und einen verifizierten PS1-Provider ergänzen.


# Versionshistorie / Changelog

## v8 – Retro Center / PS1 vorbereitet (30.09.2026)
- Retro-Bibliothek als fester Bestandteil des Control Centers umgesetzt.
- Neue API `/api/retro/status` zur Erkennung eigener ROM-/Disc-Dumps und BIOS-Dateien.
- Systemordner für NES, SNES, Sega, GBA, Arcade, PS1 und BIOS angelegt.
- PS1-Erkennung für CUE/BIN, CHD und PBP integriert.
- USB-Export kopiert eigene Retro- und BIOS-Dumps strukturiert und ergänzt SHA-256 im Manifest.
- Web-UI um Retro-Bibliotheksstatus erweitert.
- Retro-Systemdefinitionen zentral in `sources.json` ergänzt.
- PS1-Emulator-Provider technisch vorbereitet, automatische Installation bis zu einer verifizierten nativen PS4-PKG-Quelle gesperrt.
- Versionskennung von v7 auf v8 aktualisiert.

## v7 – Retro PS1 Grundstruktur
- pEMU-Provider für pNES, pSNES, pGEN, pGBA und pFBNeo integriert.
- Retro-Presets und erste USB-Ordnerstruktur eingeführt.
- PS1 als Generation-Grenze dokumentiert, aber noch ohne Bibliotheksverwaltung/Provider.

> Ab v8 wird dieser Changelog bei jeder neuen Version fortgeführt.


## v10 – PS1 Runtime Gate / echte Startvorbereitung (30.09.2026)
- PS1 bleibt höchste Retro-Priorität.
- PS4 RetroBox v1.7-stable als verifizierter PS1-Laufzeitprovider dokumentiert (RetroArch 1.22.2 / mednafen_psx).
- Konsolenprofil-Prüfung ergänzt: CUH-1000/1100 wird gemäß Upstream als getestet freigegeben; PS4 Pro CUH-7xxx wird bewusst blockiert, solange der Upstream keine verifizierte Unterstützung ausweist.
- Neue API `/api/ps1/runtime` für Runtime-/Kompatibilitätsinformationen.
- Neue API `/api/ps1/validate`: prüft bekannte PS1-BIOS-Hashes, CUE-Trackreferenzen sowie CHD/PBP-Spiele.
- Neue API `/api/ps1/prepare`: erzeugt Runtime-Staging nur für freigegebene Konsolenprofile.
- Web-UI um PS1-Prüfung, Konsolenprofil und Runtime-Vorbereitung erweitert.
- Keine fremden Kernel-/Payload-Dateien werden bei einem nicht verifizierten Profil automatisch übertragen.
- Versionskennung auf v10 aktualisiert.
