# HESPERIA v16 – dynamischer lokaler Web-Port

- Der aktive Port wird vom Server an die Oberfläche gemeldet und für alle angezeigten PC-/PS4-Adressen verwendet.
- Wenn 8088 belegt ist, wählt der Startprozess einen freien Port aus 8088–8097; die Seitenleiste und die PS4-RPI-URLs bleiben synchron.
- Der Starttext zeigt alle ermittelten PC-LAN-Adressen mit dem Port an, statt nur eine Standardnetzkarte auszugeben.
- Die route-aware PC-Adresse (v15) und der echte PC→PS4-Transferbalken (v14) bleiben aktiv.

## Verifikation und Grenzen

- Python- und JavaScript-Syntax sowie der Windows-EXE-Build werden wiederholt.
- Ein absichtlich belegter Port kann in dieser Umgebung nicht mit einer angeschlossenen PS4 end-to-end validiert werden; der Laufzeit-Port steht im Serverstatus und in allen generierten Installations-URLs.
