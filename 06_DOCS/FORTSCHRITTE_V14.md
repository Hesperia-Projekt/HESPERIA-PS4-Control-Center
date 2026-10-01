# HESPERIA v14 – echter PS4-Downloadfortschritt

- Der lokale HTTP-Server zählt beim Abruf einer PKG durch RPI die tatsächlich an die jeweilige PS4 gesendeten Bytes.
- Für den PC→PS4-Transfer zeigt das Dashboard eigenen Fortschrittsbalken, übertragen/gesamt, aktuelle Geschwindigkeit und geschätzte Restzeit.
- Vor dem ersten PS4-Abruf steht sichtbar „warte auf den Download der PS4 vom PC“; unterbrochene Transfers und vollständig übertragene PKGs erhalten eigene Zustände.
- Die Statistik ist je angeforderter Datei und PS4-IP verfügbar; der Transfer überschreibt nicht mehr die separate Anzeige für PC-Downloads.
- Die bestehende RPI-Installationsabfrage bleibt parallel aktiv, sodass Dateitransfer und Installationsauftrag nicht verwechselt werden.

## Verifikation und Grenzen

- Python-Syntax und Windows-EXE-Build werden für v14 geprüft.
- Geschwindigkeit und Dateigröße beruhen auf Bytes, die der PC-Server an RPI schreibt. Erst wenn die PS4 den Abruf startet, erscheint Fortschritt; die PS4-interne Installationsphase ist weiterhin von der RPI-Progress-API abhängig.
- Ein echter PS4-Lauf ist in dieser Entwicklungsumgebung nicht verfügbar und muss auf dem privaten LAN verifiziert werden.
