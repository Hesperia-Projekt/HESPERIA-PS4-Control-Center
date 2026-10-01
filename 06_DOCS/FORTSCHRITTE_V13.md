# HESPERIA v13 – Port-Erkennung präzisiert

- Port 12800 (offizielle flatz-RPI-API) und Port 12801 (verbreitete alternative Builds) werden geprüft.
- RPI-Ports erhalten bei der Erkennung ein längeres Antwortfenster. Das behebt den Fall, dass die PS4 gefunden und RPI bestätigt wird, die kurze Portprobe aber zuvor „geschlossen“ gespeichert hatte.
- Sobald die RPI-API bestätigt wurde, wird ihr konkreter Port auch in der Dienstliste als offen angezeigt.
- Der Verbindungsstatus zeigt die PS4-IP und den aktiven RPI-Port; bei Fehlschlag unterscheidet die App „Port geschlossen“ von „Port offen, API nicht passend“.
- Die Installationsfortschrittsabfrage verwendet den erkannten Port statt starr Port 12800 anzunehmen.
- Paketkatalog, Download, Fortschrittsanzeige, lokaler PKG-Import und USB-Auswahl bleiben im bisherigen lokalen Ablauf erhalten.

## Verifikation und Grenzen

- Python-Syntax wurde vor dem Build kompiliert; Windows-EXE-Build v13 wurde erfolgreich erstellt.
- Eine echte Installation konnte hier nicht gegen die konkrete PS4 geprüft werden. Dafür muss RPI auf der PS4 im Vordergrund laufen; PC und PS4 müssen im selben LAN erreichbar sein.
- Das flatz-README nennt Port 12800 und dokumentiert `/api/is_exists` sowie `/api/install`: https://github.com/flatz/ps4_remote_pkg_installer
