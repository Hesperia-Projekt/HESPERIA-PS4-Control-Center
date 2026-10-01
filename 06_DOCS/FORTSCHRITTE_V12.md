# HESPERIA v12 – konkrete Fortschritte

1. **Neues Interface:** Dashboard in Schwarz mit PlayStation-blauen Fokus-, Aktions- und Fortschrittsfarben, ausgelegt für PC und PS4-Browser.
2. **Sofortige Startansicht:** Paketkatalog wird lokal geladen; GitHub-Releases werden erst beim Download abgefragt.
3. **Mehr Netzwerkkarten:** PS4-Suche prüft lokale IPv4-/24-Netze statt nur eine einzelne Standardnetzkarte.
4. **Manuelle Verbindung:** PS4-IP kann eingegeben werden, wenn die automatische Suche durch Router-Isolation oder WLAN-Gastnetz nichts findet.
5. **Dienststatus:** Oberfläche zeigt, ob Port 12800 antwortet und die PS4 für RPI-Installationen erreichbar ist.
6. **Erststart-Wizard:** drei sichtbare Schritte für GoldHEN, einmalige RPI-Installation und Verbindung.
7. **RPI-Quelle:** Schnellstart verlinkt eine Community-Paketquelle und die Original-Projektseite. Die Oberfläche sagt ausdrücklich, dass die Originalseite keine fertige PKG-Datei veröffentlicht.
8. **Eigene PKGs importieren:** lokale `.pkg`-Dateien wie YouTube/Homebrew oder RPI lassen sich in HESPERIAs Paketordner übernehmen.
9. **Live-Downloadwerte:** Fortschrittsbalken, übertragene Bytes, aktuelle Geschwindigkeit und ETA werden während des Downloads aktualisiert.
10. **Direkte Installationsauswahl:** Katalogpakete und importierte PKGs können an die verbundene PS4 übergeben werden.
11. **USB-Builder ohne Überschreiben:** ausgewählte Katalogdateien und importierte PKGs landen in einem datierten Ordner mit Manifest und Installationsanleitung.
12. **Aktivitätsanzeige:** Download, Import, Verbindung und USB-Erstellung werden in der Oberfläche protokolliert.
13. **Exakte Paketauswahl:** Der Download-Index bindet jeden Katalogeintrag an genau seine heruntergeladene Datei. Ein breites Release-Muster kann daher nicht mehr andere lokale PKGs in Installationswarteschlange oder USB-Export hineinziehen.
14. **RPI-Dienstprüfung:** Die Erkennung prüft neben Port 12800 auch den dokumentierten RPI-API-Endpunkt, damit ein beliebiger offener Port weniger leicht als installierbereite PS4 erscheint.

## Verifizierte Grenzen

- Die Netzwerkerkennung findet Dienste anhand erreichbarer Ports. Router-Client-Isolation, VLANs oder getrennte Netze können sie verhindern; die manuelle IP-Verbindung bleibt dafür vorhanden.
- RPI muss auf der PS4 einmalig installiert und geöffnet werden, bevor HESPERIA über dessen API installieren kann.
- Die Originalquelle von flatz stellt aktuell Quellcode und API-Dokumentation bereit, aber keine fertige Release-PKG. Die App lädt keine ungeprüfte Binärdatei als „offiziell“ herunter.
- HESPERIA zeigt die PC-Downloadgeschwindigkeit genau. Die Installationsrate auf der PS4 kann zusätzlich nur angezeigt werden, wenn RPI für den Installationsauftrag eine Task-ID zurückgibt und dessen Progress-Endpunkt erreichbar ist.
- YouTube- oder andere nicht im Katalog enthaltene Homebrew-Pakete werden über den lokalen PKG-Import eingebunden; es wird kein fremdes App-Paket vorgetäuscht.

## Internationale Projektideen, die eingeflossen sind

- flatz dokumentiert die RPI-API, direkte Package-URLs, Task-IDs und einen Progress-Endpunkt. Das ist die Grundlage für LAN-Übergabe und die optionale Fortschrittsabfrage.
- GoldHEN dokumentiert mehrere Netzwerkdienste (unter anderem FTP und BinLoader). HESPERIA prüft diese als Hinweise auf einen aktiven PS4-Dienst und lässt manuelle Verbindung als Fallback.
- SSPI zeigt sinnvolle Paketmanager-Muster wie Warteschlange, Resume/Recovery, lokales Staging und installierte Bibliothek. HESPERIA v12 setzt hiervon schnelle lokale Katalogansicht, Download-Auftrag, Import und USB-Staging um; Resume bleibt ein nächster Ausbauschritt.
- PS4 PKG Manager dokumentiert überwachte lokale Ordner. HESPERIAs USB-Builder übernimmt die Grundidee eines verwalteten Paketordners und ergänzt einen Manifest-Export.

Quellen: https://github.com/flatz/ps4_remote_pkg_installer · https://github.com/GoldHEN/GoldHEN · https://github.com/Xyhlo/SSPI · https://github.com/hippie68/ps4-pkg-manager
