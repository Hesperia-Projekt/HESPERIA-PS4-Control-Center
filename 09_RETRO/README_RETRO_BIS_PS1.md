# HESPERIA Retro Center – v9 PS1 FIRST

## PS1 ist Kernfunktion
PS1 wird nicht mehr als Platzhalter behandelt. v9 validiert eigene BIOS-Dumps, erkennt CUE/BIN, CHD, PBP sowie weitere Libretro-PS1-Formate und unterstützt Multi-Disc-Sammlungen über M3U.

## Laufzeit
Der derzeit verifizierte PS4-Laufzeitweg ist **PS4 RetroBox** (Linux auf jailbroken PS4) mit RetroArch/`mednafen_psx`. Dieser Weg ist optional und wird ausdrücklich als Linux-Runtime gekennzeichnet. Ein nativer Orbis-PKG-Provider bleibt reserviert, wird aber erst aktiviert, wenn eine belastbare Quelle verifiziert ist.

## BIOS
Eigene BIOS-Dumps in `09_RETRO/LIBRARY/BIOS`. Das Center berechnet MD5 und vergleicht bekannte Retail-BIOS-Hashes. BIOS-Dateien werden nicht mitgeliefert.

## Multi-Disc
Für Spiele mit mehreren CDs `.m3u` verwenden. Eine Zeile pro Disc-Datei, z.B. `Game (Disc 1).chd`. Das Center prüft, ob alle referenzierten Discs vorhanden sind.

## Formate
CHD, CUE/BIN, PBP, M3U, CCD, IMG, ISO, MDF, TOC, CBN. CHD ist für eine kompakte Bibliothek besonders sinnvoll.

## Rechtliches
Keine kommerziellen Spiele oder BIOS-Dateien sind enthalten. Nur eigene rechtmäßig erstellte Dumps verwenden.


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
