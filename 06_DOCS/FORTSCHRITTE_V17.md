# HESPERIA v17 – PKG-HTTP kompatibel mit Bytebereichen

- Der lokale Paketserver beantwortet `Range: bytes=...` mit `206 Partial Content`, `Content-Range`, `Accept-Ranges` und passender `Content-Length`.
- Unterstützt werden offene Bereiche (`bytes=START-`), begrenzte Bereiche und Suffixbereiche (`bytes=-N`). Ungültige Bereiche erhalten korrekt `416` statt stillschweigend den falschen Dateianfang.
- HEAD-Anfragen liefern dieselben Range-/Längenmetadaten ohne den Paketinhalt zu übertragen.
- Der PC→PS4-Fortschritt vereinigt tatsächlich übertragene Byteintervalle; Metadaten-Ranges werden nicht als komplette PKG-Übertragung fehlinterpretiert und überlappende Abrufe nicht doppelt gezählt.
- Der RPI-Fortschrittsparser normalisiert nicht standardkonforme hexadezimale Fehlercodes und bewahrt bei anderen Antwortformaten den Rohtext, statt wegen JSON-Parsing abzubrechen.
- v14 Transfermessung, v15 netzwerkadaptergerechte PC-Adresse und v16 dynamischer Port bleiben enthalten.

## Inspiration und technische Grundlage

- Das flatz-RPI-README beschreibt API-Aufträge und Task-Fortschritt: https://github.com/flatz/ps4_remote_pkg_installer
- Das internationale Projekt `ps4-pkg-installer` dokumentiert, dass PS4-PKG-Metadaten an spezifischen Offsets gelesen werden und dafür korrekte HTTP-Range-Antworten entscheidend sind: https://github.com/KonixDev/ps4-pkg-installer
- Die unabhängige Analyse ist eine technische Inspiration, kein offizieller flatz-Supporthinweis.

## Verifikation und Grenzen

- Python- und JavaScript-Syntax sowie der Windows-EXE-Build werden geprüft.
- Der echte RPI-/PS4-End-to-End-Abruf muss mit einer angeschlossenen Konsole im selben LAN bestätigt werden.
