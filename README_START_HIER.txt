HESPERIA PS4 CONTROL CENTER v19
=============================
1) 01_START\HESPERIA_PS4_Control_Center_v19.exe starten (alternativ START_HESPERIA_PS4.cmd)
2) Die App öffnet den PC-Browser automatisch; bei belegtem Standardport wählt sie dynamisch einen freien Port zwischen 8088 und 8097.
3) Die Seitenleiste zeigt die vollständigen PC-Adressen mit dem tatsächlich aktiven Port. Für die PS4 die Adresse desselben LANs im PS4-Browser öffnen.
4) GoldHEN auf der eigenen PS4 starten. Im Schnellstart die RPI-Paketquelle öffnen, Remote Package Installer PKG laden und über „Lokale PKG importieren“ in die Bibliothek übernehmen.
5) RPI einmal per USB und normalem Package Installer auf der PS4 installieren, danach die RPI-App öffnen und geöffnet lassen.
6) „PS4 suchen“ wählen. Falls die automatische Suche nichts findet, PS4-IP in Einstellungen > Netzwerk > Verbindungsstatus anzeigen nachsehen und manuell verbinden.
7) Pakete auswählen -> herunterladen. Fortschritt, Geschwindigkeit und geschätzte Restzeit erscheinen live.
8) Danach „An PS4 installieren“ oder „USB-Ordner erstellen“ wählen. Bei Remote-Install zeigt ein zweiter Balken den Transfer vom PC zur PS4 mit Tempo und Restzeit. Der lokale PKG-Server unterstützt HTTP-Bytebereiche, die RPI für PKG-Metadaten benötigt. Die PC-Adresse wird passend zum Netz der verbundenen PS4 ermittelt und angezeigt.

Voraussetzungen für die automatische Installation: eigene PS4, GoldHEN, aktiver Remote Package Installer (üblicherweise Port 12800, manche Builds 12801), PC/PS4 im gleichen privaten Netzwerk und Windows-Firewall-Freigabe für HESPERIA.

Hinweis: Die flatz-Originalseite enthält Quellcode, aber keine fertige PKG-Datei. Die App verlinkt eine Community-Paketquelle und kennzeichnet sie als externe Quelle.

Vollständige Dokumentation:
06_DOCS\PACK_INHALTE_UND_FUNKTIONEN_VOLLSTAENDIG.md

Retro-Hinweise:
09_RETRO\README_RETRO_BIS_PS1.md

Keine Spiele, ROMs, BIOS-Dateien, Keys oder Lizenzen enthalten.


PS1 FIRST: siehe 09_RETRO/README_RETRO_BIS_PS1.md


PS1 v10: Im Retro Center zuerst „PS1 prüfen“, dann Konsolenprofil wählen. Runtime wird nur bei verifiziertem Profil vorbereitet.
