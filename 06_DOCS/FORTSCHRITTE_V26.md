# HESPERIA v26 – PKG-Prüfung und nachvollziehbarer USB-Export

- Import lehnt Dateien ohne PS4-PKG-Kopf `7F 43 4E 54` ab.
- USB-Export prüft installierbare PKGs vor dem Kopieren und vergleicht SHA-256 vor/nach dem Kopieren.
- Das Manifest enthält jetzt Paketname, relativen Pfad, Dateigröße, SHA-256 und Prüfstatus sowie fehlende/abgelehnte Einträge.
- Der Exportstatus zeigt geprüfte Paketanzahl, SHA-256-Ergebnis und Ausschlüsse an.
- Die Prüfung bestätigt nur Container-Kennung und byte-identische Kopie. Sie prüft weder Signatur/Lizenz noch PS4-Firmware-/Title-ID-Kompatibilität oder ob ein Paket rechtmäßig und vertrauenswürdig ist.

Formatreferenz: [LibOrbisPkg PKG parser](https://github.com/maxton/LibOrbisPkg/blob/master/LibOrbisPkg/PKG/Pkg.cs) definiert `MAGIC = "\\u007FCNT"`.
