# HESPERIA v15 – netzwerkadaptergerechte PC-Adresse

- Beim Verbinden bestimmt Windows über seine Routingtabelle, welche lokale PC-IP für die konkrete PS4 erreichbar ist.
- Diese Adresse erscheint nach der Verbindung als „PC-Adresse für PS4“ und wird in den Installations-URLs der RPI-Aufträge verwendet.
- Vor der PS4-Verbindung zeigt die Seitenleiste alle ermittelten privaten PC-Adressen an, damit der PS4-Browser im passenden LAN geöffnet werden kann.
- Der v14-Transferbalken für echte PC→PS4-Bytes und die RPI-Portdiagnose bleiben erhalten.

## Verifikation und Grenzen

- Ein UDP-Routenlookup sendet keine Daten an die Konsole; er fragt nur Windows ab, welche Quell-IP für das Ziel gewählt würde.
- Syntaxprüfung und EXE-Build werden für v15 wiederholt. Der tatsächliche Abruf durch RPI muss im Zielnetz verifiziert werden.
