# HESPERIA Tool -- PS4 Mod & Cheat Module

**Master-Spezifikation, Architektur, UX, Datenmodell, Integrationsplan
und Entwicklungs-Handbuch**\
Version: 1.0 · Stand: 17.09.2026 · Zielplattform: HESPERIA Tool /
Windows-Host + PlayStation 4 mit GoldHEN

> Dieses Dokument ist als vollständige Arbeitsgrundlage für Codex
> gedacht. Es beschreibt nicht nur die Oberfläche, sondern auch
> Komponenten, Datenflüsse, Update-Strategie, Fehlerbehandlung, Tests,
> Sicherheitsgrenzen, Migrationspfade und konkrete Akzeptanzkriterien.
> Es ist absichtlich so strukturiert, dass einzelne Kapitel direkt als
> Codex-Arbeitspakete verwendet werden können.

------------------------------------------------------------------------

## 0. Auftrag an Codex

Entwickle das PS4-Modul als **integrierten Bestandteil des HESPERIA
Tools**. Die bisherige CMD ist ein Prototyp und dient nur als Referenz
für Funktionsumfang und Bedienidee. Die endgültige Implementierung soll
keine Sammlung loser Batch-Dateien sein, sondern ein wartbares Modul mit
klarer Trennung zwischen UI, Geschäftslogik, Download-Providern,
PS4-Transport, Datenbank, Logging und Tests.

Das Modul soll legale Homebrew-, Modding-, Cheat-, Patch-, Theme- und
Verwaltungsfunktionen bündeln. Es soll **keine urheberrechtlich
geschützten Spiele, DLCs, Lizenzdateien, Keys, Accounts oder
Umgehungsmechanismen zur Beschaffung kommerzieller Inhalte verteilen**.
Cheats und Patches werden nur aus transparent dokumentierten Quellen
bezogen. Aktionen, die Spielstände oder Systemdateien verändern, müssen
vor Ausführung klar angezeigt und -- wo sinnvoll -- durch Backup/Restore
abgesichert werden.

### Primärziele

1.  PS4 erkennen, verbinden und Zustand verständlich anzeigen.
2.  GoldHEN-kompatible Cheats, Patches und Plugins verwalten.
3.  CUSA-ID, Region und App-Version automatisch gegen verfügbare Inhalte
    abgleichen.
4.  Itemzflow und Customizing als optionalen Bereich integrieren.
5.  USB- und Netzwerk-Workflows anbieten.
6.  Downloads reproduzierbar, prüfbar und updatefähig machen.
7.  Fehlbedienung verhindern: keine automatische Formatierung, kein
    blindes Überschreiben, keine geratenen URLs.
8.  Das Modul so kapseln, dass spätere PS4-Funktionen ohne Umbau des
    gesamten HESPERIA Tools ergänzt werden können.

### Aktuell verifizierte öffentliche Grundlagen

-   GoldHEN unterstützt laut aktuellem Release u. a. Firmware 9.60; das
    Cheat-Menü ist experimentell und der Cheat Downloader ist
    Bestandteil neuerer Builds:
    https://github.com/GoldHEN/GoldHEN/releases
-   Offizielle GoldHEN Cheat Database, Formate JSON/SHN/MC4 und
    Speicherpfade: https://github.com/GoldHEN/GoldHEN_Cheat_Repository
-   PS4 Cheats Manager von bucanero; Online-Zugriff auf Cheat- und
    Patch-Datenbanken und `make createzip` für eingebettete Daten:
    https://github.com/bucanero/PS4CheatsManager
-   GoldHEN Plugins:
    https://github.com/GoldHEN/GoldHEN_Plugins_Repository
-   Aktuelle Patch-Datenbank/Offline-USB-Verfahren:
    https://github.com/Djvttx/GoldHEN_Patch_Repository
-   Itemzflow 1.08 für PS4 und offizielle Download-Verweisung:
    https://github.com/LightningMods/Itemzflow/releases
-   Itemzflow Themes/Logs/Patch-Integration:
    https://github.com/LightningMods/Itemzflow/blob/main/README.md

------------------------------------------------------------------------

::: {style="page-break-before: always;"}
:::

# 1. Produktvision und Grenzen

Das PS4-Modul soll sich wie ein natives HESPERIA-Modul anfühlen: ruhig,
verständlich, lokal-first und mit möglichst wenigen Klicks. Ein Nutzer
soll nicht wissen müssen, in welchem Verzeichnis GoldHEN Cheats erwartet
oder wie eine CUSA-ID aufgebaut ist. Das Modul übersetzt technische
Details in klare Zustände wie **Kompatibel**, **Versionsabweichung**,
**Nicht installiert**, **Update verfügbar** oder **Backup empfohlen**.

Der wichtigste Architekturgrundsatz lautet: **Erkennen → Prüfen →
Vorschau → Sichern → Anwenden → Verifizieren → Protokollieren**. Keine
schreibende Aktion darf diesen Ablauf umgehen. Downloads sind zunächst
Artefakte im lokalen Cache. Erst nach Validierung werden sie für USB
oder Netzwerkbereitstellung freigegeben.

Nicht-Ziele sind ein PSN-Ersatz, die Verteilung kommerzieller PKGs,
Lizenz-/Account-Manipulation, automatische Systemdatei-Patches
unbekannter Herkunft oder ein Mechanismus zum Verbergen von
Online-Cheating. Das Modul ist für lokale Homebrew-, Einzelspieler-,
Test- und Customizing-Workflows ausgelegt.

**Definition of Done:** Das Modul kann unabhängig gestartet, getestet
und deaktiviert werden; ein Ausfall eines Providers legt nicht das
HESPERIA Tool lahm; jede Änderung ist im Aktivitätsprotokoll
nachvollziehbar; alle Pfade und URLs sind konfigurierbar oder aus
verifizierten Provider-Metadaten abgeleitet.

::: {style="page-break-before: always;"}
:::

# 2. Zielnutzer und Hauptszenarien

Die UI muss sowohl Einsteiger als auch erfahrene GoldHEN-Nutzer
bedienen. Im Standardmodus werden nur sichere, häufige Aktionen gezeigt.
Ein Expertenmodus blendet Rohpfade, Hashes, CUSA-Mappings,
Providerstatus und Plugin-Konfiguration ein.

Hauptszenarien: (a) PS4 verbinden und Inventar einlesen; (b) Cheats für
installierte Spiele finden; (c) passende Game-Patches wie
FPS-/Grafik-Patches anzeigen; (d) Plugin-Bestand verwalten; (e)
Itemzflow und Themes vorbereiten; (f) Offline-USB-Stick erzeugen; (g)
vorhandene Datenbank aktualisieren; (h) Save-Backup vor riskanten
Änderungen; (i) Diagnosepaket für Fehlersuche erzeugen; (j) alle
Änderungen rückgängig machen, soweit technisch möglich.

Jeder Workflow erhält einen Assistenten mit maximal fünf sichtbaren
Schritten. Fachbegriffe bekommen kurze Tooltips. Der Nutzer darf
jederzeit zur Detailansicht wechseln, ohne den aktuellen Vorgang zu
verlieren.

::: {style="page-break-before: always;"}
:::

# 3. Informationsarchitektur der Oberfläche

Empfohlene Navigation innerhalb des HESPERIA Tools:

-   **Übersicht** -- PS4-Status, GoldHEN-Status, Firmware, Netzwerk,
    Speicher, letzte Synchronisierung.
-   **Spiele** -- installierte Titel, CUSA, Version, Region, erkannte
    Cheats/Patches.
-   **Cheats** -- Datenbank, Kompatibilität, Aktivierungsstatus,
    Favoriten.
-   **Patches** -- FPS/Grafik/QoL-Patches mit Voraussetzungen und
    Konflikten.
-   **Plugins** -- installierte/verfügbare PRX-Plugins und
    `plugins.ini`-Editor.
-   **Customizing** -- Itemzflow, Themes, Wallpaper, Musik, Fonts.
-   **Transfer** -- Netzwerk, FTP, USB, Warteschlange.
-   **Backups** -- Saves, Konfigurationen, Manifeste, Restore.
-   **Diagnose** -- Logs, Providerstatus, Verbindungstest, Export.
-   **Einstellungen** -- Pfade, Cache, Expertenmodus, Updatekanäle.

Die Startseite soll keine technische Wand sein. Ein Beispiel: „23 Spiele
erkannt · für 11 Spiele Cheats verfügbar · 7 passende Patches · 2
Versionskonflikte · Datenbank vor 3 Tagen aktualisiert". Von dort führen
Karten direkt zu den betroffenen Titeln.

::: {style="page-break-before: always;"}
:::

# 4. Technische Gesamtarchitektur

Das Modul wird in Schichten aufgebaut:

``` text
HESPERIA Shell / Navigation
        |
PS4 Module UI + ViewModels
        |
Application Services
  |       |       |       |
Catalog  Match   Transfer Backup
  |       |       |       |
Provider Adapters / PS4 Adapters
        |
HTTP · GitHub API · FTP · USB · Local FS
        |
SQLite/JSON Cache + immutable artifacts
```

UI-Code darf niemals direkt GitHub, FTP oder USB ansprechen. Jede
externe Quelle implementiert ein gemeinsames Provider-Interface.
Netzwerk- und Dateisystemaktionen laufen asynchron und sind abbrechbar.
Das Modul soll nach einem Absturz den letzten konsistenten Zustand aus
der lokalen Datenbank rekonstruieren können.

Für die HESPERIA-Integration empfiehlt sich ein Modulvertrag mit
`Initialize`, `GetNavigationItems`, `GetHealth`, `HandleDeepLink`,
`Shutdown`. Interne Services werden über Dependency Injection
registriert. Provider werden per Konfiguration aktiviert und können
später ohne UI-Umbau ersetzt werden.

::: {style="page-break-before: always;"}
:::

# 5. Verzeichnis- und Cachekonzept

Empfohlene lokale Struktur:

``` text
HesperiaData/
  modules/ps4/
    config/
      ps4-module.json
      providers.json
    db/
      ps4.sqlite
    cache/
      downloads/
      metadata/
      covers/
    artifacts/
      cheats/
      patches/
      plugins/
      itemzflow/
      themes/
    custom/
      wallpapers/
      music/
      fonts/
      themes/
    backups/
      consoles/<console-id>/<timestamp>/
    logs/
    exports/
```

Downloads werden zuerst als `.partial` geschrieben. Nach erfolgreichem
Abschluss wird Hash und Größe gespeichert und anschließend atomar
umbenannt. Cache-Einträge haben Provider, Quell-URL, Abrufzeit,
ETag/Last-Modified, SHA-256 und optional Release-Tag. Ein Cache-Cleanup
darf niemals Backups oder benutzerdefinierte Inhalte löschen.

::: {style="page-break-before: always;"}
:::

# 6. Datenmodell

SQLite ist für Katalog, Match-Ergebnisse, Verlauf und Backups sinnvoll.
Große Binärdateien bleiben im Dateisystem. Kernentitäten:

``` sql
CREATE TABLE consoles(
 id TEXT PRIMARY KEY, name TEXT, ip TEXT, firmware TEXT,
 goldhen_version TEXT, last_seen TEXT, capabilities_json TEXT);
CREATE TABLE games(
 console_id TEXT, title_id TEXT, title TEXT, app_version TEXT,
 region TEXT, install_path TEXT, last_seen TEXT,
 PRIMARY KEY(console_id,title_id));
CREATE TABLE artifacts(
 id TEXT PRIMARY KEY, kind TEXT, provider TEXT, title_id TEXT,
 app_version TEXT, version TEXT, source_url TEXT, sha256 TEXT,
 local_path TEXT, fetched_at TEXT, metadata_json TEXT);
CREATE TABLE actions(
 id INTEGER PRIMARY KEY AUTOINCREMENT, ts TEXT, console_id TEXT,
 action TEXT, status TEXT, details_json TEXT);
```

Weitere Tabellen: `providers`, `matches`, `plugins`, `themes`,
`backups`, `transfer_jobs`, `settings`, `health_checks`.
Datenbankmigrationen sind versioniert. Jede Migration besitzt
Up-/Down-Strategie oder eine dokumentierte irreversible Grenze.

::: {style="page-break-before: always;"}
:::

# 7. Provider-System

Ein Provider liefert Metadaten und optional Artefakte. Er kennt seine
Quelle; die restliche Anwendung kennt nur normalisierte Modelle.

``` csharp
public interface IPs4ContentProvider {
    string Id { get; }
    Task<ProviderHealth> CheckHealthAsync(CancellationToken ct);
    Task<IReadOnlyList<ArtifactDescriptor>> RefreshCatalogAsync(CancellationToken ct);
    Task<DownloadedArtifact> DownloadAsync(ArtifactDescriptor item, CancellationToken ct);
}
```

Erste Provider: `GoldHenCheatProvider`, `GamePatchProvider`,
`GoldHenPluginProvider`, `Ps4CheatsManagerProvider`,
`ItemzflowProvider`, `ItemzflowThemeProvider`. Für GitHub wird die
Releases/API-Antwort verwendet; harte Asset-URLs sind zu vermeiden.
Falls ein offizielles Release lediglich auf eine externe Downloadseite
verweist, wird diese Information sichtbar gemacht und nicht durch eine
erfundene Direkt-URL ersetzt.

Providerfehler sind isoliert. Die Übersicht zeigt z. B. „Cheats: OK ·
Patches: OK · Itemzflow: manuelle Quelle · Plugins: temporär nicht
erreichbar". Ein Provider darf niemals vorhandene funktionierende Daten
löschen, nur weil ein Refresh scheitert.

::: {style="page-break-before: always;"}
:::

# 8. PS4-Verbindung und Capability Detection

Das Modul darf nicht einfach annehmen, dass jede PS4 dieselben
Fähigkeiten besitzt. Nach Verbindung wird ein Capability-Profil
aufgebaut: Firmware, GoldHEN-Version, FTP verfügbar, Plugin-Support,
Cheat-Menü, Patch-Engine, erreichbare Pfade, freier Speicher und
optional Itemzflow.

Die Verbindung erhält drei Modi: **Nur prüfen**, **Lesen**, **Lesen &
Schreiben**. Schreibzugriff wird erst bei einer konkreten Aktion
benötigt. Zugangsdaten werden nicht im Klartext geloggt. IP und Port
sind editierbar; ein automatischer LAN-Scan ist optional und muss
abschaltbar sein.

Fehlerzustände werden differenziert: Host nicht erreichbar, Port
geschlossen, Authentifizierung, Timeout, unerwartete
Verzeichnisstruktur, unzureichender Speicher, Transfer abgebrochen. Ein
„Verbindung testen"-Dialog zeigt jeden Teilschritt mit Laufzeit.

::: {style="page-break-before: always;"}
:::

# 9. Spieleinventar und CUSA-Erkennung

Das Spieleinventar ist der Mittelpunkt des Matchings. Für jeden Titel
werden mindestens Title-ID/CUSA, Anzeigename und App-Version benötigt.
Region wird nur angezeigt, wenn sie zuverlässig ableitbar ist; keine
Vermutung anhand des Namens.

Die UI gruppiert Dubletten und zeigt Updates getrennt vom Basistitel.
Bei unbekannter Version lautet der Zustand **Version nicht ermittelt**,
nicht „kompatibel". Das Matching ist streng: exakte CUSA + exakte
unterstützte App-Version ist grün; CUSA passend, Version
unbekannt/abweichend ist gelb; andere CUSA ist rot. Ein Expertenmodus
darf alternative Einträge zeigen, aber niemals automatisch anwenden.

::: {style="page-break-before: always;"}
:::

# 10. Cheat-System

Die offizielle GoldHEN Cheat Database unterstützt mehrere Formate. Das
Modul normalisiert Einträge, verändert die Originaldateien jedoch nicht.
Originalartefakt und normalisierte Metadaten werden getrennt
gespeichert.

Cheat-Ansicht pro Spiel: Name, Autor, Format, unterstützte App-Version,
Quelle, Datum, Risikohinweis, bekannte Konflikte. Mehrere Cheat-Dateien
für denselben Titel werden nicht automatisch zusammengeführt. Der Nutzer
kann Favoriten markieren und inkompatible Einträge ausblenden.

GoldHEN selbst bezeichnet das Cheat-Menü als experimentell. Deshalb wird
vor erstmaliger Cheat-Nutzung eines Spiels ein Save-Backup empfohlen.
Das Modul soll keine Cheats automatisch einschalten. Es verwaltet Daten,
Kompatibilität und Transfer; die Aktivierung im laufenden Spiel bleibt
eine bewusste Aktion des Nutzers.

Für Offline-Packs kann die aktuelle Datenbank als ZIP gecacht werden.
Der PS4 Cheats Manager unterstützt direkten Online-Zugriff auf Cheat-
und Patch-Datenbanken; beide Wege sollen nebeneinander existieren.

::: {style="page-break-before: always;"}
:::

# 11. Patch-System

Game-Patches werden getrennt von Cheats behandelt. Ein Patch kann
Performance, Framerate, Auflösung, FOV oder andere Laufzeitparameter
verändern. Die aktuelle Community-Datenbank verwendet XML und
Title-ID/App-Version-Metadaten. Der bekannte GoldHEN-Pfad ist
`/user/data/GoldHEN/patches/xml/`.

Das Modul liest Patch-Metadaten und erzeugt eine konfliktbewusste
Ansicht. Zwei Patches, die dieselben Speicherbereiche verändern, dürfen
nicht als konfliktfrei dargestellt werden, sofern dies aus Metadaten
oder einer statischen Analyse erkennbar ist. Ist es nicht erkennbar,
lautet der Status **Konflikt unbekannt**.

Offline-USB soll den von der Patch-Datenbank dokumentierten Weg
unterstützen: vorbereitete Patch-ZIP im USB-Root bzw. interne
HDD-Variante, anschließend Update im Cheat Manager. Die Implementierung
muss Provider-Metadaten verwenden, damit Dateinamenänderungen nicht
durch fest verdrahtete Annahmen brechen.

::: {style="page-break-before: always;"}
:::

# 12. Plugin-Manager

GoldHEN Plugins werden in `/data/GoldHEN/plugins/` abgelegt und über
`/data/GoldHEN/plugins.ini` aktiviert. Das Modul braucht daher zwei
Ebenen: **installiert** und **aktiviert**. Download allein bedeutet
niemals Aktivierung.

Plugin-Karte: Name, Version, Beschreibung, Quelle, benötigte
GoldHEN-Version, bekannte Inkompatibilitäten, Aktivierungsbereich. Vor
Änderung der `plugins.ini` wird eine versionierte Sicherung angelegt.
Der Editor bietet GUI und Rohtextansicht; Speichern validiert Syntax und
referenzierte Dateien.

Ein Safe Mode deaktiviert alle nicht essenziellen Plugins, ohne Dateien
zu löschen. Das ist wichtig, wenn Rest Mode oder ein bestimmtes Spiel
Probleme verursacht. Ein „Letzte Änderung zurücknehmen"-Button stellt
die vorherige Konfiguration wieder her.

::: {style="page-break-before: always;"}
:::

# 13. Itemzflow-Integration

Itemzflow wird als optionaler Game Manager/Customizing-Baustein
behandelt, nicht als Voraussetzung für das PS4-Modul. Der Provider
ermittelt die aktuelle PS4-Version aus dem offiziellen Release. Stand
der Recherche ist PS4-Version 1.08; die Release-Seite verweist für das
PKG auf PKG-Zone.

Funktionen im HESPERIA Tool: Installationsstatus, Versionsvergleich,
Öffnen der offiziellen Bezugsquelle, Theme-Verwaltung, Logs einsammeln,
Patch-Verknüpfung und optionale Home-Redirect-Konfiguration nur nach
ausdrücklicher Bestätigung.

Itemzflow-Logs sollen in Diagnosepakete einbezogen werden. Bekannte
Pfade aus der offiziellen Dokumentation werden als
Provider-Konfiguration hinterlegt, nicht über die UI verstreut.

::: {style="page-break-before: always;"}
:::

# 14. Theme Creator und Customizing

Der Theme Creator ist ein eigener Editor. Er soll Wallpaper, Musik, Font
und Itemzflow-Theme-Assets verwalten. Er arbeitet zerstörungsfrei:
Originalbilder bleiben unangetastet; generierte Varianten liegen in
einem Build-Ordner.

Workflow: Vorlage wählen → Hintergrund importieren → Zuschnitt/Vorschau
→ optionale Schrift/Musik → Theme-Metadaten → Validierung → Build →
USB/Netzwerk bereitstellen. Das Tool warnt bei zu großen Bildern,
unbekannten Formaten und fehlenden Pflichtdateien.

Für die originale PS4-Oberfläche wird nur unterstützt, was ohne riskante
Systemdatei-Manipulation zuverlässig möglich ist. Tiefe
Shell-Modifikationen werden nicht automatisch vorgenommen.
Itemzflow-Themes sind der bevorzugte Weg für umfangreiches visuelles
Customizing.

Ein späteres HESPERIA-Theme kann als mitgelieferte Vorlage existieren:
dunkel, minimalistisch, dezente HESPERIA-Wortmarke, keine überladene
Hacker-Ästhetik.

::: {style="page-break-before: always;"}
:::

# 15. USB Builder

Der USB Builder übernimmt die sichere Idee der bisherigen CMD und
professionalisiert sie. Er listet Wechseldatenträger mit
Laufwerksbuchstabe, Label, Größe, Dateisystem und freiem Platz. **Er
formatiert standardmäßig nie.** Ein Formatierungsassistent wäre, falls
überhaupt implementiert, ein getrenntes Expertenfeature mit doppelter
Bestätigung und eindeutiger Datenträgeridentifikation.

Der Builder erzeugt ein Manifest mit SHA-256, Quelle und Erstellzeit.
Profile: `Minimal` (Manager + benötigte Dateien), `Offline Complete`
(Datenbanken + Plugins + Dokumentation), `Custom` (Auswahl). Vor
Kopieren wird benötigter Speicher berechnet. Nach Kopieren werden Hashes
auf dem Ziel erneut geprüft.

Ein `INSTALLATION.md` wird automatisch passend zum Inhalt erzeugt. Es
nennt keine Schritte für Komponenten, die gar nicht im Pack enthalten
sind.

::: {style="page-break-before: always;"}
:::

# 16. Netzwerktransfer

Netzwerktransfer nutzt eine Warteschlange mit Resume, Retry und
Verifikation. FTP-Ziele werden aus einer zentralen Pfaddefinition
bezogen. Der Nutzer sieht Quelle, Ziel, Größe, Fortschritt,
Geschwindigkeit und ETA. Abbruch hinterlässt keine Datei, die später
fälschlich als vollständig gilt.

Schreibaktionen verwenden nach Möglichkeit temporäre Namen und
anschließendes Rename. Konfigurationsdateien werden vor Überschreiben
lokal gesichert. Bei Verbindungsabbruch wird der Job auf
**unterbrochen** gesetzt und kann fortgesetzt oder verworfen werden.

Ein Dry-Run zeigt vorab alle geplanten Änderungen: „3 Dateien neu, 1
Datei ersetzt, 0 gelöscht". Das ist für Experten und Fehlersuche
besonders wichtig.

::: {style="page-break-before: always;"}
:::

# 17. Backup- und Restore-System

Backups sind kein Zusatz, sondern Querschnittsfunktion. Mindestens
Konfigurationen, Plugin-INI, Cheat-/Patch-Bestand und vom Nutzer
ausgewählte Saves werden versioniert. Backups erhalten Console-ID, Zeit,
Firmware, GoldHEN-Version und Inhaltsmanifest.

Restore bietet drei Ebenen: einzelne Datei, Komponentenzustand,
vollständiges Modul-Backup. Vor Restore wird der aktuelle Zustand
wiederum gesichert, sofern genügend Speicher vorhanden ist. Backups
können exportiert werden, enthalten aber keine unnötigen
personenbezogenen Daten.

Retention: z. B. letzte 10 automatische Konfigurationsbackups + manuell
angeheftete Backups unbegrenzt. Löschregeln sind transparent und
abschaltbar.

::: {style="page-break-before: always;"}
:::

# 18. Update-Engine

Updates werden in **Anwendung**, **Providerkataloge**, **Datenbanken**
und **Artefakte** getrennt. Dadurch kann eine Cheat-Datenbank
aktualisiert werden, ohne das HESPERIA Tool selbst zu aktualisieren.

Provider verwenden ETag/Last-Modified, Release-Tags oder Commit-Hashes.
Ein Update schreibt zuerst in Staging, validiert und schaltet danach
atomar auf die neue Version. Die vorherige Version bleibt bis zum
erfolgreichen Abschluss verfügbar.

Kanäle: Stable standardmäßig; Nightly nur im Expertenmodus und deutlich
markiert. Nightly-Artefakte werden niemals automatisch installiert.

::: {style="page-break-before: always;"}
:::

# 19. Logging und Diagnose

Logs sind strukturiert und menschenlesbar. Jedes Ereignis besitzt
Timestamp, Severity, Component, Operation-ID und Nachricht. Secrets,
Passwörter oder Tokens werden maskiert. Ein Diagnoseexport enthält
Modulversion, Betriebssystem, Providerstatus, relevante Logs,
anonymisierte Konfiguration und optional vom Nutzer ausgewählte
PS4-Logs.

Die UI bietet „Problembericht erstellen". Vor Export wird exakt
angezeigt, welche Dateien enthalten sind. Ein ZIP kann lokal gespeichert
werden; automatisches Hochladen findet nicht statt.

Fehlerdialoge enthalten eine kurze Meldung, einen technischen
Detailbereich und eine konkrete nächste Aktion. Beispiel:
„Cheat-Datenbank konnte nicht aktualisiert werden. Die vorhandene
Datenbank bleibt aktiv. \[Erneut versuchen\] \[Details\]".

::: {style="page-break-before: always;"}
:::

# 20. Sicherheitsmodell

Sicherheitsprinzipien: Least Privilege, keine geheimen Daten im Log,
Hash-Verifikation, Provider-Allowlist, HTTPS, keine Shell-Kommandos aus
ungeprüften Metadaten, Pfadnormalisierung gegen Directory Traversal,
Größenlimits für Archive, sichere ZIP-Extraktion und atomare
Schreibvorgänge.

Archive werden vor Extraktion geprüft. Ein Eintrag wie
`../../plugins.ini` muss verworfen werden. Symlinks aus fremden Archiven
werden nicht blind übernommen. Downloads bekommen ein
Maximalgrößenlimit, das pro Provider angepasst werden kann.

Das Modul unterscheidet **vertrauenswürdige Quelle**,
**Community-Quelle** und **lokale Datei**. Vertrauen ist keine Garantie
für Kompatibilität; deshalb bleibt das CUSA/App-Version-Matching
unabhängig davon zwingend.

::: {style="page-break-before: always;"}
:::

# 21. UX-Zustände und Farblogik

Farben dürfen nie die einzige Informationsquelle sein. Jeder Zustand
besitzt Icon + Text. Empfohlene Semantik: grün „exakt kompatibel", gelb
„prüfen", rot „nicht kompatibel/Fehler", blau „Information/Update", grau
„nicht verfügbar".

Jede Spielekarte zeigt höchstens fünf Primärinformationen. Details
wandern in einen ausklappbaren Bereich. Eine Suche filtert Titel, CUSA
und Tags. Filter: Cheats verfügbar, Patches verfügbar, Versionskonflikt,
Favoriten, zuletzt gespielt/erkannt.

Bulk-Aktionen sind möglich, aber standardmäßig nur für
Downloads/Backups; nicht für massenhafte Aktivierung riskanter Patches.

::: {style="page-break-before: always;"}
:::

# 22. Einstellungen

Einstellungen werden in Kategorien gegliedert: Verbindung, Downloads,
Cache, Backups, Provider, Expertenmodus, Darstellung. Jede Einstellung
hat Default und Reset. Konfigurationsschema wird versioniert.

Wichtige Optionen: Standard-PS4, FTP-Port, Timeout, parallele Downloads,
Cachelimit, automatische Katalogaktualisierung, Backup vor
Schreibaktion, Diagnoselevel, Theme-Vorschau, Updatekanal.
Expertenoptionen sind nicht versteckt, aber klar getrennt.

::: {style="page-break-before: always;"}
:::

# 23. Deep Links und HESPERIA-Integration

Das HESPERIA Tool sollte interne Deep Links unterstützen, z. B.
`hesperia://ps4/game/CUSA12345`, `hesperia://ps4/cheats`,
`hesperia://ps4/diagnostics`. Dadurch können globale Suche,
Benachrichtigungen und spätere Module direkt in einen PS4-Kontext
springen.

Globale HESPERIA-Updates dürfen PS4-Provider nicht blockieren. Das
PS4-Modul liefert Health und Badge-Zähler an die Shell: verfügbare
Updates, Fehler, aktive Transfers.

::: {style="page-break-before: always;"}
:::

# 24. Codex-Arbeitsweise und Branch-Strategie

Codex soll in kleinen, überprüfbaren Schritten arbeiten. Empfohlene
Reihenfolge: Domainmodelle → Persistenz → Provider → Matching → Transfer
→ UI → USB → Customizing → Diagnose → Tests. Jeder Schritt endet mit
Build + Tests + kurzem Changelog.

Branches/Commits sollen nach Feature geschnitten sein. Keine riesige
Einmaländerung. Vor Refactoring vorhandene HESPERIA-Konventionen prüfen.
Bestehende gemeinsame Download-/Logging-/Settings-Komponenten
wiederverwenden, sofern sie die Anforderungen erfüllen.

Bei Unsicherheit über Framework oder vorhandene Architektur zuerst
Repository analysieren und einen Integrationsplan erzeugen; nicht
parallel eine zweite Infrastruktur erfinden.

::: {style="page-break-before: always;"}
:::

# 25. Teststrategie

Testpyramide: viele Unit-Tests für Parser/Matcher/Pfade;
Integrationstests für Provider und SQLite; wenige UI-/End-to-End-Tests.
Externe Provider werden in Tests über gespeicherte Fixtures simuliert.
Live-Tests sind separat und dürfen CI nicht unzuverlässig machen.

Pflichttests: exaktes CUSA-Matching, Versionsabweichung, unbekannte
Version, kaputtes ZIP, Zip-Slip, HTTP 404/429/500, Timeout, USB entfernt
während Transfer, FTP-Abbruch, voller Datenträger, beschädigter Cache,
Datenbankmigration, Rollback, ungültige plugins.ini, doppelter Titel,
Unicode-Titel, sehr lange Pfade.

Jeder Bugfix erhält nach Möglichkeit einen Regressionstest.

::: {style="page-break-before: always;"}
:::

# 26. Release- und Qualitätskriterien

Ein Release Candidate ist erst zulässig, wenn: alle kritischen Tests
grün sind; kein Provider eine harte, ungeprüfte Asset-URL benötigt;
Offlinebetrieb mit vorhandenem Cache funktioniert; USB Builder nichts
formatiert; Backups wiederherstellbar sind; Logs keine Secrets
enthalten; alle Schreibaktionen eine Vorschau besitzen; die Anwendung
nach Providerfehlern weiterläuft.

Performanceziele: Start mit lokalem Katalog \<2 s auf typischem PC;
1.000 Katalogeinträge filtern \<100 ms; UI bleibt während Downloads
responsiv; Hashing läuft im Hintergrund mit Fortschritt. \## 28.
Implementierungskarte: Console Discovery

**Zweck.** Diese Komponente kapselt LAN-Erkennung, manuelle IP,
Capability-Profil. Sie darf keine Verantwortung aus benachbarten
Schichten übernehmen. UI, Persistenz und Transport werden über
Interfaces angebunden, damit Tests ohne echte PS4 und ohne Internet
laufen können.

**Eingaben.** Normalisierte Konfiguration, CancellationToken, optional
ConsoleContext und bereits validierte Artefakt-Metadaten. Ungeprüfte
Texte aus Netzwerkquellen gelten grundsätzlich als nicht
vertrauenswürdig. Pfade werden vor Nutzung normalisiert; URLs werden
gegen das Provider-Schema geprüft.

**Ausgaben.** Ein typisiertes Ergebnisobjekt mit Status (`Success`,
`Warning`, `Failed`, `Cancelled`), maschinenlesbarem Fehlercode,
benutzerfreundlicher Kurzmeldung und technischen Details für das Log.
Exceptions dürfen die UI-Grenze nicht ungefiltert überschreiten.

**Ablauf.** 1. Voraussetzungen prüfen. 2. Eingaben validieren. 3.
Dry-Run bzw. Plan erzeugen. 4. Falls schreibend: Backup/Checkpoint. 5.
Operation in Staging ausführen. 6. Ergebnis validieren. 7. Atomar
übernehmen. 8. Action Journal schreiben. 9. UI aktualisieren. Bei
Fehlern wird Staging verworfen und der vorherige konsistente Zustand
beibehalten.

**Fehlerfälle.** Netzwerkverlust, Provideränderung, fehlende
Berechtigung, voller Datenträger, ungültiges Archiv, Versionskonflikt,
Benutzerabbruch und unerwartete Daten müssen getrennte Codes besitzen.
Ein Retry ist nur für idempotente Schritte automatisch erlaubt.
Schreibaktionen werden nicht blind wiederholt.

**Tests.** Happy Path, leere Eingabe, beschädigte Metadaten,
Cancellation, Timeout, doppelter Aufruf, Wiederanlauf nach Abbruch und
mindestens ein Sicherheitsfall. Dateisystem- und HTTP-Zugriffe werden
gemockt. Integrationstest nutzt ein temporäres Verzeichnis und
deterministische Fixtures.

**Akzeptanzkriterien.** Die Funktion ist über die HESPERIA-UI
erreichbar, vollständig abbrechbar, erzeugt verständliche Logs,
verändert bei Dry-Run nichts und hinterlässt bei Fehlschlag keinen halb
installierten Zustand. Dokumentation und Tooltips sind vorhanden.

## 29. Implementierungskarte: Connection Test

**Zweck.** Diese Komponente kapselt Ping/Port/FTP/Pfade getrennt prüfen.
Sie darf keine Verantwortung aus benachbarten Schichten übernehmen. UI,
Persistenz und Transport werden über Interfaces angebunden, damit Tests
ohne echte PS4 und ohne Internet laufen können.

**Eingaben.** Normalisierte Konfiguration, CancellationToken, optional
ConsoleContext und bereits validierte Artefakt-Metadaten. Ungeprüfte
Texte aus Netzwerkquellen gelten grundsätzlich als nicht
vertrauenswürdig. Pfade werden vor Nutzung normalisiert; URLs werden
gegen das Provider-Schema geprüft.

**Ausgaben.** Ein typisiertes Ergebnisobjekt mit Status (`Success`,
`Warning`, `Failed`, `Cancelled`), maschinenlesbarem Fehlercode,
benutzerfreundlicher Kurzmeldung und technischen Details für das Log.
Exceptions dürfen die UI-Grenze nicht ungefiltert überschreiten.

**Ablauf.** 1. Voraussetzungen prüfen. 2. Eingaben validieren. 3.
Dry-Run bzw. Plan erzeugen. 4. Falls schreibend: Backup/Checkpoint. 5.
Operation in Staging ausführen. 6. Ergebnis validieren. 7. Atomar
übernehmen. 8. Action Journal schreiben. 9. UI aktualisieren. Bei
Fehlern wird Staging verworfen und der vorherige konsistente Zustand
beibehalten.

**Fehlerfälle.** Netzwerkverlust, Provideränderung, fehlende
Berechtigung, voller Datenträger, ungültiges Archiv, Versionskonflikt,
Benutzerabbruch und unerwartete Daten müssen getrennte Codes besitzen.
Ein Retry ist nur für idempotente Schritte automatisch erlaubt.
Schreibaktionen werden nicht blind wiederholt.

**Tests.** Happy Path, leere Eingabe, beschädigte Metadaten,
Cancellation, Timeout, doppelter Aufruf, Wiederanlauf nach Abbruch und
mindestens ein Sicherheitsfall. Dateisystem- und HTTP-Zugriffe werden
gemockt. Integrationstest nutzt ein temporäres Verzeichnis und
deterministische Fixtures.

**Akzeptanzkriterien.** Die Funktion ist über die HESPERIA-UI
erreichbar, vollständig abbrechbar, erzeugt verständliche Logs,
verändert bei Dry-Run nichts und hinterlässt bei Fehlschlag keinen halb
installierten Zustand. Dokumentation und Tooltips sind vorhanden.

## 30. Implementierungskarte: Game Inventory

**Zweck.** Diese Komponente kapselt Titel, CUSA, App-Version einlesen.
Sie darf keine Verantwortung aus benachbarten Schichten übernehmen. UI,
Persistenz und Transport werden über Interfaces angebunden, damit Tests
ohne echte PS4 und ohne Internet laufen können.

**Eingaben.** Normalisierte Konfiguration, CancellationToken, optional
ConsoleContext und bereits validierte Artefakt-Metadaten. Ungeprüfte
Texte aus Netzwerkquellen gelten grundsätzlich als nicht
vertrauenswürdig. Pfade werden vor Nutzung normalisiert; URLs werden
gegen das Provider-Schema geprüft.

**Ausgaben.** Ein typisiertes Ergebnisobjekt mit Status (`Success`,
`Warning`, `Failed`, `Cancelled`), maschinenlesbarem Fehlercode,
benutzerfreundlicher Kurzmeldung und technischen Details für das Log.
Exceptions dürfen die UI-Grenze nicht ungefiltert überschreiten.

**Ablauf.** 1. Voraussetzungen prüfen. 2. Eingaben validieren. 3.
Dry-Run bzw. Plan erzeugen. 4. Falls schreibend: Backup/Checkpoint. 5.
Operation in Staging ausführen. 6. Ergebnis validieren. 7. Atomar
übernehmen. 8. Action Journal schreiben. 9. UI aktualisieren. Bei
Fehlern wird Staging verworfen und der vorherige konsistente Zustand
beibehalten.

**Fehlerfälle.** Netzwerkverlust, Provideränderung, fehlende
Berechtigung, voller Datenträger, ungültiges Archiv, Versionskonflikt,
Benutzerabbruch und unerwartete Daten müssen getrennte Codes besitzen.
Ein Retry ist nur für idempotente Schritte automatisch erlaubt.
Schreibaktionen werden nicht blind wiederholt.

**Tests.** Happy Path, leere Eingabe, beschädigte Metadaten,
Cancellation, Timeout, doppelter Aufruf, Wiederanlauf nach Abbruch und
mindestens ein Sicherheitsfall. Dateisystem- und HTTP-Zugriffe werden
gemockt. Integrationstest nutzt ein temporäres Verzeichnis und
deterministische Fixtures.

**Akzeptanzkriterien.** Die Funktion ist über die HESPERIA-UI
erreichbar, vollständig abbrechbar, erzeugt verständliche Logs,
verändert bei Dry-Run nichts und hinterlässt bei Fehlschlag keinen halb
installierten Zustand. Dokumentation und Tooltips sind vorhanden.

## 31. Implementierungskarte: Compatibility Matcher

**Zweck.** Diese Komponente kapselt striktes CUSA- und Versionsmatching.
Sie darf keine Verantwortung aus benachbarten Schichten übernehmen. UI,
Persistenz und Transport werden über Interfaces angebunden, damit Tests
ohne echte PS4 und ohne Internet laufen können.

**Eingaben.** Normalisierte Konfiguration, CancellationToken, optional
ConsoleContext und bereits validierte Artefakt-Metadaten. Ungeprüfte
Texte aus Netzwerkquellen gelten grundsätzlich als nicht
vertrauenswürdig. Pfade werden vor Nutzung normalisiert; URLs werden
gegen das Provider-Schema geprüft.

**Ausgaben.** Ein typisiertes Ergebnisobjekt mit Status (`Success`,
`Warning`, `Failed`, `Cancelled`), maschinenlesbarem Fehlercode,
benutzerfreundlicher Kurzmeldung und technischen Details für das Log.
Exceptions dürfen die UI-Grenze nicht ungefiltert überschreiten.

**Ablauf.** 1. Voraussetzungen prüfen. 2. Eingaben validieren. 3.
Dry-Run bzw. Plan erzeugen. 4. Falls schreibend: Backup/Checkpoint. 5.
Operation in Staging ausführen. 6. Ergebnis validieren. 7. Atomar
übernehmen. 8. Action Journal schreiben. 9. UI aktualisieren. Bei
Fehlern wird Staging verworfen und der vorherige konsistente Zustand
beibehalten.

**Fehlerfälle.** Netzwerkverlust, Provideränderung, fehlende
Berechtigung, voller Datenträger, ungültiges Archiv, Versionskonflikt,
Benutzerabbruch und unerwartete Daten müssen getrennte Codes besitzen.
Ein Retry ist nur für idempotente Schritte automatisch erlaubt.
Schreibaktionen werden nicht blind wiederholt.

**Tests.** Happy Path, leere Eingabe, beschädigte Metadaten,
Cancellation, Timeout, doppelter Aufruf, Wiederanlauf nach Abbruch und
mindestens ein Sicherheitsfall. Dateisystem- und HTTP-Zugriffe werden
gemockt. Integrationstest nutzt ein temporäres Verzeichnis und
deterministische Fixtures.

**Akzeptanzkriterien.** Die Funktion ist über die HESPERIA-UI
erreichbar, vollständig abbrechbar, erzeugt verständliche Logs,
verändert bei Dry-Run nichts und hinterlässt bei Fehlschlag keinen halb
installierten Zustand. Dokumentation und Tooltips sind vorhanden.

## 32. Implementierungskarte: Cheat Catalog

**Zweck.** Diese Komponente kapselt JSON/SHN/MC4 normalisieren. Sie darf
keine Verantwortung aus benachbarten Schichten übernehmen. UI,
Persistenz und Transport werden über Interfaces angebunden, damit Tests
ohne echte PS4 und ohne Internet laufen können.

**Eingaben.** Normalisierte Konfiguration, CancellationToken, optional
ConsoleContext und bereits validierte Artefakt-Metadaten. Ungeprüfte
Texte aus Netzwerkquellen gelten grundsätzlich als nicht
vertrauenswürdig. Pfade werden vor Nutzung normalisiert; URLs werden
gegen das Provider-Schema geprüft.

**Ausgaben.** Ein typisiertes Ergebnisobjekt mit Status (`Success`,
`Warning`, `Failed`, `Cancelled`), maschinenlesbarem Fehlercode,
benutzerfreundlicher Kurzmeldung und technischen Details für das Log.
Exceptions dürfen die UI-Grenze nicht ungefiltert überschreiten.

**Ablauf.** 1. Voraussetzungen prüfen. 2. Eingaben validieren. 3.
Dry-Run bzw. Plan erzeugen. 4. Falls schreibend: Backup/Checkpoint. 5.
Operation in Staging ausführen. 6. Ergebnis validieren. 7. Atomar
übernehmen. 8. Action Journal schreiben. 9. UI aktualisieren. Bei
Fehlern wird Staging verworfen und der vorherige konsistente Zustand
beibehalten.

**Fehlerfälle.** Netzwerkverlust, Provideränderung, fehlende
Berechtigung, voller Datenträger, ungültiges Archiv, Versionskonflikt,
Benutzerabbruch und unerwartete Daten müssen getrennte Codes besitzen.
Ein Retry ist nur für idempotente Schritte automatisch erlaubt.
Schreibaktionen werden nicht blind wiederholt.

**Tests.** Happy Path, leere Eingabe, beschädigte Metadaten,
Cancellation, Timeout, doppelter Aufruf, Wiederanlauf nach Abbruch und
mindestens ein Sicherheitsfall. Dateisystem- und HTTP-Zugriffe werden
gemockt. Integrationstest nutzt ein temporäres Verzeichnis und
deterministische Fixtures.

**Akzeptanzkriterien.** Die Funktion ist über die HESPERIA-UI
erreichbar, vollständig abbrechbar, erzeugt verständliche Logs,
verändert bei Dry-Run nichts und hinterlässt bei Fehlschlag keinen halb
installierten Zustand. Dokumentation und Tooltips sind vorhanden.

## 33. Implementierungskarte: Patch Catalog

**Zweck.** Diese Komponente kapselt XML-Metadaten und Varianten. Sie
darf keine Verantwortung aus benachbarten Schichten übernehmen. UI,
Persistenz und Transport werden über Interfaces angebunden, damit Tests
ohne echte PS4 und ohne Internet laufen können.

**Eingaben.** Normalisierte Konfiguration, CancellationToken, optional
ConsoleContext und bereits validierte Artefakt-Metadaten. Ungeprüfte
Texte aus Netzwerkquellen gelten grundsätzlich als nicht
vertrauenswürdig. Pfade werden vor Nutzung normalisiert; URLs werden
gegen das Provider-Schema geprüft.

**Ausgaben.** Ein typisiertes Ergebnisobjekt mit Status (`Success`,
`Warning`, `Failed`, `Cancelled`), maschinenlesbarem Fehlercode,
benutzerfreundlicher Kurzmeldung und technischen Details für das Log.
Exceptions dürfen die UI-Grenze nicht ungefiltert überschreiten.

**Ablauf.** 1. Voraussetzungen prüfen. 2. Eingaben validieren. 3.
Dry-Run bzw. Plan erzeugen. 4. Falls schreibend: Backup/Checkpoint. 5.
Operation in Staging ausführen. 6. Ergebnis validieren. 7. Atomar
übernehmen. 8. Action Journal schreiben. 9. UI aktualisieren. Bei
Fehlern wird Staging verworfen und der vorherige konsistente Zustand
beibehalten.

**Fehlerfälle.** Netzwerkverlust, Provideränderung, fehlende
Berechtigung, voller Datenträger, ungültiges Archiv, Versionskonflikt,
Benutzerabbruch und unerwartete Daten müssen getrennte Codes besitzen.
Ein Retry ist nur für idempotente Schritte automatisch erlaubt.
Schreibaktionen werden nicht blind wiederholt.

**Tests.** Happy Path, leere Eingabe, beschädigte Metadaten,
Cancellation, Timeout, doppelter Aufruf, Wiederanlauf nach Abbruch und
mindestens ein Sicherheitsfall. Dateisystem- und HTTP-Zugriffe werden
gemockt. Integrationstest nutzt ein temporäres Verzeichnis und
deterministische Fixtures.

**Akzeptanzkriterien.** Die Funktion ist über die HESPERIA-UI
erreichbar, vollständig abbrechbar, erzeugt verständliche Logs,
verändert bei Dry-Run nichts und hinterlässt bei Fehlschlag keinen halb
installierten Zustand. Dokumentation und Tooltips sind vorhanden.

## 34. Implementierungskarte: Plugin Catalog

**Zweck.** Diese Komponente kapselt PRX + Metadaten + Aktivierung. Sie
darf keine Verantwortung aus benachbarten Schichten übernehmen. UI,
Persistenz und Transport werden über Interfaces angebunden, damit Tests
ohne echte PS4 und ohne Internet laufen können.

**Eingaben.** Normalisierte Konfiguration, CancellationToken, optional
ConsoleContext und bereits validierte Artefakt-Metadaten. Ungeprüfte
Texte aus Netzwerkquellen gelten grundsätzlich als nicht
vertrauenswürdig. Pfade werden vor Nutzung normalisiert; URLs werden
gegen das Provider-Schema geprüft.

**Ausgaben.** Ein typisiertes Ergebnisobjekt mit Status (`Success`,
`Warning`, `Failed`, `Cancelled`), maschinenlesbarem Fehlercode,
benutzerfreundlicher Kurzmeldung und technischen Details für das Log.
Exceptions dürfen die UI-Grenze nicht ungefiltert überschreiten.

**Ablauf.** 1. Voraussetzungen prüfen. 2. Eingaben validieren. 3.
Dry-Run bzw. Plan erzeugen. 4. Falls schreibend: Backup/Checkpoint. 5.
Operation in Staging ausführen. 6. Ergebnis validieren. 7. Atomar
übernehmen. 8. Action Journal schreiben. 9. UI aktualisieren. Bei
Fehlern wird Staging verworfen und der vorherige konsistente Zustand
beibehalten.

**Fehlerfälle.** Netzwerkverlust, Provideränderung, fehlende
Berechtigung, voller Datenträger, ungültiges Archiv, Versionskonflikt,
Benutzerabbruch und unerwartete Daten müssen getrennte Codes besitzen.
Ein Retry ist nur für idempotente Schritte automatisch erlaubt.
Schreibaktionen werden nicht blind wiederholt.

**Tests.** Happy Path, leere Eingabe, beschädigte Metadaten,
Cancellation, Timeout, doppelter Aufruf, Wiederanlauf nach Abbruch und
mindestens ein Sicherheitsfall. Dateisystem- und HTTP-Zugriffe werden
gemockt. Integrationstest nutzt ein temporäres Verzeichnis und
deterministische Fixtures.

**Akzeptanzkriterien.** Die Funktion ist über die HESPERIA-UI
erreichbar, vollständig abbrechbar, erzeugt verständliche Logs,
verändert bei Dry-Run nichts und hinterlässt bei Fehlschlag keinen halb
installierten Zustand. Dokumentation und Tooltips sind vorhanden.

## 35. Implementierungskarte: Itemzflow

**Zweck.** Diese Komponente kapselt Version, Themes, Logs, optionale
Integration. Sie darf keine Verantwortung aus benachbarten Schichten
übernehmen. UI, Persistenz und Transport werden über Interfaces
angebunden, damit Tests ohne echte PS4 und ohne Internet laufen können.

**Eingaben.** Normalisierte Konfiguration, CancellationToken, optional
ConsoleContext und bereits validierte Artefakt-Metadaten. Ungeprüfte
Texte aus Netzwerkquellen gelten grundsätzlich als nicht
vertrauenswürdig. Pfade werden vor Nutzung normalisiert; URLs werden
gegen das Provider-Schema geprüft.

**Ausgaben.** Ein typisiertes Ergebnisobjekt mit Status (`Success`,
`Warning`, `Failed`, `Cancelled`), maschinenlesbarem Fehlercode,
benutzerfreundlicher Kurzmeldung und technischen Details für das Log.
Exceptions dürfen die UI-Grenze nicht ungefiltert überschreiten.

**Ablauf.** 1. Voraussetzungen prüfen. 2. Eingaben validieren. 3.
Dry-Run bzw. Plan erzeugen. 4. Falls schreibend: Backup/Checkpoint. 5.
Operation in Staging ausführen. 6. Ergebnis validieren. 7. Atomar
übernehmen. 8. Action Journal schreiben. 9. UI aktualisieren. Bei
Fehlern wird Staging verworfen und der vorherige konsistente Zustand
beibehalten.

**Fehlerfälle.** Netzwerkverlust, Provideränderung, fehlende
Berechtigung, voller Datenträger, ungültiges Archiv, Versionskonflikt,
Benutzerabbruch und unerwartete Daten müssen getrennte Codes besitzen.
Ein Retry ist nur für idempotente Schritte automatisch erlaubt.
Schreibaktionen werden nicht blind wiederholt.

**Tests.** Happy Path, leere Eingabe, beschädigte Metadaten,
Cancellation, Timeout, doppelter Aufruf, Wiederanlauf nach Abbruch und
mindestens ein Sicherheitsfall. Dateisystem- und HTTP-Zugriffe werden
gemockt. Integrationstest nutzt ein temporäres Verzeichnis und
deterministische Fixtures.

**Akzeptanzkriterien.** Die Funktion ist über die HESPERIA-UI
erreichbar, vollständig abbrechbar, erzeugt verständliche Logs,
verändert bei Dry-Run nichts und hinterlässt bei Fehlschlag keinen halb
installierten Zustand. Dokumentation und Tooltips sind vorhanden.

## 36. Implementierungskarte: Theme Builder

**Zweck.** Diese Komponente kapselt Assets validieren und Build
erzeugen. Sie darf keine Verantwortung aus benachbarten Schichten
übernehmen. UI, Persistenz und Transport werden über Interfaces
angebunden, damit Tests ohne echte PS4 und ohne Internet laufen können.

**Eingaben.** Normalisierte Konfiguration, CancellationToken, optional
ConsoleContext und bereits validierte Artefakt-Metadaten. Ungeprüfte
Texte aus Netzwerkquellen gelten grundsätzlich als nicht
vertrauenswürdig. Pfade werden vor Nutzung normalisiert; URLs werden
gegen das Provider-Schema geprüft.

**Ausgaben.** Ein typisiertes Ergebnisobjekt mit Status (`Success`,
`Warning`, `Failed`, `Cancelled`), maschinenlesbarem Fehlercode,
benutzerfreundlicher Kurzmeldung und technischen Details für das Log.
Exceptions dürfen die UI-Grenze nicht ungefiltert überschreiten.

**Ablauf.** 1. Voraussetzungen prüfen. 2. Eingaben validieren. 3.
Dry-Run bzw. Plan erzeugen. 4. Falls schreibend: Backup/Checkpoint. 5.
Operation in Staging ausführen. 6. Ergebnis validieren. 7. Atomar
übernehmen. 8. Action Journal schreiben. 9. UI aktualisieren. Bei
Fehlern wird Staging verworfen und der vorherige konsistente Zustand
beibehalten.

**Fehlerfälle.** Netzwerkverlust, Provideränderung, fehlende
Berechtigung, voller Datenträger, ungültiges Archiv, Versionskonflikt,
Benutzerabbruch und unerwartete Daten müssen getrennte Codes besitzen.
Ein Retry ist nur für idempotente Schritte automatisch erlaubt.
Schreibaktionen werden nicht blind wiederholt.

**Tests.** Happy Path, leere Eingabe, beschädigte Metadaten,
Cancellation, Timeout, doppelter Aufruf, Wiederanlauf nach Abbruch und
mindestens ein Sicherheitsfall. Dateisystem- und HTTP-Zugriffe werden
gemockt. Integrationstest nutzt ein temporäres Verzeichnis und
deterministische Fixtures.

**Akzeptanzkriterien.** Die Funktion ist über die HESPERIA-UI
erreichbar, vollständig abbrechbar, erzeugt verständliche Logs,
verändert bei Dry-Run nichts und hinterlässt bei Fehlschlag keinen halb
installierten Zustand. Dokumentation und Tooltips sind vorhanden.

## 37. Implementierungskarte: Wallpaper Pipeline

**Zweck.** Diese Komponente kapselt Import, Crop, Preview, Export. Sie
darf keine Verantwortung aus benachbarten Schichten übernehmen. UI,
Persistenz und Transport werden über Interfaces angebunden, damit Tests
ohne echte PS4 und ohne Internet laufen können.

**Eingaben.** Normalisierte Konfiguration, CancellationToken, optional
ConsoleContext und bereits validierte Artefakt-Metadaten. Ungeprüfte
Texte aus Netzwerkquellen gelten grundsätzlich als nicht
vertrauenswürdig. Pfade werden vor Nutzung normalisiert; URLs werden
gegen das Provider-Schema geprüft.

**Ausgaben.** Ein typisiertes Ergebnisobjekt mit Status (`Success`,
`Warning`, `Failed`, `Cancelled`), maschinenlesbarem Fehlercode,
benutzerfreundlicher Kurzmeldung und technischen Details für das Log.
Exceptions dürfen die UI-Grenze nicht ungefiltert überschreiten.

**Ablauf.** 1. Voraussetzungen prüfen. 2. Eingaben validieren. 3.
Dry-Run bzw. Plan erzeugen. 4. Falls schreibend: Backup/Checkpoint. 5.
Operation in Staging ausführen. 6. Ergebnis validieren. 7. Atomar
übernehmen. 8. Action Journal schreiben. 9. UI aktualisieren. Bei
Fehlern wird Staging verworfen und der vorherige konsistente Zustand
beibehalten.

**Fehlerfälle.** Netzwerkverlust, Provideränderung, fehlende
Berechtigung, voller Datenträger, ungültiges Archiv, Versionskonflikt,
Benutzerabbruch und unerwartete Daten müssen getrennte Codes besitzen.
Ein Retry ist nur für idempotente Schritte automatisch erlaubt.
Schreibaktionen werden nicht blind wiederholt.

**Tests.** Happy Path, leere Eingabe, beschädigte Metadaten,
Cancellation, Timeout, doppelter Aufruf, Wiederanlauf nach Abbruch und
mindestens ein Sicherheitsfall. Dateisystem- und HTTP-Zugriffe werden
gemockt. Integrationstest nutzt ein temporäres Verzeichnis und
deterministische Fixtures.

**Akzeptanzkriterien.** Die Funktion ist über die HESPERIA-UI
erreichbar, vollständig abbrechbar, erzeugt verständliche Logs,
verändert bei Dry-Run nichts und hinterlässt bei Fehlschlag keinen halb
installierten Zustand. Dokumentation und Tooltips sind vorhanden.

## 38. Implementierungskarte: Music Assets

**Zweck.** Diese Komponente kapselt Dateiprüfung und Größenlimits. Sie
darf keine Verantwortung aus benachbarten Schichten übernehmen. UI,
Persistenz und Transport werden über Interfaces angebunden, damit Tests
ohne echte PS4 und ohne Internet laufen können.

**Eingaben.** Normalisierte Konfiguration, CancellationToken, optional
ConsoleContext und bereits validierte Artefakt-Metadaten. Ungeprüfte
Texte aus Netzwerkquellen gelten grundsätzlich als nicht
vertrauenswürdig. Pfade werden vor Nutzung normalisiert; URLs werden
gegen das Provider-Schema geprüft.

**Ausgaben.** Ein typisiertes Ergebnisobjekt mit Status (`Success`,
`Warning`, `Failed`, `Cancelled`), maschinenlesbarem Fehlercode,
benutzerfreundlicher Kurzmeldung und technischen Details für das Log.
Exceptions dürfen die UI-Grenze nicht ungefiltert überschreiten.

**Ablauf.** 1. Voraussetzungen prüfen. 2. Eingaben validieren. 3.
Dry-Run bzw. Plan erzeugen. 4. Falls schreibend: Backup/Checkpoint. 5.
Operation in Staging ausführen. 6. Ergebnis validieren. 7. Atomar
übernehmen. 8. Action Journal schreiben. 9. UI aktualisieren. Bei
Fehlern wird Staging verworfen und der vorherige konsistente Zustand
beibehalten.

**Fehlerfälle.** Netzwerkverlust, Provideränderung, fehlende
Berechtigung, voller Datenträger, ungültiges Archiv, Versionskonflikt,
Benutzerabbruch und unerwartete Daten müssen getrennte Codes besitzen.
Ein Retry ist nur für idempotente Schritte automatisch erlaubt.
Schreibaktionen werden nicht blind wiederholt.

**Tests.** Happy Path, leere Eingabe, beschädigte Metadaten,
Cancellation, Timeout, doppelter Aufruf, Wiederanlauf nach Abbruch und
mindestens ein Sicherheitsfall. Dateisystem- und HTTP-Zugriffe werden
gemockt. Integrationstest nutzt ein temporäres Verzeichnis und
deterministische Fixtures.

**Akzeptanzkriterien.** Die Funktion ist über die HESPERIA-UI
erreichbar, vollständig abbrechbar, erzeugt verständliche Logs,
verändert bei Dry-Run nichts und hinterlässt bei Fehlschlag keinen halb
installierten Zustand. Dokumentation und Tooltips sind vorhanden.

## 39. Implementierungskarte: Font Assets

**Zweck.** Diese Komponente kapselt TTF-Prüfung und Fallback. Sie darf
keine Verantwortung aus benachbarten Schichten übernehmen. UI,
Persistenz und Transport werden über Interfaces angebunden, damit Tests
ohne echte PS4 und ohne Internet laufen können.

**Eingaben.** Normalisierte Konfiguration, CancellationToken, optional
ConsoleContext und bereits validierte Artefakt-Metadaten. Ungeprüfte
Texte aus Netzwerkquellen gelten grundsätzlich als nicht
vertrauenswürdig. Pfade werden vor Nutzung normalisiert; URLs werden
gegen das Provider-Schema geprüft.

**Ausgaben.** Ein typisiertes Ergebnisobjekt mit Status (`Success`,
`Warning`, `Failed`, `Cancelled`), maschinenlesbarem Fehlercode,
benutzerfreundlicher Kurzmeldung und technischen Details für das Log.
Exceptions dürfen die UI-Grenze nicht ungefiltert überschreiten.

**Ablauf.** 1. Voraussetzungen prüfen. 2. Eingaben validieren. 3.
Dry-Run bzw. Plan erzeugen. 4. Falls schreibend: Backup/Checkpoint. 5.
Operation in Staging ausführen. 6. Ergebnis validieren. 7. Atomar
übernehmen. 8. Action Journal schreiben. 9. UI aktualisieren. Bei
Fehlern wird Staging verworfen und der vorherige konsistente Zustand
beibehalten.

**Fehlerfälle.** Netzwerkverlust, Provideränderung, fehlende
Berechtigung, voller Datenträger, ungültiges Archiv, Versionskonflikt,
Benutzerabbruch und unerwartete Daten müssen getrennte Codes besitzen.
Ein Retry ist nur für idempotente Schritte automatisch erlaubt.
Schreibaktionen werden nicht blind wiederholt.

**Tests.** Happy Path, leere Eingabe, beschädigte Metadaten,
Cancellation, Timeout, doppelter Aufruf, Wiederanlauf nach Abbruch und
mindestens ein Sicherheitsfall. Dateisystem- und HTTP-Zugriffe werden
gemockt. Integrationstest nutzt ein temporäres Verzeichnis und
deterministische Fixtures.

**Akzeptanzkriterien.** Die Funktion ist über die HESPERIA-UI
erreichbar, vollständig abbrechbar, erzeugt verständliche Logs,
verändert bei Dry-Run nichts und hinterlässt bei Fehlschlag keinen halb
installierten Zustand. Dokumentation und Tooltips sind vorhanden.

## 40. Implementierungskarte: USB Builder

**Zweck.** Diese Komponente kapselt Profile, Manifest, Hashprüfung. Sie
darf keine Verantwortung aus benachbarten Schichten übernehmen. UI,
Persistenz und Transport werden über Interfaces angebunden, damit Tests
ohne echte PS4 und ohne Internet laufen können.

**Eingaben.** Normalisierte Konfiguration, CancellationToken, optional
ConsoleContext und bereits validierte Artefakt-Metadaten. Ungeprüfte
Texte aus Netzwerkquellen gelten grundsätzlich als nicht
vertrauenswürdig. Pfade werden vor Nutzung normalisiert; URLs werden
gegen das Provider-Schema geprüft.

**Ausgaben.** Ein typisiertes Ergebnisobjekt mit Status (`Success`,
`Warning`, `Failed`, `Cancelled`), maschinenlesbarem Fehlercode,
benutzerfreundlicher Kurzmeldung und technischen Details für das Log.
Exceptions dürfen die UI-Grenze nicht ungefiltert überschreiten.

**Ablauf.** 1. Voraussetzungen prüfen. 2. Eingaben validieren. 3.
Dry-Run bzw. Plan erzeugen. 4. Falls schreibend: Backup/Checkpoint. 5.
Operation in Staging ausführen. 6. Ergebnis validieren. 7. Atomar
übernehmen. 8. Action Journal schreiben. 9. UI aktualisieren. Bei
Fehlern wird Staging verworfen und der vorherige konsistente Zustand
beibehalten.

**Fehlerfälle.** Netzwerkverlust, Provideränderung, fehlende
Berechtigung, voller Datenträger, ungültiges Archiv, Versionskonflikt,
Benutzerabbruch und unerwartete Daten müssen getrennte Codes besitzen.
Ein Retry ist nur für idempotente Schritte automatisch erlaubt.
Schreibaktionen werden nicht blind wiederholt.

**Tests.** Happy Path, leere Eingabe, beschädigte Metadaten,
Cancellation, Timeout, doppelter Aufruf, Wiederanlauf nach Abbruch und
mindestens ein Sicherheitsfall. Dateisystem- und HTTP-Zugriffe werden
gemockt. Integrationstest nutzt ein temporäres Verzeichnis und
deterministische Fixtures.

**Akzeptanzkriterien.** Die Funktion ist über die HESPERIA-UI
erreichbar, vollständig abbrechbar, erzeugt verständliche Logs,
verändert bei Dry-Run nichts und hinterlässt bei Fehlschlag keinen halb
installierten Zustand. Dokumentation und Tooltips sind vorhanden.

## 41. Implementierungskarte: FTP Transfer

**Zweck.** Diese Komponente kapselt Queue, Retry, Resume. Sie darf keine
Verantwortung aus benachbarten Schichten übernehmen. UI, Persistenz und
Transport werden über Interfaces angebunden, damit Tests ohne echte PS4
und ohne Internet laufen können.

**Eingaben.** Normalisierte Konfiguration, CancellationToken, optional
ConsoleContext und bereits validierte Artefakt-Metadaten. Ungeprüfte
Texte aus Netzwerkquellen gelten grundsätzlich als nicht
vertrauenswürdig. Pfade werden vor Nutzung normalisiert; URLs werden
gegen das Provider-Schema geprüft.

**Ausgaben.** Ein typisiertes Ergebnisobjekt mit Status (`Success`,
`Warning`, `Failed`, `Cancelled`), maschinenlesbarem Fehlercode,
benutzerfreundlicher Kurzmeldung und technischen Details für das Log.
Exceptions dürfen die UI-Grenze nicht ungefiltert überschreiten.

**Ablauf.** 1. Voraussetzungen prüfen. 2. Eingaben validieren. 3.
Dry-Run bzw. Plan erzeugen. 4. Falls schreibend: Backup/Checkpoint. 5.
Operation in Staging ausführen. 6. Ergebnis validieren. 7. Atomar
übernehmen. 8. Action Journal schreiben. 9. UI aktualisieren. Bei
Fehlern wird Staging verworfen und der vorherige konsistente Zustand
beibehalten.

**Fehlerfälle.** Netzwerkverlust, Provideränderung, fehlende
Berechtigung, voller Datenträger, ungültiges Archiv, Versionskonflikt,
Benutzerabbruch und unerwartete Daten müssen getrennte Codes besitzen.
Ein Retry ist nur für idempotente Schritte automatisch erlaubt.
Schreibaktionen werden nicht blind wiederholt.

**Tests.** Happy Path, leere Eingabe, beschädigte Metadaten,
Cancellation, Timeout, doppelter Aufruf, Wiederanlauf nach Abbruch und
mindestens ein Sicherheitsfall. Dateisystem- und HTTP-Zugriffe werden
gemockt. Integrationstest nutzt ein temporäres Verzeichnis und
deterministische Fixtures.

**Akzeptanzkriterien.** Die Funktion ist über die HESPERIA-UI
erreichbar, vollständig abbrechbar, erzeugt verständliche Logs,
verändert bei Dry-Run nichts und hinterlässt bei Fehlschlag keinen halb
installierten Zustand. Dokumentation und Tooltips sind vorhanden.

## 42. Implementierungskarte: Backup Engine

**Zweck.** Diese Komponente kapselt Versionierung und Restore. Sie darf
keine Verantwortung aus benachbarten Schichten übernehmen. UI,
Persistenz und Transport werden über Interfaces angebunden, damit Tests
ohne echte PS4 und ohne Internet laufen können.

**Eingaben.** Normalisierte Konfiguration, CancellationToken, optional
ConsoleContext und bereits validierte Artefakt-Metadaten. Ungeprüfte
Texte aus Netzwerkquellen gelten grundsätzlich als nicht
vertrauenswürdig. Pfade werden vor Nutzung normalisiert; URLs werden
gegen das Provider-Schema geprüft.

**Ausgaben.** Ein typisiertes Ergebnisobjekt mit Status (`Success`,
`Warning`, `Failed`, `Cancelled`), maschinenlesbarem Fehlercode,
benutzerfreundlicher Kurzmeldung und technischen Details für das Log.
Exceptions dürfen die UI-Grenze nicht ungefiltert überschreiten.

**Ablauf.** 1. Voraussetzungen prüfen. 2. Eingaben validieren. 3.
Dry-Run bzw. Plan erzeugen. 4. Falls schreibend: Backup/Checkpoint. 5.
Operation in Staging ausführen. 6. Ergebnis validieren. 7. Atomar
übernehmen. 8. Action Journal schreiben. 9. UI aktualisieren. Bei
Fehlern wird Staging verworfen und der vorherige konsistente Zustand
beibehalten.

**Fehlerfälle.** Netzwerkverlust, Provideränderung, fehlende
Berechtigung, voller Datenträger, ungültiges Archiv, Versionskonflikt,
Benutzerabbruch und unerwartete Daten müssen getrennte Codes besitzen.
Ein Retry ist nur für idempotente Schritte automatisch erlaubt.
Schreibaktionen werden nicht blind wiederholt.

**Tests.** Happy Path, leere Eingabe, beschädigte Metadaten,
Cancellation, Timeout, doppelter Aufruf, Wiederanlauf nach Abbruch und
mindestens ein Sicherheitsfall. Dateisystem- und HTTP-Zugriffe werden
gemockt. Integrationstest nutzt ein temporäres Verzeichnis und
deterministische Fixtures.

**Akzeptanzkriterien.** Die Funktion ist über die HESPERIA-UI
erreichbar, vollständig abbrechbar, erzeugt verständliche Logs,
verändert bei Dry-Run nichts und hinterlässt bei Fehlschlag keinen halb
installierten Zustand. Dokumentation und Tooltips sind vorhanden.

## 43. Implementierungskarte: Provider Health

**Zweck.** Diese Komponente kapselt Status und Fallback. Sie darf keine
Verantwortung aus benachbarten Schichten übernehmen. UI, Persistenz und
Transport werden über Interfaces angebunden, damit Tests ohne echte PS4
und ohne Internet laufen können.

**Eingaben.** Normalisierte Konfiguration, CancellationToken, optional
ConsoleContext und bereits validierte Artefakt-Metadaten. Ungeprüfte
Texte aus Netzwerkquellen gelten grundsätzlich als nicht
vertrauenswürdig. Pfade werden vor Nutzung normalisiert; URLs werden
gegen das Provider-Schema geprüft.

**Ausgaben.** Ein typisiertes Ergebnisobjekt mit Status (`Success`,
`Warning`, `Failed`, `Cancelled`), maschinenlesbarem Fehlercode,
benutzerfreundlicher Kurzmeldung und technischen Details für das Log.
Exceptions dürfen die UI-Grenze nicht ungefiltert überschreiten.

**Ablauf.** 1. Voraussetzungen prüfen. 2. Eingaben validieren. 3.
Dry-Run bzw. Plan erzeugen. 4. Falls schreibend: Backup/Checkpoint. 5.
Operation in Staging ausführen. 6. Ergebnis validieren. 7. Atomar
übernehmen. 8. Action Journal schreiben. 9. UI aktualisieren. Bei
Fehlern wird Staging verworfen und der vorherige konsistente Zustand
beibehalten.

**Fehlerfälle.** Netzwerkverlust, Provideränderung, fehlende
Berechtigung, voller Datenträger, ungültiges Archiv, Versionskonflikt,
Benutzerabbruch und unerwartete Daten müssen getrennte Codes besitzen.
Ein Retry ist nur für idempotente Schritte automatisch erlaubt.
Schreibaktionen werden nicht blind wiederholt.

**Tests.** Happy Path, leere Eingabe, beschädigte Metadaten,
Cancellation, Timeout, doppelter Aufruf, Wiederanlauf nach Abbruch und
mindestens ein Sicherheitsfall. Dateisystem- und HTTP-Zugriffe werden
gemockt. Integrationstest nutzt ein temporäres Verzeichnis und
deterministische Fixtures.

**Akzeptanzkriterien.** Die Funktion ist über die HESPERIA-UI
erreichbar, vollständig abbrechbar, erzeugt verständliche Logs,
verändert bei Dry-Run nichts und hinterlässt bei Fehlschlag keinen halb
installierten Zustand. Dokumentation und Tooltips sind vorhanden.

## 44. Implementierungskarte: GitHub Adapter

**Zweck.** Diese Komponente kapselt Release/API/Rate-Limit. Sie darf
keine Verantwortung aus benachbarten Schichten übernehmen. UI,
Persistenz und Transport werden über Interfaces angebunden, damit Tests
ohne echte PS4 und ohne Internet laufen können.

**Eingaben.** Normalisierte Konfiguration, CancellationToken, optional
ConsoleContext und bereits validierte Artefakt-Metadaten. Ungeprüfte
Texte aus Netzwerkquellen gelten grundsätzlich als nicht
vertrauenswürdig. Pfade werden vor Nutzung normalisiert; URLs werden
gegen das Provider-Schema geprüft.

**Ausgaben.** Ein typisiertes Ergebnisobjekt mit Status (`Success`,
`Warning`, `Failed`, `Cancelled`), maschinenlesbarem Fehlercode,
benutzerfreundlicher Kurzmeldung und technischen Details für das Log.
Exceptions dürfen die UI-Grenze nicht ungefiltert überschreiten.

**Ablauf.** 1. Voraussetzungen prüfen. 2. Eingaben validieren. 3.
Dry-Run bzw. Plan erzeugen. 4. Falls schreibend: Backup/Checkpoint. 5.
Operation in Staging ausführen. 6. Ergebnis validieren. 7. Atomar
übernehmen. 8. Action Journal schreiben. 9. UI aktualisieren. Bei
Fehlern wird Staging verworfen und der vorherige konsistente Zustand
beibehalten.

**Fehlerfälle.** Netzwerkverlust, Provideränderung, fehlende
Berechtigung, voller Datenträger, ungültiges Archiv, Versionskonflikt,
Benutzerabbruch und unerwartete Daten müssen getrennte Codes besitzen.
Ein Retry ist nur für idempotente Schritte automatisch erlaubt.
Schreibaktionen werden nicht blind wiederholt.

**Tests.** Happy Path, leere Eingabe, beschädigte Metadaten,
Cancellation, Timeout, doppelter Aufruf, Wiederanlauf nach Abbruch und
mindestens ein Sicherheitsfall. Dateisystem- und HTTP-Zugriffe werden
gemockt. Integrationstest nutzt ein temporäres Verzeichnis und
deterministische Fixtures.

**Akzeptanzkriterien.** Die Funktion ist über die HESPERIA-UI
erreichbar, vollständig abbrechbar, erzeugt verständliche Logs,
verändert bei Dry-Run nichts und hinterlässt bei Fehlschlag keinen halb
installierten Zustand. Dokumentation und Tooltips sind vorhanden.

## 45. Implementierungskarte: HTTP Cache

**Zweck.** Diese Komponente kapselt ETag und atomare Updates. Sie darf
keine Verantwortung aus benachbarten Schichten übernehmen. UI,
Persistenz und Transport werden über Interfaces angebunden, damit Tests
ohne echte PS4 und ohne Internet laufen können.

**Eingaben.** Normalisierte Konfiguration, CancellationToken, optional
ConsoleContext und bereits validierte Artefakt-Metadaten. Ungeprüfte
Texte aus Netzwerkquellen gelten grundsätzlich als nicht
vertrauenswürdig. Pfade werden vor Nutzung normalisiert; URLs werden
gegen das Provider-Schema geprüft.

**Ausgaben.** Ein typisiertes Ergebnisobjekt mit Status (`Success`,
`Warning`, `Failed`, `Cancelled`), maschinenlesbarem Fehlercode,
benutzerfreundlicher Kurzmeldung und technischen Details für das Log.
Exceptions dürfen die UI-Grenze nicht ungefiltert überschreiten.

**Ablauf.** 1. Voraussetzungen prüfen. 2. Eingaben validieren. 3.
Dry-Run bzw. Plan erzeugen. 4. Falls schreibend: Backup/Checkpoint. 5.
Operation in Staging ausführen. 6. Ergebnis validieren. 7. Atomar
übernehmen. 8. Action Journal schreiben. 9. UI aktualisieren. Bei
Fehlern wird Staging verworfen und der vorherige konsistente Zustand
beibehalten.

**Fehlerfälle.** Netzwerkverlust, Provideränderung, fehlende
Berechtigung, voller Datenträger, ungültiges Archiv, Versionskonflikt,
Benutzerabbruch und unerwartete Daten müssen getrennte Codes besitzen.
Ein Retry ist nur für idempotente Schritte automatisch erlaubt.
Schreibaktionen werden nicht blind wiederholt.

**Tests.** Happy Path, leere Eingabe, beschädigte Metadaten,
Cancellation, Timeout, doppelter Aufruf, Wiederanlauf nach Abbruch und
mindestens ein Sicherheitsfall. Dateisystem- und HTTP-Zugriffe werden
gemockt. Integrationstest nutzt ein temporäres Verzeichnis und
deterministische Fixtures.

**Akzeptanzkriterien.** Die Funktion ist über die HESPERIA-UI
erreichbar, vollständig abbrechbar, erzeugt verständliche Logs,
verändert bei Dry-Run nichts und hinterlässt bei Fehlschlag keinen halb
installierten Zustand. Dokumentation und Tooltips sind vorhanden.

## 46. Implementierungskarte: Artifact Store

**Zweck.** Diese Komponente kapselt immutable Downloads + SHA-256. Sie
darf keine Verantwortung aus benachbarten Schichten übernehmen. UI,
Persistenz und Transport werden über Interfaces angebunden, damit Tests
ohne echte PS4 und ohne Internet laufen können.

**Eingaben.** Normalisierte Konfiguration, CancellationToken, optional
ConsoleContext und bereits validierte Artefakt-Metadaten. Ungeprüfte
Texte aus Netzwerkquellen gelten grundsätzlich als nicht
vertrauenswürdig. Pfade werden vor Nutzung normalisiert; URLs werden
gegen das Provider-Schema geprüft.

**Ausgaben.** Ein typisiertes Ergebnisobjekt mit Status (`Success`,
`Warning`, `Failed`, `Cancelled`), maschinenlesbarem Fehlercode,
benutzerfreundlicher Kurzmeldung und technischen Details für das Log.
Exceptions dürfen die UI-Grenze nicht ungefiltert überschreiten.

**Ablauf.** 1. Voraussetzungen prüfen. 2. Eingaben validieren. 3.
Dry-Run bzw. Plan erzeugen. 4. Falls schreibend: Backup/Checkpoint. 5.
Operation in Staging ausführen. 6. Ergebnis validieren. 7. Atomar
übernehmen. 8. Action Journal schreiben. 9. UI aktualisieren. Bei
Fehlern wird Staging verworfen und der vorherige konsistente Zustand
beibehalten.

**Fehlerfälle.** Netzwerkverlust, Provideränderung, fehlende
Berechtigung, voller Datenträger, ungültiges Archiv, Versionskonflikt,
Benutzerabbruch und unerwartete Daten müssen getrennte Codes besitzen.
Ein Retry ist nur für idempotente Schritte automatisch erlaubt.
Schreibaktionen werden nicht blind wiederholt.

**Tests.** Happy Path, leere Eingabe, beschädigte Metadaten,
Cancellation, Timeout, doppelter Aufruf, Wiederanlauf nach Abbruch und
mindestens ein Sicherheitsfall. Dateisystem- und HTTP-Zugriffe werden
gemockt. Integrationstest nutzt ein temporäres Verzeichnis und
deterministische Fixtures.

**Akzeptanzkriterien.** Die Funktion ist über die HESPERIA-UI
erreichbar, vollständig abbrechbar, erzeugt verständliche Logs,
verändert bei Dry-Run nichts und hinterlässt bei Fehlschlag keinen halb
installierten Zustand. Dokumentation und Tooltips sind vorhanden.

## 47. Implementierungskarte: SQLite Store

**Zweck.** Diese Komponente kapselt Migrationen und Transaktionen. Sie
darf keine Verantwortung aus benachbarten Schichten übernehmen. UI,
Persistenz und Transport werden über Interfaces angebunden, damit Tests
ohne echte PS4 und ohne Internet laufen können.

**Eingaben.** Normalisierte Konfiguration, CancellationToken, optional
ConsoleContext und bereits validierte Artefakt-Metadaten. Ungeprüfte
Texte aus Netzwerkquellen gelten grundsätzlich als nicht
vertrauenswürdig. Pfade werden vor Nutzung normalisiert; URLs werden
gegen das Provider-Schema geprüft.

**Ausgaben.** Ein typisiertes Ergebnisobjekt mit Status (`Success`,
`Warning`, `Failed`, `Cancelled`), maschinenlesbarem Fehlercode,
benutzerfreundlicher Kurzmeldung und technischen Details für das Log.
Exceptions dürfen die UI-Grenze nicht ungefiltert überschreiten.

**Ablauf.** 1. Voraussetzungen prüfen. 2. Eingaben validieren. 3.
Dry-Run bzw. Plan erzeugen. 4. Falls schreibend: Backup/Checkpoint. 5.
Operation in Staging ausführen. 6. Ergebnis validieren. 7. Atomar
übernehmen. 8. Action Journal schreiben. 9. UI aktualisieren. Bei
Fehlern wird Staging verworfen und der vorherige konsistente Zustand
beibehalten.

**Fehlerfälle.** Netzwerkverlust, Provideränderung, fehlende
Berechtigung, voller Datenträger, ungültiges Archiv, Versionskonflikt,
Benutzerabbruch und unerwartete Daten müssen getrennte Codes besitzen.
Ein Retry ist nur für idempotente Schritte automatisch erlaubt.
Schreibaktionen werden nicht blind wiederholt.

**Tests.** Happy Path, leere Eingabe, beschädigte Metadaten,
Cancellation, Timeout, doppelter Aufruf, Wiederanlauf nach Abbruch und
mindestens ein Sicherheitsfall. Dateisystem- und HTTP-Zugriffe werden
gemockt. Integrationstest nutzt ein temporäres Verzeichnis und
deterministische Fixtures.

**Akzeptanzkriterien.** Die Funktion ist über die HESPERIA-UI
erreichbar, vollständig abbrechbar, erzeugt verständliche Logs,
verändert bei Dry-Run nichts und hinterlässt bei Fehlschlag keinen halb
installierten Zustand. Dokumentation und Tooltips sind vorhanden.

## 48. Implementierungskarte: Action Journal

**Zweck.** Diese Komponente kapselt Audit-Trail. Sie darf keine
Verantwortung aus benachbarten Schichten übernehmen. UI, Persistenz und
Transport werden über Interfaces angebunden, damit Tests ohne echte PS4
und ohne Internet laufen können.

**Eingaben.** Normalisierte Konfiguration, CancellationToken, optional
ConsoleContext und bereits validierte Artefakt-Metadaten. Ungeprüfte
Texte aus Netzwerkquellen gelten grundsätzlich als nicht
vertrauenswürdig. Pfade werden vor Nutzung normalisiert; URLs werden
gegen das Provider-Schema geprüft.

**Ausgaben.** Ein typisiertes Ergebnisobjekt mit Status (`Success`,
`Warning`, `Failed`, `Cancelled`), maschinenlesbarem Fehlercode,
benutzerfreundlicher Kurzmeldung und technischen Details für das Log.
Exceptions dürfen die UI-Grenze nicht ungefiltert überschreiten.

**Ablauf.** 1. Voraussetzungen prüfen. 2. Eingaben validieren. 3.
Dry-Run bzw. Plan erzeugen. 4. Falls schreibend: Backup/Checkpoint. 5.
Operation in Staging ausführen. 6. Ergebnis validieren. 7. Atomar
übernehmen. 8. Action Journal schreiben. 9. UI aktualisieren. Bei
Fehlern wird Staging verworfen und der vorherige konsistente Zustand
beibehalten.

**Fehlerfälle.** Netzwerkverlust, Provideränderung, fehlende
Berechtigung, voller Datenträger, ungültiges Archiv, Versionskonflikt,
Benutzerabbruch und unerwartete Daten müssen getrennte Codes besitzen.
Ein Retry ist nur für idempotente Schritte automatisch erlaubt.
Schreibaktionen werden nicht blind wiederholt.

**Tests.** Happy Path, leere Eingabe, beschädigte Metadaten,
Cancellation, Timeout, doppelter Aufruf, Wiederanlauf nach Abbruch und
mindestens ein Sicherheitsfall. Dateisystem- und HTTP-Zugriffe werden
gemockt. Integrationstest nutzt ein temporäres Verzeichnis und
deterministische Fixtures.

**Akzeptanzkriterien.** Die Funktion ist über die HESPERIA-UI
erreichbar, vollständig abbrechbar, erzeugt verständliche Logs,
verändert bei Dry-Run nichts und hinterlässt bei Fehlschlag keinen halb
installierten Zustand. Dokumentation und Tooltips sind vorhanden.

## 49. Implementierungskarte: Diagnostics

**Zweck.** Diese Komponente kapselt Logs und Supportbundle. Sie darf
keine Verantwortung aus benachbarten Schichten übernehmen. UI,
Persistenz und Transport werden über Interfaces angebunden, damit Tests
ohne echte PS4 und ohne Internet laufen können.

**Eingaben.** Normalisierte Konfiguration, CancellationToken, optional
ConsoleContext und bereits validierte Artefakt-Metadaten. Ungeprüfte
Texte aus Netzwerkquellen gelten grundsätzlich als nicht
vertrauenswürdig. Pfade werden vor Nutzung normalisiert; URLs werden
gegen das Provider-Schema geprüft.

**Ausgaben.** Ein typisiertes Ergebnisobjekt mit Status (`Success`,
`Warning`, `Failed`, `Cancelled`), maschinenlesbarem Fehlercode,
benutzerfreundlicher Kurzmeldung und technischen Details für das Log.
Exceptions dürfen die UI-Grenze nicht ungefiltert überschreiten.

**Ablauf.** 1. Voraussetzungen prüfen. 2. Eingaben validieren. 3.
Dry-Run bzw. Plan erzeugen. 4. Falls schreibend: Backup/Checkpoint. 5.
Operation in Staging ausführen. 6. Ergebnis validieren. 7. Atomar
übernehmen. 8. Action Journal schreiben. 9. UI aktualisieren. Bei
Fehlern wird Staging verworfen und der vorherige konsistente Zustand
beibehalten.

**Fehlerfälle.** Netzwerkverlust, Provideränderung, fehlende
Berechtigung, voller Datenträger, ungültiges Archiv, Versionskonflikt,
Benutzerabbruch und unerwartete Daten müssen getrennte Codes besitzen.
Ein Retry ist nur für idempotente Schritte automatisch erlaubt.
Schreibaktionen werden nicht blind wiederholt.

**Tests.** Happy Path, leere Eingabe, beschädigte Metadaten,
Cancellation, Timeout, doppelter Aufruf, Wiederanlauf nach Abbruch und
mindestens ein Sicherheitsfall. Dateisystem- und HTTP-Zugriffe werden
gemockt. Integrationstest nutzt ein temporäres Verzeichnis und
deterministische Fixtures.

**Akzeptanzkriterien.** Die Funktion ist über die HESPERIA-UI
erreichbar, vollständig abbrechbar, erzeugt verständliche Logs,
verändert bei Dry-Run nichts und hinterlässt bei Fehlschlag keinen halb
installierten Zustand. Dokumentation und Tooltips sind vorhanden.

## 50. Implementierungskarte: Settings

**Zweck.** Diese Komponente kapselt Schema und Defaults. Sie darf keine
Verantwortung aus benachbarten Schichten übernehmen. UI, Persistenz und
Transport werden über Interfaces angebunden, damit Tests ohne echte PS4
und ohne Internet laufen können.

**Eingaben.** Normalisierte Konfiguration, CancellationToken, optional
ConsoleContext und bereits validierte Artefakt-Metadaten. Ungeprüfte
Texte aus Netzwerkquellen gelten grundsätzlich als nicht
vertrauenswürdig. Pfade werden vor Nutzung normalisiert; URLs werden
gegen das Provider-Schema geprüft.

**Ausgaben.** Ein typisiertes Ergebnisobjekt mit Status (`Success`,
`Warning`, `Failed`, `Cancelled`), maschinenlesbarem Fehlercode,
benutzerfreundlicher Kurzmeldung und technischen Details für das Log.
Exceptions dürfen die UI-Grenze nicht ungefiltert überschreiten.

**Ablauf.** 1. Voraussetzungen prüfen. 2. Eingaben validieren. 3.
Dry-Run bzw. Plan erzeugen. 4. Falls schreibend: Backup/Checkpoint. 5.
Operation in Staging ausführen. 6. Ergebnis validieren. 7. Atomar
übernehmen. 8. Action Journal schreiben. 9. UI aktualisieren. Bei
Fehlern wird Staging verworfen und der vorherige konsistente Zustand
beibehalten.

**Fehlerfälle.** Netzwerkverlust, Provideränderung, fehlende
Berechtigung, voller Datenträger, ungültiges Archiv, Versionskonflikt,
Benutzerabbruch und unerwartete Daten müssen getrennte Codes besitzen.
Ein Retry ist nur für idempotente Schritte automatisch erlaubt.
Schreibaktionen werden nicht blind wiederholt.

**Tests.** Happy Path, leere Eingabe, beschädigte Metadaten,
Cancellation, Timeout, doppelter Aufruf, Wiederanlauf nach Abbruch und
mindestens ein Sicherheitsfall. Dateisystem- und HTTP-Zugriffe werden
gemockt. Integrationstest nutzt ein temporäres Verzeichnis und
deterministische Fixtures.

**Akzeptanzkriterien.** Die Funktion ist über die HESPERIA-UI
erreichbar, vollständig abbrechbar, erzeugt verständliche Logs,
verändert bei Dry-Run nichts und hinterlässt bei Fehlschlag keinen halb
installierten Zustand. Dokumentation und Tooltips sind vorhanden.

## 51. Implementierungskarte: Expert Mode

**Zweck.** Diese Komponente kapselt Rohdaten ohne Sicherheitsabbau. Sie
darf keine Verantwortung aus benachbarten Schichten übernehmen. UI,
Persistenz und Transport werden über Interfaces angebunden, damit Tests
ohne echte PS4 und ohne Internet laufen können.

**Eingaben.** Normalisierte Konfiguration, CancellationToken, optional
ConsoleContext und bereits validierte Artefakt-Metadaten. Ungeprüfte
Texte aus Netzwerkquellen gelten grundsätzlich als nicht
vertrauenswürdig. Pfade werden vor Nutzung normalisiert; URLs werden
gegen das Provider-Schema geprüft.

**Ausgaben.** Ein typisiertes Ergebnisobjekt mit Status (`Success`,
`Warning`, `Failed`, `Cancelled`), maschinenlesbarem Fehlercode,
benutzerfreundlicher Kurzmeldung und technischen Details für das Log.
Exceptions dürfen die UI-Grenze nicht ungefiltert überschreiten.

**Ablauf.** 1. Voraussetzungen prüfen. 2. Eingaben validieren. 3.
Dry-Run bzw. Plan erzeugen. 4. Falls schreibend: Backup/Checkpoint. 5.
Operation in Staging ausführen. 6. Ergebnis validieren. 7. Atomar
übernehmen. 8. Action Journal schreiben. 9. UI aktualisieren. Bei
Fehlern wird Staging verworfen und der vorherige konsistente Zustand
beibehalten.

**Fehlerfälle.** Netzwerkverlust, Provideränderung, fehlende
Berechtigung, voller Datenträger, ungültiges Archiv, Versionskonflikt,
Benutzerabbruch und unerwartete Daten müssen getrennte Codes besitzen.
Ein Retry ist nur für idempotente Schritte automatisch erlaubt.
Schreibaktionen werden nicht blind wiederholt.

**Tests.** Happy Path, leere Eingabe, beschädigte Metadaten,
Cancellation, Timeout, doppelter Aufruf, Wiederanlauf nach Abbruch und
mindestens ein Sicherheitsfall. Dateisystem- und HTTP-Zugriffe werden
gemockt. Integrationstest nutzt ein temporäres Verzeichnis und
deterministische Fixtures.

**Akzeptanzkriterien.** Die Funktion ist über die HESPERIA-UI
erreichbar, vollständig abbrechbar, erzeugt verständliche Logs,
verändert bei Dry-Run nichts und hinterlässt bei Fehlschlag keinen halb
installierten Zustand. Dokumentation und Tooltips sind vorhanden.

## 52. Implementierungskarte: Notifications

**Zweck.** Diese Komponente kapselt Updates und Fehler ohne Spam. Sie
darf keine Verantwortung aus benachbarten Schichten übernehmen. UI,
Persistenz und Transport werden über Interfaces angebunden, damit Tests
ohne echte PS4 und ohne Internet laufen können.

**Eingaben.** Normalisierte Konfiguration, CancellationToken, optional
ConsoleContext und bereits validierte Artefakt-Metadaten. Ungeprüfte
Texte aus Netzwerkquellen gelten grundsätzlich als nicht
vertrauenswürdig. Pfade werden vor Nutzung normalisiert; URLs werden
gegen das Provider-Schema geprüft.

**Ausgaben.** Ein typisiertes Ergebnisobjekt mit Status (`Success`,
`Warning`, `Failed`, `Cancelled`), maschinenlesbarem Fehlercode,
benutzerfreundlicher Kurzmeldung und technischen Details für das Log.
Exceptions dürfen die UI-Grenze nicht ungefiltert überschreiten.

**Ablauf.** 1. Voraussetzungen prüfen. 2. Eingaben validieren. 3.
Dry-Run bzw. Plan erzeugen. 4. Falls schreibend: Backup/Checkpoint. 5.
Operation in Staging ausführen. 6. Ergebnis validieren. 7. Atomar
übernehmen. 8. Action Journal schreiben. 9. UI aktualisieren. Bei
Fehlern wird Staging verworfen und der vorherige konsistente Zustand
beibehalten.

**Fehlerfälle.** Netzwerkverlust, Provideränderung, fehlende
Berechtigung, voller Datenträger, ungültiges Archiv, Versionskonflikt,
Benutzerabbruch und unerwartete Daten müssen getrennte Codes besitzen.
Ein Retry ist nur für idempotente Schritte automatisch erlaubt.
Schreibaktionen werden nicht blind wiederholt.

**Tests.** Happy Path, leere Eingabe, beschädigte Metadaten,
Cancellation, Timeout, doppelter Aufruf, Wiederanlauf nach Abbruch und
mindestens ein Sicherheitsfall. Dateisystem- und HTTP-Zugriffe werden
gemockt. Integrationstest nutzt ein temporäres Verzeichnis und
deterministische Fixtures.

**Akzeptanzkriterien.** Die Funktion ist über die HESPERIA-UI
erreichbar, vollständig abbrechbar, erzeugt verständliche Logs,
verändert bei Dry-Run nichts und hinterlässt bei Fehlschlag keinen halb
installierten Zustand. Dokumentation und Tooltips sind vorhanden.

## 53. Implementierungskarte: Search

**Zweck.** Diese Komponente kapselt Titel/CUSA/Tags. Sie darf keine
Verantwortung aus benachbarten Schichten übernehmen. UI, Persistenz und
Transport werden über Interfaces angebunden, damit Tests ohne echte PS4
und ohne Internet laufen können.

**Eingaben.** Normalisierte Konfiguration, CancellationToken, optional
ConsoleContext und bereits validierte Artefakt-Metadaten. Ungeprüfte
Texte aus Netzwerkquellen gelten grundsätzlich als nicht
vertrauenswürdig. Pfade werden vor Nutzung normalisiert; URLs werden
gegen das Provider-Schema geprüft.

**Ausgaben.** Ein typisiertes Ergebnisobjekt mit Status (`Success`,
`Warning`, `Failed`, `Cancelled`), maschinenlesbarem Fehlercode,
benutzerfreundlicher Kurzmeldung und technischen Details für das Log.
Exceptions dürfen die UI-Grenze nicht ungefiltert überschreiten.

**Ablauf.** 1. Voraussetzungen prüfen. 2. Eingaben validieren. 3.
Dry-Run bzw. Plan erzeugen. 4. Falls schreibend: Backup/Checkpoint. 5.
Operation in Staging ausführen. 6. Ergebnis validieren. 7. Atomar
übernehmen. 8. Action Journal schreiben. 9. UI aktualisieren. Bei
Fehlern wird Staging verworfen und der vorherige konsistente Zustand
beibehalten.

**Fehlerfälle.** Netzwerkverlust, Provideränderung, fehlende
Berechtigung, voller Datenträger, ungültiges Archiv, Versionskonflikt,
Benutzerabbruch und unerwartete Daten müssen getrennte Codes besitzen.
Ein Retry ist nur für idempotente Schritte automatisch erlaubt.
Schreibaktionen werden nicht blind wiederholt.

**Tests.** Happy Path, leere Eingabe, beschädigte Metadaten,
Cancellation, Timeout, doppelter Aufruf, Wiederanlauf nach Abbruch und
mindestens ein Sicherheitsfall. Dateisystem- und HTTP-Zugriffe werden
gemockt. Integrationstest nutzt ein temporäres Verzeichnis und
deterministische Fixtures.

**Akzeptanzkriterien.** Die Funktion ist über die HESPERIA-UI
erreichbar, vollständig abbrechbar, erzeugt verständliche Logs,
verändert bei Dry-Run nichts und hinterlässt bei Fehlschlag keinen halb
installierten Zustand. Dokumentation und Tooltips sind vorhanden.

## 54. Implementierungskarte: Bulk Download

**Zweck.** Diese Komponente kapselt sichere Mehrfachdownloads. Sie darf
keine Verantwortung aus benachbarten Schichten übernehmen. UI,
Persistenz und Transport werden über Interfaces angebunden, damit Tests
ohne echte PS4 und ohne Internet laufen können.

**Eingaben.** Normalisierte Konfiguration, CancellationToken, optional
ConsoleContext und bereits validierte Artefakt-Metadaten. Ungeprüfte
Texte aus Netzwerkquellen gelten grundsätzlich als nicht
vertrauenswürdig. Pfade werden vor Nutzung normalisiert; URLs werden
gegen das Provider-Schema geprüft.

**Ausgaben.** Ein typisiertes Ergebnisobjekt mit Status (`Success`,
`Warning`, `Failed`, `Cancelled`), maschinenlesbarem Fehlercode,
benutzerfreundlicher Kurzmeldung und technischen Details für das Log.
Exceptions dürfen die UI-Grenze nicht ungefiltert überschreiten.

**Ablauf.** 1. Voraussetzungen prüfen. 2. Eingaben validieren. 3.
Dry-Run bzw. Plan erzeugen. 4. Falls schreibend: Backup/Checkpoint. 5.
Operation in Staging ausführen. 6. Ergebnis validieren. 7. Atomar
übernehmen. 8. Action Journal schreiben. 9. UI aktualisieren. Bei
Fehlern wird Staging verworfen und der vorherige konsistente Zustand
beibehalten.

**Fehlerfälle.** Netzwerkverlust, Provideränderung, fehlende
Berechtigung, voller Datenträger, ungültiges Archiv, Versionskonflikt,
Benutzerabbruch und unerwartete Daten müssen getrennte Codes besitzen.
Ein Retry ist nur für idempotente Schritte automatisch erlaubt.
Schreibaktionen werden nicht blind wiederholt.

**Tests.** Happy Path, leere Eingabe, beschädigte Metadaten,
Cancellation, Timeout, doppelter Aufruf, Wiederanlauf nach Abbruch und
mindestens ein Sicherheitsfall. Dateisystem- und HTTP-Zugriffe werden
gemockt. Integrationstest nutzt ein temporäres Verzeichnis und
deterministische Fixtures.

**Akzeptanzkriterien.** Die Funktion ist über die HESPERIA-UI
erreichbar, vollständig abbrechbar, erzeugt verständliche Logs,
verändert bei Dry-Run nichts und hinterlässt bei Fehlschlag keinen halb
installierten Zustand. Dokumentation und Tooltips sind vorhanden.

## 55. Implementierungskarte: Conflict Detection

**Zweck.** Diese Komponente kapselt Patch-/Plugin-Konflikte. Sie darf
keine Verantwortung aus benachbarten Schichten übernehmen. UI,
Persistenz und Transport werden über Interfaces angebunden, damit Tests
ohne echte PS4 und ohne Internet laufen können.

**Eingaben.** Normalisierte Konfiguration, CancellationToken, optional
ConsoleContext und bereits validierte Artefakt-Metadaten. Ungeprüfte
Texte aus Netzwerkquellen gelten grundsätzlich als nicht
vertrauenswürdig. Pfade werden vor Nutzung normalisiert; URLs werden
gegen das Provider-Schema geprüft.

**Ausgaben.** Ein typisiertes Ergebnisobjekt mit Status (`Success`,
`Warning`, `Failed`, `Cancelled`), maschinenlesbarem Fehlercode,
benutzerfreundlicher Kurzmeldung und technischen Details für das Log.
Exceptions dürfen die UI-Grenze nicht ungefiltert überschreiten.

**Ablauf.** 1. Voraussetzungen prüfen. 2. Eingaben validieren. 3.
Dry-Run bzw. Plan erzeugen. 4. Falls schreibend: Backup/Checkpoint. 5.
Operation in Staging ausführen. 6. Ergebnis validieren. 7. Atomar
übernehmen. 8. Action Journal schreiben. 9. UI aktualisieren. Bei
Fehlern wird Staging verworfen und der vorherige konsistente Zustand
beibehalten.

**Fehlerfälle.** Netzwerkverlust, Provideränderung, fehlende
Berechtigung, voller Datenträger, ungültiges Archiv, Versionskonflikt,
Benutzerabbruch und unerwartete Daten müssen getrennte Codes besitzen.
Ein Retry ist nur für idempotente Schritte automatisch erlaubt.
Schreibaktionen werden nicht blind wiederholt.

**Tests.** Happy Path, leere Eingabe, beschädigte Metadaten,
Cancellation, Timeout, doppelter Aufruf, Wiederanlauf nach Abbruch und
mindestens ein Sicherheitsfall. Dateisystem- und HTTP-Zugriffe werden
gemockt. Integrationstest nutzt ein temporäres Verzeichnis und
deterministische Fixtures.

**Akzeptanzkriterien.** Die Funktion ist über die HESPERIA-UI
erreichbar, vollständig abbrechbar, erzeugt verständliche Logs,
verändert bei Dry-Run nichts und hinterlässt bei Fehlschlag keinen halb
installierten Zustand. Dokumentation und Tooltips sind vorhanden.

## 56. Implementierungskarte: Rollback

**Zweck.** Diese Komponente kapselt letzte Änderung zurücknehmen. Sie
darf keine Verantwortung aus benachbarten Schichten übernehmen. UI,
Persistenz und Transport werden über Interfaces angebunden, damit Tests
ohne echte PS4 und ohne Internet laufen können.

**Eingaben.** Normalisierte Konfiguration, CancellationToken, optional
ConsoleContext und bereits validierte Artefakt-Metadaten. Ungeprüfte
Texte aus Netzwerkquellen gelten grundsätzlich als nicht
vertrauenswürdig. Pfade werden vor Nutzung normalisiert; URLs werden
gegen das Provider-Schema geprüft.

**Ausgaben.** Ein typisiertes Ergebnisobjekt mit Status (`Success`,
`Warning`, `Failed`, `Cancelled`), maschinenlesbarem Fehlercode,
benutzerfreundlicher Kurzmeldung und technischen Details für das Log.
Exceptions dürfen die UI-Grenze nicht ungefiltert überschreiten.

**Ablauf.** 1. Voraussetzungen prüfen. 2. Eingaben validieren. 3.
Dry-Run bzw. Plan erzeugen. 4. Falls schreibend: Backup/Checkpoint. 5.
Operation in Staging ausführen. 6. Ergebnis validieren. 7. Atomar
übernehmen. 8. Action Journal schreiben. 9. UI aktualisieren. Bei
Fehlern wird Staging verworfen und der vorherige konsistente Zustand
beibehalten.

**Fehlerfälle.** Netzwerkverlust, Provideränderung, fehlende
Berechtigung, voller Datenträger, ungültiges Archiv, Versionskonflikt,
Benutzerabbruch und unerwartete Daten müssen getrennte Codes besitzen.
Ein Retry ist nur für idempotente Schritte automatisch erlaubt.
Schreibaktionen werden nicht blind wiederholt.

**Tests.** Happy Path, leere Eingabe, beschädigte Metadaten,
Cancellation, Timeout, doppelter Aufruf, Wiederanlauf nach Abbruch und
mindestens ein Sicherheitsfall. Dateisystem- und HTTP-Zugriffe werden
gemockt. Integrationstest nutzt ein temporäres Verzeichnis und
deterministische Fixtures.

**Akzeptanzkriterien.** Die Funktion ist über die HESPERIA-UI
erreichbar, vollständig abbrechbar, erzeugt verständliche Logs,
verändert bei Dry-Run nichts und hinterlässt bei Fehlschlag keinen halb
installierten Zustand. Dokumentation und Tooltips sind vorhanden.

## 57. Implementierungskarte: Offline Mode

**Zweck.** Diese Komponente kapselt vollständig aus Cache arbeiten. Sie
darf keine Verantwortung aus benachbarten Schichten übernehmen. UI,
Persistenz und Transport werden über Interfaces angebunden, damit Tests
ohne echte PS4 und ohne Internet laufen können.

**Eingaben.** Normalisierte Konfiguration, CancellationToken, optional
ConsoleContext und bereits validierte Artefakt-Metadaten. Ungeprüfte
Texte aus Netzwerkquellen gelten grundsätzlich als nicht
vertrauenswürdig. Pfade werden vor Nutzung normalisiert; URLs werden
gegen das Provider-Schema geprüft.

**Ausgaben.** Ein typisiertes Ergebnisobjekt mit Status (`Success`,
`Warning`, `Failed`, `Cancelled`), maschinenlesbarem Fehlercode,
benutzerfreundlicher Kurzmeldung und technischen Details für das Log.
Exceptions dürfen die UI-Grenze nicht ungefiltert überschreiten.

**Ablauf.** 1. Voraussetzungen prüfen. 2. Eingaben validieren. 3.
Dry-Run bzw. Plan erzeugen. 4. Falls schreibend: Backup/Checkpoint. 5.
Operation in Staging ausführen. 6. Ergebnis validieren. 7. Atomar
übernehmen. 8. Action Journal schreiben. 9. UI aktualisieren. Bei
Fehlern wird Staging verworfen und der vorherige konsistente Zustand
beibehalten.

**Fehlerfälle.** Netzwerkverlust, Provideränderung, fehlende
Berechtigung, voller Datenträger, ungültiges Archiv, Versionskonflikt,
Benutzerabbruch und unerwartete Daten müssen getrennte Codes besitzen.
Ein Retry ist nur für idempotente Schritte automatisch erlaubt.
Schreibaktionen werden nicht blind wiederholt.

**Tests.** Happy Path, leere Eingabe, beschädigte Metadaten,
Cancellation, Timeout, doppelter Aufruf, Wiederanlauf nach Abbruch und
mindestens ein Sicherheitsfall. Dateisystem- und HTTP-Zugriffe werden
gemockt. Integrationstest nutzt ein temporäres Verzeichnis und
deterministische Fixtures.

**Akzeptanzkriterien.** Die Funktion ist über die HESPERIA-UI
erreichbar, vollständig abbrechbar, erzeugt verständliche Logs,
verändert bei Dry-Run nichts und hinterlässt bei Fehlschlag keinen halb
installierten Zustand. Dokumentation und Tooltips sind vorhanden.

## 58. Implementierungskarte: Import Local

**Zweck.** Diese Komponente kapselt lokale Cheats/Patches prüfen. Sie
darf keine Verantwortung aus benachbarten Schichten übernehmen. UI,
Persistenz und Transport werden über Interfaces angebunden, damit Tests
ohne echte PS4 und ohne Internet laufen können.

**Eingaben.** Normalisierte Konfiguration, CancellationToken, optional
ConsoleContext und bereits validierte Artefakt-Metadaten. Ungeprüfte
Texte aus Netzwerkquellen gelten grundsätzlich als nicht
vertrauenswürdig. Pfade werden vor Nutzung normalisiert; URLs werden
gegen das Provider-Schema geprüft.

**Ausgaben.** Ein typisiertes Ergebnisobjekt mit Status (`Success`,
`Warning`, `Failed`, `Cancelled`), maschinenlesbarem Fehlercode,
benutzerfreundlicher Kurzmeldung und technischen Details für das Log.
Exceptions dürfen die UI-Grenze nicht ungefiltert überschreiten.

**Ablauf.** 1. Voraussetzungen prüfen. 2. Eingaben validieren. 3.
Dry-Run bzw. Plan erzeugen. 4. Falls schreibend: Backup/Checkpoint. 5.
Operation in Staging ausführen. 6. Ergebnis validieren. 7. Atomar
übernehmen. 8. Action Journal schreiben. 9. UI aktualisieren. Bei
Fehlern wird Staging verworfen und der vorherige konsistente Zustand
beibehalten.

**Fehlerfälle.** Netzwerkverlust, Provideränderung, fehlende
Berechtigung, voller Datenträger, ungültiges Archiv, Versionskonflikt,
Benutzerabbruch und unerwartete Daten müssen getrennte Codes besitzen.
Ein Retry ist nur für idempotente Schritte automatisch erlaubt.
Schreibaktionen werden nicht blind wiederholt.

**Tests.** Happy Path, leere Eingabe, beschädigte Metadaten,
Cancellation, Timeout, doppelter Aufruf, Wiederanlauf nach Abbruch und
mindestens ein Sicherheitsfall. Dateisystem- und HTTP-Zugriffe werden
gemockt. Integrationstest nutzt ein temporäres Verzeichnis und
deterministische Fixtures.

**Akzeptanzkriterien.** Die Funktion ist über die HESPERIA-UI
erreichbar, vollständig abbrechbar, erzeugt verständliche Logs,
verändert bei Dry-Run nichts und hinterlässt bei Fehlschlag keinen halb
installierten Zustand. Dokumentation und Tooltips sind vorhanden.

## 59. Implementierungskarte: Export Pack

**Zweck.** Diese Komponente kapselt reproduzierbares Offline-Pack. Sie
darf keine Verantwortung aus benachbarten Schichten übernehmen. UI,
Persistenz und Transport werden über Interfaces angebunden, damit Tests
ohne echte PS4 und ohne Internet laufen können.

**Eingaben.** Normalisierte Konfiguration, CancellationToken, optional
ConsoleContext und bereits validierte Artefakt-Metadaten. Ungeprüfte
Texte aus Netzwerkquellen gelten grundsätzlich als nicht
vertrauenswürdig. Pfade werden vor Nutzung normalisiert; URLs werden
gegen das Provider-Schema geprüft.

**Ausgaben.** Ein typisiertes Ergebnisobjekt mit Status (`Success`,
`Warning`, `Failed`, `Cancelled`), maschinenlesbarem Fehlercode,
benutzerfreundlicher Kurzmeldung und technischen Details für das Log.
Exceptions dürfen die UI-Grenze nicht ungefiltert überschreiten.

**Ablauf.** 1. Voraussetzungen prüfen. 2. Eingaben validieren. 3.
Dry-Run bzw. Plan erzeugen. 4. Falls schreibend: Backup/Checkpoint. 5.
Operation in Staging ausführen. 6. Ergebnis validieren. 7. Atomar
übernehmen. 8. Action Journal schreiben. 9. UI aktualisieren. Bei
Fehlern wird Staging verworfen und der vorherige konsistente Zustand
beibehalten.

**Fehlerfälle.** Netzwerkverlust, Provideränderung, fehlende
Berechtigung, voller Datenträger, ungültiges Archiv, Versionskonflikt,
Benutzerabbruch und unerwartete Daten müssen getrennte Codes besitzen.
Ein Retry ist nur für idempotente Schritte automatisch erlaubt.
Schreibaktionen werden nicht blind wiederholt.

**Tests.** Happy Path, leere Eingabe, beschädigte Metadaten,
Cancellation, Timeout, doppelter Aufruf, Wiederanlauf nach Abbruch und
mindestens ein Sicherheitsfall. Dateisystem- und HTTP-Zugriffe werden
gemockt. Integrationstest nutzt ein temporäres Verzeichnis und
deterministische Fixtures.

**Akzeptanzkriterien.** Die Funktion ist über die HESPERIA-UI
erreichbar, vollständig abbrechbar, erzeugt verständliche Logs,
verändert bei Dry-Run nichts und hinterlässt bei Fehlschlag keinen halb
installierten Zustand. Dokumentation und Tooltips sind vorhanden.

## 60. Implementierungskarte: Manifest

**Zweck.** Diese Komponente kapselt Quellen/Hashes/Versionen. Sie darf
keine Verantwortung aus benachbarten Schichten übernehmen. UI,
Persistenz und Transport werden über Interfaces angebunden, damit Tests
ohne echte PS4 und ohne Internet laufen können.

**Eingaben.** Normalisierte Konfiguration, CancellationToken, optional
ConsoleContext und bereits validierte Artefakt-Metadaten. Ungeprüfte
Texte aus Netzwerkquellen gelten grundsätzlich als nicht
vertrauenswürdig. Pfade werden vor Nutzung normalisiert; URLs werden
gegen das Provider-Schema geprüft.

**Ausgaben.** Ein typisiertes Ergebnisobjekt mit Status (`Success`,
`Warning`, `Failed`, `Cancelled`), maschinenlesbarem Fehlercode,
benutzerfreundlicher Kurzmeldung und technischen Details für das Log.
Exceptions dürfen die UI-Grenze nicht ungefiltert überschreiten.

**Ablauf.** 1. Voraussetzungen prüfen. 2. Eingaben validieren. 3.
Dry-Run bzw. Plan erzeugen. 4. Falls schreibend: Backup/Checkpoint. 5.
Operation in Staging ausführen. 6. Ergebnis validieren. 7. Atomar
übernehmen. 8. Action Journal schreiben. 9. UI aktualisieren. Bei
Fehlern wird Staging verworfen und der vorherige konsistente Zustand
beibehalten.

**Fehlerfälle.** Netzwerkverlust, Provideränderung, fehlende
Berechtigung, voller Datenträger, ungültiges Archiv, Versionskonflikt,
Benutzerabbruch und unerwartete Daten müssen getrennte Codes besitzen.
Ein Retry ist nur für idempotente Schritte automatisch erlaubt.
Schreibaktionen werden nicht blind wiederholt.

**Tests.** Happy Path, leere Eingabe, beschädigte Metadaten,
Cancellation, Timeout, doppelter Aufruf, Wiederanlauf nach Abbruch und
mindestens ein Sicherheitsfall. Dateisystem- und HTTP-Zugriffe werden
gemockt. Integrationstest nutzt ein temporäres Verzeichnis und
deterministische Fixtures.

**Akzeptanzkriterien.** Die Funktion ist über die HESPERIA-UI
erreichbar, vollständig abbrechbar, erzeugt verständliche Logs,
verändert bei Dry-Run nichts und hinterlässt bei Fehlschlag keinen halb
installierten Zustand. Dokumentation und Tooltips sind vorhanden.

## 61. Implementierungskarte: Update Scheduler

**Zweck.** Diese Komponente kapselt manuell/periodisch ohne Zwang. Sie
darf keine Verantwortung aus benachbarten Schichten übernehmen. UI,
Persistenz und Transport werden über Interfaces angebunden, damit Tests
ohne echte PS4 und ohne Internet laufen können.

**Eingaben.** Normalisierte Konfiguration, CancellationToken, optional
ConsoleContext und bereits validierte Artefakt-Metadaten. Ungeprüfte
Texte aus Netzwerkquellen gelten grundsätzlich als nicht
vertrauenswürdig. Pfade werden vor Nutzung normalisiert; URLs werden
gegen das Provider-Schema geprüft.

**Ausgaben.** Ein typisiertes Ergebnisobjekt mit Status (`Success`,
`Warning`, `Failed`, `Cancelled`), maschinenlesbarem Fehlercode,
benutzerfreundlicher Kurzmeldung und technischen Details für das Log.
Exceptions dürfen die UI-Grenze nicht ungefiltert überschreiten.

**Ablauf.** 1. Voraussetzungen prüfen. 2. Eingaben validieren. 3.
Dry-Run bzw. Plan erzeugen. 4. Falls schreibend: Backup/Checkpoint. 5.
Operation in Staging ausführen. 6. Ergebnis validieren. 7. Atomar
übernehmen. 8. Action Journal schreiben. 9. UI aktualisieren. Bei
Fehlern wird Staging verworfen und der vorherige konsistente Zustand
beibehalten.

**Fehlerfälle.** Netzwerkverlust, Provideränderung, fehlende
Berechtigung, voller Datenträger, ungültiges Archiv, Versionskonflikt,
Benutzerabbruch und unerwartete Daten müssen getrennte Codes besitzen.
Ein Retry ist nur für idempotente Schritte automatisch erlaubt.
Schreibaktionen werden nicht blind wiederholt.

**Tests.** Happy Path, leere Eingabe, beschädigte Metadaten,
Cancellation, Timeout, doppelter Aufruf, Wiederanlauf nach Abbruch und
mindestens ein Sicherheitsfall. Dateisystem- und HTTP-Zugriffe werden
gemockt. Integrationstest nutzt ein temporäres Verzeichnis und
deterministische Fixtures.

**Akzeptanzkriterien.** Die Funktion ist über die HESPERIA-UI
erreichbar, vollständig abbrechbar, erzeugt verständliche Logs,
verändert bei Dry-Run nichts und hinterlässt bei Fehlschlag keinen halb
installierten Zustand. Dokumentation und Tooltips sind vorhanden.

## 62. Implementierungskarte: UI Accessibility

**Zweck.** Diese Komponente kapselt Tastatur, Kontrast, Skalierung. Sie
darf keine Verantwortung aus benachbarten Schichten übernehmen. UI,
Persistenz und Transport werden über Interfaces angebunden, damit Tests
ohne echte PS4 und ohne Internet laufen können.

**Eingaben.** Normalisierte Konfiguration, CancellationToken, optional
ConsoleContext und bereits validierte Artefakt-Metadaten. Ungeprüfte
Texte aus Netzwerkquellen gelten grundsätzlich als nicht
vertrauenswürdig. Pfade werden vor Nutzung normalisiert; URLs werden
gegen das Provider-Schema geprüft.

**Ausgaben.** Ein typisiertes Ergebnisobjekt mit Status (`Success`,
`Warning`, `Failed`, `Cancelled`), maschinenlesbarem Fehlercode,
benutzerfreundlicher Kurzmeldung und technischen Details für das Log.
Exceptions dürfen die UI-Grenze nicht ungefiltert überschreiten.

**Ablauf.** 1. Voraussetzungen prüfen. 2. Eingaben validieren. 3.
Dry-Run bzw. Plan erzeugen. 4. Falls schreibend: Backup/Checkpoint. 5.
Operation in Staging ausführen. 6. Ergebnis validieren. 7. Atomar
übernehmen. 8. Action Journal schreiben. 9. UI aktualisieren. Bei
Fehlern wird Staging verworfen und der vorherige konsistente Zustand
beibehalten.

**Fehlerfälle.** Netzwerkverlust, Provideränderung, fehlende
Berechtigung, voller Datenträger, ungültiges Archiv, Versionskonflikt,
Benutzerabbruch und unerwartete Daten müssen getrennte Codes besitzen.
Ein Retry ist nur für idempotente Schritte automatisch erlaubt.
Schreibaktionen werden nicht blind wiederholt.

**Tests.** Happy Path, leere Eingabe, beschädigte Metadaten,
Cancellation, Timeout, doppelter Aufruf, Wiederanlauf nach Abbruch und
mindestens ein Sicherheitsfall. Dateisystem- und HTTP-Zugriffe werden
gemockt. Integrationstest nutzt ein temporäres Verzeichnis und
deterministische Fixtures.

**Akzeptanzkriterien.** Die Funktion ist über die HESPERIA-UI
erreichbar, vollständig abbrechbar, erzeugt verständliche Logs,
verändert bei Dry-Run nichts und hinterlässt bei Fehlschlag keinen halb
installierten Zustand. Dokumentation und Tooltips sind vorhanden.

## 63. Implementierungskarte: Localization

**Zweck.** Diese Komponente kapselt DE primär, EN vorbereiten. Sie darf
keine Verantwortung aus benachbarten Schichten übernehmen. UI,
Persistenz und Transport werden über Interfaces angebunden, damit Tests
ohne echte PS4 und ohne Internet laufen können.

**Eingaben.** Normalisierte Konfiguration, CancellationToken, optional
ConsoleContext und bereits validierte Artefakt-Metadaten. Ungeprüfte
Texte aus Netzwerkquellen gelten grundsätzlich als nicht
vertrauenswürdig. Pfade werden vor Nutzung normalisiert; URLs werden
gegen das Provider-Schema geprüft.

**Ausgaben.** Ein typisiertes Ergebnisobjekt mit Status (`Success`,
`Warning`, `Failed`, `Cancelled`), maschinenlesbarem Fehlercode,
benutzerfreundlicher Kurzmeldung und technischen Details für das Log.
Exceptions dürfen die UI-Grenze nicht ungefiltert überschreiten.

**Ablauf.** 1. Voraussetzungen prüfen. 2. Eingaben validieren. 3.
Dry-Run bzw. Plan erzeugen. 4. Falls schreibend: Backup/Checkpoint. 5.
Operation in Staging ausführen. 6. Ergebnis validieren. 7. Atomar
übernehmen. 8. Action Journal schreiben. 9. UI aktualisieren. Bei
Fehlern wird Staging verworfen und der vorherige konsistente Zustand
beibehalten.

**Fehlerfälle.** Netzwerkverlust, Provideränderung, fehlende
Berechtigung, voller Datenträger, ungültiges Archiv, Versionskonflikt,
Benutzerabbruch und unerwartete Daten müssen getrennte Codes besitzen.
Ein Retry ist nur für idempotente Schritte automatisch erlaubt.
Schreibaktionen werden nicht blind wiederholt.

**Tests.** Happy Path, leere Eingabe, beschädigte Metadaten,
Cancellation, Timeout, doppelter Aufruf, Wiederanlauf nach Abbruch und
mindestens ein Sicherheitsfall. Dateisystem- und HTTP-Zugriffe werden
gemockt. Integrationstest nutzt ein temporäres Verzeichnis und
deterministische Fixtures.

**Akzeptanzkriterien.** Die Funktion ist über die HESPERIA-UI
erreichbar, vollständig abbrechbar, erzeugt verständliche Logs,
verändert bei Dry-Run nichts und hinterlässt bei Fehlschlag keinen halb
installierten Zustand. Dokumentation und Tooltips sind vorhanden.

## 64. Implementierungskarte: Telemetry

**Zweck.** Diese Komponente kapselt standardmäßig keine externe
Telemetrie. Sie darf keine Verantwortung aus benachbarten Schichten
übernehmen. UI, Persistenz und Transport werden über Interfaces
angebunden, damit Tests ohne echte PS4 und ohne Internet laufen können.

**Eingaben.** Normalisierte Konfiguration, CancellationToken, optional
ConsoleContext und bereits validierte Artefakt-Metadaten. Ungeprüfte
Texte aus Netzwerkquellen gelten grundsätzlich als nicht
vertrauenswürdig. Pfade werden vor Nutzung normalisiert; URLs werden
gegen das Provider-Schema geprüft.

**Ausgaben.** Ein typisiertes Ergebnisobjekt mit Status (`Success`,
`Warning`, `Failed`, `Cancelled`), maschinenlesbarem Fehlercode,
benutzerfreundlicher Kurzmeldung und technischen Details für das Log.
Exceptions dürfen die UI-Grenze nicht ungefiltert überschreiten.

**Ablauf.** 1. Voraussetzungen prüfen. 2. Eingaben validieren. 3.
Dry-Run bzw. Plan erzeugen. 4. Falls schreibend: Backup/Checkpoint. 5.
Operation in Staging ausführen. 6. Ergebnis validieren. 7. Atomar
übernehmen. 8. Action Journal schreiben. 9. UI aktualisieren. Bei
Fehlern wird Staging verworfen und der vorherige konsistente Zustand
beibehalten.

**Fehlerfälle.** Netzwerkverlust, Provideränderung, fehlende
Berechtigung, voller Datenträger, ungültiges Archiv, Versionskonflikt,
Benutzerabbruch und unerwartete Daten müssen getrennte Codes besitzen.
Ein Retry ist nur für idempotente Schritte automatisch erlaubt.
Schreibaktionen werden nicht blind wiederholt.

**Tests.** Happy Path, leere Eingabe, beschädigte Metadaten,
Cancellation, Timeout, doppelter Aufruf, Wiederanlauf nach Abbruch und
mindestens ein Sicherheitsfall. Dateisystem- und HTTP-Zugriffe werden
gemockt. Integrationstest nutzt ein temporäres Verzeichnis und
deterministische Fixtures.

**Akzeptanzkriterien.** Die Funktion ist über die HESPERIA-UI
erreichbar, vollständig abbrechbar, erzeugt verständliche Logs,
verändert bei Dry-Run nichts und hinterlässt bei Fehlschlag keinen halb
installierten Zustand. Dokumentation und Tooltips sind vorhanden.

## 65. Implementierungskarte: Privacy

**Zweck.** Diese Komponente kapselt minimale lokale Daten. Sie darf
keine Verantwortung aus benachbarten Schichten übernehmen. UI,
Persistenz und Transport werden über Interfaces angebunden, damit Tests
ohne echte PS4 und ohne Internet laufen können.

**Eingaben.** Normalisierte Konfiguration, CancellationToken, optional
ConsoleContext und bereits validierte Artefakt-Metadaten. Ungeprüfte
Texte aus Netzwerkquellen gelten grundsätzlich als nicht
vertrauenswürdig. Pfade werden vor Nutzung normalisiert; URLs werden
gegen das Provider-Schema geprüft.

**Ausgaben.** Ein typisiertes Ergebnisobjekt mit Status (`Success`,
`Warning`, `Failed`, `Cancelled`), maschinenlesbarem Fehlercode,
benutzerfreundlicher Kurzmeldung und technischen Details für das Log.
Exceptions dürfen die UI-Grenze nicht ungefiltert überschreiten.

**Ablauf.** 1. Voraussetzungen prüfen. 2. Eingaben validieren. 3.
Dry-Run bzw. Plan erzeugen. 4. Falls schreibend: Backup/Checkpoint. 5.
Operation in Staging ausführen. 6. Ergebnis validieren. 7. Atomar
übernehmen. 8. Action Journal schreiben. 9. UI aktualisieren. Bei
Fehlern wird Staging verworfen und der vorherige konsistente Zustand
beibehalten.

**Fehlerfälle.** Netzwerkverlust, Provideränderung, fehlende
Berechtigung, voller Datenträger, ungültiges Archiv, Versionskonflikt,
Benutzerabbruch und unerwartete Daten müssen getrennte Codes besitzen.
Ein Retry ist nur für idempotente Schritte automatisch erlaubt.
Schreibaktionen werden nicht blind wiederholt.

**Tests.** Happy Path, leere Eingabe, beschädigte Metadaten,
Cancellation, Timeout, doppelter Aufruf, Wiederanlauf nach Abbruch und
mindestens ein Sicherheitsfall. Dateisystem- und HTTP-Zugriffe werden
gemockt. Integrationstest nutzt ein temporäres Verzeichnis und
deterministische Fixtures.

**Akzeptanzkriterien.** Die Funktion ist über die HESPERIA-UI
erreichbar, vollständig abbrechbar, erzeugt verständliche Logs,
verändert bei Dry-Run nichts und hinterlässt bei Fehlschlag keinen halb
installierten Zustand. Dokumentation und Tooltips sind vorhanden.

## 66. Implementierungskarte: Security

**Zweck.** Diese Komponente kapselt Zip-Slip, Pfadprüfung, Limits. Sie
darf keine Verantwortung aus benachbarten Schichten übernehmen. UI,
Persistenz und Transport werden über Interfaces angebunden, damit Tests
ohne echte PS4 und ohne Internet laufen können.

**Eingaben.** Normalisierte Konfiguration, CancellationToken, optional
ConsoleContext und bereits validierte Artefakt-Metadaten. Ungeprüfte
Texte aus Netzwerkquellen gelten grundsätzlich als nicht
vertrauenswürdig. Pfade werden vor Nutzung normalisiert; URLs werden
gegen das Provider-Schema geprüft.

**Ausgaben.** Ein typisiertes Ergebnisobjekt mit Status (`Success`,
`Warning`, `Failed`, `Cancelled`), maschinenlesbarem Fehlercode,
benutzerfreundlicher Kurzmeldung und technischen Details für das Log.
Exceptions dürfen die UI-Grenze nicht ungefiltert überschreiten.

**Ablauf.** 1. Voraussetzungen prüfen. 2. Eingaben validieren. 3.
Dry-Run bzw. Plan erzeugen. 4. Falls schreibend: Backup/Checkpoint. 5.
Operation in Staging ausführen. 6. Ergebnis validieren. 7. Atomar
übernehmen. 8. Action Journal schreiben. 9. UI aktualisieren. Bei
Fehlern wird Staging verworfen und der vorherige konsistente Zustand
beibehalten.

**Fehlerfälle.** Netzwerkverlust, Provideränderung, fehlende
Berechtigung, voller Datenträger, ungültiges Archiv, Versionskonflikt,
Benutzerabbruch und unerwartete Daten müssen getrennte Codes besitzen.
Ein Retry ist nur für idempotente Schritte automatisch erlaubt.
Schreibaktionen werden nicht blind wiederholt.

**Tests.** Happy Path, leere Eingabe, beschädigte Metadaten,
Cancellation, Timeout, doppelter Aufruf, Wiederanlauf nach Abbruch und
mindestens ein Sicherheitsfall. Dateisystem- und HTTP-Zugriffe werden
gemockt. Integrationstest nutzt ein temporäres Verzeichnis und
deterministische Fixtures.

**Akzeptanzkriterien.** Die Funktion ist über die HESPERIA-UI
erreichbar, vollständig abbrechbar, erzeugt verständliche Logs,
verändert bei Dry-Run nichts und hinterlässt bei Fehlschlag keinen halb
installierten Zustand. Dokumentation und Tooltips sind vorhanden.

## 67. Implementierungskarte: Recovery

**Zweck.** Diese Komponente kapselt kaputter Cache/DB/Transfer. Sie darf
keine Verantwortung aus benachbarten Schichten übernehmen. UI,
Persistenz und Transport werden über Interfaces angebunden, damit Tests
ohne echte PS4 und ohne Internet laufen können.

**Eingaben.** Normalisierte Konfiguration, CancellationToken, optional
ConsoleContext und bereits validierte Artefakt-Metadaten. Ungeprüfte
Texte aus Netzwerkquellen gelten grundsätzlich als nicht
vertrauenswürdig. Pfade werden vor Nutzung normalisiert; URLs werden
gegen das Provider-Schema geprüft.

**Ausgaben.** Ein typisiertes Ergebnisobjekt mit Status (`Success`,
`Warning`, `Failed`, `Cancelled`), maschinenlesbarem Fehlercode,
benutzerfreundlicher Kurzmeldung und technischen Details für das Log.
Exceptions dürfen die UI-Grenze nicht ungefiltert überschreiten.

**Ablauf.** 1. Voraussetzungen prüfen. 2. Eingaben validieren. 3.
Dry-Run bzw. Plan erzeugen. 4. Falls schreibend: Backup/Checkpoint. 5.
Operation in Staging ausführen. 6. Ergebnis validieren. 7. Atomar
übernehmen. 8. Action Journal schreiben. 9. UI aktualisieren. Bei
Fehlern wird Staging verworfen und der vorherige konsistente Zustand
beibehalten.

**Fehlerfälle.** Netzwerkverlust, Provideränderung, fehlende
Berechtigung, voller Datenträger, ungültiges Archiv, Versionskonflikt,
Benutzerabbruch und unerwartete Daten müssen getrennte Codes besitzen.
Ein Retry ist nur für idempotente Schritte automatisch erlaubt.
Schreibaktionen werden nicht blind wiederholt.

**Tests.** Happy Path, leere Eingabe, beschädigte Metadaten,
Cancellation, Timeout, doppelter Aufruf, Wiederanlauf nach Abbruch und
mindestens ein Sicherheitsfall. Dateisystem- und HTTP-Zugriffe werden
gemockt. Integrationstest nutzt ein temporäres Verzeichnis und
deterministische Fixtures.

**Akzeptanzkriterien.** Die Funktion ist über die HESPERIA-UI
erreichbar, vollständig abbrechbar, erzeugt verständliche Logs,
verändert bei Dry-Run nichts und hinterlässt bei Fehlschlag keinen halb
installierten Zustand. Dokumentation und Tooltips sind vorhanden.

## 68. Implementierungskarte: Performance

**Zweck.** Diese Komponente kapselt Indexe, Lazy Loading. Sie darf keine
Verantwortung aus benachbarten Schichten übernehmen. UI, Persistenz und
Transport werden über Interfaces angebunden, damit Tests ohne echte PS4
und ohne Internet laufen können.

**Eingaben.** Normalisierte Konfiguration, CancellationToken, optional
ConsoleContext und bereits validierte Artefakt-Metadaten. Ungeprüfte
Texte aus Netzwerkquellen gelten grundsätzlich als nicht
vertrauenswürdig. Pfade werden vor Nutzung normalisiert; URLs werden
gegen das Provider-Schema geprüft.

**Ausgaben.** Ein typisiertes Ergebnisobjekt mit Status (`Success`,
`Warning`, `Failed`, `Cancelled`), maschinenlesbarem Fehlercode,
benutzerfreundlicher Kurzmeldung und technischen Details für das Log.
Exceptions dürfen die UI-Grenze nicht ungefiltert überschreiten.

**Ablauf.** 1. Voraussetzungen prüfen. 2. Eingaben validieren. 3.
Dry-Run bzw. Plan erzeugen. 4. Falls schreibend: Backup/Checkpoint. 5.
Operation in Staging ausführen. 6. Ergebnis validieren. 7. Atomar
übernehmen. 8. Action Journal schreiben. 9. UI aktualisieren. Bei
Fehlern wird Staging verworfen und der vorherige konsistente Zustand
beibehalten.

**Fehlerfälle.** Netzwerkverlust, Provideränderung, fehlende
Berechtigung, voller Datenträger, ungültiges Archiv, Versionskonflikt,
Benutzerabbruch und unerwartete Daten müssen getrennte Codes besitzen.
Ein Retry ist nur für idempotente Schritte automatisch erlaubt.
Schreibaktionen werden nicht blind wiederholt.

**Tests.** Happy Path, leere Eingabe, beschädigte Metadaten,
Cancellation, Timeout, doppelter Aufruf, Wiederanlauf nach Abbruch und
mindestens ein Sicherheitsfall. Dateisystem- und HTTP-Zugriffe werden
gemockt. Integrationstest nutzt ein temporäres Verzeichnis und
deterministische Fixtures.

**Akzeptanzkriterien.** Die Funktion ist über die HESPERIA-UI
erreichbar, vollständig abbrechbar, erzeugt verständliche Logs,
verändert bei Dry-Run nichts und hinterlässt bei Fehlschlag keinen halb
installierten Zustand. Dokumentation und Tooltips sind vorhanden.

## 69. Implementierungskarte: Testing

**Zweck.** Diese Komponente kapselt Fixtures und Regressionen. Sie darf
keine Verantwortung aus benachbarten Schichten übernehmen. UI,
Persistenz und Transport werden über Interfaces angebunden, damit Tests
ohne echte PS4 und ohne Internet laufen können.

**Eingaben.** Normalisierte Konfiguration, CancellationToken, optional
ConsoleContext und bereits validierte Artefakt-Metadaten. Ungeprüfte
Texte aus Netzwerkquellen gelten grundsätzlich als nicht
vertrauenswürdig. Pfade werden vor Nutzung normalisiert; URLs werden
gegen das Provider-Schema geprüft.

**Ausgaben.** Ein typisiertes Ergebnisobjekt mit Status (`Success`,
`Warning`, `Failed`, `Cancelled`), maschinenlesbarem Fehlercode,
benutzerfreundlicher Kurzmeldung und technischen Details für das Log.
Exceptions dürfen die UI-Grenze nicht ungefiltert überschreiten.

**Ablauf.** 1. Voraussetzungen prüfen. 2. Eingaben validieren. 3.
Dry-Run bzw. Plan erzeugen. 4. Falls schreibend: Backup/Checkpoint. 5.
Operation in Staging ausführen. 6. Ergebnis validieren. 7. Atomar
übernehmen. 8. Action Journal schreiben. 9. UI aktualisieren. Bei
Fehlern wird Staging verworfen und der vorherige konsistente Zustand
beibehalten.

**Fehlerfälle.** Netzwerkverlust, Provideränderung, fehlende
Berechtigung, voller Datenträger, ungültiges Archiv, Versionskonflikt,
Benutzerabbruch und unerwartete Daten müssen getrennte Codes besitzen.
Ein Retry ist nur für idempotente Schritte automatisch erlaubt.
Schreibaktionen werden nicht blind wiederholt.

**Tests.** Happy Path, leere Eingabe, beschädigte Metadaten,
Cancellation, Timeout, doppelter Aufruf, Wiederanlauf nach Abbruch und
mindestens ein Sicherheitsfall. Dateisystem- und HTTP-Zugriffe werden
gemockt. Integrationstest nutzt ein temporäres Verzeichnis und
deterministische Fixtures.

**Akzeptanzkriterien.** Die Funktion ist über die HESPERIA-UI
erreichbar, vollständig abbrechbar, erzeugt verständliche Logs,
verändert bei Dry-Run nichts und hinterlässt bei Fehlschlag keinen halb
installierten Zustand. Dokumentation und Tooltips sind vorhanden.

## 70. Implementierungskarte: CI

**Zweck.** Diese Komponente kapselt Build, Tests, Artefaktprüfung. Sie
darf keine Verantwortung aus benachbarten Schichten übernehmen. UI,
Persistenz und Transport werden über Interfaces angebunden, damit Tests
ohne echte PS4 und ohne Internet laufen können.

**Eingaben.** Normalisierte Konfiguration, CancellationToken, optional
ConsoleContext und bereits validierte Artefakt-Metadaten. Ungeprüfte
Texte aus Netzwerkquellen gelten grundsätzlich als nicht
vertrauenswürdig. Pfade werden vor Nutzung normalisiert; URLs werden
gegen das Provider-Schema geprüft.

**Ausgaben.** Ein typisiertes Ergebnisobjekt mit Status (`Success`,
`Warning`, `Failed`, `Cancelled`), maschinenlesbarem Fehlercode,
benutzerfreundlicher Kurzmeldung und technischen Details für das Log.
Exceptions dürfen die UI-Grenze nicht ungefiltert überschreiten.

**Ablauf.** 1. Voraussetzungen prüfen. 2. Eingaben validieren. 3.
Dry-Run bzw. Plan erzeugen. 4. Falls schreibend: Backup/Checkpoint. 5.
Operation in Staging ausführen. 6. Ergebnis validieren. 7. Atomar
übernehmen. 8. Action Journal schreiben. 9. UI aktualisieren. Bei
Fehlern wird Staging verworfen und der vorherige konsistente Zustand
beibehalten.

**Fehlerfälle.** Netzwerkverlust, Provideränderung, fehlende
Berechtigung, voller Datenträger, ungültiges Archiv, Versionskonflikt,
Benutzerabbruch und unerwartete Daten müssen getrennte Codes besitzen.
Ein Retry ist nur für idempotente Schritte automatisch erlaubt.
Schreibaktionen werden nicht blind wiederholt.

**Tests.** Happy Path, leere Eingabe, beschädigte Metadaten,
Cancellation, Timeout, doppelter Aufruf, Wiederanlauf nach Abbruch und
mindestens ein Sicherheitsfall. Dateisystem- und HTTP-Zugriffe werden
gemockt. Integrationstest nutzt ein temporäres Verzeichnis und
deterministische Fixtures.

**Akzeptanzkriterien.** Die Funktion ist über die HESPERIA-UI
erreichbar, vollständig abbrechbar, erzeugt verständliche Logs,
verändert bei Dry-Run nichts und hinterlässt bei Fehlschlag keinen halb
installierten Zustand. Dokumentation und Tooltips sind vorhanden.

## 71. Implementierungskarte: Documentation

**Zweck.** Diese Komponente kapselt In-App-Hilfe und README. Sie darf
keine Verantwortung aus benachbarten Schichten übernehmen. UI,
Persistenz und Transport werden über Interfaces angebunden, damit Tests
ohne echte PS4 und ohne Internet laufen können.

**Eingaben.** Normalisierte Konfiguration, CancellationToken, optional
ConsoleContext und bereits validierte Artefakt-Metadaten. Ungeprüfte
Texte aus Netzwerkquellen gelten grundsätzlich als nicht
vertrauenswürdig. Pfade werden vor Nutzung normalisiert; URLs werden
gegen das Provider-Schema geprüft.

**Ausgaben.** Ein typisiertes Ergebnisobjekt mit Status (`Success`,
`Warning`, `Failed`, `Cancelled`), maschinenlesbarem Fehlercode,
benutzerfreundlicher Kurzmeldung und technischen Details für das Log.
Exceptions dürfen die UI-Grenze nicht ungefiltert überschreiten.

**Ablauf.** 1. Voraussetzungen prüfen. 2. Eingaben validieren. 3.
Dry-Run bzw. Plan erzeugen. 4. Falls schreibend: Backup/Checkpoint. 5.
Operation in Staging ausführen. 6. Ergebnis validieren. 7. Atomar
übernehmen. 8. Action Journal schreiben. 9. UI aktualisieren. Bei
Fehlern wird Staging verworfen und der vorherige konsistente Zustand
beibehalten.

**Fehlerfälle.** Netzwerkverlust, Provideränderung, fehlende
Berechtigung, voller Datenträger, ungültiges Archiv, Versionskonflikt,
Benutzerabbruch und unerwartete Daten müssen getrennte Codes besitzen.
Ein Retry ist nur für idempotente Schritte automatisch erlaubt.
Schreibaktionen werden nicht blind wiederholt.

**Tests.** Happy Path, leere Eingabe, beschädigte Metadaten,
Cancellation, Timeout, doppelter Aufruf, Wiederanlauf nach Abbruch und
mindestens ein Sicherheitsfall. Dateisystem- und HTTP-Zugriffe werden
gemockt. Integrationstest nutzt ein temporäres Verzeichnis und
deterministische Fixtures.

**Akzeptanzkriterien.** Die Funktion ist über die HESPERIA-UI
erreichbar, vollständig abbrechbar, erzeugt verständliche Logs,
verändert bei Dry-Run nichts und hinterlässt bei Fehlschlag keinen halb
installierten Zustand. Dokumentation und Tooltips sind vorhanden.

## 72. Implementierungskarte: HESPERIA Shell

**Zweck.** Diese Komponente kapselt Navigation/Deep Links/Badges. Sie
darf keine Verantwortung aus benachbarten Schichten übernehmen. UI,
Persistenz und Transport werden über Interfaces angebunden, damit Tests
ohne echte PS4 und ohne Internet laufen können.

**Eingaben.** Normalisierte Konfiguration, CancellationToken, optional
ConsoleContext und bereits validierte Artefakt-Metadaten. Ungeprüfte
Texte aus Netzwerkquellen gelten grundsätzlich als nicht
vertrauenswürdig. Pfade werden vor Nutzung normalisiert; URLs werden
gegen das Provider-Schema geprüft.

**Ausgaben.** Ein typisiertes Ergebnisobjekt mit Status (`Success`,
`Warning`, `Failed`, `Cancelled`), maschinenlesbarem Fehlercode,
benutzerfreundlicher Kurzmeldung und technischen Details für das Log.
Exceptions dürfen die UI-Grenze nicht ungefiltert überschreiten.

**Ablauf.** 1. Voraussetzungen prüfen. 2. Eingaben validieren. 3.
Dry-Run bzw. Plan erzeugen. 4. Falls schreibend: Backup/Checkpoint. 5.
Operation in Staging ausführen. 6. Ergebnis validieren. 7. Atomar
übernehmen. 8. Action Journal schreiben. 9. UI aktualisieren. Bei
Fehlern wird Staging verworfen und der vorherige konsistente Zustand
beibehalten.

**Fehlerfälle.** Netzwerkverlust, Provideränderung, fehlende
Berechtigung, voller Datenträger, ungültiges Archiv, Versionskonflikt,
Benutzerabbruch und unerwartete Daten müssen getrennte Codes besitzen.
Ein Retry ist nur für idempotente Schritte automatisch erlaubt.
Schreibaktionen werden nicht blind wiederholt.

**Tests.** Happy Path, leere Eingabe, beschädigte Metadaten,
Cancellation, Timeout, doppelter Aufruf, Wiederanlauf nach Abbruch und
mindestens ein Sicherheitsfall. Dateisystem- und HTTP-Zugriffe werden
gemockt. Integrationstest nutzt ein temporäres Verzeichnis und
deterministische Fixtures.

**Akzeptanzkriterien.** Die Funktion ist über die HESPERIA-UI
erreichbar, vollständig abbrechbar, erzeugt verständliche Logs,
verändert bei Dry-Run nichts und hinterlässt bei Fehlschlag keinen halb
installierten Zustand. Dokumentation und Tooltips sind vorhanden.

## 73. Implementierungskarte: Migration CMD

**Zweck.** Diese Komponente kapselt Alt-CMD als Legacy-Import. Sie darf
keine Verantwortung aus benachbarten Schichten übernehmen. UI,
Persistenz und Transport werden über Interfaces angebunden, damit Tests
ohne echte PS4 und ohne Internet laufen können.

**Eingaben.** Normalisierte Konfiguration, CancellationToken, optional
ConsoleContext und bereits validierte Artefakt-Metadaten. Ungeprüfte
Texte aus Netzwerkquellen gelten grundsätzlich als nicht
vertrauenswürdig. Pfade werden vor Nutzung normalisiert; URLs werden
gegen das Provider-Schema geprüft.

**Ausgaben.** Ein typisiertes Ergebnisobjekt mit Status (`Success`,
`Warning`, `Failed`, `Cancelled`), maschinenlesbarem Fehlercode,
benutzerfreundlicher Kurzmeldung und technischen Details für das Log.
Exceptions dürfen die UI-Grenze nicht ungefiltert überschreiten.

**Ablauf.** 1. Voraussetzungen prüfen. 2. Eingaben validieren. 3.
Dry-Run bzw. Plan erzeugen. 4. Falls schreibend: Backup/Checkpoint. 5.
Operation in Staging ausführen. 6. Ergebnis validieren. 7. Atomar
übernehmen. 8. Action Journal schreiben. 9. UI aktualisieren. Bei
Fehlern wird Staging verworfen und der vorherige konsistente Zustand
beibehalten.

**Fehlerfälle.** Netzwerkverlust, Provideränderung, fehlende
Berechtigung, voller Datenträger, ungültiges Archiv, Versionskonflikt,
Benutzerabbruch und unerwartete Daten müssen getrennte Codes besitzen.
Ein Retry ist nur für idempotente Schritte automatisch erlaubt.
Schreibaktionen werden nicht blind wiederholt.

**Tests.** Happy Path, leere Eingabe, beschädigte Metadaten,
Cancellation, Timeout, doppelter Aufruf, Wiederanlauf nach Abbruch und
mindestens ein Sicherheitsfall. Dateisystem- und HTTP-Zugriffe werden
gemockt. Integrationstest nutzt ein temporäres Verzeichnis und
deterministische Fixtures.

**Akzeptanzkriterien.** Die Funktion ist über die HESPERIA-UI
erreichbar, vollständig abbrechbar, erzeugt verständliche Logs,
verändert bei Dry-Run nichts und hinterlässt bei Fehlschlag keinen halb
installierten Zustand. Dokumentation und Tooltips sind vorhanden.

## 74. Implementierungskarte: Safe Mode

**Zweck.** Diese Komponente kapselt Plugins/Patches deaktivieren. Sie
darf keine Verantwortung aus benachbarten Schichten übernehmen. UI,
Persistenz und Transport werden über Interfaces angebunden, damit Tests
ohne echte PS4 und ohne Internet laufen können.

**Eingaben.** Normalisierte Konfiguration, CancellationToken, optional
ConsoleContext und bereits validierte Artefakt-Metadaten. Ungeprüfte
Texte aus Netzwerkquellen gelten grundsätzlich als nicht
vertrauenswürdig. Pfade werden vor Nutzung normalisiert; URLs werden
gegen das Provider-Schema geprüft.

**Ausgaben.** Ein typisiertes Ergebnisobjekt mit Status (`Success`,
`Warning`, `Failed`, `Cancelled`), maschinenlesbarem Fehlercode,
benutzerfreundlicher Kurzmeldung und technischen Details für das Log.
Exceptions dürfen die UI-Grenze nicht ungefiltert überschreiten.

**Ablauf.** 1. Voraussetzungen prüfen. 2. Eingaben validieren. 3.
Dry-Run bzw. Plan erzeugen. 4. Falls schreibend: Backup/Checkpoint. 5.
Operation in Staging ausführen. 6. Ergebnis validieren. 7. Atomar
übernehmen. 8. Action Journal schreiben. 9. UI aktualisieren. Bei
Fehlern wird Staging verworfen und der vorherige konsistente Zustand
beibehalten.

**Fehlerfälle.** Netzwerkverlust, Provideränderung, fehlende
Berechtigung, voller Datenträger, ungültiges Archiv, Versionskonflikt,
Benutzerabbruch und unerwartete Daten müssen getrennte Codes besitzen.
Ein Retry ist nur für idempotente Schritte automatisch erlaubt.
Schreibaktionen werden nicht blind wiederholt.

**Tests.** Happy Path, leere Eingabe, beschädigte Metadaten,
Cancellation, Timeout, doppelter Aufruf, Wiederanlauf nach Abbruch und
mindestens ein Sicherheitsfall. Dateisystem- und HTTP-Zugriffe werden
gemockt. Integrationstest nutzt ein temporäres Verzeichnis und
deterministische Fixtures.

**Akzeptanzkriterien.** Die Funktion ist über die HESPERIA-UI
erreichbar, vollständig abbrechbar, erzeugt verständliche Logs,
verändert bei Dry-Run nichts und hinterlässt bei Fehlschlag keinen halb
installierten Zustand. Dokumentation und Tooltips sind vorhanden.

## 75. Implementierungskarte: Save Safety

**Zweck.** Diese Komponente kapselt Backup-Hinweise und Restore. Sie
darf keine Verantwortung aus benachbarten Schichten übernehmen. UI,
Persistenz und Transport werden über Interfaces angebunden, damit Tests
ohne echte PS4 und ohne Internet laufen können.

**Eingaben.** Normalisierte Konfiguration, CancellationToken, optional
ConsoleContext und bereits validierte Artefakt-Metadaten. Ungeprüfte
Texte aus Netzwerkquellen gelten grundsätzlich als nicht
vertrauenswürdig. Pfade werden vor Nutzung normalisiert; URLs werden
gegen das Provider-Schema geprüft.

**Ausgaben.** Ein typisiertes Ergebnisobjekt mit Status (`Success`,
`Warning`, `Failed`, `Cancelled`), maschinenlesbarem Fehlercode,
benutzerfreundlicher Kurzmeldung und technischen Details für das Log.
Exceptions dürfen die UI-Grenze nicht ungefiltert überschreiten.

**Ablauf.** 1. Voraussetzungen prüfen. 2. Eingaben validieren. 3.
Dry-Run bzw. Plan erzeugen. 4. Falls schreibend: Backup/Checkpoint. 5.
Operation in Staging ausführen. 6. Ergebnis validieren. 7. Atomar
übernehmen. 8. Action Journal schreiben. 9. UI aktualisieren. Bei
Fehlern wird Staging verworfen und der vorherige konsistente Zustand
beibehalten.

**Fehlerfälle.** Netzwerkverlust, Provideränderung, fehlende
Berechtigung, voller Datenträger, ungültiges Archiv, Versionskonflikt,
Benutzerabbruch und unerwartete Daten müssen getrennte Codes besitzen.
Ein Retry ist nur für idempotente Schritte automatisch erlaubt.
Schreibaktionen werden nicht blind wiederholt.

**Tests.** Happy Path, leere Eingabe, beschädigte Metadaten,
Cancellation, Timeout, doppelter Aufruf, Wiederanlauf nach Abbruch und
mindestens ein Sicherheitsfall. Dateisystem- und HTTP-Zugriffe werden
gemockt. Integrationstest nutzt ein temporäres Verzeichnis und
deterministische Fixtures.

**Akzeptanzkriterien.** Die Funktion ist über die HESPERIA-UI
erreichbar, vollständig abbrechbar, erzeugt verständliche Logs,
verändert bei Dry-Run nichts und hinterlässt bei Fehlschlag keinen halb
installierten Zustand. Dokumentation und Tooltips sind vorhanden.

## 76. Implementierungskarte: Source Attribution

**Zweck.** Diese Komponente kapselt Autoren/Quellen sichtbar. Sie darf
keine Verantwortung aus benachbarten Schichten übernehmen. UI,
Persistenz und Transport werden über Interfaces angebunden, damit Tests
ohne echte PS4 und ohne Internet laufen können.

**Eingaben.** Normalisierte Konfiguration, CancellationToken, optional
ConsoleContext und bereits validierte Artefakt-Metadaten. Ungeprüfte
Texte aus Netzwerkquellen gelten grundsätzlich als nicht
vertrauenswürdig. Pfade werden vor Nutzung normalisiert; URLs werden
gegen das Provider-Schema geprüft.

**Ausgaben.** Ein typisiertes Ergebnisobjekt mit Status (`Success`,
`Warning`, `Failed`, `Cancelled`), maschinenlesbarem Fehlercode,
benutzerfreundlicher Kurzmeldung und technischen Details für das Log.
Exceptions dürfen die UI-Grenze nicht ungefiltert überschreiten.

**Ablauf.** 1. Voraussetzungen prüfen. 2. Eingaben validieren. 3.
Dry-Run bzw. Plan erzeugen. 4. Falls schreibend: Backup/Checkpoint. 5.
Operation in Staging ausführen. 6. Ergebnis validieren. 7. Atomar
übernehmen. 8. Action Journal schreiben. 9. UI aktualisieren. Bei
Fehlern wird Staging verworfen und der vorherige konsistente Zustand
beibehalten.

**Fehlerfälle.** Netzwerkverlust, Provideränderung, fehlende
Berechtigung, voller Datenträger, ungültiges Archiv, Versionskonflikt,
Benutzerabbruch und unerwartete Daten müssen getrennte Codes besitzen.
Ein Retry ist nur für idempotente Schritte automatisch erlaubt.
Schreibaktionen werden nicht blind wiederholt.

**Tests.** Happy Path, leere Eingabe, beschädigte Metadaten,
Cancellation, Timeout, doppelter Aufruf, Wiederanlauf nach Abbruch und
mindestens ein Sicherheitsfall. Dateisystem- und HTTP-Zugriffe werden
gemockt. Integrationstest nutzt ein temporäres Verzeichnis und
deterministische Fixtures.

**Akzeptanzkriterien.** Die Funktion ist über die HESPERIA-UI
erreichbar, vollständig abbrechbar, erzeugt verständliche Logs,
verändert bei Dry-Run nichts und hinterlässt bei Fehlschlag keinen halb
installierten Zustand. Dokumentation und Tooltips sind vorhanden.

## 77. Implementierungskarte: Future Extensions

**Zweck.** Diese Komponente kapselt weitere Homebrew-Provider. Sie darf
keine Verantwortung aus benachbarten Schichten übernehmen. UI,
Persistenz und Transport werden über Interfaces angebunden, damit Tests
ohne echte PS4 und ohne Internet laufen können.

**Eingaben.** Normalisierte Konfiguration, CancellationToken, optional
ConsoleContext und bereits validierte Artefakt-Metadaten. Ungeprüfte
Texte aus Netzwerkquellen gelten grundsätzlich als nicht
vertrauenswürdig. Pfade werden vor Nutzung normalisiert; URLs werden
gegen das Provider-Schema geprüft.

**Ausgaben.** Ein typisiertes Ergebnisobjekt mit Status (`Success`,
`Warning`, `Failed`, `Cancelled`), maschinenlesbarem Fehlercode,
benutzerfreundlicher Kurzmeldung und technischen Details für das Log.
Exceptions dürfen die UI-Grenze nicht ungefiltert überschreiten.

**Ablauf.** 1. Voraussetzungen prüfen. 2. Eingaben validieren. 3.
Dry-Run bzw. Plan erzeugen. 4. Falls schreibend: Backup/Checkpoint. 5.
Operation in Staging ausführen. 6. Ergebnis validieren. 7. Atomar
übernehmen. 8. Action Journal schreiben. 9. UI aktualisieren. Bei
Fehlern wird Staging verworfen und der vorherige konsistente Zustand
beibehalten.

**Fehlerfälle.** Netzwerkverlust, Provideränderung, fehlende
Berechtigung, voller Datenträger, ungültiges Archiv, Versionskonflikt,
Benutzerabbruch und unerwartete Daten müssen getrennte Codes besitzen.
Ein Retry ist nur für idempotente Schritte automatisch erlaubt.
Schreibaktionen werden nicht blind wiederholt.

**Tests.** Happy Path, leere Eingabe, beschädigte Metadaten,
Cancellation, Timeout, doppelter Aufruf, Wiederanlauf nach Abbruch und
mindestens ein Sicherheitsfall. Dateisystem- und HTTP-Zugriffe werden
gemockt. Integrationstest nutzt ein temporäres Verzeichnis und
deterministische Fixtures.

**Akzeptanzkriterien.** Die Funktion ist über die HESPERIA-UI
erreichbar, vollständig abbrechbar, erzeugt verständliche Logs,
verändert bei Dry-Run nichts und hinterlässt bei Fehlschlag keinen halb
installierten Zustand. Dokumentation und Tooltips sind vorhanden.

::: {style="page-break-before: always;"}
:::

# 78. Fehlercode-Katalog

-   `PS4-0100` -- reservierter, stabiler Fehlercode. UI zeigt eine kurze
    Ursache; Log enthält Operation-ID, Komponente und technische
    Details. Codes dürfen nach Veröffentlichung nicht für eine andere
    Bedeutung wiederverwendet werden.
-   `PS4-0101` -- reservierter, stabiler Fehlercode. UI zeigt eine kurze
    Ursache; Log enthält Operation-ID, Komponente und technische
    Details. Codes dürfen nach Veröffentlichung nicht für eine andere
    Bedeutung wiederverwendet werden.
-   `PS4-0102` -- reservierter, stabiler Fehlercode. UI zeigt eine kurze
    Ursache; Log enthält Operation-ID, Komponente und technische
    Details. Codes dürfen nach Veröffentlichung nicht für eine andere
    Bedeutung wiederverwendet werden.
-   `PS4-0103` -- reservierter, stabiler Fehlercode. UI zeigt eine kurze
    Ursache; Log enthält Operation-ID, Komponente und technische
    Details. Codes dürfen nach Veröffentlichung nicht für eine andere
    Bedeutung wiederverwendet werden.
-   `PS4-0104` -- reservierter, stabiler Fehlercode. UI zeigt eine kurze
    Ursache; Log enthält Operation-ID, Komponente und technische
    Details. Codes dürfen nach Veröffentlichung nicht für eine andere
    Bedeutung wiederverwendet werden.
-   `PS4-0105` -- reservierter, stabiler Fehlercode. UI zeigt eine kurze
    Ursache; Log enthält Operation-ID, Komponente und technische
    Details. Codes dürfen nach Veröffentlichung nicht für eine andere
    Bedeutung wiederverwendet werden.
-   `PS4-0106` -- reservierter, stabiler Fehlercode. UI zeigt eine kurze
    Ursache; Log enthält Operation-ID, Komponente und technische
    Details. Codes dürfen nach Veröffentlichung nicht für eine andere
    Bedeutung wiederverwendet werden.
-   `PS4-0107` -- reservierter, stabiler Fehlercode. UI zeigt eine kurze
    Ursache; Log enthält Operation-ID, Komponente und technische
    Details. Codes dürfen nach Veröffentlichung nicht für eine andere
    Bedeutung wiederverwendet werden.
-   `PS4-0108` -- reservierter, stabiler Fehlercode. UI zeigt eine kurze
    Ursache; Log enthält Operation-ID, Komponente und technische
    Details. Codes dürfen nach Veröffentlichung nicht für eine andere
    Bedeutung wiederverwendet werden.
-   `PS4-0109` -- reservierter, stabiler Fehlercode. UI zeigt eine kurze
    Ursache; Log enthält Operation-ID, Komponente und technische
    Details. Codes dürfen nach Veröffentlichung nicht für eine andere
    Bedeutung wiederverwendet werden.
-   `PS4-0110` -- reservierter, stabiler Fehlercode. UI zeigt eine kurze
    Ursache; Log enthält Operation-ID, Komponente und technische
    Details. Codes dürfen nach Veröffentlichung nicht für eine andere
    Bedeutung wiederverwendet werden.
-   `PS4-0111` -- reservierter, stabiler Fehlercode. UI zeigt eine kurze
    Ursache; Log enthält Operation-ID, Komponente und technische
    Details. Codes dürfen nach Veröffentlichung nicht für eine andere
    Bedeutung wiederverwendet werden.
-   `PS4-0112` -- reservierter, stabiler Fehlercode. UI zeigt eine kurze
    Ursache; Log enthält Operation-ID, Komponente und technische
    Details. Codes dürfen nach Veröffentlichung nicht für eine andere
    Bedeutung wiederverwendet werden.
-   `PS4-0113` -- reservierter, stabiler Fehlercode. UI zeigt eine kurze
    Ursache; Log enthält Operation-ID, Komponente und technische
    Details. Codes dürfen nach Veröffentlichung nicht für eine andere
    Bedeutung wiederverwendet werden.
-   `PS4-0114` -- reservierter, stabiler Fehlercode. UI zeigt eine kurze
    Ursache; Log enthält Operation-ID, Komponente und technische
    Details. Codes dürfen nach Veröffentlichung nicht für eine andere
    Bedeutung wiederverwendet werden.
-   `PS4-0115` -- reservierter, stabiler Fehlercode. UI zeigt eine kurze
    Ursache; Log enthält Operation-ID, Komponente und technische
    Details. Codes dürfen nach Veröffentlichung nicht für eine andere
    Bedeutung wiederverwendet werden.
-   `PS4-0116` -- reservierter, stabiler Fehlercode. UI zeigt eine kurze
    Ursache; Log enthält Operation-ID, Komponente und technische
    Details. Codes dürfen nach Veröffentlichung nicht für eine andere
    Bedeutung wiederverwendet werden.
-   `PS4-0117` -- reservierter, stabiler Fehlercode. UI zeigt eine kurze
    Ursache; Log enthält Operation-ID, Komponente und technische
    Details. Codes dürfen nach Veröffentlichung nicht für eine andere
    Bedeutung wiederverwendet werden.
-   `PS4-0118` -- reservierter, stabiler Fehlercode. UI zeigt eine kurze
    Ursache; Log enthält Operation-ID, Komponente und technische
    Details. Codes dürfen nach Veröffentlichung nicht für eine andere
    Bedeutung wiederverwendet werden.
-   `PS4-0119` -- reservierter, stabiler Fehlercode. UI zeigt eine kurze
    Ursache; Log enthält Operation-ID, Komponente und technische
    Details. Codes dürfen nach Veröffentlichung nicht für eine andere
    Bedeutung wiederverwendet werden.
-   `PS4-0120` -- reservierter, stabiler Fehlercode. UI zeigt eine kurze
    Ursache; Log enthält Operation-ID, Komponente und technische
    Details. Codes dürfen nach Veröffentlichung nicht für eine andere
    Bedeutung wiederverwendet werden.
-   `PS4-0121` -- reservierter, stabiler Fehlercode. UI zeigt eine kurze
    Ursache; Log enthält Operation-ID, Komponente und technische
    Details. Codes dürfen nach Veröffentlichung nicht für eine andere
    Bedeutung wiederverwendet werden.
-   `PS4-0122` -- reservierter, stabiler Fehlercode. UI zeigt eine kurze
    Ursache; Log enthält Operation-ID, Komponente und technische
    Details. Codes dürfen nach Veröffentlichung nicht für eine andere
    Bedeutung wiederverwendet werden.
-   `PS4-0123` -- reservierter, stabiler Fehlercode. UI zeigt eine kurze
    Ursache; Log enthält Operation-ID, Komponente und technische
    Details. Codes dürfen nach Veröffentlichung nicht für eine andere
    Bedeutung wiederverwendet werden.
-   `PS4-0124` -- reservierter, stabiler Fehlercode. UI zeigt eine kurze
    Ursache; Log enthält Operation-ID, Komponente und technische
    Details. Codes dürfen nach Veröffentlichung nicht für eine andere
    Bedeutung wiederverwendet werden.
-   `PS4-0125` -- reservierter, stabiler Fehlercode. UI zeigt eine kurze
    Ursache; Log enthält Operation-ID, Komponente und technische
    Details. Codes dürfen nach Veröffentlichung nicht für eine andere
    Bedeutung wiederverwendet werden.
-   `PS4-0126` -- reservierter, stabiler Fehlercode. UI zeigt eine kurze
    Ursache; Log enthält Operation-ID, Komponente und technische
    Details. Codes dürfen nach Veröffentlichung nicht für eine andere
    Bedeutung wiederverwendet werden.
-   `PS4-0127` -- reservierter, stabiler Fehlercode. UI zeigt eine kurze
    Ursache; Log enthält Operation-ID, Komponente und technische
    Details. Codes dürfen nach Veröffentlichung nicht für eine andere
    Bedeutung wiederverwendet werden.
-   `PS4-0128` -- reservierter, stabiler Fehlercode. UI zeigt eine kurze
    Ursache; Log enthält Operation-ID, Komponente und technische
    Details. Codes dürfen nach Veröffentlichung nicht für eine andere
    Bedeutung wiederverwendet werden.
-   `PS4-0129` -- reservierter, stabiler Fehlercode. UI zeigt eine kurze
    Ursache; Log enthält Operation-ID, Komponente und technische
    Details. Codes dürfen nach Veröffentlichung nicht für eine andere
    Bedeutung wiederverwendet werden.
-   `PS4-0130` -- reservierter, stabiler Fehlercode. UI zeigt eine kurze
    Ursache; Log enthält Operation-ID, Komponente und technische
    Details. Codes dürfen nach Veröffentlichung nicht für eine andere
    Bedeutung wiederverwendet werden.
-   `PS4-0131` -- reservierter, stabiler Fehlercode. UI zeigt eine kurze
    Ursache; Log enthält Operation-ID, Komponente und technische
    Details. Codes dürfen nach Veröffentlichung nicht für eine andere
    Bedeutung wiederverwendet werden.
-   `PS4-0132` -- reservierter, stabiler Fehlercode. UI zeigt eine kurze
    Ursache; Log enthält Operation-ID, Komponente und technische
    Details. Codes dürfen nach Veröffentlichung nicht für eine andere
    Bedeutung wiederverwendet werden.
-   `PS4-0133` -- reservierter, stabiler Fehlercode. UI zeigt eine kurze
    Ursache; Log enthält Operation-ID, Komponente und technische
    Details. Codes dürfen nach Veröffentlichung nicht für eine andere
    Bedeutung wiederverwendet werden.
-   `PS4-0134` -- reservierter, stabiler Fehlercode. UI zeigt eine kurze
    Ursache; Log enthält Operation-ID, Komponente und technische
    Details. Codes dürfen nach Veröffentlichung nicht für eine andere
    Bedeutung wiederverwendet werden.
-   `PS4-0135` -- reservierter, stabiler Fehlercode. UI zeigt eine kurze
    Ursache; Log enthält Operation-ID, Komponente und technische
    Details. Codes dürfen nach Veröffentlichung nicht für eine andere
    Bedeutung wiederverwendet werden.
-   `PS4-0136` -- reservierter, stabiler Fehlercode. UI zeigt eine kurze
    Ursache; Log enthält Operation-ID, Komponente und technische
    Details. Codes dürfen nach Veröffentlichung nicht für eine andere
    Bedeutung wiederverwendet werden.
-   `PS4-0137` -- reservierter, stabiler Fehlercode. UI zeigt eine kurze
    Ursache; Log enthält Operation-ID, Komponente und technische
    Details. Codes dürfen nach Veröffentlichung nicht für eine andere
    Bedeutung wiederverwendet werden.
-   `PS4-0138` -- reservierter, stabiler Fehlercode. UI zeigt eine kurze
    Ursache; Log enthält Operation-ID, Komponente und technische
    Details. Codes dürfen nach Veröffentlichung nicht für eine andere
    Bedeutung wiederverwendet werden.
-   `PS4-0139` -- reservierter, stabiler Fehlercode. UI zeigt eine kurze
    Ursache; Log enthält Operation-ID, Komponente und technische
    Details. Codes dürfen nach Veröffentlichung nicht für eine andere
    Bedeutung wiederverwendet werden.
-   `PS4-0140` -- reservierter, stabiler Fehlercode. UI zeigt eine kurze
    Ursache; Log enthält Operation-ID, Komponente und technische
    Details. Codes dürfen nach Veröffentlichung nicht für eine andere
    Bedeutung wiederverwendet werden.
-   `PS4-0141` -- reservierter, stabiler Fehlercode. UI zeigt eine kurze
    Ursache; Log enthält Operation-ID, Komponente und technische
    Details. Codes dürfen nach Veröffentlichung nicht für eine andere
    Bedeutung wiederverwendet werden.
-   `PS4-0142` -- reservierter, stabiler Fehlercode. UI zeigt eine kurze
    Ursache; Log enthält Operation-ID, Komponente und technische
    Details. Codes dürfen nach Veröffentlichung nicht für eine andere
    Bedeutung wiederverwendet werden.
-   `PS4-0143` -- reservierter, stabiler Fehlercode. UI zeigt eine kurze
    Ursache; Log enthält Operation-ID, Komponente und technische
    Details. Codes dürfen nach Veröffentlichung nicht für eine andere
    Bedeutung wiederverwendet werden.
-   `PS4-0144` -- reservierter, stabiler Fehlercode. UI zeigt eine kurze
    Ursache; Log enthält Operation-ID, Komponente und technische
    Details. Codes dürfen nach Veröffentlichung nicht für eine andere
    Bedeutung wiederverwendet werden.
-   `PS4-0145` -- reservierter, stabiler Fehlercode. UI zeigt eine kurze
    Ursache; Log enthält Operation-ID, Komponente und technische
    Details. Codes dürfen nach Veröffentlichung nicht für eine andere
    Bedeutung wiederverwendet werden.
-   `PS4-0146` -- reservierter, stabiler Fehlercode. UI zeigt eine kurze
    Ursache; Log enthält Operation-ID, Komponente und technische
    Details. Codes dürfen nach Veröffentlichung nicht für eine andere
    Bedeutung wiederverwendet werden.
-   `PS4-0147` -- reservierter, stabiler Fehlercode. UI zeigt eine kurze
    Ursache; Log enthält Operation-ID, Komponente und technische
    Details. Codes dürfen nach Veröffentlichung nicht für eine andere
    Bedeutung wiederverwendet werden.
-   `PS4-0148` -- reservierter, stabiler Fehlercode. UI zeigt eine kurze
    Ursache; Log enthält Operation-ID, Komponente und technische
    Details. Codes dürfen nach Veröffentlichung nicht für eine andere
    Bedeutung wiederverwendet werden.
-   `PS4-0149` -- reservierter, stabiler Fehlercode. UI zeigt eine kurze
    Ursache; Log enthält Operation-ID, Komponente und technische
    Details. Codes dürfen nach Veröffentlichung nicht für eine andere
    Bedeutung wiederverwendet werden.
-   `PS4-0150` -- reservierter, stabiler Fehlercode. UI zeigt eine kurze
    Ursache; Log enthält Operation-ID, Komponente und technische
    Details. Codes dürfen nach Veröffentlichung nicht für eine andere
    Bedeutung wiederverwendet werden.
-   `PS4-0151` -- reservierter, stabiler Fehlercode. UI zeigt eine kurze
    Ursache; Log enthält Operation-ID, Komponente und technische
    Details. Codes dürfen nach Veröffentlichung nicht für eine andere
    Bedeutung wiederverwendet werden.
-   `PS4-0152` -- reservierter, stabiler Fehlercode. UI zeigt eine kurze
    Ursache; Log enthält Operation-ID, Komponente und technische
    Details. Codes dürfen nach Veröffentlichung nicht für eine andere
    Bedeutung wiederverwendet werden.
-   `PS4-0153` -- reservierter, stabiler Fehlercode. UI zeigt eine kurze
    Ursache; Log enthält Operation-ID, Komponente und technische
    Details. Codes dürfen nach Veröffentlichung nicht für eine andere
    Bedeutung wiederverwendet werden.
-   `PS4-0154` -- reservierter, stabiler Fehlercode. UI zeigt eine kurze
    Ursache; Log enthält Operation-ID, Komponente und technische
    Details. Codes dürfen nach Veröffentlichung nicht für eine andere
    Bedeutung wiederverwendet werden.
-   `PS4-0155` -- reservierter, stabiler Fehlercode. UI zeigt eine kurze
    Ursache; Log enthält Operation-ID, Komponente und technische
    Details. Codes dürfen nach Veröffentlichung nicht für eine andere
    Bedeutung wiederverwendet werden.
-   `PS4-0156` -- reservierter, stabiler Fehlercode. UI zeigt eine kurze
    Ursache; Log enthält Operation-ID, Komponente und technische
    Details. Codes dürfen nach Veröffentlichung nicht für eine andere
    Bedeutung wiederverwendet werden.
-   `PS4-0157` -- reservierter, stabiler Fehlercode. UI zeigt eine kurze
    Ursache; Log enthält Operation-ID, Komponente und technische
    Details. Codes dürfen nach Veröffentlichung nicht für eine andere
    Bedeutung wiederverwendet werden.
-   `PS4-0158` -- reservierter, stabiler Fehlercode. UI zeigt eine kurze
    Ursache; Log enthält Operation-ID, Komponente und technische
    Details. Codes dürfen nach Veröffentlichung nicht für eine andere
    Bedeutung wiederverwendet werden.
-   `PS4-0159` -- reservierter, stabiler Fehlercode. UI zeigt eine kurze
    Ursache; Log enthält Operation-ID, Komponente und technische
    Details. Codes dürfen nach Veröffentlichung nicht für eine andere
    Bedeutung wiederverwendet werden.
-   `PS4-0160` -- reservierter, stabiler Fehlercode. UI zeigt eine kurze
    Ursache; Log enthält Operation-ID, Komponente und technische
    Details. Codes dürfen nach Veröffentlichung nicht für eine andere
    Bedeutung wiederverwendet werden.
-   `PS4-0161` -- reservierter, stabiler Fehlercode. UI zeigt eine kurze
    Ursache; Log enthält Operation-ID, Komponente und technische
    Details. Codes dürfen nach Veröffentlichung nicht für eine andere
    Bedeutung wiederverwendet werden.
-   `PS4-0162` -- reservierter, stabiler Fehlercode. UI zeigt eine kurze
    Ursache; Log enthält Operation-ID, Komponente und technische
    Details. Codes dürfen nach Veröffentlichung nicht für eine andere
    Bedeutung wiederverwendet werden.
-   `PS4-0163` -- reservierter, stabiler Fehlercode. UI zeigt eine kurze
    Ursache; Log enthält Operation-ID, Komponente und technische
    Details. Codes dürfen nach Veröffentlichung nicht für eine andere
    Bedeutung wiederverwendet werden.
-   `PS4-0164` -- reservierter, stabiler Fehlercode. UI zeigt eine kurze
    Ursache; Log enthält Operation-ID, Komponente und technische
    Details. Codes dürfen nach Veröffentlichung nicht für eine andere
    Bedeutung wiederverwendet werden.
-   `PS4-0165` -- reservierter, stabiler Fehlercode. UI zeigt eine kurze
    Ursache; Log enthält Operation-ID, Komponente und technische
    Details. Codes dürfen nach Veröffentlichung nicht für eine andere
    Bedeutung wiederverwendet werden.
-   `PS4-0166` -- reservierter, stabiler Fehlercode. UI zeigt eine kurze
    Ursache; Log enthält Operation-ID, Komponente und technische
    Details. Codes dürfen nach Veröffentlichung nicht für eine andere
    Bedeutung wiederverwendet werden.
-   `PS4-0167` -- reservierter, stabiler Fehlercode. UI zeigt eine kurze
    Ursache; Log enthält Operation-ID, Komponente und technische
    Details. Codes dürfen nach Veröffentlichung nicht für eine andere
    Bedeutung wiederverwendet werden.
-   `PS4-0168` -- reservierter, stabiler Fehlercode. UI zeigt eine kurze
    Ursache; Log enthält Operation-ID, Komponente und technische
    Details. Codes dürfen nach Veröffentlichung nicht für eine andere
    Bedeutung wiederverwendet werden.
-   `PS4-0169` -- reservierter, stabiler Fehlercode. UI zeigt eine kurze
    Ursache; Log enthält Operation-ID, Komponente und technische
    Details. Codes dürfen nach Veröffentlichung nicht für eine andere
    Bedeutung wiederverwendet werden.
-   `PS4-0170` -- reservierter, stabiler Fehlercode. UI zeigt eine kurze
    Ursache; Log enthält Operation-ID, Komponente und technische
    Details. Codes dürfen nach Veröffentlichung nicht für eine andere
    Bedeutung wiederverwendet werden.
-   `PS4-0171` -- reservierter, stabiler Fehlercode. UI zeigt eine kurze
    Ursache; Log enthält Operation-ID, Komponente und technische
    Details. Codes dürfen nach Veröffentlichung nicht für eine andere
    Bedeutung wiederverwendet werden.
-   `PS4-0172` -- reservierter, stabiler Fehlercode. UI zeigt eine kurze
    Ursache; Log enthält Operation-ID, Komponente und technische
    Details. Codes dürfen nach Veröffentlichung nicht für eine andere
    Bedeutung wiederverwendet werden.
-   `PS4-0173` -- reservierter, stabiler Fehlercode. UI zeigt eine kurze
    Ursache; Log enthält Operation-ID, Komponente und technische
    Details. Codes dürfen nach Veröffentlichung nicht für eine andere
    Bedeutung wiederverwendet werden.
-   `PS4-0174` -- reservierter, stabiler Fehlercode. UI zeigt eine kurze
    Ursache; Log enthält Operation-ID, Komponente und technische
    Details. Codes dürfen nach Veröffentlichung nicht für eine andere
    Bedeutung wiederverwendet werden.
-   `PS4-0175` -- reservierter, stabiler Fehlercode. UI zeigt eine kurze
    Ursache; Log enthält Operation-ID, Komponente und technische
    Details. Codes dürfen nach Veröffentlichung nicht für eine andere
    Bedeutung wiederverwendet werden.
-   `PS4-0176` -- reservierter, stabiler Fehlercode. UI zeigt eine kurze
    Ursache; Log enthält Operation-ID, Komponente und technische
    Details. Codes dürfen nach Veröffentlichung nicht für eine andere
    Bedeutung wiederverwendet werden.
-   `PS4-0177` -- reservierter, stabiler Fehlercode. UI zeigt eine kurze
    Ursache; Log enthält Operation-ID, Komponente und technische
    Details. Codes dürfen nach Veröffentlichung nicht für eine andere
    Bedeutung wiederverwendet werden.
-   `PS4-0178` -- reservierter, stabiler Fehlercode. UI zeigt eine kurze
    Ursache; Log enthält Operation-ID, Komponente und technische
    Details. Codes dürfen nach Veröffentlichung nicht für eine andere
    Bedeutung wiederverwendet werden.
-   `PS4-0179` -- reservierter, stabiler Fehlercode. UI zeigt eine kurze
    Ursache; Log enthält Operation-ID, Komponente und technische
    Details. Codes dürfen nach Veröffentlichung nicht für eine andere
    Bedeutung wiederverwendet werden.

::: {style="page-break-before: always;"}
:::

# 79. Ereignis- und Audit-Katalog

-   `EVENT_001` -- Ereignis für Zustandswechsel 1; mindestens Timestamp,
    Console-ID (falls vorhanden), Component, Result und Correlation-ID
    protokollieren. Keine Tokens oder Passwörter.
-   `EVENT_002` -- Ereignis für Zustandswechsel 2; mindestens Timestamp,
    Console-ID (falls vorhanden), Component, Result und Correlation-ID
    protokollieren. Keine Tokens oder Passwörter.
-   `EVENT_003` -- Ereignis für Zustandswechsel 3; mindestens Timestamp,
    Console-ID (falls vorhanden), Component, Result und Correlation-ID
    protokollieren. Keine Tokens oder Passwörter.
-   `EVENT_004` -- Ereignis für Zustandswechsel 4; mindestens Timestamp,
    Console-ID (falls vorhanden), Component, Result und Correlation-ID
    protokollieren. Keine Tokens oder Passwörter.
-   `EVENT_005` -- Ereignis für Zustandswechsel 5; mindestens Timestamp,
    Console-ID (falls vorhanden), Component, Result und Correlation-ID
    protokollieren. Keine Tokens oder Passwörter.
-   `EVENT_006` -- Ereignis für Zustandswechsel 6; mindestens Timestamp,
    Console-ID (falls vorhanden), Component, Result und Correlation-ID
    protokollieren. Keine Tokens oder Passwörter.
-   `EVENT_007` -- Ereignis für Zustandswechsel 7; mindestens Timestamp,
    Console-ID (falls vorhanden), Component, Result und Correlation-ID
    protokollieren. Keine Tokens oder Passwörter.
-   `EVENT_008` -- Ereignis für Zustandswechsel 8; mindestens Timestamp,
    Console-ID (falls vorhanden), Component, Result und Correlation-ID
    protokollieren. Keine Tokens oder Passwörter.
-   `EVENT_009` -- Ereignis für Zustandswechsel 9; mindestens Timestamp,
    Console-ID (falls vorhanden), Component, Result und Correlation-ID
    protokollieren. Keine Tokens oder Passwörter.
-   `EVENT_010` -- Ereignis für Zustandswechsel 10; mindestens
    Timestamp, Console-ID (falls vorhanden), Component, Result und
    Correlation-ID protokollieren. Keine Tokens oder Passwörter.
-   `EVENT_011` -- Ereignis für Zustandswechsel 11; mindestens
    Timestamp, Console-ID (falls vorhanden), Component, Result und
    Correlation-ID protokollieren. Keine Tokens oder Passwörter.
-   `EVENT_012` -- Ereignis für Zustandswechsel 12; mindestens
    Timestamp, Console-ID (falls vorhanden), Component, Result und
    Correlation-ID protokollieren. Keine Tokens oder Passwörter.
-   `EVENT_013` -- Ereignis für Zustandswechsel 13; mindestens
    Timestamp, Console-ID (falls vorhanden), Component, Result und
    Correlation-ID protokollieren. Keine Tokens oder Passwörter.
-   `EVENT_014` -- Ereignis für Zustandswechsel 14; mindestens
    Timestamp, Console-ID (falls vorhanden), Component, Result und
    Correlation-ID protokollieren. Keine Tokens oder Passwörter.
-   `EVENT_015` -- Ereignis für Zustandswechsel 15; mindestens
    Timestamp, Console-ID (falls vorhanden), Component, Result und
    Correlation-ID protokollieren. Keine Tokens oder Passwörter.
-   `EVENT_016` -- Ereignis für Zustandswechsel 16; mindestens
    Timestamp, Console-ID (falls vorhanden), Component, Result und
    Correlation-ID protokollieren. Keine Tokens oder Passwörter.
-   `EVENT_017` -- Ereignis für Zustandswechsel 17; mindestens
    Timestamp, Console-ID (falls vorhanden), Component, Result und
    Correlation-ID protokollieren. Keine Tokens oder Passwörter.
-   `EVENT_018` -- Ereignis für Zustandswechsel 18; mindestens
    Timestamp, Console-ID (falls vorhanden), Component, Result und
    Correlation-ID protokollieren. Keine Tokens oder Passwörter.
-   `EVENT_019` -- Ereignis für Zustandswechsel 19; mindestens
    Timestamp, Console-ID (falls vorhanden), Component, Result und
    Correlation-ID protokollieren. Keine Tokens oder Passwörter.
-   `EVENT_020` -- Ereignis für Zustandswechsel 20; mindestens
    Timestamp, Console-ID (falls vorhanden), Component, Result und
    Correlation-ID protokollieren. Keine Tokens oder Passwörter.
-   `EVENT_021` -- Ereignis für Zustandswechsel 21; mindestens
    Timestamp, Console-ID (falls vorhanden), Component, Result und
    Correlation-ID protokollieren. Keine Tokens oder Passwörter.
-   `EVENT_022` -- Ereignis für Zustandswechsel 22; mindestens
    Timestamp, Console-ID (falls vorhanden), Component, Result und
    Correlation-ID protokollieren. Keine Tokens oder Passwörter.
-   `EVENT_023` -- Ereignis für Zustandswechsel 23; mindestens
    Timestamp, Console-ID (falls vorhanden), Component, Result und
    Correlation-ID protokollieren. Keine Tokens oder Passwörter.
-   `EVENT_024` -- Ereignis für Zustandswechsel 24; mindestens
    Timestamp, Console-ID (falls vorhanden), Component, Result und
    Correlation-ID protokollieren. Keine Tokens oder Passwörter.
-   `EVENT_025` -- Ereignis für Zustandswechsel 25; mindestens
    Timestamp, Console-ID (falls vorhanden), Component, Result und
    Correlation-ID protokollieren. Keine Tokens oder Passwörter.
-   `EVENT_026` -- Ereignis für Zustandswechsel 26; mindestens
    Timestamp, Console-ID (falls vorhanden), Component, Result und
    Correlation-ID protokollieren. Keine Tokens oder Passwörter.
-   `EVENT_027` -- Ereignis für Zustandswechsel 27; mindestens
    Timestamp, Console-ID (falls vorhanden), Component, Result und
    Correlation-ID protokollieren. Keine Tokens oder Passwörter.
-   `EVENT_028` -- Ereignis für Zustandswechsel 28; mindestens
    Timestamp, Console-ID (falls vorhanden), Component, Result und
    Correlation-ID protokollieren. Keine Tokens oder Passwörter.
-   `EVENT_029` -- Ereignis für Zustandswechsel 29; mindestens
    Timestamp, Console-ID (falls vorhanden), Component, Result und
    Correlation-ID protokollieren. Keine Tokens oder Passwörter.
-   `EVENT_030` -- Ereignis für Zustandswechsel 30; mindestens
    Timestamp, Console-ID (falls vorhanden), Component, Result und
    Correlation-ID protokollieren. Keine Tokens oder Passwörter.
-   `EVENT_031` -- Ereignis für Zustandswechsel 31; mindestens
    Timestamp, Console-ID (falls vorhanden), Component, Result und
    Correlation-ID protokollieren. Keine Tokens oder Passwörter.
-   `EVENT_032` -- Ereignis für Zustandswechsel 32; mindestens
    Timestamp, Console-ID (falls vorhanden), Component, Result und
    Correlation-ID protokollieren. Keine Tokens oder Passwörter.
-   `EVENT_033` -- Ereignis für Zustandswechsel 33; mindestens
    Timestamp, Console-ID (falls vorhanden), Component, Result und
    Correlation-ID protokollieren. Keine Tokens oder Passwörter.
-   `EVENT_034` -- Ereignis für Zustandswechsel 34; mindestens
    Timestamp, Console-ID (falls vorhanden), Component, Result und
    Correlation-ID protokollieren. Keine Tokens oder Passwörter.
-   `EVENT_035` -- Ereignis für Zustandswechsel 35; mindestens
    Timestamp, Console-ID (falls vorhanden), Component, Result und
    Correlation-ID protokollieren. Keine Tokens oder Passwörter.
-   `EVENT_036` -- Ereignis für Zustandswechsel 36; mindestens
    Timestamp, Console-ID (falls vorhanden), Component, Result und
    Correlation-ID protokollieren. Keine Tokens oder Passwörter.
-   `EVENT_037` -- Ereignis für Zustandswechsel 37; mindestens
    Timestamp, Console-ID (falls vorhanden), Component, Result und
    Correlation-ID protokollieren. Keine Tokens oder Passwörter.
-   `EVENT_038` -- Ereignis für Zustandswechsel 38; mindestens
    Timestamp, Console-ID (falls vorhanden), Component, Result und
    Correlation-ID protokollieren. Keine Tokens oder Passwörter.
-   `EVENT_039` -- Ereignis für Zustandswechsel 39; mindestens
    Timestamp, Console-ID (falls vorhanden), Component, Result und
    Correlation-ID protokollieren. Keine Tokens oder Passwörter.
-   `EVENT_040` -- Ereignis für Zustandswechsel 40; mindestens
    Timestamp, Console-ID (falls vorhanden), Component, Result und
    Correlation-ID protokollieren. Keine Tokens oder Passwörter.
-   `EVENT_041` -- Ereignis für Zustandswechsel 41; mindestens
    Timestamp, Console-ID (falls vorhanden), Component, Result und
    Correlation-ID protokollieren. Keine Tokens oder Passwörter.
-   `EVENT_042` -- Ereignis für Zustandswechsel 42; mindestens
    Timestamp, Console-ID (falls vorhanden), Component, Result und
    Correlation-ID protokollieren. Keine Tokens oder Passwörter.
-   `EVENT_043` -- Ereignis für Zustandswechsel 43; mindestens
    Timestamp, Console-ID (falls vorhanden), Component, Result und
    Correlation-ID protokollieren. Keine Tokens oder Passwörter.
-   `EVENT_044` -- Ereignis für Zustandswechsel 44; mindestens
    Timestamp, Console-ID (falls vorhanden), Component, Result und
    Correlation-ID protokollieren. Keine Tokens oder Passwörter.
-   `EVENT_045` -- Ereignis für Zustandswechsel 45; mindestens
    Timestamp, Console-ID (falls vorhanden), Component, Result und
    Correlation-ID protokollieren. Keine Tokens oder Passwörter.
-   `EVENT_046` -- Ereignis für Zustandswechsel 46; mindestens
    Timestamp, Console-ID (falls vorhanden), Component, Result und
    Correlation-ID protokollieren. Keine Tokens oder Passwörter.
-   `EVENT_047` -- Ereignis für Zustandswechsel 47; mindestens
    Timestamp, Console-ID (falls vorhanden), Component, Result und
    Correlation-ID protokollieren. Keine Tokens oder Passwörter.
-   `EVENT_048` -- Ereignis für Zustandswechsel 48; mindestens
    Timestamp, Console-ID (falls vorhanden), Component, Result und
    Correlation-ID protokollieren. Keine Tokens oder Passwörter.
-   `EVENT_049` -- Ereignis für Zustandswechsel 49; mindestens
    Timestamp, Console-ID (falls vorhanden), Component, Result und
    Correlation-ID protokollieren. Keine Tokens oder Passwörter.
-   `EVENT_050` -- Ereignis für Zustandswechsel 50; mindestens
    Timestamp, Console-ID (falls vorhanden), Component, Result und
    Correlation-ID protokollieren. Keine Tokens oder Passwörter.
-   `EVENT_051` -- Ereignis für Zustandswechsel 51; mindestens
    Timestamp, Console-ID (falls vorhanden), Component, Result und
    Correlation-ID protokollieren. Keine Tokens oder Passwörter.
-   `EVENT_052` -- Ereignis für Zustandswechsel 52; mindestens
    Timestamp, Console-ID (falls vorhanden), Component, Result und
    Correlation-ID protokollieren. Keine Tokens oder Passwörter.
-   `EVENT_053` -- Ereignis für Zustandswechsel 53; mindestens
    Timestamp, Console-ID (falls vorhanden), Component, Result und
    Correlation-ID protokollieren. Keine Tokens oder Passwörter.
-   `EVENT_054` -- Ereignis für Zustandswechsel 54; mindestens
    Timestamp, Console-ID (falls vorhanden), Component, Result und
    Correlation-ID protokollieren. Keine Tokens oder Passwörter.
-   `EVENT_055` -- Ereignis für Zustandswechsel 55; mindestens
    Timestamp, Console-ID (falls vorhanden), Component, Result und
    Correlation-ID protokollieren. Keine Tokens oder Passwörter.
-   `EVENT_056` -- Ereignis für Zustandswechsel 56; mindestens
    Timestamp, Console-ID (falls vorhanden), Component, Result und
    Correlation-ID protokollieren. Keine Tokens oder Passwörter.
-   `EVENT_057` -- Ereignis für Zustandswechsel 57; mindestens
    Timestamp, Console-ID (falls vorhanden), Component, Result und
    Correlation-ID protokollieren. Keine Tokens oder Passwörter.
-   `EVENT_058` -- Ereignis für Zustandswechsel 58; mindestens
    Timestamp, Console-ID (falls vorhanden), Component, Result und
    Correlation-ID protokollieren. Keine Tokens oder Passwörter.
-   `EVENT_059` -- Ereignis für Zustandswechsel 59; mindestens
    Timestamp, Console-ID (falls vorhanden), Component, Result und
    Correlation-ID protokollieren. Keine Tokens oder Passwörter.
-   `EVENT_060` -- Ereignis für Zustandswechsel 60; mindestens
    Timestamp, Console-ID (falls vorhanden), Component, Result und
    Correlation-ID protokollieren. Keine Tokens oder Passwörter.
-   `EVENT_061` -- Ereignis für Zustandswechsel 61; mindestens
    Timestamp, Console-ID (falls vorhanden), Component, Result und
    Correlation-ID protokollieren. Keine Tokens oder Passwörter.
-   `EVENT_062` -- Ereignis für Zustandswechsel 62; mindestens
    Timestamp, Console-ID (falls vorhanden), Component, Result und
    Correlation-ID protokollieren. Keine Tokens oder Passwörter.
-   `EVENT_063` -- Ereignis für Zustandswechsel 63; mindestens
    Timestamp, Console-ID (falls vorhanden), Component, Result und
    Correlation-ID protokollieren. Keine Tokens oder Passwörter.
-   `EVENT_064` -- Ereignis für Zustandswechsel 64; mindestens
    Timestamp, Console-ID (falls vorhanden), Component, Result und
    Correlation-ID protokollieren. Keine Tokens oder Passwörter.
-   `EVENT_065` -- Ereignis für Zustandswechsel 65; mindestens
    Timestamp, Console-ID (falls vorhanden), Component, Result und
    Correlation-ID protokollieren. Keine Tokens oder Passwörter.
-   `EVENT_066` -- Ereignis für Zustandswechsel 66; mindestens
    Timestamp, Console-ID (falls vorhanden), Component, Result und
    Correlation-ID protokollieren. Keine Tokens oder Passwörter.
-   `EVENT_067` -- Ereignis für Zustandswechsel 67; mindestens
    Timestamp, Console-ID (falls vorhanden), Component, Result und
    Correlation-ID protokollieren. Keine Tokens oder Passwörter.
-   `EVENT_068` -- Ereignis für Zustandswechsel 68; mindestens
    Timestamp, Console-ID (falls vorhanden), Component, Result und
    Correlation-ID protokollieren. Keine Tokens oder Passwörter.
-   `EVENT_069` -- Ereignis für Zustandswechsel 69; mindestens
    Timestamp, Console-ID (falls vorhanden), Component, Result und
    Correlation-ID protokollieren. Keine Tokens oder Passwörter.
-   `EVENT_070` -- Ereignis für Zustandswechsel 70; mindestens
    Timestamp, Console-ID (falls vorhanden), Component, Result und
    Correlation-ID protokollieren. Keine Tokens oder Passwörter.
-   `EVENT_071` -- Ereignis für Zustandswechsel 71; mindestens
    Timestamp, Console-ID (falls vorhanden), Component, Result und
    Correlation-ID protokollieren. Keine Tokens oder Passwörter.
-   `EVENT_072` -- Ereignis für Zustandswechsel 72; mindestens
    Timestamp, Console-ID (falls vorhanden), Component, Result und
    Correlation-ID protokollieren. Keine Tokens oder Passwörter.
-   `EVENT_073` -- Ereignis für Zustandswechsel 73; mindestens
    Timestamp, Console-ID (falls vorhanden), Component, Result und
    Correlation-ID protokollieren. Keine Tokens oder Passwörter.
-   `EVENT_074` -- Ereignis für Zustandswechsel 74; mindestens
    Timestamp, Console-ID (falls vorhanden), Component, Result und
    Correlation-ID protokollieren. Keine Tokens oder Passwörter.
-   `EVENT_075` -- Ereignis für Zustandswechsel 75; mindestens
    Timestamp, Console-ID (falls vorhanden), Component, Result und
    Correlation-ID protokollieren. Keine Tokens oder Passwörter.
-   `EVENT_076` -- Ereignis für Zustandswechsel 76; mindestens
    Timestamp, Console-ID (falls vorhanden), Component, Result und
    Correlation-ID protokollieren. Keine Tokens oder Passwörter.
-   `EVENT_077` -- Ereignis für Zustandswechsel 77; mindestens
    Timestamp, Console-ID (falls vorhanden), Component, Result und
    Correlation-ID protokollieren. Keine Tokens oder Passwörter.
-   `EVENT_078` -- Ereignis für Zustandswechsel 78; mindestens
    Timestamp, Console-ID (falls vorhanden), Component, Result und
    Correlation-ID protokollieren. Keine Tokens oder Passwörter.
-   `EVENT_079` -- Ereignis für Zustandswechsel 79; mindestens
    Timestamp, Console-ID (falls vorhanden), Component, Result und
    Correlation-ID protokollieren. Keine Tokens oder Passwörter.
-   `EVENT_080` -- Ereignis für Zustandswechsel 80; mindestens
    Timestamp, Console-ID (falls vorhanden), Component, Result und
    Correlation-ID protokollieren. Keine Tokens oder Passwörter.

::: {style="page-break-before: always;"}
:::

# 80. UI-Akzeptanzfälle

### UI-001

**Given** ein definierter Modulzustand. **When** der Nutzer Aktion 1
ausführt. **Then** bleibt die Oberfläche responsiv, zeigt Fortschritt
oder unmittelbares Ergebnis, bietet bei Fehlern Details und verändert
ohne Bestätigung keine schreibgeschützten bzw. riskanten Ziele.
Tastaturfokus und Zurück-Navigation funktionieren. \### UI-002 **Given**
ein definierter Modulzustand. **When** der Nutzer Aktion 2 ausführt.
**Then** bleibt die Oberfläche responsiv, zeigt Fortschritt oder
unmittelbares Ergebnis, bietet bei Fehlern Details und verändert ohne
Bestätigung keine schreibgeschützten bzw. riskanten Ziele. Tastaturfokus
und Zurück-Navigation funktionieren. \### UI-003 **Given** ein
definierter Modulzustand. **When** der Nutzer Aktion 3 ausführt.
**Then** bleibt die Oberfläche responsiv, zeigt Fortschritt oder
unmittelbares Ergebnis, bietet bei Fehlern Details und verändert ohne
Bestätigung keine schreibgeschützten bzw. riskanten Ziele. Tastaturfokus
und Zurück-Navigation funktionieren. \### UI-004 **Given** ein
definierter Modulzustand. **When** der Nutzer Aktion 4 ausführt.
**Then** bleibt die Oberfläche responsiv, zeigt Fortschritt oder
unmittelbares Ergebnis, bietet bei Fehlern Details und verändert ohne
Bestätigung keine schreibgeschützten bzw. riskanten Ziele. Tastaturfokus
und Zurück-Navigation funktionieren. \### UI-005 **Given** ein
definierter Modulzustand. **When** der Nutzer Aktion 5 ausführt.
**Then** bleibt die Oberfläche responsiv, zeigt Fortschritt oder
unmittelbares Ergebnis, bietet bei Fehlern Details und verändert ohne
Bestätigung keine schreibgeschützten bzw. riskanten Ziele. Tastaturfokus
und Zurück-Navigation funktionieren. \### UI-006 **Given** ein
definierter Modulzustand. **When** der Nutzer Aktion 6 ausführt.
**Then** bleibt die Oberfläche responsiv, zeigt Fortschritt oder
unmittelbares Ergebnis, bietet bei Fehlern Details und verändert ohne
Bestätigung keine schreibgeschützten bzw. riskanten Ziele. Tastaturfokus
und Zurück-Navigation funktionieren. \### UI-007 **Given** ein
definierter Modulzustand. **When** der Nutzer Aktion 7 ausführt.
**Then** bleibt die Oberfläche responsiv, zeigt Fortschritt oder
unmittelbares Ergebnis, bietet bei Fehlern Details und verändert ohne
Bestätigung keine schreibgeschützten bzw. riskanten Ziele. Tastaturfokus
und Zurück-Navigation funktionieren. \### UI-008 **Given** ein
definierter Modulzustand. **When** der Nutzer Aktion 8 ausführt.
**Then** bleibt die Oberfläche responsiv, zeigt Fortschritt oder
unmittelbares Ergebnis, bietet bei Fehlern Details und verändert ohne
Bestätigung keine schreibgeschützten bzw. riskanten Ziele. Tastaturfokus
und Zurück-Navigation funktionieren. \### UI-009 **Given** ein
definierter Modulzustand. **When** der Nutzer Aktion 9 ausführt.
**Then** bleibt die Oberfläche responsiv, zeigt Fortschritt oder
unmittelbares Ergebnis, bietet bei Fehlern Details und verändert ohne
Bestätigung keine schreibgeschützten bzw. riskanten Ziele. Tastaturfokus
und Zurück-Navigation funktionieren. \### UI-010 **Given** ein
definierter Modulzustand. **When** der Nutzer Aktion 10 ausführt.
**Then** bleibt die Oberfläche responsiv, zeigt Fortschritt oder
unmittelbares Ergebnis, bietet bei Fehlern Details und verändert ohne
Bestätigung keine schreibgeschützten bzw. riskanten Ziele. Tastaturfokus
und Zurück-Navigation funktionieren. \### UI-011 **Given** ein
definierter Modulzustand. **When** der Nutzer Aktion 11 ausführt.
**Then** bleibt die Oberfläche responsiv, zeigt Fortschritt oder
unmittelbares Ergebnis, bietet bei Fehlern Details und verändert ohne
Bestätigung keine schreibgeschützten bzw. riskanten Ziele. Tastaturfokus
und Zurück-Navigation funktionieren. \### UI-012 **Given** ein
definierter Modulzustand. **When** der Nutzer Aktion 12 ausführt.
**Then** bleibt die Oberfläche responsiv, zeigt Fortschritt oder
unmittelbares Ergebnis, bietet bei Fehlern Details und verändert ohne
Bestätigung keine schreibgeschützten bzw. riskanten Ziele. Tastaturfokus
und Zurück-Navigation funktionieren. \### UI-013 **Given** ein
definierter Modulzustand. **When** der Nutzer Aktion 13 ausführt.
**Then** bleibt die Oberfläche responsiv, zeigt Fortschritt oder
unmittelbares Ergebnis, bietet bei Fehlern Details und verändert ohne
Bestätigung keine schreibgeschützten bzw. riskanten Ziele. Tastaturfokus
und Zurück-Navigation funktionieren. \### UI-014 **Given** ein
definierter Modulzustand. **When** der Nutzer Aktion 14 ausführt.
**Then** bleibt die Oberfläche responsiv, zeigt Fortschritt oder
unmittelbares Ergebnis, bietet bei Fehlern Details und verändert ohne
Bestätigung keine schreibgeschützten bzw. riskanten Ziele. Tastaturfokus
und Zurück-Navigation funktionieren. \### UI-015 **Given** ein
definierter Modulzustand. **When** der Nutzer Aktion 15 ausführt.
**Then** bleibt die Oberfläche responsiv, zeigt Fortschritt oder
unmittelbares Ergebnis, bietet bei Fehlern Details und verändert ohne
Bestätigung keine schreibgeschützten bzw. riskanten Ziele. Tastaturfokus
und Zurück-Navigation funktionieren. \### UI-016 **Given** ein
definierter Modulzustand. **When** der Nutzer Aktion 16 ausführt.
**Then** bleibt die Oberfläche responsiv, zeigt Fortschritt oder
unmittelbares Ergebnis, bietet bei Fehlern Details und verändert ohne
Bestätigung keine schreibgeschützten bzw. riskanten Ziele. Tastaturfokus
und Zurück-Navigation funktionieren. \### UI-017 **Given** ein
definierter Modulzustand. **When** der Nutzer Aktion 17 ausführt.
**Then** bleibt die Oberfläche responsiv, zeigt Fortschritt oder
unmittelbares Ergebnis, bietet bei Fehlern Details und verändert ohne
Bestätigung keine schreibgeschützten bzw. riskanten Ziele. Tastaturfokus
und Zurück-Navigation funktionieren. \### UI-018 **Given** ein
definierter Modulzustand. **When** der Nutzer Aktion 18 ausführt.
**Then** bleibt die Oberfläche responsiv, zeigt Fortschritt oder
unmittelbares Ergebnis, bietet bei Fehlern Details und verändert ohne
Bestätigung keine schreibgeschützten bzw. riskanten Ziele. Tastaturfokus
und Zurück-Navigation funktionieren. \### UI-019 **Given** ein
definierter Modulzustand. **When** der Nutzer Aktion 19 ausführt.
**Then** bleibt die Oberfläche responsiv, zeigt Fortschritt oder
unmittelbares Ergebnis, bietet bei Fehlern Details und verändert ohne
Bestätigung keine schreibgeschützten bzw. riskanten Ziele. Tastaturfokus
und Zurück-Navigation funktionieren. \### UI-020 **Given** ein
definierter Modulzustand. **When** der Nutzer Aktion 20 ausführt.
**Then** bleibt die Oberfläche responsiv, zeigt Fortschritt oder
unmittelbares Ergebnis, bietet bei Fehlern Details und verändert ohne
Bestätigung keine schreibgeschützten bzw. riskanten Ziele. Tastaturfokus
und Zurück-Navigation funktionieren. \### UI-021 **Given** ein
definierter Modulzustand. **When** der Nutzer Aktion 21 ausführt.
**Then** bleibt die Oberfläche responsiv, zeigt Fortschritt oder
unmittelbares Ergebnis, bietet bei Fehlern Details und verändert ohne
Bestätigung keine schreibgeschützten bzw. riskanten Ziele. Tastaturfokus
und Zurück-Navigation funktionieren. \### UI-022 **Given** ein
definierter Modulzustand. **When** der Nutzer Aktion 22 ausführt.
**Then** bleibt die Oberfläche responsiv, zeigt Fortschritt oder
unmittelbares Ergebnis, bietet bei Fehlern Details und verändert ohne
Bestätigung keine schreibgeschützten bzw. riskanten Ziele. Tastaturfokus
und Zurück-Navigation funktionieren. \### UI-023 **Given** ein
definierter Modulzustand. **When** der Nutzer Aktion 23 ausführt.
**Then** bleibt die Oberfläche responsiv, zeigt Fortschritt oder
unmittelbares Ergebnis, bietet bei Fehlern Details und verändert ohne
Bestätigung keine schreibgeschützten bzw. riskanten Ziele. Tastaturfokus
und Zurück-Navigation funktionieren. \### UI-024 **Given** ein
definierter Modulzustand. **When** der Nutzer Aktion 24 ausführt.
**Then** bleibt die Oberfläche responsiv, zeigt Fortschritt oder
unmittelbares Ergebnis, bietet bei Fehlern Details und verändert ohne
Bestätigung keine schreibgeschützten bzw. riskanten Ziele. Tastaturfokus
und Zurück-Navigation funktionieren. \### UI-025 **Given** ein
definierter Modulzustand. **When** der Nutzer Aktion 25 ausführt.
**Then** bleibt die Oberfläche responsiv, zeigt Fortschritt oder
unmittelbares Ergebnis, bietet bei Fehlern Details und verändert ohne
Bestätigung keine schreibgeschützten bzw. riskanten Ziele. Tastaturfokus
und Zurück-Navigation funktionieren. \### UI-026 **Given** ein
definierter Modulzustand. **When** der Nutzer Aktion 26 ausführt.
**Then** bleibt die Oberfläche responsiv, zeigt Fortschritt oder
unmittelbares Ergebnis, bietet bei Fehlern Details und verändert ohne
Bestätigung keine schreibgeschützten bzw. riskanten Ziele. Tastaturfokus
und Zurück-Navigation funktionieren. \### UI-027 **Given** ein
definierter Modulzustand. **When** der Nutzer Aktion 27 ausführt.
**Then** bleibt die Oberfläche responsiv, zeigt Fortschritt oder
unmittelbares Ergebnis, bietet bei Fehlern Details und verändert ohne
Bestätigung keine schreibgeschützten bzw. riskanten Ziele. Tastaturfokus
und Zurück-Navigation funktionieren. \### UI-028 **Given** ein
definierter Modulzustand. **When** der Nutzer Aktion 28 ausführt.
**Then** bleibt die Oberfläche responsiv, zeigt Fortschritt oder
unmittelbares Ergebnis, bietet bei Fehlern Details und verändert ohne
Bestätigung keine schreibgeschützten bzw. riskanten Ziele. Tastaturfokus
und Zurück-Navigation funktionieren. \### UI-029 **Given** ein
definierter Modulzustand. **When** der Nutzer Aktion 29 ausführt.
**Then** bleibt die Oberfläche responsiv, zeigt Fortschritt oder
unmittelbares Ergebnis, bietet bei Fehlern Details und verändert ohne
Bestätigung keine schreibgeschützten bzw. riskanten Ziele. Tastaturfokus
und Zurück-Navigation funktionieren. \### UI-030 **Given** ein
definierter Modulzustand. **When** der Nutzer Aktion 30 ausführt.
**Then** bleibt die Oberfläche responsiv, zeigt Fortschritt oder
unmittelbares Ergebnis, bietet bei Fehlern Details und verändert ohne
Bestätigung keine schreibgeschützten bzw. riskanten Ziele. Tastaturfokus
und Zurück-Navigation funktionieren. \### UI-031 **Given** ein
definierter Modulzustand. **When** der Nutzer Aktion 31 ausführt.
**Then** bleibt die Oberfläche responsiv, zeigt Fortschritt oder
unmittelbares Ergebnis, bietet bei Fehlern Details und verändert ohne
Bestätigung keine schreibgeschützten bzw. riskanten Ziele. Tastaturfokus
und Zurück-Navigation funktionieren. \### UI-032 **Given** ein
definierter Modulzustand. **When** der Nutzer Aktion 32 ausführt.
**Then** bleibt die Oberfläche responsiv, zeigt Fortschritt oder
unmittelbares Ergebnis, bietet bei Fehlern Details und verändert ohne
Bestätigung keine schreibgeschützten bzw. riskanten Ziele. Tastaturfokus
und Zurück-Navigation funktionieren. \### UI-033 **Given** ein
definierter Modulzustand. **When** der Nutzer Aktion 33 ausführt.
**Then** bleibt die Oberfläche responsiv, zeigt Fortschritt oder
unmittelbares Ergebnis, bietet bei Fehlern Details und verändert ohne
Bestätigung keine schreibgeschützten bzw. riskanten Ziele. Tastaturfokus
und Zurück-Navigation funktionieren. \### UI-034 **Given** ein
definierter Modulzustand. **When** der Nutzer Aktion 34 ausführt.
**Then** bleibt die Oberfläche responsiv, zeigt Fortschritt oder
unmittelbares Ergebnis, bietet bei Fehlern Details und verändert ohne
Bestätigung keine schreibgeschützten bzw. riskanten Ziele. Tastaturfokus
und Zurück-Navigation funktionieren. \### UI-035 **Given** ein
definierter Modulzustand. **When** der Nutzer Aktion 35 ausführt.
**Then** bleibt die Oberfläche responsiv, zeigt Fortschritt oder
unmittelbares Ergebnis, bietet bei Fehlern Details und verändert ohne
Bestätigung keine schreibgeschützten bzw. riskanten Ziele. Tastaturfokus
und Zurück-Navigation funktionieren. \### UI-036 **Given** ein
definierter Modulzustand. **When** der Nutzer Aktion 36 ausführt.
**Then** bleibt die Oberfläche responsiv, zeigt Fortschritt oder
unmittelbares Ergebnis, bietet bei Fehlern Details und verändert ohne
Bestätigung keine schreibgeschützten bzw. riskanten Ziele. Tastaturfokus
und Zurück-Navigation funktionieren. \### UI-037 **Given** ein
definierter Modulzustand. **When** der Nutzer Aktion 37 ausführt.
**Then** bleibt die Oberfläche responsiv, zeigt Fortschritt oder
unmittelbares Ergebnis, bietet bei Fehlern Details und verändert ohne
Bestätigung keine schreibgeschützten bzw. riskanten Ziele. Tastaturfokus
und Zurück-Navigation funktionieren. \### UI-038 **Given** ein
definierter Modulzustand. **When** der Nutzer Aktion 38 ausführt.
**Then** bleibt die Oberfläche responsiv, zeigt Fortschritt oder
unmittelbares Ergebnis, bietet bei Fehlern Details und verändert ohne
Bestätigung keine schreibgeschützten bzw. riskanten Ziele. Tastaturfokus
und Zurück-Navigation funktionieren. \### UI-039 **Given** ein
definierter Modulzustand. **When** der Nutzer Aktion 39 ausführt.
**Then** bleibt die Oberfläche responsiv, zeigt Fortschritt oder
unmittelbares Ergebnis, bietet bei Fehlern Details und verändert ohne
Bestätigung keine schreibgeschützten bzw. riskanten Ziele. Tastaturfokus
und Zurück-Navigation funktionieren. \### UI-040 **Given** ein
definierter Modulzustand. **When** der Nutzer Aktion 40 ausführt.
**Then** bleibt die Oberfläche responsiv, zeigt Fortschritt oder
unmittelbares Ergebnis, bietet bei Fehlern Details und verändert ohne
Bestätigung keine schreibgeschützten bzw. riskanten Ziele. Tastaturfokus
und Zurück-Navigation funktionieren. \### UI-041 **Given** ein
definierter Modulzustand. **When** der Nutzer Aktion 41 ausführt.
**Then** bleibt die Oberfläche responsiv, zeigt Fortschritt oder
unmittelbares Ergebnis, bietet bei Fehlern Details und verändert ohne
Bestätigung keine schreibgeschützten bzw. riskanten Ziele. Tastaturfokus
und Zurück-Navigation funktionieren. \### UI-042 **Given** ein
definierter Modulzustand. **When** der Nutzer Aktion 42 ausführt.
**Then** bleibt die Oberfläche responsiv, zeigt Fortschritt oder
unmittelbares Ergebnis, bietet bei Fehlern Details und verändert ohne
Bestätigung keine schreibgeschützten bzw. riskanten Ziele. Tastaturfokus
und Zurück-Navigation funktionieren. \### UI-043 **Given** ein
definierter Modulzustand. **When** der Nutzer Aktion 43 ausführt.
**Then** bleibt die Oberfläche responsiv, zeigt Fortschritt oder
unmittelbares Ergebnis, bietet bei Fehlern Details und verändert ohne
Bestätigung keine schreibgeschützten bzw. riskanten Ziele. Tastaturfokus
und Zurück-Navigation funktionieren. \### UI-044 **Given** ein
definierter Modulzustand. **When** der Nutzer Aktion 44 ausführt.
**Then** bleibt die Oberfläche responsiv, zeigt Fortschritt oder
unmittelbares Ergebnis, bietet bei Fehlern Details und verändert ohne
Bestätigung keine schreibgeschützten bzw. riskanten Ziele. Tastaturfokus
und Zurück-Navigation funktionieren. \### UI-045 **Given** ein
definierter Modulzustand. **When** der Nutzer Aktion 45 ausführt.
**Then** bleibt die Oberfläche responsiv, zeigt Fortschritt oder
unmittelbares Ergebnis, bietet bei Fehlern Details und verändert ohne
Bestätigung keine schreibgeschützten bzw. riskanten Ziele. Tastaturfokus
und Zurück-Navigation funktionieren. \### UI-046 **Given** ein
definierter Modulzustand. **When** der Nutzer Aktion 46 ausführt.
**Then** bleibt die Oberfläche responsiv, zeigt Fortschritt oder
unmittelbares Ergebnis, bietet bei Fehlern Details und verändert ohne
Bestätigung keine schreibgeschützten bzw. riskanten Ziele. Tastaturfokus
und Zurück-Navigation funktionieren. \### UI-047 **Given** ein
definierter Modulzustand. **When** der Nutzer Aktion 47 ausführt.
**Then** bleibt die Oberfläche responsiv, zeigt Fortschritt oder
unmittelbares Ergebnis, bietet bei Fehlern Details und verändert ohne
Bestätigung keine schreibgeschützten bzw. riskanten Ziele. Tastaturfokus
und Zurück-Navigation funktionieren. \### UI-048 **Given** ein
definierter Modulzustand. **When** der Nutzer Aktion 48 ausführt.
**Then** bleibt die Oberfläche responsiv, zeigt Fortschritt oder
unmittelbares Ergebnis, bietet bei Fehlern Details und verändert ohne
Bestätigung keine schreibgeschützten bzw. riskanten Ziele. Tastaturfokus
und Zurück-Navigation funktionieren. \### UI-049 **Given** ein
definierter Modulzustand. **When** der Nutzer Aktion 49 ausführt.
**Then** bleibt die Oberfläche responsiv, zeigt Fortschritt oder
unmittelbares Ergebnis, bietet bei Fehlern Details und verändert ohne
Bestätigung keine schreibgeschützten bzw. riskanten Ziele. Tastaturfokus
und Zurück-Navigation funktionieren. \### UI-050 **Given** ein
definierter Modulzustand. **When** der Nutzer Aktion 50 ausführt.
**Then** bleibt die Oberfläche responsiv, zeigt Fortschritt oder
unmittelbares Ergebnis, bietet bei Fehlern Details und verändert ohne
Bestätigung keine schreibgeschützten bzw. riskanten Ziele. Tastaturfokus
und Zurück-Navigation funktionieren. \### UI-051 **Given** ein
definierter Modulzustand. **When** der Nutzer Aktion 51 ausführt.
**Then** bleibt die Oberfläche responsiv, zeigt Fortschritt oder
unmittelbares Ergebnis, bietet bei Fehlern Details und verändert ohne
Bestätigung keine schreibgeschützten bzw. riskanten Ziele. Tastaturfokus
und Zurück-Navigation funktionieren. \### UI-052 **Given** ein
definierter Modulzustand. **When** der Nutzer Aktion 52 ausführt.
**Then** bleibt die Oberfläche responsiv, zeigt Fortschritt oder
unmittelbares Ergebnis, bietet bei Fehlern Details und verändert ohne
Bestätigung keine schreibgeschützten bzw. riskanten Ziele. Tastaturfokus
und Zurück-Navigation funktionieren. \### UI-053 **Given** ein
definierter Modulzustand. **When** der Nutzer Aktion 53 ausführt.
**Then** bleibt die Oberfläche responsiv, zeigt Fortschritt oder
unmittelbares Ergebnis, bietet bei Fehlern Details und verändert ohne
Bestätigung keine schreibgeschützten bzw. riskanten Ziele. Tastaturfokus
und Zurück-Navigation funktionieren. \### UI-054 **Given** ein
definierter Modulzustand. **When** der Nutzer Aktion 54 ausführt.
**Then** bleibt die Oberfläche responsiv, zeigt Fortschritt oder
unmittelbares Ergebnis, bietet bei Fehlern Details und verändert ohne
Bestätigung keine schreibgeschützten bzw. riskanten Ziele. Tastaturfokus
und Zurück-Navigation funktionieren. \### UI-055 **Given** ein
definierter Modulzustand. **When** der Nutzer Aktion 55 ausführt.
**Then** bleibt die Oberfläche responsiv, zeigt Fortschritt oder
unmittelbares Ergebnis, bietet bei Fehlern Details und verändert ohne
Bestätigung keine schreibgeschützten bzw. riskanten Ziele. Tastaturfokus
und Zurück-Navigation funktionieren. \### UI-056 **Given** ein
definierter Modulzustand. **When** der Nutzer Aktion 56 ausführt.
**Then** bleibt die Oberfläche responsiv, zeigt Fortschritt oder
unmittelbares Ergebnis, bietet bei Fehlern Details und verändert ohne
Bestätigung keine schreibgeschützten bzw. riskanten Ziele. Tastaturfokus
und Zurück-Navigation funktionieren. \### UI-057 **Given** ein
definierter Modulzustand. **When** der Nutzer Aktion 57 ausführt.
**Then** bleibt die Oberfläche responsiv, zeigt Fortschritt oder
unmittelbares Ergebnis, bietet bei Fehlern Details und verändert ohne
Bestätigung keine schreibgeschützten bzw. riskanten Ziele. Tastaturfokus
und Zurück-Navigation funktionieren. \### UI-058 **Given** ein
definierter Modulzustand. **When** der Nutzer Aktion 58 ausführt.
**Then** bleibt die Oberfläche responsiv, zeigt Fortschritt oder
unmittelbares Ergebnis, bietet bei Fehlern Details und verändert ohne
Bestätigung keine schreibgeschützten bzw. riskanten Ziele. Tastaturfokus
und Zurück-Navigation funktionieren. \### UI-059 **Given** ein
definierter Modulzustand. **When** der Nutzer Aktion 59 ausführt.
**Then** bleibt die Oberfläche responsiv, zeigt Fortschritt oder
unmittelbares Ergebnis, bietet bei Fehlern Details und verändert ohne
Bestätigung keine schreibgeschützten bzw. riskanten Ziele. Tastaturfokus
und Zurück-Navigation funktionieren. \### UI-060 **Given** ein
definierter Modulzustand. **When** der Nutzer Aktion 60 ausführt.
**Then** bleibt die Oberfläche responsiv, zeigt Fortschritt oder
unmittelbares Ergebnis, bietet bei Fehlern Details und verändert ohne
Bestätigung keine schreibgeschützten bzw. riskanten Ziele. Tastaturfokus
und Zurück-Navigation funktionieren.

::: {style="page-break-before: always;"}
:::

# 81. Provider-Vertrag -- Detailanforderungen

Jeder Provider besitzt eine feste ID, Anzeigename, Homepage,
Vertrauensklasse, Katalogversion und Capability-Liste. `RefreshCatalog`
darf nur Metadaten aktualisieren. `Download` lädt genau ein
beschriebenes Artefakt. `Validate` prüft das Artefakt unabhängig vom
Downloadpfad. Dadurch können auch lokal importierte Dateien durch
denselben Validator laufen.

Provider müssen HTTP 304, 403/Rate-Limit, 404 und 5xx unterscheiden. Bei
Rate-Limit wird der vorhandene Cache weiterverwendet und eine nächste
sinnvolle Abrufzeit angezeigt. Redirects werden begrenzt. Content-Type
allein gilt nicht als Validierung. ZIPs werden anhand Signatur/Struktur
geprüft.

Provider-Metadaten werden mit `retrieved_at`, `source_revision` und
`parser_version` gespeichert. Ändert sich der Parser, kann der lokale
Katalog ohne erneuten Download der Binärartefakte neu aufgebaut werden.

::: {style="page-break-before: always;"}
:::

# 82. Beispiel-Konfiguration

``` json
{
  "schemaVersion": 1,
  "module": "ps4",
  "expertMode": false,
  "network": { "ftpPort": 2121, "timeoutSeconds": 10 },
  "downloads": { "parallel": 3, "verifySha256": true },
  "backups": { "beforeWrite": true, "keepAutomatic": 10 },
  "providers": {
    "goldhen-cheats": { "enabled": true },
    "game-patches": { "enabled": true },
    "goldhen-plugins": { "enabled": true },
    "itemzflow": { "enabled": true }
  }
}
```

Die echte Implementierung soll Secrets nicht in dieser Datei speichern.
Unbekannte Felder werden beim Laden toleriert, bekannte Felder streng
validiert. Bei beschädigter Konfiguration wird nicht still auf riskante
Defaults zurückgefallen; stattdessen wird ein Recovery-Dialog angeboten.

::: {style="page-break-before: always;"}
:::

# 83. Beispiel eines normalisierten Artefakts

``` json
{
  "id": "goldhen-cheat:CUSA00001:01.23:example",
  "kind": "cheat",
  "provider": "goldhen-cheats",
  "titleId": "CUSA00001",
  "appVersions": ["01.23"],
  "format": "json",
  "sourceRevision": "<commit-or-release>",
  "sourceUrl": "<provider supplied>",
  "sha256": "<calculated after download>",
  "compatibility": "exact",
  "authors": ["Example Author"]
}
```

Die ID muss deterministisch sein. Ein Wechsel des Downloadservers darf
nicht automatisch eine neue fachliche Identität erzeugen. Änderungen am
Inhalt werden über Revision und Hash sichtbar.

::: {style="page-break-before: always;"}
:::

# 84. Matching-Algorithmus -- Pseudocode

``` text
function match(game, artifact):
    if artifact.titleIds does not contain game.titleId:
        return INCOMPATIBLE_TITLE
    if game.appVersion is unknown:
        return TITLE_MATCH_VERSION_UNKNOWN
    if artifact.appVersions is empty:
        return TITLE_MATCH_PROVIDER_VERSION_UNSPECIFIED
    if artifact.appVersions contains game.appVersion:
        return EXACT
    return TITLE_MATCH_VERSION_MISMATCH
```

Es gibt absichtlich keinen „wird schon passen"-Fallback.
Pattern-basierte Patches können eine eigene Capability `version_mask`
besitzen; deren Bewertung erfolgt in einem separaten Matcher und muss in
der UI als solche gekennzeichnet werden.

::: {style="page-break-before: always;"}
:::

# 85. Download-Pipeline -- Pseudocode

``` text
resolve descriptor
  -> validate URL/provider
  -> check cache/revision
  -> create .partial
  -> stream download with cancellation
  -> enforce max size
  -> calculate SHA-256
  -> provider validation
  -> safe archive inspection
  -> write manifest
  -> atomic rename
  -> register artifact in SQLite
```

Ein Abbruch löscht `.partial` oder markiert ihn eindeutig für Resume,
sofern der Server Range Requests unterstützt. Eine Datei wird niemals
nur wegen ihres Dateinamens als gültig angesehen.

::: {style="page-break-before: always;"}
:::

# 86. USB-Manifest -- Beispiel

``` json
{
  "createdBy": "HESPERIA Tool / PS4 Module",
  "createdAt": "2026-09-17T22:00:00+02:00",
  "profile": "offline-complete",
  "files": [
    {"path":"Downloads/Cheats/database.zip","sha256":"...","source":"goldhen-cheats"},
    {"path":"Downloads/Patches/patch1.zip","sha256":"...","source":"game-patches"}
  ]
}
```

Beim erneuten Einlesen eines HESPERIA-USB-Packs kann das Tool anhand des
Manifests erkennen, ob Dateien verändert oder beschädigt wurden.

::: {style="page-break-before: always;"}
:::

# 87. Theme-Builder -- Buildvertrag

Der Theme Builder arbeitet in `custom/themes/<theme-id>/src` und erzeugt
`build`. Ein Build ist reproduzierbar: gleiche Eingaben + gleiche
Builder-Version ergeben dieselbe Struktur. Metadaten enthalten Name,
Autor, Version, Ziel (Itemzflow), Assetliste und Builder-Version.

Bildverarbeitung darf Originale nicht überschreiben. Vorschauen werden
gecacht. Nicht unterstützte Musik- oder Fontformate werden nicht
heimlich konvertiert, sofern keine explizite, lizenzkompatible
Konvertierungskomponente vorhanden ist.

::: {style="page-break-before: always;"}
:::

# 88. Diagnose-Checkliste

-   [ ] Diagnose 01: Zustand erfassen, erwarteten Wert mit tatsächlichem
    Wert vergleichen, Ergebnis mit Dauer protokollieren und bei
    Abweichung eine konkrete nächste Aktion anbieten.
-   [ ] Diagnose 02: Zustand erfassen, erwarteten Wert mit tatsächlichem
    Wert vergleichen, Ergebnis mit Dauer protokollieren und bei
    Abweichung eine konkrete nächste Aktion anbieten.
-   [ ] Diagnose 03: Zustand erfassen, erwarteten Wert mit tatsächlichem
    Wert vergleichen, Ergebnis mit Dauer protokollieren und bei
    Abweichung eine konkrete nächste Aktion anbieten.
-   [ ] Diagnose 04: Zustand erfassen, erwarteten Wert mit tatsächlichem
    Wert vergleichen, Ergebnis mit Dauer protokollieren und bei
    Abweichung eine konkrete nächste Aktion anbieten.
-   [ ] Diagnose 05: Zustand erfassen, erwarteten Wert mit tatsächlichem
    Wert vergleichen, Ergebnis mit Dauer protokollieren und bei
    Abweichung eine konkrete nächste Aktion anbieten.
-   [ ] Diagnose 06: Zustand erfassen, erwarteten Wert mit tatsächlichem
    Wert vergleichen, Ergebnis mit Dauer protokollieren und bei
    Abweichung eine konkrete nächste Aktion anbieten.
-   [ ] Diagnose 07: Zustand erfassen, erwarteten Wert mit tatsächlichem
    Wert vergleichen, Ergebnis mit Dauer protokollieren und bei
    Abweichung eine konkrete nächste Aktion anbieten.
-   [ ] Diagnose 08: Zustand erfassen, erwarteten Wert mit tatsächlichem
    Wert vergleichen, Ergebnis mit Dauer protokollieren und bei
    Abweichung eine konkrete nächste Aktion anbieten.
-   [ ] Diagnose 09: Zustand erfassen, erwarteten Wert mit tatsächlichem
    Wert vergleichen, Ergebnis mit Dauer protokollieren und bei
    Abweichung eine konkrete nächste Aktion anbieten.
-   [ ] Diagnose 10: Zustand erfassen, erwarteten Wert mit tatsächlichem
    Wert vergleichen, Ergebnis mit Dauer protokollieren und bei
    Abweichung eine konkrete nächste Aktion anbieten.
-   [ ] Diagnose 11: Zustand erfassen, erwarteten Wert mit tatsächlichem
    Wert vergleichen, Ergebnis mit Dauer protokollieren und bei
    Abweichung eine konkrete nächste Aktion anbieten.
-   [ ] Diagnose 12: Zustand erfassen, erwarteten Wert mit tatsächlichem
    Wert vergleichen, Ergebnis mit Dauer protokollieren und bei
    Abweichung eine konkrete nächste Aktion anbieten.
-   [ ] Diagnose 13: Zustand erfassen, erwarteten Wert mit tatsächlichem
    Wert vergleichen, Ergebnis mit Dauer protokollieren und bei
    Abweichung eine konkrete nächste Aktion anbieten.
-   [ ] Diagnose 14: Zustand erfassen, erwarteten Wert mit tatsächlichem
    Wert vergleichen, Ergebnis mit Dauer protokollieren und bei
    Abweichung eine konkrete nächste Aktion anbieten.
-   [ ] Diagnose 15: Zustand erfassen, erwarteten Wert mit tatsächlichem
    Wert vergleichen, Ergebnis mit Dauer protokollieren und bei
    Abweichung eine konkrete nächste Aktion anbieten.
-   [ ] Diagnose 16: Zustand erfassen, erwarteten Wert mit tatsächlichem
    Wert vergleichen, Ergebnis mit Dauer protokollieren und bei
    Abweichung eine konkrete nächste Aktion anbieten.
-   [ ] Diagnose 17: Zustand erfassen, erwarteten Wert mit tatsächlichem
    Wert vergleichen, Ergebnis mit Dauer protokollieren und bei
    Abweichung eine konkrete nächste Aktion anbieten.
-   [ ] Diagnose 18: Zustand erfassen, erwarteten Wert mit tatsächlichem
    Wert vergleichen, Ergebnis mit Dauer protokollieren und bei
    Abweichung eine konkrete nächste Aktion anbieten.
-   [ ] Diagnose 19: Zustand erfassen, erwarteten Wert mit tatsächlichem
    Wert vergleichen, Ergebnis mit Dauer protokollieren und bei
    Abweichung eine konkrete nächste Aktion anbieten.
-   [ ] Diagnose 20: Zustand erfassen, erwarteten Wert mit tatsächlichem
    Wert vergleichen, Ergebnis mit Dauer protokollieren und bei
    Abweichung eine konkrete nächste Aktion anbieten.
-   [ ] Diagnose 21: Zustand erfassen, erwarteten Wert mit tatsächlichem
    Wert vergleichen, Ergebnis mit Dauer protokollieren und bei
    Abweichung eine konkrete nächste Aktion anbieten.
-   [ ] Diagnose 22: Zustand erfassen, erwarteten Wert mit tatsächlichem
    Wert vergleichen, Ergebnis mit Dauer protokollieren und bei
    Abweichung eine konkrete nächste Aktion anbieten.
-   [ ] Diagnose 23: Zustand erfassen, erwarteten Wert mit tatsächlichem
    Wert vergleichen, Ergebnis mit Dauer protokollieren und bei
    Abweichung eine konkrete nächste Aktion anbieten.
-   [ ] Diagnose 24: Zustand erfassen, erwarteten Wert mit tatsächlichem
    Wert vergleichen, Ergebnis mit Dauer protokollieren und bei
    Abweichung eine konkrete nächste Aktion anbieten.
-   [ ] Diagnose 25: Zustand erfassen, erwarteten Wert mit tatsächlichem
    Wert vergleichen, Ergebnis mit Dauer protokollieren und bei
    Abweichung eine konkrete nächste Aktion anbieten.
-   [ ] Diagnose 26: Zustand erfassen, erwarteten Wert mit tatsächlichem
    Wert vergleichen, Ergebnis mit Dauer protokollieren und bei
    Abweichung eine konkrete nächste Aktion anbieten.
-   [ ] Diagnose 27: Zustand erfassen, erwarteten Wert mit tatsächlichem
    Wert vergleichen, Ergebnis mit Dauer protokollieren und bei
    Abweichung eine konkrete nächste Aktion anbieten.
-   [ ] Diagnose 28: Zustand erfassen, erwarteten Wert mit tatsächlichem
    Wert vergleichen, Ergebnis mit Dauer protokollieren und bei
    Abweichung eine konkrete nächste Aktion anbieten.
-   [ ] Diagnose 29: Zustand erfassen, erwarteten Wert mit tatsächlichem
    Wert vergleichen, Ergebnis mit Dauer protokollieren und bei
    Abweichung eine konkrete nächste Aktion anbieten.
-   [ ] Diagnose 30: Zustand erfassen, erwarteten Wert mit tatsächlichem
    Wert vergleichen, Ergebnis mit Dauer protokollieren und bei
    Abweichung eine konkrete nächste Aktion anbieten.
-   [ ] Diagnose 31: Zustand erfassen, erwarteten Wert mit tatsächlichem
    Wert vergleichen, Ergebnis mit Dauer protokollieren und bei
    Abweichung eine konkrete nächste Aktion anbieten.
-   [ ] Diagnose 32: Zustand erfassen, erwarteten Wert mit tatsächlichem
    Wert vergleichen, Ergebnis mit Dauer protokollieren und bei
    Abweichung eine konkrete nächste Aktion anbieten.
-   [ ] Diagnose 33: Zustand erfassen, erwarteten Wert mit tatsächlichem
    Wert vergleichen, Ergebnis mit Dauer protokollieren und bei
    Abweichung eine konkrete nächste Aktion anbieten.
-   [ ] Diagnose 34: Zustand erfassen, erwarteten Wert mit tatsächlichem
    Wert vergleichen, Ergebnis mit Dauer protokollieren und bei
    Abweichung eine konkrete nächste Aktion anbieten.
-   [ ] Diagnose 35: Zustand erfassen, erwarteten Wert mit tatsächlichem
    Wert vergleichen, Ergebnis mit Dauer protokollieren und bei
    Abweichung eine konkrete nächste Aktion anbieten.
-   [ ] Diagnose 36: Zustand erfassen, erwarteten Wert mit tatsächlichem
    Wert vergleichen, Ergebnis mit Dauer protokollieren und bei
    Abweichung eine konkrete nächste Aktion anbieten.
-   [ ] Diagnose 37: Zustand erfassen, erwarteten Wert mit tatsächlichem
    Wert vergleichen, Ergebnis mit Dauer protokollieren und bei
    Abweichung eine konkrete nächste Aktion anbieten.
-   [ ] Diagnose 38: Zustand erfassen, erwarteten Wert mit tatsächlichem
    Wert vergleichen, Ergebnis mit Dauer protokollieren und bei
    Abweichung eine konkrete nächste Aktion anbieten.
-   [ ] Diagnose 39: Zustand erfassen, erwarteten Wert mit tatsächlichem
    Wert vergleichen, Ergebnis mit Dauer protokollieren und bei
    Abweichung eine konkrete nächste Aktion anbieten.
-   [ ] Diagnose 40: Zustand erfassen, erwarteten Wert mit tatsächlichem
    Wert vergleichen, Ergebnis mit Dauer protokollieren und bei
    Abweichung eine konkrete nächste Aktion anbieten.
-   [ ] Diagnose 41: Zustand erfassen, erwarteten Wert mit tatsächlichem
    Wert vergleichen, Ergebnis mit Dauer protokollieren und bei
    Abweichung eine konkrete nächste Aktion anbieten.
-   [ ] Diagnose 42: Zustand erfassen, erwarteten Wert mit tatsächlichem
    Wert vergleichen, Ergebnis mit Dauer protokollieren und bei
    Abweichung eine konkrete nächste Aktion anbieten.
-   [ ] Diagnose 43: Zustand erfassen, erwarteten Wert mit tatsächlichem
    Wert vergleichen, Ergebnis mit Dauer protokollieren und bei
    Abweichung eine konkrete nächste Aktion anbieten.
-   [ ] Diagnose 44: Zustand erfassen, erwarteten Wert mit tatsächlichem
    Wert vergleichen, Ergebnis mit Dauer protokollieren und bei
    Abweichung eine konkrete nächste Aktion anbieten.
-   [ ] Diagnose 45: Zustand erfassen, erwarteten Wert mit tatsächlichem
    Wert vergleichen, Ergebnis mit Dauer protokollieren und bei
    Abweichung eine konkrete nächste Aktion anbieten.
-   [ ] Diagnose 46: Zustand erfassen, erwarteten Wert mit tatsächlichem
    Wert vergleichen, Ergebnis mit Dauer protokollieren und bei
    Abweichung eine konkrete nächste Aktion anbieten.
-   [ ] Diagnose 47: Zustand erfassen, erwarteten Wert mit tatsächlichem
    Wert vergleichen, Ergebnis mit Dauer protokollieren und bei
    Abweichung eine konkrete nächste Aktion anbieten.
-   [ ] Diagnose 48: Zustand erfassen, erwarteten Wert mit tatsächlichem
    Wert vergleichen, Ergebnis mit Dauer protokollieren und bei
    Abweichung eine konkrete nächste Aktion anbieten.
-   [ ] Diagnose 49: Zustand erfassen, erwarteten Wert mit tatsächlichem
    Wert vergleichen, Ergebnis mit Dauer protokollieren und bei
    Abweichung eine konkrete nächste Aktion anbieten.
-   [ ] Diagnose 50: Zustand erfassen, erwarteten Wert mit tatsächlichem
    Wert vergleichen, Ergebnis mit Dauer protokollieren und bei
    Abweichung eine konkrete nächste Aktion anbieten.

::: {style="page-break-before: always;"}
:::

# 89. Regressionstest-Matrix

  -----------------------------------------------------------------------------
  Test              Bereich           Szenario                Erwartung
  ----------------- ----------------- ----------------------- -----------------
  T001              Komponente 2      Normal/Fehler/Abbruch   Erwartung:
                                                              konsistenter
                                                              Zustand,
                                                              verständliche
                                                              Meldung, kein
                                                              Datenverlust

  T002              Komponente 3      Normal/Fehler/Abbruch   Erwartung:
                                                              konsistenter
                                                              Zustand,
                                                              verständliche
                                                              Meldung, kein
                                                              Datenverlust

  T003              Komponente 4      Normal/Fehler/Abbruch   Erwartung:
                                                              konsistenter
                                                              Zustand,
                                                              verständliche
                                                              Meldung, kein
                                                              Datenverlust

  T004              Komponente 5      Normal/Fehler/Abbruch   Erwartung:
                                                              konsistenter
                                                              Zustand,
                                                              verständliche
                                                              Meldung, kein
                                                              Datenverlust

  T005              Komponente 6      Normal/Fehler/Abbruch   Erwartung:
                                                              konsistenter
                                                              Zustand,
                                                              verständliche
                                                              Meldung, kein
                                                              Datenverlust

  T006              Komponente 7      Normal/Fehler/Abbruch   Erwartung:
                                                              konsistenter
                                                              Zustand,
                                                              verständliche
                                                              Meldung, kein
                                                              Datenverlust

  T007              Komponente 8      Normal/Fehler/Abbruch   Erwartung:
                                                              konsistenter
                                                              Zustand,
                                                              verständliche
                                                              Meldung, kein
                                                              Datenverlust

  T008              Komponente 9      Normal/Fehler/Abbruch   Erwartung:
                                                              konsistenter
                                                              Zustand,
                                                              verständliche
                                                              Meldung, kein
                                                              Datenverlust

  T009              Komponente 10     Normal/Fehler/Abbruch   Erwartung:
                                                              konsistenter
                                                              Zustand,
                                                              verständliche
                                                              Meldung, kein
                                                              Datenverlust

  T010              Komponente 11     Normal/Fehler/Abbruch   Erwartung:
                                                              konsistenter
                                                              Zustand,
                                                              verständliche
                                                              Meldung, kein
                                                              Datenverlust

  T011              Komponente 12     Normal/Fehler/Abbruch   Erwartung:
                                                              konsistenter
                                                              Zustand,
                                                              verständliche
                                                              Meldung, kein
                                                              Datenverlust

  T012              Komponente 1      Normal/Fehler/Abbruch   Erwartung:
                                                              konsistenter
                                                              Zustand,
                                                              verständliche
                                                              Meldung, kein
                                                              Datenverlust

  T013              Komponente 2      Normal/Fehler/Abbruch   Erwartung:
                                                              konsistenter
                                                              Zustand,
                                                              verständliche
                                                              Meldung, kein
                                                              Datenverlust

  T014              Komponente 3      Normal/Fehler/Abbruch   Erwartung:
                                                              konsistenter
                                                              Zustand,
                                                              verständliche
                                                              Meldung, kein
                                                              Datenverlust

  T015              Komponente 4      Normal/Fehler/Abbruch   Erwartung:
                                                              konsistenter
                                                              Zustand,
                                                              verständliche
                                                              Meldung, kein
                                                              Datenverlust

  T016              Komponente 5      Normal/Fehler/Abbruch   Erwartung:
                                                              konsistenter
                                                              Zustand,
                                                              verständliche
                                                              Meldung, kein
                                                              Datenverlust

  T017              Komponente 6      Normal/Fehler/Abbruch   Erwartung:
                                                              konsistenter
                                                              Zustand,
                                                              verständliche
                                                              Meldung, kein
                                                              Datenverlust

  T018              Komponente 7      Normal/Fehler/Abbruch   Erwartung:
                                                              konsistenter
                                                              Zustand,
                                                              verständliche
                                                              Meldung, kein
                                                              Datenverlust

  T019              Komponente 8      Normal/Fehler/Abbruch   Erwartung:
                                                              konsistenter
                                                              Zustand,
                                                              verständliche
                                                              Meldung, kein
                                                              Datenverlust

  T020              Komponente 9      Normal/Fehler/Abbruch   Erwartung:
                                                              konsistenter
                                                              Zustand,
                                                              verständliche
                                                              Meldung, kein
                                                              Datenverlust

  T021              Komponente 10     Normal/Fehler/Abbruch   Erwartung:
                                                              konsistenter
                                                              Zustand,
                                                              verständliche
                                                              Meldung, kein
                                                              Datenverlust

  T022              Komponente 11     Normal/Fehler/Abbruch   Erwartung:
                                                              konsistenter
                                                              Zustand,
                                                              verständliche
                                                              Meldung, kein
                                                              Datenverlust

  T023              Komponente 12     Normal/Fehler/Abbruch   Erwartung:
                                                              konsistenter
                                                              Zustand,
                                                              verständliche
                                                              Meldung, kein
                                                              Datenverlust

  T024              Komponente 1      Normal/Fehler/Abbruch   Erwartung:
                                                              konsistenter
                                                              Zustand,
                                                              verständliche
                                                              Meldung, kein
                                                              Datenverlust

  T025              Komponente 2      Normal/Fehler/Abbruch   Erwartung:
                                                              konsistenter
                                                              Zustand,
                                                              verständliche
                                                              Meldung, kein
                                                              Datenverlust

  T026              Komponente 3      Normal/Fehler/Abbruch   Erwartung:
                                                              konsistenter
                                                              Zustand,
                                                              verständliche
                                                              Meldung, kein
                                                              Datenverlust

  T027              Komponente 4      Normal/Fehler/Abbruch   Erwartung:
                                                              konsistenter
                                                              Zustand,
                                                              verständliche
                                                              Meldung, kein
                                                              Datenverlust

  T028              Komponente 5      Normal/Fehler/Abbruch   Erwartung:
                                                              konsistenter
                                                              Zustand,
                                                              verständliche
                                                              Meldung, kein
                                                              Datenverlust

  T029              Komponente 6      Normal/Fehler/Abbruch   Erwartung:
                                                              konsistenter
                                                              Zustand,
                                                              verständliche
                                                              Meldung, kein
                                                              Datenverlust

  T030              Komponente 7      Normal/Fehler/Abbruch   Erwartung:
                                                              konsistenter
                                                              Zustand,
                                                              verständliche
                                                              Meldung, kein
                                                              Datenverlust

  T031              Komponente 8      Normal/Fehler/Abbruch   Erwartung:
                                                              konsistenter
                                                              Zustand,
                                                              verständliche
                                                              Meldung, kein
                                                              Datenverlust

  T032              Komponente 9      Normal/Fehler/Abbruch   Erwartung:
                                                              konsistenter
                                                              Zustand,
                                                              verständliche
                                                              Meldung, kein
                                                              Datenverlust

  T033              Komponente 10     Normal/Fehler/Abbruch   Erwartung:
                                                              konsistenter
                                                              Zustand,
                                                              verständliche
                                                              Meldung, kein
                                                              Datenverlust

  T034              Komponente 11     Normal/Fehler/Abbruch   Erwartung:
                                                              konsistenter
                                                              Zustand,
                                                              verständliche
                                                              Meldung, kein
                                                              Datenverlust

  T035              Komponente 12     Normal/Fehler/Abbruch   Erwartung:
                                                              konsistenter
                                                              Zustand,
                                                              verständliche
                                                              Meldung, kein
                                                              Datenverlust

  T036              Komponente 1      Normal/Fehler/Abbruch   Erwartung:
                                                              konsistenter
                                                              Zustand,
                                                              verständliche
                                                              Meldung, kein
                                                              Datenverlust

  T037              Komponente 2      Normal/Fehler/Abbruch   Erwartung:
                                                              konsistenter
                                                              Zustand,
                                                              verständliche
                                                              Meldung, kein
                                                              Datenverlust

  T038              Komponente 3      Normal/Fehler/Abbruch   Erwartung:
                                                              konsistenter
                                                              Zustand,
                                                              verständliche
                                                              Meldung, kein
                                                              Datenverlust

  T039              Komponente 4      Normal/Fehler/Abbruch   Erwartung:
                                                              konsistenter
                                                              Zustand,
                                                              verständliche
                                                              Meldung, kein
                                                              Datenverlust

  T040              Komponente 5      Normal/Fehler/Abbruch   Erwartung:
                                                              konsistenter
                                                              Zustand,
                                                              verständliche
                                                              Meldung, kein
                                                              Datenverlust

  T041              Komponente 6      Normal/Fehler/Abbruch   Erwartung:
                                                              konsistenter
                                                              Zustand,
                                                              verständliche
                                                              Meldung, kein
                                                              Datenverlust

  T042              Komponente 7      Normal/Fehler/Abbruch   Erwartung:
                                                              konsistenter
                                                              Zustand,
                                                              verständliche
                                                              Meldung, kein
                                                              Datenverlust

  T043              Komponente 8      Normal/Fehler/Abbruch   Erwartung:
                                                              konsistenter
                                                              Zustand,
                                                              verständliche
                                                              Meldung, kein
                                                              Datenverlust

  T044              Komponente 9      Normal/Fehler/Abbruch   Erwartung:
                                                              konsistenter
                                                              Zustand,
                                                              verständliche
                                                              Meldung, kein
                                                              Datenverlust

  T045              Komponente 10     Normal/Fehler/Abbruch   Erwartung:
                                                              konsistenter
                                                              Zustand,
                                                              verständliche
                                                              Meldung, kein
                                                              Datenverlust

  T046              Komponente 11     Normal/Fehler/Abbruch   Erwartung:
                                                              konsistenter
                                                              Zustand,
                                                              verständliche
                                                              Meldung, kein
                                                              Datenverlust

  T047              Komponente 12     Normal/Fehler/Abbruch   Erwartung:
                                                              konsistenter
                                                              Zustand,
                                                              verständliche
                                                              Meldung, kein
                                                              Datenverlust

  T048              Komponente 1      Normal/Fehler/Abbruch   Erwartung:
                                                              konsistenter
                                                              Zustand,
                                                              verständliche
                                                              Meldung, kein
                                                              Datenverlust

  T049              Komponente 2      Normal/Fehler/Abbruch   Erwartung:
                                                              konsistenter
                                                              Zustand,
                                                              verständliche
                                                              Meldung, kein
                                                              Datenverlust

  T050              Komponente 3      Normal/Fehler/Abbruch   Erwartung:
                                                              konsistenter
                                                              Zustand,
                                                              verständliche
                                                              Meldung, kein
                                                              Datenverlust

  T051              Komponente 4      Normal/Fehler/Abbruch   Erwartung:
                                                              konsistenter
                                                              Zustand,
                                                              verständliche
                                                              Meldung, kein
                                                              Datenverlust

  T052              Komponente 5      Normal/Fehler/Abbruch   Erwartung:
                                                              konsistenter
                                                              Zustand,
                                                              verständliche
                                                              Meldung, kein
                                                              Datenverlust

  T053              Komponente 6      Normal/Fehler/Abbruch   Erwartung:
                                                              konsistenter
                                                              Zustand,
                                                              verständliche
                                                              Meldung, kein
                                                              Datenverlust

  T054              Komponente 7      Normal/Fehler/Abbruch   Erwartung:
                                                              konsistenter
                                                              Zustand,
                                                              verständliche
                                                              Meldung, kein
                                                              Datenverlust

  T055              Komponente 8      Normal/Fehler/Abbruch   Erwartung:
                                                              konsistenter
                                                              Zustand,
                                                              verständliche
                                                              Meldung, kein
                                                              Datenverlust

  T056              Komponente 9      Normal/Fehler/Abbruch   Erwartung:
                                                              konsistenter
                                                              Zustand,
                                                              verständliche
                                                              Meldung, kein
                                                              Datenverlust

  T057              Komponente 10     Normal/Fehler/Abbruch   Erwartung:
                                                              konsistenter
                                                              Zustand,
                                                              verständliche
                                                              Meldung, kein
                                                              Datenverlust

  T058              Komponente 11     Normal/Fehler/Abbruch   Erwartung:
                                                              konsistenter
                                                              Zustand,
                                                              verständliche
                                                              Meldung, kein
                                                              Datenverlust

  T059              Komponente 12     Normal/Fehler/Abbruch   Erwartung:
                                                              konsistenter
                                                              Zustand,
                                                              verständliche
                                                              Meldung, kein
                                                              Datenverlust

  T060              Komponente 1      Normal/Fehler/Abbruch   Erwartung:
                                                              konsistenter
                                                              Zustand,
                                                              verständliche
                                                              Meldung, kein
                                                              Datenverlust

  T061              Komponente 2      Normal/Fehler/Abbruch   Erwartung:
                                                              konsistenter
                                                              Zustand,
                                                              verständliche
                                                              Meldung, kein
                                                              Datenverlust

  T062              Komponente 3      Normal/Fehler/Abbruch   Erwartung:
                                                              konsistenter
                                                              Zustand,
                                                              verständliche
                                                              Meldung, kein
                                                              Datenverlust

  T063              Komponente 4      Normal/Fehler/Abbruch   Erwartung:
                                                              konsistenter
                                                              Zustand,
                                                              verständliche
                                                              Meldung, kein
                                                              Datenverlust

  T064              Komponente 5      Normal/Fehler/Abbruch   Erwartung:
                                                              konsistenter
                                                              Zustand,
                                                              verständliche
                                                              Meldung, kein
                                                              Datenverlust

  T065              Komponente 6      Normal/Fehler/Abbruch   Erwartung:
                                                              konsistenter
                                                              Zustand,
                                                              verständliche
                                                              Meldung, kein
                                                              Datenverlust

  T066              Komponente 7      Normal/Fehler/Abbruch   Erwartung:
                                                              konsistenter
                                                              Zustand,
                                                              verständliche
                                                              Meldung, kein
                                                              Datenverlust

  T067              Komponente 8      Normal/Fehler/Abbruch   Erwartung:
                                                              konsistenter
                                                              Zustand,
                                                              verständliche
                                                              Meldung, kein
                                                              Datenverlust

  T068              Komponente 9      Normal/Fehler/Abbruch   Erwartung:
                                                              konsistenter
                                                              Zustand,
                                                              verständliche
                                                              Meldung, kein
                                                              Datenverlust

  T069              Komponente 10     Normal/Fehler/Abbruch   Erwartung:
                                                              konsistenter
                                                              Zustand,
                                                              verständliche
                                                              Meldung, kein
                                                              Datenverlust

  T070              Komponente 11     Normal/Fehler/Abbruch   Erwartung:
                                                              konsistenter
                                                              Zustand,
                                                              verständliche
                                                              Meldung, kein
                                                              Datenverlust

  T071              Komponente 12     Normal/Fehler/Abbruch   Erwartung:
                                                              konsistenter
                                                              Zustand,
                                                              verständliche
                                                              Meldung, kein
                                                              Datenverlust

  T072              Komponente 1      Normal/Fehler/Abbruch   Erwartung:
                                                              konsistenter
                                                              Zustand,
                                                              verständliche
                                                              Meldung, kein
                                                              Datenverlust

  T073              Komponente 2      Normal/Fehler/Abbruch   Erwartung:
                                                              konsistenter
                                                              Zustand,
                                                              verständliche
                                                              Meldung, kein
                                                              Datenverlust

  T074              Komponente 3      Normal/Fehler/Abbruch   Erwartung:
                                                              konsistenter
                                                              Zustand,
                                                              verständliche
                                                              Meldung, kein
                                                              Datenverlust

  T075              Komponente 4      Normal/Fehler/Abbruch   Erwartung:
                                                              konsistenter
                                                              Zustand,
                                                              verständliche
                                                              Meldung, kein
                                                              Datenverlust

  T076              Komponente 5      Normal/Fehler/Abbruch   Erwartung:
                                                              konsistenter
                                                              Zustand,
                                                              verständliche
                                                              Meldung, kein
                                                              Datenverlust

  T077              Komponente 6      Normal/Fehler/Abbruch   Erwartung:
                                                              konsistenter
                                                              Zustand,
                                                              verständliche
                                                              Meldung, kein
                                                              Datenverlust

  T078              Komponente 7      Normal/Fehler/Abbruch   Erwartung:
                                                              konsistenter
                                                              Zustand,
                                                              verständliche
                                                              Meldung, kein
                                                              Datenverlust

  T079              Komponente 8      Normal/Fehler/Abbruch   Erwartung:
                                                              konsistenter
                                                              Zustand,
                                                              verständliche
                                                              Meldung, kein
                                                              Datenverlust

  T080              Komponente 9      Normal/Fehler/Abbruch   Erwartung:
                                                              konsistenter
                                                              Zustand,
                                                              verständliche
                                                              Meldung, kein
                                                              Datenverlust

  T081              Komponente 10     Normal/Fehler/Abbruch   Erwartung:
                                                              konsistenter
                                                              Zustand,
                                                              verständliche
                                                              Meldung, kein
                                                              Datenverlust

  T082              Komponente 11     Normal/Fehler/Abbruch   Erwartung:
                                                              konsistenter
                                                              Zustand,
                                                              verständliche
                                                              Meldung, kein
                                                              Datenverlust

  T083              Komponente 12     Normal/Fehler/Abbruch   Erwartung:
                                                              konsistenter
                                                              Zustand,
                                                              verständliche
                                                              Meldung, kein
                                                              Datenverlust

  T084              Komponente 1      Normal/Fehler/Abbruch   Erwartung:
                                                              konsistenter
                                                              Zustand,
                                                              verständliche
                                                              Meldung, kein
                                                              Datenverlust

  T085              Komponente 2      Normal/Fehler/Abbruch   Erwartung:
                                                              konsistenter
                                                              Zustand,
                                                              verständliche
                                                              Meldung, kein
                                                              Datenverlust

  T086              Komponente 3      Normal/Fehler/Abbruch   Erwartung:
                                                              konsistenter
                                                              Zustand,
                                                              verständliche
                                                              Meldung, kein
                                                              Datenverlust

  T087              Komponente 4      Normal/Fehler/Abbruch   Erwartung:
                                                              konsistenter
                                                              Zustand,
                                                              verständliche
                                                              Meldung, kein
                                                              Datenverlust

  T088              Komponente 5      Normal/Fehler/Abbruch   Erwartung:
                                                              konsistenter
                                                              Zustand,
                                                              verständliche
                                                              Meldung, kein
                                                              Datenverlust

  T089              Komponente 6      Normal/Fehler/Abbruch   Erwartung:
                                                              konsistenter
                                                              Zustand,
                                                              verständliche
                                                              Meldung, kein
                                                              Datenverlust

  T090              Komponente 7      Normal/Fehler/Abbruch   Erwartung:
                                                              konsistenter
                                                              Zustand,
                                                              verständliche
                                                              Meldung, kein
                                                              Datenverlust

  T091              Komponente 8      Normal/Fehler/Abbruch   Erwartung:
                                                              konsistenter
                                                              Zustand,
                                                              verständliche
                                                              Meldung, kein
                                                              Datenverlust

  T092              Komponente 9      Normal/Fehler/Abbruch   Erwartung:
                                                              konsistenter
                                                              Zustand,
                                                              verständliche
                                                              Meldung, kein
                                                              Datenverlust

  T093              Komponente 10     Normal/Fehler/Abbruch   Erwartung:
                                                              konsistenter
                                                              Zustand,
                                                              verständliche
                                                              Meldung, kein
                                                              Datenverlust

  T094              Komponente 11     Normal/Fehler/Abbruch   Erwartung:
                                                              konsistenter
                                                              Zustand,
                                                              verständliche
                                                              Meldung, kein
                                                              Datenverlust

  T095              Komponente 12     Normal/Fehler/Abbruch   Erwartung:
                                                              konsistenter
                                                              Zustand,
                                                              verständliche
                                                              Meldung, kein
                                                              Datenverlust

  T096              Komponente 1      Normal/Fehler/Abbruch   Erwartung:
                                                              konsistenter
                                                              Zustand,
                                                              verständliche
                                                              Meldung, kein
                                                              Datenverlust

  T097              Komponente 2      Normal/Fehler/Abbruch   Erwartung:
                                                              konsistenter
                                                              Zustand,
                                                              verständliche
                                                              Meldung, kein
                                                              Datenverlust

  T098              Komponente 3      Normal/Fehler/Abbruch   Erwartung:
                                                              konsistenter
                                                              Zustand,
                                                              verständliche
                                                              Meldung, kein
                                                              Datenverlust

  T099              Komponente 4      Normal/Fehler/Abbruch   Erwartung:
                                                              konsistenter
                                                              Zustand,
                                                              verständliche
                                                              Meldung, kein
                                                              Datenverlust

  T100              Komponente 5      Normal/Fehler/Abbruch   Erwartung:
                                                              konsistenter
                                                              Zustand,
                                                              verständliche
                                                              Meldung, kein
                                                              Datenverlust
  -----------------------------------------------------------------------------

::: {style="page-break-before: always;"}
:::

# 90. Performance- und Lasttests

Katalogtests werden mit 100, 1.000, 10.000 und 50.000 Artefakten
ausgeführt. Suchindex, Filter und Matching sollen nicht linear die UI
blockieren. Hashing großer Dateien läuft streambasiert. Mehrere
Downloads teilen Bandbreite fair und respektieren das konfigurierte
Parallelitätslimit.

Ein künstlich langsamer FTP-Server und ein Server mit sporadischen
Disconnects gehören zu den Testfixtures. Speicherverbrauch wird bei
großen ZIPs geprüft; Archive dürfen nicht vollständig unkomprimiert in
RAM geladen werden.

::: {style="page-break-before: always;"}
:::

# 91. Accessibility und Bedienqualität

Alle Kernaktionen sind per Tastatur erreichbar. Fokus ist sichtbar.
Tooltips ersetzen keine Labels. Skalierung bis mindestens 150--200 %
darf keine Bedienelemente abschneiden. Statusinformationen besitzen Text
und Icon zusätzlich zur Farbe. Fehlermeldungen sind kopierbar.

Fortschrittsanzeigen dürfen nicht springen, wenn die Gesamtgröße bekannt
ist. Bei unbekannter Größe wird indeterminierter Fortschritt angezeigt.
Abbrechen muss tatsächlich abbrechen und nicht nur den Dialog schließen.

::: {style="page-break-before: always;"}
:::

# 92. Datenschutz und lokale Daten

Das PS4-Modul benötigt keine Cloud-Konten. Konsolen-IP, lokale Pfade,
Inventar und Logs bleiben lokal. Externe Requests gehen nur an
aktivierte Provider und enthalten nur technisch notwendige HTTP-Daten.
Keine Werbe-/Tracking-SDKs.

Diagnoseexporte werden vor Erstellung angezeigt. Nutzer kann Logteile
abwählen. Eine Funktion „Lokale PS4-Moduldaten löschen" entfernt Cache
und Datenbank nach Bestätigung, lässt exportierte Backups auf Wunsch
bestehen.

::: {style="page-break-before: always;"}
:::

# 93. Migration der bisherigen CMD

Die vorhandene `HESPERIA_PS4_GoldHEN_Toolkit.cmd` bleibt zunächst als
Legacy-Prototyp. Das neue Modul kann dessen Downloadordner einmalig
importieren. Importierte Dateien werden gehasht, Provider soweit möglich
erkannt und ansonsten als `local-legacy` markiert.

Nach erfolgreicher Migration soll die UI erklären, dass die CMD nicht
mehr benötigt wird. Sie wird nicht automatisch gelöscht. Dadurch bleibt
der Übergang reversibel.

::: {style="page-break-before: always;"}
:::

# 94. Entwicklungsphasen

**Phase A -- Fundament:** Modulregistrierung, Models, SQLite, Logging,
Settings, Provider-Interface.\
**Phase B -- Katalog:** Cheats, Patches, Plugins, Matching, Cache.\
**Phase C -- Konsole:** Verbindung, Inventar, FTP, Capability
Detection.\
**Phase D -- Sicherheit:** Backup, Restore, Dry-Run, Hashing, Manifest.\
**Phase E -- UX:** Spieleansicht, Detailseiten, Suche, Filter, Status.\
**Phase F -- Customizing:** Itemzflow, Theme Creator,
Wallpaper/Musik/Fonts.\
**Phase G -- USB:** Profile, Verifikation, Installationsanleitung.\
**Phase H -- Diagnose:** Supportbundle, Safe Mode, Recovery.\
**Phase I -- Hardening:** Security Tests, Performance, Accessibility.\
**Phase J -- Integration:** Deep Links, HESPERIA Update/Navigation,
Dokumentation.

Jede Phase muss einzeln lauffähig sein. Keine Phase darf voraussetzen,
dass spätere Funktionen bereits existieren.

::: {style="page-break-before: always;"}
:::

# 95. Codex-Aufträge -- konkrete Reihenfolge

### Auftrag 01

Analysiere den aktuellen Repository-Zustand, implementiere Arbeitspaket
1 gemäß dieser Spezifikation, ändere nur notwendige Dateien, ergänze
Tests und Dokumentation, führe Build/Test aus und liefere am Ende eine
kurze Liste geänderter Dateien, Entscheidungen, offener Risiken und des
nächsten sinnvollen Schritts. Keine Attrappen als „fertig" markieren.
\### Auftrag 02 Analysiere den aktuellen Repository-Zustand,
implementiere Arbeitspaket 2 gemäß dieser Spezifikation, ändere nur
notwendige Dateien, ergänze Tests und Dokumentation, führe Build/Test
aus und liefere am Ende eine kurze Liste geänderter Dateien,
Entscheidungen, offener Risiken und des nächsten sinnvollen Schritts.
Keine Attrappen als „fertig" markieren. \### Auftrag 03 Analysiere den
aktuellen Repository-Zustand, implementiere Arbeitspaket 3 gemäß dieser
Spezifikation, ändere nur notwendige Dateien, ergänze Tests und
Dokumentation, führe Build/Test aus und liefere am Ende eine kurze Liste
geänderter Dateien, Entscheidungen, offener Risiken und des nächsten
sinnvollen Schritts. Keine Attrappen als „fertig" markieren. \###
Auftrag 04 Analysiere den aktuellen Repository-Zustand, implementiere
Arbeitspaket 4 gemäß dieser Spezifikation, ändere nur notwendige
Dateien, ergänze Tests und Dokumentation, führe Build/Test aus und
liefere am Ende eine kurze Liste geänderter Dateien, Entscheidungen,
offener Risiken und des nächsten sinnvollen Schritts. Keine Attrappen
als „fertig" markieren. \### Auftrag 05 Analysiere den aktuellen
Repository-Zustand, implementiere Arbeitspaket 5 gemäß dieser
Spezifikation, ändere nur notwendige Dateien, ergänze Tests und
Dokumentation, führe Build/Test aus und liefere am Ende eine kurze Liste
geänderter Dateien, Entscheidungen, offener Risiken und des nächsten
sinnvollen Schritts. Keine Attrappen als „fertig" markieren. \###
Auftrag 06 Analysiere den aktuellen Repository-Zustand, implementiere
Arbeitspaket 6 gemäß dieser Spezifikation, ändere nur notwendige
Dateien, ergänze Tests und Dokumentation, führe Build/Test aus und
liefere am Ende eine kurze Liste geänderter Dateien, Entscheidungen,
offener Risiken und des nächsten sinnvollen Schritts. Keine Attrappen
als „fertig" markieren. \### Auftrag 07 Analysiere den aktuellen
Repository-Zustand, implementiere Arbeitspaket 7 gemäß dieser
Spezifikation, ändere nur notwendige Dateien, ergänze Tests und
Dokumentation, führe Build/Test aus und liefere am Ende eine kurze Liste
geänderter Dateien, Entscheidungen, offener Risiken und des nächsten
sinnvollen Schritts. Keine Attrappen als „fertig" markieren. \###
Auftrag 08 Analysiere den aktuellen Repository-Zustand, implementiere
Arbeitspaket 8 gemäß dieser Spezifikation, ändere nur notwendige
Dateien, ergänze Tests und Dokumentation, führe Build/Test aus und
liefere am Ende eine kurze Liste geänderter Dateien, Entscheidungen,
offener Risiken und des nächsten sinnvollen Schritts. Keine Attrappen
als „fertig" markieren. \### Auftrag 09 Analysiere den aktuellen
Repository-Zustand, implementiere Arbeitspaket 9 gemäß dieser
Spezifikation, ändere nur notwendige Dateien, ergänze Tests und
Dokumentation, führe Build/Test aus und liefere am Ende eine kurze Liste
geänderter Dateien, Entscheidungen, offener Risiken und des nächsten
sinnvollen Schritts. Keine Attrappen als „fertig" markieren. \###
Auftrag 10 Analysiere den aktuellen Repository-Zustand, implementiere
Arbeitspaket 10 gemäß dieser Spezifikation, ändere nur notwendige
Dateien, ergänze Tests und Dokumentation, führe Build/Test aus und
liefere am Ende eine kurze Liste geänderter Dateien, Entscheidungen,
offener Risiken und des nächsten sinnvollen Schritts. Keine Attrappen
als „fertig" markieren. \### Auftrag 11 Analysiere den aktuellen
Repository-Zustand, implementiere Arbeitspaket 11 gemäß dieser
Spezifikation, ändere nur notwendige Dateien, ergänze Tests und
Dokumentation, führe Build/Test aus und liefere am Ende eine kurze Liste
geänderter Dateien, Entscheidungen, offener Risiken und des nächsten
sinnvollen Schritts. Keine Attrappen als „fertig" markieren. \###
Auftrag 12 Analysiere den aktuellen Repository-Zustand, implementiere
Arbeitspaket 12 gemäß dieser Spezifikation, ändere nur notwendige
Dateien, ergänze Tests und Dokumentation, führe Build/Test aus und
liefere am Ende eine kurze Liste geänderter Dateien, Entscheidungen,
offener Risiken und des nächsten sinnvollen Schritts. Keine Attrappen
als „fertig" markieren. \### Auftrag 13 Analysiere den aktuellen
Repository-Zustand, implementiere Arbeitspaket 13 gemäß dieser
Spezifikation, ändere nur notwendige Dateien, ergänze Tests und
Dokumentation, führe Build/Test aus und liefere am Ende eine kurze Liste
geänderter Dateien, Entscheidungen, offener Risiken und des nächsten
sinnvollen Schritts. Keine Attrappen als „fertig" markieren. \###
Auftrag 14 Analysiere den aktuellen Repository-Zustand, implementiere
Arbeitspaket 14 gemäß dieser Spezifikation, ändere nur notwendige
Dateien, ergänze Tests und Dokumentation, führe Build/Test aus und
liefere am Ende eine kurze Liste geänderter Dateien, Entscheidungen,
offener Risiken und des nächsten sinnvollen Schritts. Keine Attrappen
als „fertig" markieren. \### Auftrag 15 Analysiere den aktuellen
Repository-Zustand, implementiere Arbeitspaket 15 gemäß dieser
Spezifikation, ändere nur notwendige Dateien, ergänze Tests und
Dokumentation, führe Build/Test aus und liefere am Ende eine kurze Liste
geänderter Dateien, Entscheidungen, offener Risiken und des nächsten
sinnvollen Schritts. Keine Attrappen als „fertig" markieren. \###
Auftrag 16 Analysiere den aktuellen Repository-Zustand, implementiere
Arbeitspaket 16 gemäß dieser Spezifikation, ändere nur notwendige
Dateien, ergänze Tests und Dokumentation, führe Build/Test aus und
liefere am Ende eine kurze Liste geänderter Dateien, Entscheidungen,
offener Risiken und des nächsten sinnvollen Schritts. Keine Attrappen
als „fertig" markieren. \### Auftrag 17 Analysiere den aktuellen
Repository-Zustand, implementiere Arbeitspaket 17 gemäß dieser
Spezifikation, ändere nur notwendige Dateien, ergänze Tests und
Dokumentation, führe Build/Test aus und liefere am Ende eine kurze Liste
geänderter Dateien, Entscheidungen, offener Risiken und des nächsten
sinnvollen Schritts. Keine Attrappen als „fertig" markieren. \###
Auftrag 18 Analysiere den aktuellen Repository-Zustand, implementiere
Arbeitspaket 18 gemäß dieser Spezifikation, ändere nur notwendige
Dateien, ergänze Tests und Dokumentation, führe Build/Test aus und
liefere am Ende eine kurze Liste geänderter Dateien, Entscheidungen,
offener Risiken und des nächsten sinnvollen Schritts. Keine Attrappen
als „fertig" markieren. \### Auftrag 19 Analysiere den aktuellen
Repository-Zustand, implementiere Arbeitspaket 19 gemäß dieser
Spezifikation, ändere nur notwendige Dateien, ergänze Tests und
Dokumentation, führe Build/Test aus und liefere am Ende eine kurze Liste
geänderter Dateien, Entscheidungen, offener Risiken und des nächsten
sinnvollen Schritts. Keine Attrappen als „fertig" markieren. \###
Auftrag 20 Analysiere den aktuellen Repository-Zustand, implementiere
Arbeitspaket 20 gemäß dieser Spezifikation, ändere nur notwendige
Dateien, ergänze Tests und Dokumentation, führe Build/Test aus und
liefere am Ende eine kurze Liste geänderter Dateien, Entscheidungen,
offener Risiken und des nächsten sinnvollen Schritts. Keine Attrappen
als „fertig" markieren. \### Auftrag 21 Analysiere den aktuellen
Repository-Zustand, implementiere Arbeitspaket 21 gemäß dieser
Spezifikation, ändere nur notwendige Dateien, ergänze Tests und
Dokumentation, führe Build/Test aus und liefere am Ende eine kurze Liste
geänderter Dateien, Entscheidungen, offener Risiken und des nächsten
sinnvollen Schritts. Keine Attrappen als „fertig" markieren. \###
Auftrag 22 Analysiere den aktuellen Repository-Zustand, implementiere
Arbeitspaket 22 gemäß dieser Spezifikation, ändere nur notwendige
Dateien, ergänze Tests und Dokumentation, führe Build/Test aus und
liefere am Ende eine kurze Liste geänderter Dateien, Entscheidungen,
offener Risiken und des nächsten sinnvollen Schritts. Keine Attrappen
als „fertig" markieren. \### Auftrag 23 Analysiere den aktuellen
Repository-Zustand, implementiere Arbeitspaket 23 gemäß dieser
Spezifikation, ändere nur notwendige Dateien, ergänze Tests und
Dokumentation, führe Build/Test aus und liefere am Ende eine kurze Liste
geänderter Dateien, Entscheidungen, offener Risiken und des nächsten
sinnvollen Schritts. Keine Attrappen als „fertig" markieren. \###
Auftrag 24 Analysiere den aktuellen Repository-Zustand, implementiere
Arbeitspaket 24 gemäß dieser Spezifikation, ändere nur notwendige
Dateien, ergänze Tests und Dokumentation, führe Build/Test aus und
liefere am Ende eine kurze Liste geänderter Dateien, Entscheidungen,
offener Risiken und des nächsten sinnvollen Schritts. Keine Attrappen
als „fertig" markieren. \### Auftrag 25 Analysiere den aktuellen
Repository-Zustand, implementiere Arbeitspaket 25 gemäß dieser
Spezifikation, ändere nur notwendige Dateien, ergänze Tests und
Dokumentation, führe Build/Test aus und liefere am Ende eine kurze Liste
geänderter Dateien, Entscheidungen, offener Risiken und des nächsten
sinnvollen Schritts. Keine Attrappen als „fertig" markieren. \###
Auftrag 26 Analysiere den aktuellen Repository-Zustand, implementiere
Arbeitspaket 26 gemäß dieser Spezifikation, ändere nur notwendige
Dateien, ergänze Tests und Dokumentation, führe Build/Test aus und
liefere am Ende eine kurze Liste geänderter Dateien, Entscheidungen,
offener Risiken und des nächsten sinnvollen Schritts. Keine Attrappen
als „fertig" markieren. \### Auftrag 27 Analysiere den aktuellen
Repository-Zustand, implementiere Arbeitspaket 27 gemäß dieser
Spezifikation, ändere nur notwendige Dateien, ergänze Tests und
Dokumentation, führe Build/Test aus und liefere am Ende eine kurze Liste
geänderter Dateien, Entscheidungen, offener Risiken und des nächsten
sinnvollen Schritts. Keine Attrappen als „fertig" markieren. \###
Auftrag 28 Analysiere den aktuellen Repository-Zustand, implementiere
Arbeitspaket 28 gemäß dieser Spezifikation, ändere nur notwendige
Dateien, ergänze Tests und Dokumentation, führe Build/Test aus und
liefere am Ende eine kurze Liste geänderter Dateien, Entscheidungen,
offener Risiken und des nächsten sinnvollen Schritts. Keine Attrappen
als „fertig" markieren. \### Auftrag 29 Analysiere den aktuellen
Repository-Zustand, implementiere Arbeitspaket 29 gemäß dieser
Spezifikation, ändere nur notwendige Dateien, ergänze Tests und
Dokumentation, führe Build/Test aus und liefere am Ende eine kurze Liste
geänderter Dateien, Entscheidungen, offener Risiken und des nächsten
sinnvollen Schritts. Keine Attrappen als „fertig" markieren. \###
Auftrag 30 Analysiere den aktuellen Repository-Zustand, implementiere
Arbeitspaket 30 gemäß dieser Spezifikation, ändere nur notwendige
Dateien, ergänze Tests und Dokumentation, führe Build/Test aus und
liefere am Ende eine kurze Liste geänderter Dateien, Entscheidungen,
offener Risiken und des nächsten sinnvollen Schritts. Keine Attrappen
als „fertig" markieren.

::: {style="page-break-before: always;"}
:::

# 96. Definition of Done pro Feature

Ein Feature ist nur fertig, wenn: Implementierung vorhanden; UI
angebunden; Fehlerfälle behandelt; Cancellation unterstützt; Logging
vorhanden; Unit-/Integrationstest passend zur Ebene vorhanden;
Dokumentation aktualisiert; keine hartcodierten lokalen Pfade; keine
ungeprüften externen Shell-Aufrufe; Build grün; bestehende Funktionen
nicht regressieren.

„Button vorhanden" ist keine Fertigstellung. Mockdaten dürfen in
Entwicklungsbuilds existieren, müssen aber sichtbar markiert und vor
Release entfernt oder über einen Demo-Modus isoliert werden.

::: {style="page-break-before: always;"}
:::

# 97. Nicht implementieren / rote Linien

-   Keine automatische Beschaffung kommerzieller Spiele oder DLCs.
-   Keine Lizenz-/Account-Key-Verteilung.
-   Keine Funktion, deren Zweck das unbemerkte Cheaten in
    Online-Multiplayer ist.
-   Keine ungeprüften Systemdatei-Modifikationen.
-   Keine automatische Formatierung eines Datenträgers im
    Standardworkflow.
-   Keine automatische Aktivierung aller Plugins/Patches.
-   Keine Behauptung „kompatibel", wenn CUSA/App-Version nicht
    verifiziert ist.
-   Keine fest verdrahteten Drittanbieter-Downloadlinks, wenn eine
    offizielle Release-/Providerauflösung möglich ist.
-   Keine Secrets in Logs oder Diagnosepaketen.

::: {style="page-break-before: always;"}
:::

# 98. Quellen- und Updatepolitik

Primärquellen haben Vorrang: offizielle GitHub-Repositories der Projekte
und von deren Releases ausdrücklich genannte Bezugsquellen.
Community-Forks können als zusätzliche Provider aufgenommen werden,
müssen aber sichtbar als solche gekennzeichnet sein.

Die Providerliste ist Datenkonfiguration, kein über die gesamte
Codebasis verstreuter URL-Satz. Bei einem Providerwechsel wird zuerst
die Quelle aktualisiert und getestet, nicht die UI.

Stand 17.09.2026 wurden für diese Spezifikation insbesondere GoldHEN,
GoldHEN Cheat Repository, PS4 Cheats Manager, GoldHEN Plugins, die
aktuelle Patch-Repository-Dokumentation und Itemzflow geprüft.

::: {style="page-break-before: always;"}
:::

# 99. Abschlussarchitektur

Das fertige PS4-Modul ist kein „Cheat Downloader mit Extras", sondern
ein **PS4 Homebrew Control Center innerhalb des HESPERIA Tools**. Cheats
sind ein Teil davon. Der eigentliche Wert entsteht durch automatische
Inventarisierung, exaktes Matching, reproduzierbare Quellen, Backups,
sichere Transfers, Diagnose und eine Oberfläche, die die vielen
GoldHEN-Einzelwerkzeuge zusammenführt, ohne deren Herkunft zu
verschleiern.

Die bisherige CMD hat ihren Zweck erfüllt: Sie beweist den Workflow. In
der finalen Architektur wird ihre Funktionalität in Provider,
Downloadservice, USB Builder und UI zerlegt. Dadurch bleibt HESPERIA
langfristig wartbar.

::: {style="page-break-before: always;"}
:::

# 100. Finale Codex-Anweisung

1.  Lies dieses Dokument vollständig und behandle es als
    Zielarchitektur.\
2.  Analysiere zuerst das bestehende HESPERIA-Repository und
    dokumentiere, welche vorhandenen Komponenten wiederverwendet
    werden.\
3.  Erstelle danach einen Implementierungsplan mit Abhängigkeiten und
    beginne unmittelbar mit Phase A.\
4.  Arbeite iterativ; nach jedem Paket Build und Tests.\
5.  Ersetze keine funktionierende HESPERIA-Infrastruktur durch
    Parallelcode ohne begründeten technischen Vorteil.\
6.  Verwende echte Provider und echte Parser; keine dauerhaft
    verbleibenden Mock-Buttons.\
7.  Behalte die Legacy-CMD nur als Migrationsquelle.\
8.  Jede schreibende PS4-Aktion benötigt Vorschau, Backupstrategie und
    nachvollziehbares Log.\
9.  Kompatibilität wird niemals geraten. CUSA und App-Version sind
    zentrale Schlüssel.\
10. Wenn eine externe Quelle ihre Struktur ändert, muss der Fehler lokal
    auf den Provider begrenzt bleiben.\
11. Das PS4-Modul muss auch ohne Internet mit bereits gecachten Daten
    sinnvoll funktionieren.\
12. Am Ende jeder Phase aktualisiere diese technische Dokumentation bzw.
    die daraus abgeleitete Projektdokumentation im Repository.

**Endzustand:** Der Nutzer öffnet HESPERIA → PS4, sieht seine Konsole
und Spiele, erkennt sofort passende Cheats/Patches/Plugins, kann Inhalte
sicher herunterladen, per USB oder Netzwerk bereitstellen, Backups und
Restore durchführen, Itemzflow/Themes verwalten und bei Problemen ein
Diagnosepaket erzeugen. Alle Vorgänge sind nachvollziehbar und
reversibel, soweit die Zielplattform dies zulässt.

::: {style="page-break-before: always;"}
:::

# Anhang A -- 120 End-to-End-Szenarien

## E2E-001

**Ziel:** Repräsentativer End-to-End-Fall für Kombination 1.\
**Vorbedingung:** HESPERIA Tool läuft, PS4-Modul ist initialisiert;
Provider- und Konsolenzustand werden als Fixture definiert.\
**Ablauf:** Modul öffnen → Zustand erfassen → Katalog/Inventar
synchronisieren → Kompatibilität berechnen → geplante Aktion in der
Vorschau prüfen → bei schreibender Aktion Checkpoint anlegen → Aktion
ausführen → Ergebnis verifizieren → Journal und UI aktualisieren.\
**Fehlerinjektion:** Je nach Test Netzwerkabbruch, Versionsabweichung,
voller Datenträger, ungültiges Archiv, Benutzerabbruch oder
Providerfehler einstreuen.\
**Erwartung:** Kein Datenverlust, keine falsche Kompatibilitätsaussage,
keine halb installierte Datei; Fehler bleibt auf betroffene Operation
begrenzt. Vorzustand ist wiederherstellbar oder unverändert.\
**Nachweis:** Assertions für Datenbank, Dateisystem, Action Journal und
sichtbaren UI-Status.

## E2E-002

**Ziel:** Repräsentativer End-to-End-Fall für Kombination 2.\
**Vorbedingung:** HESPERIA Tool läuft, PS4-Modul ist initialisiert;
Provider- und Konsolenzustand werden als Fixture definiert.\
**Ablauf:** Modul öffnen → Zustand erfassen → Katalog/Inventar
synchronisieren → Kompatibilität berechnen → geplante Aktion in der
Vorschau prüfen → bei schreibender Aktion Checkpoint anlegen → Aktion
ausführen → Ergebnis verifizieren → Journal und UI aktualisieren.\
**Fehlerinjektion:** Je nach Test Netzwerkabbruch, Versionsabweichung,
voller Datenträger, ungültiges Archiv, Benutzerabbruch oder
Providerfehler einstreuen.\
**Erwartung:** Kein Datenverlust, keine falsche Kompatibilitätsaussage,
keine halb installierte Datei; Fehler bleibt auf betroffene Operation
begrenzt. Vorzustand ist wiederherstellbar oder unverändert.\
**Nachweis:** Assertions für Datenbank, Dateisystem, Action Journal und
sichtbaren UI-Status.

## E2E-003

**Ziel:** Repräsentativer End-to-End-Fall für Kombination 3.\
**Vorbedingung:** HESPERIA Tool läuft, PS4-Modul ist initialisiert;
Provider- und Konsolenzustand werden als Fixture definiert.\
**Ablauf:** Modul öffnen → Zustand erfassen → Katalog/Inventar
synchronisieren → Kompatibilität berechnen → geplante Aktion in der
Vorschau prüfen → bei schreibender Aktion Checkpoint anlegen → Aktion
ausführen → Ergebnis verifizieren → Journal und UI aktualisieren.\
**Fehlerinjektion:** Je nach Test Netzwerkabbruch, Versionsabweichung,
voller Datenträger, ungültiges Archiv, Benutzerabbruch oder
Providerfehler einstreuen.\
**Erwartung:** Kein Datenverlust, keine falsche Kompatibilitätsaussage,
keine halb installierte Datei; Fehler bleibt auf betroffene Operation
begrenzt. Vorzustand ist wiederherstellbar oder unverändert.\
**Nachweis:** Assertions für Datenbank, Dateisystem, Action Journal und
sichtbaren UI-Status.

## E2E-004

**Ziel:** Repräsentativer End-to-End-Fall für Kombination 4.\
**Vorbedingung:** HESPERIA Tool läuft, PS4-Modul ist initialisiert;
Provider- und Konsolenzustand werden als Fixture definiert.\
**Ablauf:** Modul öffnen → Zustand erfassen → Katalog/Inventar
synchronisieren → Kompatibilität berechnen → geplante Aktion in der
Vorschau prüfen → bei schreibender Aktion Checkpoint anlegen → Aktion
ausführen → Ergebnis verifizieren → Journal und UI aktualisieren.\
**Fehlerinjektion:** Je nach Test Netzwerkabbruch, Versionsabweichung,
voller Datenträger, ungültiges Archiv, Benutzerabbruch oder
Providerfehler einstreuen.\
**Erwartung:** Kein Datenverlust, keine falsche Kompatibilitätsaussage,
keine halb installierte Datei; Fehler bleibt auf betroffene Operation
begrenzt. Vorzustand ist wiederherstellbar oder unverändert.\
**Nachweis:** Assertions für Datenbank, Dateisystem, Action Journal und
sichtbaren UI-Status.

## E2E-005

**Ziel:** Repräsentativer End-to-End-Fall für Kombination 5.\
**Vorbedingung:** HESPERIA Tool läuft, PS4-Modul ist initialisiert;
Provider- und Konsolenzustand werden als Fixture definiert.\
**Ablauf:** Modul öffnen → Zustand erfassen → Katalog/Inventar
synchronisieren → Kompatibilität berechnen → geplante Aktion in der
Vorschau prüfen → bei schreibender Aktion Checkpoint anlegen → Aktion
ausführen → Ergebnis verifizieren → Journal und UI aktualisieren.\
**Fehlerinjektion:** Je nach Test Netzwerkabbruch, Versionsabweichung,
voller Datenträger, ungültiges Archiv, Benutzerabbruch oder
Providerfehler einstreuen.\
**Erwartung:** Kein Datenverlust, keine falsche Kompatibilitätsaussage,
keine halb installierte Datei; Fehler bleibt auf betroffene Operation
begrenzt. Vorzustand ist wiederherstellbar oder unverändert.\
**Nachweis:** Assertions für Datenbank, Dateisystem, Action Journal und
sichtbaren UI-Status.

## E2E-006

**Ziel:** Repräsentativer End-to-End-Fall für Kombination 6.\
**Vorbedingung:** HESPERIA Tool läuft, PS4-Modul ist initialisiert;
Provider- und Konsolenzustand werden als Fixture definiert.\
**Ablauf:** Modul öffnen → Zustand erfassen → Katalog/Inventar
synchronisieren → Kompatibilität berechnen → geplante Aktion in der
Vorschau prüfen → bei schreibender Aktion Checkpoint anlegen → Aktion
ausführen → Ergebnis verifizieren → Journal und UI aktualisieren.\
**Fehlerinjektion:** Je nach Test Netzwerkabbruch, Versionsabweichung,
voller Datenträger, ungültiges Archiv, Benutzerabbruch oder
Providerfehler einstreuen.\
**Erwartung:** Kein Datenverlust, keine falsche Kompatibilitätsaussage,
keine halb installierte Datei; Fehler bleibt auf betroffene Operation
begrenzt. Vorzustand ist wiederherstellbar oder unverändert.\
**Nachweis:** Assertions für Datenbank, Dateisystem, Action Journal und
sichtbaren UI-Status.

## E2E-007

**Ziel:** Repräsentativer End-to-End-Fall für Kombination 7.\
**Vorbedingung:** HESPERIA Tool läuft, PS4-Modul ist initialisiert;
Provider- und Konsolenzustand werden als Fixture definiert.\
**Ablauf:** Modul öffnen → Zustand erfassen → Katalog/Inventar
synchronisieren → Kompatibilität berechnen → geplante Aktion in der
Vorschau prüfen → bei schreibender Aktion Checkpoint anlegen → Aktion
ausführen → Ergebnis verifizieren → Journal und UI aktualisieren.\
**Fehlerinjektion:** Je nach Test Netzwerkabbruch, Versionsabweichung,
voller Datenträger, ungültiges Archiv, Benutzerabbruch oder
Providerfehler einstreuen.\
**Erwartung:** Kein Datenverlust, keine falsche Kompatibilitätsaussage,
keine halb installierte Datei; Fehler bleibt auf betroffene Operation
begrenzt. Vorzustand ist wiederherstellbar oder unverändert.\
**Nachweis:** Assertions für Datenbank, Dateisystem, Action Journal und
sichtbaren UI-Status.

## E2E-008

**Ziel:** Repräsentativer End-to-End-Fall für Kombination 8.\
**Vorbedingung:** HESPERIA Tool läuft, PS4-Modul ist initialisiert;
Provider- und Konsolenzustand werden als Fixture definiert.\
**Ablauf:** Modul öffnen → Zustand erfassen → Katalog/Inventar
synchronisieren → Kompatibilität berechnen → geplante Aktion in der
Vorschau prüfen → bei schreibender Aktion Checkpoint anlegen → Aktion
ausführen → Ergebnis verifizieren → Journal und UI aktualisieren.\
**Fehlerinjektion:** Je nach Test Netzwerkabbruch, Versionsabweichung,
voller Datenträger, ungültiges Archiv, Benutzerabbruch oder
Providerfehler einstreuen.\
**Erwartung:** Kein Datenverlust, keine falsche Kompatibilitätsaussage,
keine halb installierte Datei; Fehler bleibt auf betroffene Operation
begrenzt. Vorzustand ist wiederherstellbar oder unverändert.\
**Nachweis:** Assertions für Datenbank, Dateisystem, Action Journal und
sichtbaren UI-Status.

## E2E-009

**Ziel:** Repräsentativer End-to-End-Fall für Kombination 9.\
**Vorbedingung:** HESPERIA Tool läuft, PS4-Modul ist initialisiert;
Provider- und Konsolenzustand werden als Fixture definiert.\
**Ablauf:** Modul öffnen → Zustand erfassen → Katalog/Inventar
synchronisieren → Kompatibilität berechnen → geplante Aktion in der
Vorschau prüfen → bei schreibender Aktion Checkpoint anlegen → Aktion
ausführen → Ergebnis verifizieren → Journal und UI aktualisieren.\
**Fehlerinjektion:** Je nach Test Netzwerkabbruch, Versionsabweichung,
voller Datenträger, ungültiges Archiv, Benutzerabbruch oder
Providerfehler einstreuen.\
**Erwartung:** Kein Datenverlust, keine falsche Kompatibilitätsaussage,
keine halb installierte Datei; Fehler bleibt auf betroffene Operation
begrenzt. Vorzustand ist wiederherstellbar oder unverändert.\
**Nachweis:** Assertions für Datenbank, Dateisystem, Action Journal und
sichtbaren UI-Status.

## E2E-010

**Ziel:** Repräsentativer End-to-End-Fall für Kombination 10.\
**Vorbedingung:** HESPERIA Tool läuft, PS4-Modul ist initialisiert;
Provider- und Konsolenzustand werden als Fixture definiert.\
**Ablauf:** Modul öffnen → Zustand erfassen → Katalog/Inventar
synchronisieren → Kompatibilität berechnen → geplante Aktion in der
Vorschau prüfen → bei schreibender Aktion Checkpoint anlegen → Aktion
ausführen → Ergebnis verifizieren → Journal und UI aktualisieren.\
**Fehlerinjektion:** Je nach Test Netzwerkabbruch, Versionsabweichung,
voller Datenträger, ungültiges Archiv, Benutzerabbruch oder
Providerfehler einstreuen.\
**Erwartung:** Kein Datenverlust, keine falsche Kompatibilitätsaussage,
keine halb installierte Datei; Fehler bleibt auf betroffene Operation
begrenzt. Vorzustand ist wiederherstellbar oder unverändert.\
**Nachweis:** Assertions für Datenbank, Dateisystem, Action Journal und
sichtbaren UI-Status.

## E2E-011

**Ziel:** Repräsentativer End-to-End-Fall für Kombination 11.\
**Vorbedingung:** HESPERIA Tool läuft, PS4-Modul ist initialisiert;
Provider- und Konsolenzustand werden als Fixture definiert.\
**Ablauf:** Modul öffnen → Zustand erfassen → Katalog/Inventar
synchronisieren → Kompatibilität berechnen → geplante Aktion in der
Vorschau prüfen → bei schreibender Aktion Checkpoint anlegen → Aktion
ausführen → Ergebnis verifizieren → Journal und UI aktualisieren.\
**Fehlerinjektion:** Je nach Test Netzwerkabbruch, Versionsabweichung,
voller Datenträger, ungültiges Archiv, Benutzerabbruch oder
Providerfehler einstreuen.\
**Erwartung:** Kein Datenverlust, keine falsche Kompatibilitätsaussage,
keine halb installierte Datei; Fehler bleibt auf betroffene Operation
begrenzt. Vorzustand ist wiederherstellbar oder unverändert.\
**Nachweis:** Assertions für Datenbank, Dateisystem, Action Journal und
sichtbaren UI-Status.

## E2E-012

**Ziel:** Repräsentativer End-to-End-Fall für Kombination 12.\
**Vorbedingung:** HESPERIA Tool läuft, PS4-Modul ist initialisiert;
Provider- und Konsolenzustand werden als Fixture definiert.\
**Ablauf:** Modul öffnen → Zustand erfassen → Katalog/Inventar
synchronisieren → Kompatibilität berechnen → geplante Aktion in der
Vorschau prüfen → bei schreibender Aktion Checkpoint anlegen → Aktion
ausführen → Ergebnis verifizieren → Journal und UI aktualisieren.\
**Fehlerinjektion:** Je nach Test Netzwerkabbruch, Versionsabweichung,
voller Datenträger, ungültiges Archiv, Benutzerabbruch oder
Providerfehler einstreuen.\
**Erwartung:** Kein Datenverlust, keine falsche Kompatibilitätsaussage,
keine halb installierte Datei; Fehler bleibt auf betroffene Operation
begrenzt. Vorzustand ist wiederherstellbar oder unverändert.\
**Nachweis:** Assertions für Datenbank, Dateisystem, Action Journal und
sichtbaren UI-Status.

## E2E-013

**Ziel:** Repräsentativer End-to-End-Fall für Kombination 13.\
**Vorbedingung:** HESPERIA Tool läuft, PS4-Modul ist initialisiert;
Provider- und Konsolenzustand werden als Fixture definiert.\
**Ablauf:** Modul öffnen → Zustand erfassen → Katalog/Inventar
synchronisieren → Kompatibilität berechnen → geplante Aktion in der
Vorschau prüfen → bei schreibender Aktion Checkpoint anlegen → Aktion
ausführen → Ergebnis verifizieren → Journal und UI aktualisieren.\
**Fehlerinjektion:** Je nach Test Netzwerkabbruch, Versionsabweichung,
voller Datenträger, ungültiges Archiv, Benutzerabbruch oder
Providerfehler einstreuen.\
**Erwartung:** Kein Datenverlust, keine falsche Kompatibilitätsaussage,
keine halb installierte Datei; Fehler bleibt auf betroffene Operation
begrenzt. Vorzustand ist wiederherstellbar oder unverändert.\
**Nachweis:** Assertions für Datenbank, Dateisystem, Action Journal und
sichtbaren UI-Status.

## E2E-014

**Ziel:** Repräsentativer End-to-End-Fall für Kombination 14.\
**Vorbedingung:** HESPERIA Tool läuft, PS4-Modul ist initialisiert;
Provider- und Konsolenzustand werden als Fixture definiert.\
**Ablauf:** Modul öffnen → Zustand erfassen → Katalog/Inventar
synchronisieren → Kompatibilität berechnen → geplante Aktion in der
Vorschau prüfen → bei schreibender Aktion Checkpoint anlegen → Aktion
ausführen → Ergebnis verifizieren → Journal und UI aktualisieren.\
**Fehlerinjektion:** Je nach Test Netzwerkabbruch, Versionsabweichung,
voller Datenträger, ungültiges Archiv, Benutzerabbruch oder
Providerfehler einstreuen.\
**Erwartung:** Kein Datenverlust, keine falsche Kompatibilitätsaussage,
keine halb installierte Datei; Fehler bleibt auf betroffene Operation
begrenzt. Vorzustand ist wiederherstellbar oder unverändert.\
**Nachweis:** Assertions für Datenbank, Dateisystem, Action Journal und
sichtbaren UI-Status.

## E2E-015

**Ziel:** Repräsentativer End-to-End-Fall für Kombination 15.\
**Vorbedingung:** HESPERIA Tool läuft, PS4-Modul ist initialisiert;
Provider- und Konsolenzustand werden als Fixture definiert.\
**Ablauf:** Modul öffnen → Zustand erfassen → Katalog/Inventar
synchronisieren → Kompatibilität berechnen → geplante Aktion in der
Vorschau prüfen → bei schreibender Aktion Checkpoint anlegen → Aktion
ausführen → Ergebnis verifizieren → Journal und UI aktualisieren.\
**Fehlerinjektion:** Je nach Test Netzwerkabbruch, Versionsabweichung,
voller Datenträger, ungültiges Archiv, Benutzerabbruch oder
Providerfehler einstreuen.\
**Erwartung:** Kein Datenverlust, keine falsche Kompatibilitätsaussage,
keine halb installierte Datei; Fehler bleibt auf betroffene Operation
begrenzt. Vorzustand ist wiederherstellbar oder unverändert.\
**Nachweis:** Assertions für Datenbank, Dateisystem, Action Journal und
sichtbaren UI-Status.

## E2E-016

**Ziel:** Repräsentativer End-to-End-Fall für Kombination 16.\
**Vorbedingung:** HESPERIA Tool läuft, PS4-Modul ist initialisiert;
Provider- und Konsolenzustand werden als Fixture definiert.\
**Ablauf:** Modul öffnen → Zustand erfassen → Katalog/Inventar
synchronisieren → Kompatibilität berechnen → geplante Aktion in der
Vorschau prüfen → bei schreibender Aktion Checkpoint anlegen → Aktion
ausführen → Ergebnis verifizieren → Journal und UI aktualisieren.\
**Fehlerinjektion:** Je nach Test Netzwerkabbruch, Versionsabweichung,
voller Datenträger, ungültiges Archiv, Benutzerabbruch oder
Providerfehler einstreuen.\
**Erwartung:** Kein Datenverlust, keine falsche Kompatibilitätsaussage,
keine halb installierte Datei; Fehler bleibt auf betroffene Operation
begrenzt. Vorzustand ist wiederherstellbar oder unverändert.\
**Nachweis:** Assertions für Datenbank, Dateisystem, Action Journal und
sichtbaren UI-Status.

## E2E-017

**Ziel:** Repräsentativer End-to-End-Fall für Kombination 17.\
**Vorbedingung:** HESPERIA Tool läuft, PS4-Modul ist initialisiert;
Provider- und Konsolenzustand werden als Fixture definiert.\
**Ablauf:** Modul öffnen → Zustand erfassen → Katalog/Inventar
synchronisieren → Kompatibilität berechnen → geplante Aktion in der
Vorschau prüfen → bei schreibender Aktion Checkpoint anlegen → Aktion
ausführen → Ergebnis verifizieren → Journal und UI aktualisieren.\
**Fehlerinjektion:** Je nach Test Netzwerkabbruch, Versionsabweichung,
voller Datenträger, ungültiges Archiv, Benutzerabbruch oder
Providerfehler einstreuen.\
**Erwartung:** Kein Datenverlust, keine falsche Kompatibilitätsaussage,
keine halb installierte Datei; Fehler bleibt auf betroffene Operation
begrenzt. Vorzustand ist wiederherstellbar oder unverändert.\
**Nachweis:** Assertions für Datenbank, Dateisystem, Action Journal und
sichtbaren UI-Status.

## E2E-018

**Ziel:** Repräsentativer End-to-End-Fall für Kombination 18.\
**Vorbedingung:** HESPERIA Tool läuft, PS4-Modul ist initialisiert;
Provider- und Konsolenzustand werden als Fixture definiert.\
**Ablauf:** Modul öffnen → Zustand erfassen → Katalog/Inventar
synchronisieren → Kompatibilität berechnen → geplante Aktion in der
Vorschau prüfen → bei schreibender Aktion Checkpoint anlegen → Aktion
ausführen → Ergebnis verifizieren → Journal und UI aktualisieren.\
**Fehlerinjektion:** Je nach Test Netzwerkabbruch, Versionsabweichung,
voller Datenträger, ungültiges Archiv, Benutzerabbruch oder
Providerfehler einstreuen.\
**Erwartung:** Kein Datenverlust, keine falsche Kompatibilitätsaussage,
keine halb installierte Datei; Fehler bleibt auf betroffene Operation
begrenzt. Vorzustand ist wiederherstellbar oder unverändert.\
**Nachweis:** Assertions für Datenbank, Dateisystem, Action Journal und
sichtbaren UI-Status.

## E2E-019

**Ziel:** Repräsentativer End-to-End-Fall für Kombination 19.\
**Vorbedingung:** HESPERIA Tool läuft, PS4-Modul ist initialisiert;
Provider- und Konsolenzustand werden als Fixture definiert.\
**Ablauf:** Modul öffnen → Zustand erfassen → Katalog/Inventar
synchronisieren → Kompatibilität berechnen → geplante Aktion in der
Vorschau prüfen → bei schreibender Aktion Checkpoint anlegen → Aktion
ausführen → Ergebnis verifizieren → Journal und UI aktualisieren.\
**Fehlerinjektion:** Je nach Test Netzwerkabbruch, Versionsabweichung,
voller Datenträger, ungültiges Archiv, Benutzerabbruch oder
Providerfehler einstreuen.\
**Erwartung:** Kein Datenverlust, keine falsche Kompatibilitätsaussage,
keine halb installierte Datei; Fehler bleibt auf betroffene Operation
begrenzt. Vorzustand ist wiederherstellbar oder unverändert.\
**Nachweis:** Assertions für Datenbank, Dateisystem, Action Journal und
sichtbaren UI-Status.

## E2E-020

**Ziel:** Repräsentativer End-to-End-Fall für Kombination 20.\
**Vorbedingung:** HESPERIA Tool läuft, PS4-Modul ist initialisiert;
Provider- und Konsolenzustand werden als Fixture definiert.\
**Ablauf:** Modul öffnen → Zustand erfassen → Katalog/Inventar
synchronisieren → Kompatibilität berechnen → geplante Aktion in der
Vorschau prüfen → bei schreibender Aktion Checkpoint anlegen → Aktion
ausführen → Ergebnis verifizieren → Journal und UI aktualisieren.\
**Fehlerinjektion:** Je nach Test Netzwerkabbruch, Versionsabweichung,
voller Datenträger, ungültiges Archiv, Benutzerabbruch oder
Providerfehler einstreuen.\
**Erwartung:** Kein Datenverlust, keine falsche Kompatibilitätsaussage,
keine halb installierte Datei; Fehler bleibt auf betroffene Operation
begrenzt. Vorzustand ist wiederherstellbar oder unverändert.\
**Nachweis:** Assertions für Datenbank, Dateisystem, Action Journal und
sichtbaren UI-Status.

## E2E-021

**Ziel:** Repräsentativer End-to-End-Fall für Kombination 21.\
**Vorbedingung:** HESPERIA Tool läuft, PS4-Modul ist initialisiert;
Provider- und Konsolenzustand werden als Fixture definiert.\
**Ablauf:** Modul öffnen → Zustand erfassen → Katalog/Inventar
synchronisieren → Kompatibilität berechnen → geplante Aktion in der
Vorschau prüfen → bei schreibender Aktion Checkpoint anlegen → Aktion
ausführen → Ergebnis verifizieren → Journal und UI aktualisieren.\
**Fehlerinjektion:** Je nach Test Netzwerkabbruch, Versionsabweichung,
voller Datenträger, ungültiges Archiv, Benutzerabbruch oder
Providerfehler einstreuen.\
**Erwartung:** Kein Datenverlust, keine falsche Kompatibilitätsaussage,
keine halb installierte Datei; Fehler bleibt auf betroffene Operation
begrenzt. Vorzustand ist wiederherstellbar oder unverändert.\
**Nachweis:** Assertions für Datenbank, Dateisystem, Action Journal und
sichtbaren UI-Status.

## E2E-022

**Ziel:** Repräsentativer End-to-End-Fall für Kombination 22.\
**Vorbedingung:** HESPERIA Tool läuft, PS4-Modul ist initialisiert;
Provider- und Konsolenzustand werden als Fixture definiert.\
**Ablauf:** Modul öffnen → Zustand erfassen → Katalog/Inventar
synchronisieren → Kompatibilität berechnen → geplante Aktion in der
Vorschau prüfen → bei schreibender Aktion Checkpoint anlegen → Aktion
ausführen → Ergebnis verifizieren → Journal und UI aktualisieren.\
**Fehlerinjektion:** Je nach Test Netzwerkabbruch, Versionsabweichung,
voller Datenträger, ungültiges Archiv, Benutzerabbruch oder
Providerfehler einstreuen.\
**Erwartung:** Kein Datenverlust, keine falsche Kompatibilitätsaussage,
keine halb installierte Datei; Fehler bleibt auf betroffene Operation
begrenzt. Vorzustand ist wiederherstellbar oder unverändert.\
**Nachweis:** Assertions für Datenbank, Dateisystem, Action Journal und
sichtbaren UI-Status.

## E2E-023

**Ziel:** Repräsentativer End-to-End-Fall für Kombination 23.\
**Vorbedingung:** HESPERIA Tool läuft, PS4-Modul ist initialisiert;
Provider- und Konsolenzustand werden als Fixture definiert.\
**Ablauf:** Modul öffnen → Zustand erfassen → Katalog/Inventar
synchronisieren → Kompatibilität berechnen → geplante Aktion in der
Vorschau prüfen → bei schreibender Aktion Checkpoint anlegen → Aktion
ausführen → Ergebnis verifizieren → Journal und UI aktualisieren.\
**Fehlerinjektion:** Je nach Test Netzwerkabbruch, Versionsabweichung,
voller Datenträger, ungültiges Archiv, Benutzerabbruch oder
Providerfehler einstreuen.\
**Erwartung:** Kein Datenverlust, keine falsche Kompatibilitätsaussage,
keine halb installierte Datei; Fehler bleibt auf betroffene Operation
begrenzt. Vorzustand ist wiederherstellbar oder unverändert.\
**Nachweis:** Assertions für Datenbank, Dateisystem, Action Journal und
sichtbaren UI-Status.

## E2E-024

**Ziel:** Repräsentativer End-to-End-Fall für Kombination 24.\
**Vorbedingung:** HESPERIA Tool läuft, PS4-Modul ist initialisiert;
Provider- und Konsolenzustand werden als Fixture definiert.\
**Ablauf:** Modul öffnen → Zustand erfassen → Katalog/Inventar
synchronisieren → Kompatibilität berechnen → geplante Aktion in der
Vorschau prüfen → bei schreibender Aktion Checkpoint anlegen → Aktion
ausführen → Ergebnis verifizieren → Journal und UI aktualisieren.\
**Fehlerinjektion:** Je nach Test Netzwerkabbruch, Versionsabweichung,
voller Datenträger, ungültiges Archiv, Benutzerabbruch oder
Providerfehler einstreuen.\
**Erwartung:** Kein Datenverlust, keine falsche Kompatibilitätsaussage,
keine halb installierte Datei; Fehler bleibt auf betroffene Operation
begrenzt. Vorzustand ist wiederherstellbar oder unverändert.\
**Nachweis:** Assertions für Datenbank, Dateisystem, Action Journal und
sichtbaren UI-Status.

## E2E-025

**Ziel:** Repräsentativer End-to-End-Fall für Kombination 25.\
**Vorbedingung:** HESPERIA Tool läuft, PS4-Modul ist initialisiert;
Provider- und Konsolenzustand werden als Fixture definiert.\
**Ablauf:** Modul öffnen → Zustand erfassen → Katalog/Inventar
synchronisieren → Kompatibilität berechnen → geplante Aktion in der
Vorschau prüfen → bei schreibender Aktion Checkpoint anlegen → Aktion
ausführen → Ergebnis verifizieren → Journal und UI aktualisieren.\
**Fehlerinjektion:** Je nach Test Netzwerkabbruch, Versionsabweichung,
voller Datenträger, ungültiges Archiv, Benutzerabbruch oder
Providerfehler einstreuen.\
**Erwartung:** Kein Datenverlust, keine falsche Kompatibilitätsaussage,
keine halb installierte Datei; Fehler bleibt auf betroffene Operation
begrenzt. Vorzustand ist wiederherstellbar oder unverändert.\
**Nachweis:** Assertions für Datenbank, Dateisystem, Action Journal und
sichtbaren UI-Status.

## E2E-026

**Ziel:** Repräsentativer End-to-End-Fall für Kombination 26.\
**Vorbedingung:** HESPERIA Tool läuft, PS4-Modul ist initialisiert;
Provider- und Konsolenzustand werden als Fixture definiert.\
**Ablauf:** Modul öffnen → Zustand erfassen → Katalog/Inventar
synchronisieren → Kompatibilität berechnen → geplante Aktion in der
Vorschau prüfen → bei schreibender Aktion Checkpoint anlegen → Aktion
ausführen → Ergebnis verifizieren → Journal und UI aktualisieren.\
**Fehlerinjektion:** Je nach Test Netzwerkabbruch, Versionsabweichung,
voller Datenträger, ungültiges Archiv, Benutzerabbruch oder
Providerfehler einstreuen.\
**Erwartung:** Kein Datenverlust, keine falsche Kompatibilitätsaussage,
keine halb installierte Datei; Fehler bleibt auf betroffene Operation
begrenzt. Vorzustand ist wiederherstellbar oder unverändert.\
**Nachweis:** Assertions für Datenbank, Dateisystem, Action Journal und
sichtbaren UI-Status.

## E2E-027

**Ziel:** Repräsentativer End-to-End-Fall für Kombination 27.\
**Vorbedingung:** HESPERIA Tool läuft, PS4-Modul ist initialisiert;
Provider- und Konsolenzustand werden als Fixture definiert.\
**Ablauf:** Modul öffnen → Zustand erfassen → Katalog/Inventar
synchronisieren → Kompatibilität berechnen → geplante Aktion in der
Vorschau prüfen → bei schreibender Aktion Checkpoint anlegen → Aktion
ausführen → Ergebnis verifizieren → Journal und UI aktualisieren.\
**Fehlerinjektion:** Je nach Test Netzwerkabbruch, Versionsabweichung,
voller Datenträger, ungültiges Archiv, Benutzerabbruch oder
Providerfehler einstreuen.\
**Erwartung:** Kein Datenverlust, keine falsche Kompatibilitätsaussage,
keine halb installierte Datei; Fehler bleibt auf betroffene Operation
begrenzt. Vorzustand ist wiederherstellbar oder unverändert.\
**Nachweis:** Assertions für Datenbank, Dateisystem, Action Journal und
sichtbaren UI-Status.

## E2E-028

**Ziel:** Repräsentativer End-to-End-Fall für Kombination 28.\
**Vorbedingung:** HESPERIA Tool läuft, PS4-Modul ist initialisiert;
Provider- und Konsolenzustand werden als Fixture definiert.\
**Ablauf:** Modul öffnen → Zustand erfassen → Katalog/Inventar
synchronisieren → Kompatibilität berechnen → geplante Aktion in der
Vorschau prüfen → bei schreibender Aktion Checkpoint anlegen → Aktion
ausführen → Ergebnis verifizieren → Journal und UI aktualisieren.\
**Fehlerinjektion:** Je nach Test Netzwerkabbruch, Versionsabweichung,
voller Datenträger, ungültiges Archiv, Benutzerabbruch oder
Providerfehler einstreuen.\
**Erwartung:** Kein Datenverlust, keine falsche Kompatibilitätsaussage,
keine halb installierte Datei; Fehler bleibt auf betroffene Operation
begrenzt. Vorzustand ist wiederherstellbar oder unverändert.\
**Nachweis:** Assertions für Datenbank, Dateisystem, Action Journal und
sichtbaren UI-Status.

## E2E-029

**Ziel:** Repräsentativer End-to-End-Fall für Kombination 29.\
**Vorbedingung:** HESPERIA Tool läuft, PS4-Modul ist initialisiert;
Provider- und Konsolenzustand werden als Fixture definiert.\
**Ablauf:** Modul öffnen → Zustand erfassen → Katalog/Inventar
synchronisieren → Kompatibilität berechnen → geplante Aktion in der
Vorschau prüfen → bei schreibender Aktion Checkpoint anlegen → Aktion
ausführen → Ergebnis verifizieren → Journal und UI aktualisieren.\
**Fehlerinjektion:** Je nach Test Netzwerkabbruch, Versionsabweichung,
voller Datenträger, ungültiges Archiv, Benutzerabbruch oder
Providerfehler einstreuen.\
**Erwartung:** Kein Datenverlust, keine falsche Kompatibilitätsaussage,
keine halb installierte Datei; Fehler bleibt auf betroffene Operation
begrenzt. Vorzustand ist wiederherstellbar oder unverändert.\
**Nachweis:** Assertions für Datenbank, Dateisystem, Action Journal und
sichtbaren UI-Status.

## E2E-030

**Ziel:** Repräsentativer End-to-End-Fall für Kombination 30.\
**Vorbedingung:** HESPERIA Tool läuft, PS4-Modul ist initialisiert;
Provider- und Konsolenzustand werden als Fixture definiert.\
**Ablauf:** Modul öffnen → Zustand erfassen → Katalog/Inventar
synchronisieren → Kompatibilität berechnen → geplante Aktion in der
Vorschau prüfen → bei schreibender Aktion Checkpoint anlegen → Aktion
ausführen → Ergebnis verifizieren → Journal und UI aktualisieren.\
**Fehlerinjektion:** Je nach Test Netzwerkabbruch, Versionsabweichung,
voller Datenträger, ungültiges Archiv, Benutzerabbruch oder
Providerfehler einstreuen.\
**Erwartung:** Kein Datenverlust, keine falsche Kompatibilitätsaussage,
keine halb installierte Datei; Fehler bleibt auf betroffene Operation
begrenzt. Vorzustand ist wiederherstellbar oder unverändert.\
**Nachweis:** Assertions für Datenbank, Dateisystem, Action Journal und
sichtbaren UI-Status.

## E2E-031

**Ziel:** Repräsentativer End-to-End-Fall für Kombination 31.\
**Vorbedingung:** HESPERIA Tool läuft, PS4-Modul ist initialisiert;
Provider- und Konsolenzustand werden als Fixture definiert.\
**Ablauf:** Modul öffnen → Zustand erfassen → Katalog/Inventar
synchronisieren → Kompatibilität berechnen → geplante Aktion in der
Vorschau prüfen → bei schreibender Aktion Checkpoint anlegen → Aktion
ausführen → Ergebnis verifizieren → Journal und UI aktualisieren.\
**Fehlerinjektion:** Je nach Test Netzwerkabbruch, Versionsabweichung,
voller Datenträger, ungültiges Archiv, Benutzerabbruch oder
Providerfehler einstreuen.\
**Erwartung:** Kein Datenverlust, keine falsche Kompatibilitätsaussage,
keine halb installierte Datei; Fehler bleibt auf betroffene Operation
begrenzt. Vorzustand ist wiederherstellbar oder unverändert.\
**Nachweis:** Assertions für Datenbank, Dateisystem, Action Journal und
sichtbaren UI-Status.

## E2E-032

**Ziel:** Repräsentativer End-to-End-Fall für Kombination 32.\
**Vorbedingung:** HESPERIA Tool läuft, PS4-Modul ist initialisiert;
Provider- und Konsolenzustand werden als Fixture definiert.\
**Ablauf:** Modul öffnen → Zustand erfassen → Katalog/Inventar
synchronisieren → Kompatibilität berechnen → geplante Aktion in der
Vorschau prüfen → bei schreibender Aktion Checkpoint anlegen → Aktion
ausführen → Ergebnis verifizieren → Journal und UI aktualisieren.\
**Fehlerinjektion:** Je nach Test Netzwerkabbruch, Versionsabweichung,
voller Datenträger, ungültiges Archiv, Benutzerabbruch oder
Providerfehler einstreuen.\
**Erwartung:** Kein Datenverlust, keine falsche Kompatibilitätsaussage,
keine halb installierte Datei; Fehler bleibt auf betroffene Operation
begrenzt. Vorzustand ist wiederherstellbar oder unverändert.\
**Nachweis:** Assertions für Datenbank, Dateisystem, Action Journal und
sichtbaren UI-Status.

## E2E-033

**Ziel:** Repräsentativer End-to-End-Fall für Kombination 33.\
**Vorbedingung:** HESPERIA Tool läuft, PS4-Modul ist initialisiert;
Provider- und Konsolenzustand werden als Fixture definiert.\
**Ablauf:** Modul öffnen → Zustand erfassen → Katalog/Inventar
synchronisieren → Kompatibilität berechnen → geplante Aktion in der
Vorschau prüfen → bei schreibender Aktion Checkpoint anlegen → Aktion
ausführen → Ergebnis verifizieren → Journal und UI aktualisieren.\
**Fehlerinjektion:** Je nach Test Netzwerkabbruch, Versionsabweichung,
voller Datenträger, ungültiges Archiv, Benutzerabbruch oder
Providerfehler einstreuen.\
**Erwartung:** Kein Datenverlust, keine falsche Kompatibilitätsaussage,
keine halb installierte Datei; Fehler bleibt auf betroffene Operation
begrenzt. Vorzustand ist wiederherstellbar oder unverändert.\
**Nachweis:** Assertions für Datenbank, Dateisystem, Action Journal und
sichtbaren UI-Status.

## E2E-034

**Ziel:** Repräsentativer End-to-End-Fall für Kombination 34.\
**Vorbedingung:** HESPERIA Tool läuft, PS4-Modul ist initialisiert;
Provider- und Konsolenzustand werden als Fixture definiert.\
**Ablauf:** Modul öffnen → Zustand erfassen → Katalog/Inventar
synchronisieren → Kompatibilität berechnen → geplante Aktion in der
Vorschau prüfen → bei schreibender Aktion Checkpoint anlegen → Aktion
ausführen → Ergebnis verifizieren → Journal und UI aktualisieren.\
**Fehlerinjektion:** Je nach Test Netzwerkabbruch, Versionsabweichung,
voller Datenträger, ungültiges Archiv, Benutzerabbruch oder
Providerfehler einstreuen.\
**Erwartung:** Kein Datenverlust, keine falsche Kompatibilitätsaussage,
keine halb installierte Datei; Fehler bleibt auf betroffene Operation
begrenzt. Vorzustand ist wiederherstellbar oder unverändert.\
**Nachweis:** Assertions für Datenbank, Dateisystem, Action Journal und
sichtbaren UI-Status.

## E2E-035

**Ziel:** Repräsentativer End-to-End-Fall für Kombination 35.\
**Vorbedingung:** HESPERIA Tool läuft, PS4-Modul ist initialisiert;
Provider- und Konsolenzustand werden als Fixture definiert.\
**Ablauf:** Modul öffnen → Zustand erfassen → Katalog/Inventar
synchronisieren → Kompatibilität berechnen → geplante Aktion in der
Vorschau prüfen → bei schreibender Aktion Checkpoint anlegen → Aktion
ausführen → Ergebnis verifizieren → Journal und UI aktualisieren.\
**Fehlerinjektion:** Je nach Test Netzwerkabbruch, Versionsabweichung,
voller Datenträger, ungültiges Archiv, Benutzerabbruch oder
Providerfehler einstreuen.\
**Erwartung:** Kein Datenverlust, keine falsche Kompatibilitätsaussage,
keine halb installierte Datei; Fehler bleibt auf betroffene Operation
begrenzt. Vorzustand ist wiederherstellbar oder unverändert.\
**Nachweis:** Assertions für Datenbank, Dateisystem, Action Journal und
sichtbaren UI-Status.

## E2E-036

**Ziel:** Repräsentativer End-to-End-Fall für Kombination 36.\
**Vorbedingung:** HESPERIA Tool läuft, PS4-Modul ist initialisiert;
Provider- und Konsolenzustand werden als Fixture definiert.\
**Ablauf:** Modul öffnen → Zustand erfassen → Katalog/Inventar
synchronisieren → Kompatibilität berechnen → geplante Aktion in der
Vorschau prüfen → bei schreibender Aktion Checkpoint anlegen → Aktion
ausführen → Ergebnis verifizieren → Journal und UI aktualisieren.\
**Fehlerinjektion:** Je nach Test Netzwerkabbruch, Versionsabweichung,
voller Datenträger, ungültiges Archiv, Benutzerabbruch oder
Providerfehler einstreuen.\
**Erwartung:** Kein Datenverlust, keine falsche Kompatibilitätsaussage,
keine halb installierte Datei; Fehler bleibt auf betroffene Operation
begrenzt. Vorzustand ist wiederherstellbar oder unverändert.\
**Nachweis:** Assertions für Datenbank, Dateisystem, Action Journal und
sichtbaren UI-Status.

## E2E-037

**Ziel:** Repräsentativer End-to-End-Fall für Kombination 37.\
**Vorbedingung:** HESPERIA Tool läuft, PS4-Modul ist initialisiert;
Provider- und Konsolenzustand werden als Fixture definiert.\
**Ablauf:** Modul öffnen → Zustand erfassen → Katalog/Inventar
synchronisieren → Kompatibilität berechnen → geplante Aktion in der
Vorschau prüfen → bei schreibender Aktion Checkpoint anlegen → Aktion
ausführen → Ergebnis verifizieren → Journal und UI aktualisieren.\
**Fehlerinjektion:** Je nach Test Netzwerkabbruch, Versionsabweichung,
voller Datenträger, ungültiges Archiv, Benutzerabbruch oder
Providerfehler einstreuen.\
**Erwartung:** Kein Datenverlust, keine falsche Kompatibilitätsaussage,
keine halb installierte Datei; Fehler bleibt auf betroffene Operation
begrenzt. Vorzustand ist wiederherstellbar oder unverändert.\
**Nachweis:** Assertions für Datenbank, Dateisystem, Action Journal und
sichtbaren UI-Status.

## E2E-038

**Ziel:** Repräsentativer End-to-End-Fall für Kombination 38.\
**Vorbedingung:** HESPERIA Tool läuft, PS4-Modul ist initialisiert;
Provider- und Konsolenzustand werden als Fixture definiert.\
**Ablauf:** Modul öffnen → Zustand erfassen → Katalog/Inventar
synchronisieren → Kompatibilität berechnen → geplante Aktion in der
Vorschau prüfen → bei schreibender Aktion Checkpoint anlegen → Aktion
ausführen → Ergebnis verifizieren → Journal und UI aktualisieren.\
**Fehlerinjektion:** Je nach Test Netzwerkabbruch, Versionsabweichung,
voller Datenträger, ungültiges Archiv, Benutzerabbruch oder
Providerfehler einstreuen.\
**Erwartung:** Kein Datenverlust, keine falsche Kompatibilitätsaussage,
keine halb installierte Datei; Fehler bleibt auf betroffene Operation
begrenzt. Vorzustand ist wiederherstellbar oder unverändert.\
**Nachweis:** Assertions für Datenbank, Dateisystem, Action Journal und
sichtbaren UI-Status.

## E2E-039

**Ziel:** Repräsentativer End-to-End-Fall für Kombination 39.\
**Vorbedingung:** HESPERIA Tool läuft, PS4-Modul ist initialisiert;
Provider- und Konsolenzustand werden als Fixture definiert.\
**Ablauf:** Modul öffnen → Zustand erfassen → Katalog/Inventar
synchronisieren → Kompatibilität berechnen → geplante Aktion in der
Vorschau prüfen → bei schreibender Aktion Checkpoint anlegen → Aktion
ausführen → Ergebnis verifizieren → Journal und UI aktualisieren.\
**Fehlerinjektion:** Je nach Test Netzwerkabbruch, Versionsabweichung,
voller Datenträger, ungültiges Archiv, Benutzerabbruch oder
Providerfehler einstreuen.\
**Erwartung:** Kein Datenverlust, keine falsche Kompatibilitätsaussage,
keine halb installierte Datei; Fehler bleibt auf betroffene Operation
begrenzt. Vorzustand ist wiederherstellbar oder unverändert.\
**Nachweis:** Assertions für Datenbank, Dateisystem, Action Journal und
sichtbaren UI-Status.

## E2E-040

**Ziel:** Repräsentativer End-to-End-Fall für Kombination 40.\
**Vorbedingung:** HESPERIA Tool läuft, PS4-Modul ist initialisiert;
Provider- und Konsolenzustand werden als Fixture definiert.\
**Ablauf:** Modul öffnen → Zustand erfassen → Katalog/Inventar
synchronisieren → Kompatibilität berechnen → geplante Aktion in der
Vorschau prüfen → bei schreibender Aktion Checkpoint anlegen → Aktion
ausführen → Ergebnis verifizieren → Journal und UI aktualisieren.\
**Fehlerinjektion:** Je nach Test Netzwerkabbruch, Versionsabweichung,
voller Datenträger, ungültiges Archiv, Benutzerabbruch oder
Providerfehler einstreuen.\
**Erwartung:** Kein Datenverlust, keine falsche Kompatibilitätsaussage,
keine halb installierte Datei; Fehler bleibt auf betroffene Operation
begrenzt. Vorzustand ist wiederherstellbar oder unverändert.\
**Nachweis:** Assertions für Datenbank, Dateisystem, Action Journal und
sichtbaren UI-Status.

## E2E-041

**Ziel:** Repräsentativer End-to-End-Fall für Kombination 41.\
**Vorbedingung:** HESPERIA Tool läuft, PS4-Modul ist initialisiert;
Provider- und Konsolenzustand werden als Fixture definiert.\
**Ablauf:** Modul öffnen → Zustand erfassen → Katalog/Inventar
synchronisieren → Kompatibilität berechnen → geplante Aktion in der
Vorschau prüfen → bei schreibender Aktion Checkpoint anlegen → Aktion
ausführen → Ergebnis verifizieren → Journal und UI aktualisieren.\
**Fehlerinjektion:** Je nach Test Netzwerkabbruch, Versionsabweichung,
voller Datenträger, ungültiges Archiv, Benutzerabbruch oder
Providerfehler einstreuen.\
**Erwartung:** Kein Datenverlust, keine falsche Kompatibilitätsaussage,
keine halb installierte Datei; Fehler bleibt auf betroffene Operation
begrenzt. Vorzustand ist wiederherstellbar oder unverändert.\
**Nachweis:** Assertions für Datenbank, Dateisystem, Action Journal und
sichtbaren UI-Status.

## E2E-042

**Ziel:** Repräsentativer End-to-End-Fall für Kombination 42.\
**Vorbedingung:** HESPERIA Tool läuft, PS4-Modul ist initialisiert;
Provider- und Konsolenzustand werden als Fixture definiert.\
**Ablauf:** Modul öffnen → Zustand erfassen → Katalog/Inventar
synchronisieren → Kompatibilität berechnen → geplante Aktion in der
Vorschau prüfen → bei schreibender Aktion Checkpoint anlegen → Aktion
ausführen → Ergebnis verifizieren → Journal und UI aktualisieren.\
**Fehlerinjektion:** Je nach Test Netzwerkabbruch, Versionsabweichung,
voller Datenträger, ungültiges Archiv, Benutzerabbruch oder
Providerfehler einstreuen.\
**Erwartung:** Kein Datenverlust, keine falsche Kompatibilitätsaussage,
keine halb installierte Datei; Fehler bleibt auf betroffene Operation
begrenzt. Vorzustand ist wiederherstellbar oder unverändert.\
**Nachweis:** Assertions für Datenbank, Dateisystem, Action Journal und
sichtbaren UI-Status.

## E2E-043

**Ziel:** Repräsentativer End-to-End-Fall für Kombination 43.\
**Vorbedingung:** HESPERIA Tool läuft, PS4-Modul ist initialisiert;
Provider- und Konsolenzustand werden als Fixture definiert.\
**Ablauf:** Modul öffnen → Zustand erfassen → Katalog/Inventar
synchronisieren → Kompatibilität berechnen → geplante Aktion in der
Vorschau prüfen → bei schreibender Aktion Checkpoint anlegen → Aktion
ausführen → Ergebnis verifizieren → Journal und UI aktualisieren.\
**Fehlerinjektion:** Je nach Test Netzwerkabbruch, Versionsabweichung,
voller Datenträger, ungültiges Archiv, Benutzerabbruch oder
Providerfehler einstreuen.\
**Erwartung:** Kein Datenverlust, keine falsche Kompatibilitätsaussage,
keine halb installierte Datei; Fehler bleibt auf betroffene Operation
begrenzt. Vorzustand ist wiederherstellbar oder unverändert.\
**Nachweis:** Assertions für Datenbank, Dateisystem, Action Journal und
sichtbaren UI-Status.

## E2E-044

**Ziel:** Repräsentativer End-to-End-Fall für Kombination 44.\
**Vorbedingung:** HESPERIA Tool läuft, PS4-Modul ist initialisiert;
Provider- und Konsolenzustand werden als Fixture definiert.\
**Ablauf:** Modul öffnen → Zustand erfassen → Katalog/Inventar
synchronisieren → Kompatibilität berechnen → geplante Aktion in der
Vorschau prüfen → bei schreibender Aktion Checkpoint anlegen → Aktion
ausführen → Ergebnis verifizieren → Journal und UI aktualisieren.\
**Fehlerinjektion:** Je nach Test Netzwerkabbruch, Versionsabweichung,
voller Datenträger, ungültiges Archiv, Benutzerabbruch oder
Providerfehler einstreuen.\
**Erwartung:** Kein Datenverlust, keine falsche Kompatibilitätsaussage,
keine halb installierte Datei; Fehler bleibt auf betroffene Operation
begrenzt. Vorzustand ist wiederherstellbar oder unverändert.\
**Nachweis:** Assertions für Datenbank, Dateisystem, Action Journal und
sichtbaren UI-Status.

## E2E-045

**Ziel:** Repräsentativer End-to-End-Fall für Kombination 45.\
**Vorbedingung:** HESPERIA Tool läuft, PS4-Modul ist initialisiert;
Provider- und Konsolenzustand werden als Fixture definiert.\
**Ablauf:** Modul öffnen → Zustand erfassen → Katalog/Inventar
synchronisieren → Kompatibilität berechnen → geplante Aktion in der
Vorschau prüfen → bei schreibender Aktion Checkpoint anlegen → Aktion
ausführen → Ergebnis verifizieren → Journal und UI aktualisieren.\
**Fehlerinjektion:** Je nach Test Netzwerkabbruch, Versionsabweichung,
voller Datenträger, ungültiges Archiv, Benutzerabbruch oder
Providerfehler einstreuen.\
**Erwartung:** Kein Datenverlust, keine falsche Kompatibilitätsaussage,
keine halb installierte Datei; Fehler bleibt auf betroffene Operation
begrenzt. Vorzustand ist wiederherstellbar oder unverändert.\
**Nachweis:** Assertions für Datenbank, Dateisystem, Action Journal und
sichtbaren UI-Status.

## E2E-046

**Ziel:** Repräsentativer End-to-End-Fall für Kombination 46.\
**Vorbedingung:** HESPERIA Tool läuft, PS4-Modul ist initialisiert;
Provider- und Konsolenzustand werden als Fixture definiert.\
**Ablauf:** Modul öffnen → Zustand erfassen → Katalog/Inventar
synchronisieren → Kompatibilität berechnen → geplante Aktion in der
Vorschau prüfen → bei schreibender Aktion Checkpoint anlegen → Aktion
ausführen → Ergebnis verifizieren → Journal und UI aktualisieren.\
**Fehlerinjektion:** Je nach Test Netzwerkabbruch, Versionsabweichung,
voller Datenträger, ungültiges Archiv, Benutzerabbruch oder
Providerfehler einstreuen.\
**Erwartung:** Kein Datenverlust, keine falsche Kompatibilitätsaussage,
keine halb installierte Datei; Fehler bleibt auf betroffene Operation
begrenzt. Vorzustand ist wiederherstellbar oder unverändert.\
**Nachweis:** Assertions für Datenbank, Dateisystem, Action Journal und
sichtbaren UI-Status.

## E2E-047

**Ziel:** Repräsentativer End-to-End-Fall für Kombination 47.\
**Vorbedingung:** HESPERIA Tool läuft, PS4-Modul ist initialisiert;
Provider- und Konsolenzustand werden als Fixture definiert.\
**Ablauf:** Modul öffnen → Zustand erfassen → Katalog/Inventar
synchronisieren → Kompatibilität berechnen → geplante Aktion in der
Vorschau prüfen → bei schreibender Aktion Checkpoint anlegen → Aktion
ausführen → Ergebnis verifizieren → Journal und UI aktualisieren.\
**Fehlerinjektion:** Je nach Test Netzwerkabbruch, Versionsabweichung,
voller Datenträger, ungültiges Archiv, Benutzerabbruch oder
Providerfehler einstreuen.\
**Erwartung:** Kein Datenverlust, keine falsche Kompatibilitätsaussage,
keine halb installierte Datei; Fehler bleibt auf betroffene Operation
begrenzt. Vorzustand ist wiederherstellbar oder unverändert.\
**Nachweis:** Assertions für Datenbank, Dateisystem, Action Journal und
sichtbaren UI-Status.

## E2E-048

**Ziel:** Repräsentativer End-to-End-Fall für Kombination 48.\
**Vorbedingung:** HESPERIA Tool läuft, PS4-Modul ist initialisiert;
Provider- und Konsolenzustand werden als Fixture definiert.\
**Ablauf:** Modul öffnen → Zustand erfassen → Katalog/Inventar
synchronisieren → Kompatibilität berechnen → geplante Aktion in der
Vorschau prüfen → bei schreibender Aktion Checkpoint anlegen → Aktion
ausführen → Ergebnis verifizieren → Journal und UI aktualisieren.\
**Fehlerinjektion:** Je nach Test Netzwerkabbruch, Versionsabweichung,
voller Datenträger, ungültiges Archiv, Benutzerabbruch oder
Providerfehler einstreuen.\
**Erwartung:** Kein Datenverlust, keine falsche Kompatibilitätsaussage,
keine halb installierte Datei; Fehler bleibt auf betroffene Operation
begrenzt. Vorzustand ist wiederherstellbar oder unverändert.\
**Nachweis:** Assertions für Datenbank, Dateisystem, Action Journal und
sichtbaren UI-Status.

## E2E-049

**Ziel:** Repräsentativer End-to-End-Fall für Kombination 49.\
**Vorbedingung:** HESPERIA Tool läuft, PS4-Modul ist initialisiert;
Provider- und Konsolenzustand werden als Fixture definiert.\
**Ablauf:** Modul öffnen → Zustand erfassen → Katalog/Inventar
synchronisieren → Kompatibilität berechnen → geplante Aktion in der
Vorschau prüfen → bei schreibender Aktion Checkpoint anlegen → Aktion
ausführen → Ergebnis verifizieren → Journal und UI aktualisieren.\
**Fehlerinjektion:** Je nach Test Netzwerkabbruch, Versionsabweichung,
voller Datenträger, ungültiges Archiv, Benutzerabbruch oder
Providerfehler einstreuen.\
**Erwartung:** Kein Datenverlust, keine falsche Kompatibilitätsaussage,
keine halb installierte Datei; Fehler bleibt auf betroffene Operation
begrenzt. Vorzustand ist wiederherstellbar oder unverändert.\
**Nachweis:** Assertions für Datenbank, Dateisystem, Action Journal und
sichtbaren UI-Status.

## E2E-050

**Ziel:** Repräsentativer End-to-End-Fall für Kombination 50.\
**Vorbedingung:** HESPERIA Tool läuft, PS4-Modul ist initialisiert;
Provider- und Konsolenzustand werden als Fixture definiert.\
**Ablauf:** Modul öffnen → Zustand erfassen → Katalog/Inventar
synchronisieren → Kompatibilität berechnen → geplante Aktion in der
Vorschau prüfen → bei schreibender Aktion Checkpoint anlegen → Aktion
ausführen → Ergebnis verifizieren → Journal und UI aktualisieren.\
**Fehlerinjektion:** Je nach Test Netzwerkabbruch, Versionsabweichung,
voller Datenträger, ungültiges Archiv, Benutzerabbruch oder
Providerfehler einstreuen.\
**Erwartung:** Kein Datenverlust, keine falsche Kompatibilitätsaussage,
keine halb installierte Datei; Fehler bleibt auf betroffene Operation
begrenzt. Vorzustand ist wiederherstellbar oder unverändert.\
**Nachweis:** Assertions für Datenbank, Dateisystem, Action Journal und
sichtbaren UI-Status.

## E2E-051

**Ziel:** Repräsentativer End-to-End-Fall für Kombination 51.\
**Vorbedingung:** HESPERIA Tool läuft, PS4-Modul ist initialisiert;
Provider- und Konsolenzustand werden als Fixture definiert.\
**Ablauf:** Modul öffnen → Zustand erfassen → Katalog/Inventar
synchronisieren → Kompatibilität berechnen → geplante Aktion in der
Vorschau prüfen → bei schreibender Aktion Checkpoint anlegen → Aktion
ausführen → Ergebnis verifizieren → Journal und UI aktualisieren.\
**Fehlerinjektion:** Je nach Test Netzwerkabbruch, Versionsabweichung,
voller Datenträger, ungültiges Archiv, Benutzerabbruch oder
Providerfehler einstreuen.\
**Erwartung:** Kein Datenverlust, keine falsche Kompatibilitätsaussage,
keine halb installierte Datei; Fehler bleibt auf betroffene Operation
begrenzt. Vorzustand ist wiederherstellbar oder unverändert.\
**Nachweis:** Assertions für Datenbank, Dateisystem, Action Journal und
sichtbaren UI-Status.

## E2E-052

**Ziel:** Repräsentativer End-to-End-Fall für Kombination 52.\
**Vorbedingung:** HESPERIA Tool läuft, PS4-Modul ist initialisiert;
Provider- und Konsolenzustand werden als Fixture definiert.\
**Ablauf:** Modul öffnen → Zustand erfassen → Katalog/Inventar
synchronisieren → Kompatibilität berechnen → geplante Aktion in der
Vorschau prüfen → bei schreibender Aktion Checkpoint anlegen → Aktion
ausführen → Ergebnis verifizieren → Journal und UI aktualisieren.\
**Fehlerinjektion:** Je nach Test Netzwerkabbruch, Versionsabweichung,
voller Datenträger, ungültiges Archiv, Benutzerabbruch oder
Providerfehler einstreuen.\
**Erwartung:** Kein Datenverlust, keine falsche Kompatibilitätsaussage,
keine halb installierte Datei; Fehler bleibt auf betroffene Operation
begrenzt. Vorzustand ist wiederherstellbar oder unverändert.\
**Nachweis:** Assertions für Datenbank, Dateisystem, Action Journal und
sichtbaren UI-Status.

## E2E-053

**Ziel:** Repräsentativer End-to-End-Fall für Kombination 53.\
**Vorbedingung:** HESPERIA Tool läuft, PS4-Modul ist initialisiert;
Provider- und Konsolenzustand werden als Fixture definiert.\
**Ablauf:** Modul öffnen → Zustand erfassen → Katalog/Inventar
synchronisieren → Kompatibilität berechnen → geplante Aktion in der
Vorschau prüfen → bei schreibender Aktion Checkpoint anlegen → Aktion
ausführen → Ergebnis verifizieren → Journal und UI aktualisieren.\
**Fehlerinjektion:** Je nach Test Netzwerkabbruch, Versionsabweichung,
voller Datenträger, ungültiges Archiv, Benutzerabbruch oder
Providerfehler einstreuen.\
**Erwartung:** Kein Datenverlust, keine falsche Kompatibilitätsaussage,
keine halb installierte Datei; Fehler bleibt auf betroffene Operation
begrenzt. Vorzustand ist wiederherstellbar oder unverändert.\
**Nachweis:** Assertions für Datenbank, Dateisystem, Action Journal und
sichtbaren UI-Status.

## E2E-054

**Ziel:** Repräsentativer End-to-End-Fall für Kombination 54.\
**Vorbedingung:** HESPERIA Tool läuft, PS4-Modul ist initialisiert;
Provider- und Konsolenzustand werden als Fixture definiert.\
**Ablauf:** Modul öffnen → Zustand erfassen → Katalog/Inventar
synchronisieren → Kompatibilität berechnen → geplante Aktion in der
Vorschau prüfen → bei schreibender Aktion Checkpoint anlegen → Aktion
ausführen → Ergebnis verifizieren → Journal und UI aktualisieren.\
**Fehlerinjektion:** Je nach Test Netzwerkabbruch, Versionsabweichung,
voller Datenträger, ungültiges Archiv, Benutzerabbruch oder
Providerfehler einstreuen.\
**Erwartung:** Kein Datenverlust, keine falsche Kompatibilitätsaussage,
keine halb installierte Datei; Fehler bleibt auf betroffene Operation
begrenzt. Vorzustand ist wiederherstellbar oder unverändert.\
**Nachweis:** Assertions für Datenbank, Dateisystem, Action Journal und
sichtbaren UI-Status.

## E2E-055

**Ziel:** Repräsentativer End-to-End-Fall für Kombination 55.\
**Vorbedingung:** HESPERIA Tool läuft, PS4-Modul ist initialisiert;
Provider- und Konsolenzustand werden als Fixture definiert.\
**Ablauf:** Modul öffnen → Zustand erfassen → Katalog/Inventar
synchronisieren → Kompatibilität berechnen → geplante Aktion in der
Vorschau prüfen → bei schreibender Aktion Checkpoint anlegen → Aktion
ausführen → Ergebnis verifizieren → Journal und UI aktualisieren.\
**Fehlerinjektion:** Je nach Test Netzwerkabbruch, Versionsabweichung,
voller Datenträger, ungültiges Archiv, Benutzerabbruch oder
Providerfehler einstreuen.\
**Erwartung:** Kein Datenverlust, keine falsche Kompatibilitätsaussage,
keine halb installierte Datei; Fehler bleibt auf betroffene Operation
begrenzt. Vorzustand ist wiederherstellbar oder unverändert.\
**Nachweis:** Assertions für Datenbank, Dateisystem, Action Journal und
sichtbaren UI-Status.

## E2E-056

**Ziel:** Repräsentativer End-to-End-Fall für Kombination 56.\
**Vorbedingung:** HESPERIA Tool läuft, PS4-Modul ist initialisiert;
Provider- und Konsolenzustand werden als Fixture definiert.\
**Ablauf:** Modul öffnen → Zustand erfassen → Katalog/Inventar
synchronisieren → Kompatibilität berechnen → geplante Aktion in der
Vorschau prüfen → bei schreibender Aktion Checkpoint anlegen → Aktion
ausführen → Ergebnis verifizieren → Journal und UI aktualisieren.\
**Fehlerinjektion:** Je nach Test Netzwerkabbruch, Versionsabweichung,
voller Datenträger, ungültiges Archiv, Benutzerabbruch oder
Providerfehler einstreuen.\
**Erwartung:** Kein Datenverlust, keine falsche Kompatibilitätsaussage,
keine halb installierte Datei; Fehler bleibt auf betroffene Operation
begrenzt. Vorzustand ist wiederherstellbar oder unverändert.\
**Nachweis:** Assertions für Datenbank, Dateisystem, Action Journal und
sichtbaren UI-Status.

## E2E-057

**Ziel:** Repräsentativer End-to-End-Fall für Kombination 57.\
**Vorbedingung:** HESPERIA Tool läuft, PS4-Modul ist initialisiert;
Provider- und Konsolenzustand werden als Fixture definiert.\
**Ablauf:** Modul öffnen → Zustand erfassen → Katalog/Inventar
synchronisieren → Kompatibilität berechnen → geplante Aktion in der
Vorschau prüfen → bei schreibender Aktion Checkpoint anlegen → Aktion
ausführen → Ergebnis verifizieren → Journal und UI aktualisieren.\
**Fehlerinjektion:** Je nach Test Netzwerkabbruch, Versionsabweichung,
voller Datenträger, ungültiges Archiv, Benutzerabbruch oder
Providerfehler einstreuen.\
**Erwartung:** Kein Datenverlust, keine falsche Kompatibilitätsaussage,
keine halb installierte Datei; Fehler bleibt auf betroffene Operation
begrenzt. Vorzustand ist wiederherstellbar oder unverändert.\
**Nachweis:** Assertions für Datenbank, Dateisystem, Action Journal und
sichtbaren UI-Status.

## E2E-058

**Ziel:** Repräsentativer End-to-End-Fall für Kombination 58.\
**Vorbedingung:** HESPERIA Tool läuft, PS4-Modul ist initialisiert;
Provider- und Konsolenzustand werden als Fixture definiert.\
**Ablauf:** Modul öffnen → Zustand erfassen → Katalog/Inventar
synchronisieren → Kompatibilität berechnen → geplante Aktion in der
Vorschau prüfen → bei schreibender Aktion Checkpoint anlegen → Aktion
ausführen → Ergebnis verifizieren → Journal und UI aktualisieren.\
**Fehlerinjektion:** Je nach Test Netzwerkabbruch, Versionsabweichung,
voller Datenträger, ungültiges Archiv, Benutzerabbruch oder
Providerfehler einstreuen.\
**Erwartung:** Kein Datenverlust, keine falsche Kompatibilitätsaussage,
keine halb installierte Datei; Fehler bleibt auf betroffene Operation
begrenzt. Vorzustand ist wiederherstellbar oder unverändert.\
**Nachweis:** Assertions für Datenbank, Dateisystem, Action Journal und
sichtbaren UI-Status.

## E2E-059

**Ziel:** Repräsentativer End-to-End-Fall für Kombination 59.\
**Vorbedingung:** HESPERIA Tool läuft, PS4-Modul ist initialisiert;
Provider- und Konsolenzustand werden als Fixture definiert.\
**Ablauf:** Modul öffnen → Zustand erfassen → Katalog/Inventar
synchronisieren → Kompatibilität berechnen → geplante Aktion in der
Vorschau prüfen → bei schreibender Aktion Checkpoint anlegen → Aktion
ausführen → Ergebnis verifizieren → Journal und UI aktualisieren.\
**Fehlerinjektion:** Je nach Test Netzwerkabbruch, Versionsabweichung,
voller Datenträger, ungültiges Archiv, Benutzerabbruch oder
Providerfehler einstreuen.\
**Erwartung:** Kein Datenverlust, keine falsche Kompatibilitätsaussage,
keine halb installierte Datei; Fehler bleibt auf betroffene Operation
begrenzt. Vorzustand ist wiederherstellbar oder unverändert.\
**Nachweis:** Assertions für Datenbank, Dateisystem, Action Journal und
sichtbaren UI-Status.

## E2E-060

**Ziel:** Repräsentativer End-to-End-Fall für Kombination 60.\
**Vorbedingung:** HESPERIA Tool läuft, PS4-Modul ist initialisiert;
Provider- und Konsolenzustand werden als Fixture definiert.\
**Ablauf:** Modul öffnen → Zustand erfassen → Katalog/Inventar
synchronisieren → Kompatibilität berechnen → geplante Aktion in der
Vorschau prüfen → bei schreibender Aktion Checkpoint anlegen → Aktion
ausführen → Ergebnis verifizieren → Journal und UI aktualisieren.\
**Fehlerinjektion:** Je nach Test Netzwerkabbruch, Versionsabweichung,
voller Datenträger, ungültiges Archiv, Benutzerabbruch oder
Providerfehler einstreuen.\
**Erwartung:** Kein Datenverlust, keine falsche Kompatibilitätsaussage,
keine halb installierte Datei; Fehler bleibt auf betroffene Operation
begrenzt. Vorzustand ist wiederherstellbar oder unverändert.\
**Nachweis:** Assertions für Datenbank, Dateisystem, Action Journal und
sichtbaren UI-Status.

## E2E-061

**Ziel:** Repräsentativer End-to-End-Fall für Kombination 61.\
**Vorbedingung:** HESPERIA Tool läuft, PS4-Modul ist initialisiert;
Provider- und Konsolenzustand werden als Fixture definiert.\
**Ablauf:** Modul öffnen → Zustand erfassen → Katalog/Inventar
synchronisieren → Kompatibilität berechnen → geplante Aktion in der
Vorschau prüfen → bei schreibender Aktion Checkpoint anlegen → Aktion
ausführen → Ergebnis verifizieren → Journal und UI aktualisieren.\
**Fehlerinjektion:** Je nach Test Netzwerkabbruch, Versionsabweichung,
voller Datenträger, ungültiges Archiv, Benutzerabbruch oder
Providerfehler einstreuen.\
**Erwartung:** Kein Datenverlust, keine falsche Kompatibilitätsaussage,
keine halb installierte Datei; Fehler bleibt auf betroffene Operation
begrenzt. Vorzustand ist wiederherstellbar oder unverändert.\
**Nachweis:** Assertions für Datenbank, Dateisystem, Action Journal und
sichtbaren UI-Status.

## E2E-062

**Ziel:** Repräsentativer End-to-End-Fall für Kombination 62.\
**Vorbedingung:** HESPERIA Tool läuft, PS4-Modul ist initialisiert;
Provider- und Konsolenzustand werden als Fixture definiert.\
**Ablauf:** Modul öffnen → Zustand erfassen → Katalog/Inventar
synchronisieren → Kompatibilität berechnen → geplante Aktion in der
Vorschau prüfen → bei schreibender Aktion Checkpoint anlegen → Aktion
ausführen → Ergebnis verifizieren → Journal und UI aktualisieren.\
**Fehlerinjektion:** Je nach Test Netzwerkabbruch, Versionsabweichung,
voller Datenträger, ungültiges Archiv, Benutzerabbruch oder
Providerfehler einstreuen.\
**Erwartung:** Kein Datenverlust, keine falsche Kompatibilitätsaussage,
keine halb installierte Datei; Fehler bleibt auf betroffene Operation
begrenzt. Vorzustand ist wiederherstellbar oder unverändert.\
**Nachweis:** Assertions für Datenbank, Dateisystem, Action Journal und
sichtbaren UI-Status.

## E2E-063

**Ziel:** Repräsentativer End-to-End-Fall für Kombination 63.\
**Vorbedingung:** HESPERIA Tool läuft, PS4-Modul ist initialisiert;
Provider- und Konsolenzustand werden als Fixture definiert.\
**Ablauf:** Modul öffnen → Zustand erfassen → Katalog/Inventar
synchronisieren → Kompatibilität berechnen → geplante Aktion in der
Vorschau prüfen → bei schreibender Aktion Checkpoint anlegen → Aktion
ausführen → Ergebnis verifizieren → Journal und UI aktualisieren.\
**Fehlerinjektion:** Je nach Test Netzwerkabbruch, Versionsabweichung,
voller Datenträger, ungültiges Archiv, Benutzerabbruch oder
Providerfehler einstreuen.\
**Erwartung:** Kein Datenverlust, keine falsche Kompatibilitätsaussage,
keine halb installierte Datei; Fehler bleibt auf betroffene Operation
begrenzt. Vorzustand ist wiederherstellbar oder unverändert.\
**Nachweis:** Assertions für Datenbank, Dateisystem, Action Journal und
sichtbaren UI-Status.

## E2E-064

**Ziel:** Repräsentativer End-to-End-Fall für Kombination 64.\
**Vorbedingung:** HESPERIA Tool läuft, PS4-Modul ist initialisiert;
Provider- und Konsolenzustand werden als Fixture definiert.\
**Ablauf:** Modul öffnen → Zustand erfassen → Katalog/Inventar
synchronisieren → Kompatibilität berechnen → geplante Aktion in der
Vorschau prüfen → bei schreibender Aktion Checkpoint anlegen → Aktion
ausführen → Ergebnis verifizieren → Journal und UI aktualisieren.\
**Fehlerinjektion:** Je nach Test Netzwerkabbruch, Versionsabweichung,
voller Datenträger, ungültiges Archiv, Benutzerabbruch oder
Providerfehler einstreuen.\
**Erwartung:** Kein Datenverlust, keine falsche Kompatibilitätsaussage,
keine halb installierte Datei; Fehler bleibt auf betroffene Operation
begrenzt. Vorzustand ist wiederherstellbar oder unverändert.\
**Nachweis:** Assertions für Datenbank, Dateisystem, Action Journal und
sichtbaren UI-Status.

## E2E-065

**Ziel:** Repräsentativer End-to-End-Fall für Kombination 65.\
**Vorbedingung:** HESPERIA Tool läuft, PS4-Modul ist initialisiert;
Provider- und Konsolenzustand werden als Fixture definiert.\
**Ablauf:** Modul öffnen → Zustand erfassen → Katalog/Inventar
synchronisieren → Kompatibilität berechnen → geplante Aktion in der
Vorschau prüfen → bei schreibender Aktion Checkpoint anlegen → Aktion
ausführen → Ergebnis verifizieren → Journal und UI aktualisieren.\
**Fehlerinjektion:** Je nach Test Netzwerkabbruch, Versionsabweichung,
voller Datenträger, ungültiges Archiv, Benutzerabbruch oder
Providerfehler einstreuen.\
**Erwartung:** Kein Datenverlust, keine falsche Kompatibilitätsaussage,
keine halb installierte Datei; Fehler bleibt auf betroffene Operation
begrenzt. Vorzustand ist wiederherstellbar oder unverändert.\
**Nachweis:** Assertions für Datenbank, Dateisystem, Action Journal und
sichtbaren UI-Status.

## E2E-066

**Ziel:** Repräsentativer End-to-End-Fall für Kombination 66.\
**Vorbedingung:** HESPERIA Tool läuft, PS4-Modul ist initialisiert;
Provider- und Konsolenzustand werden als Fixture definiert.\
**Ablauf:** Modul öffnen → Zustand erfassen → Katalog/Inventar
synchronisieren → Kompatibilität berechnen → geplante Aktion in der
Vorschau prüfen → bei schreibender Aktion Checkpoint anlegen → Aktion
ausführen → Ergebnis verifizieren → Journal und UI aktualisieren.\
**Fehlerinjektion:** Je nach Test Netzwerkabbruch, Versionsabweichung,
voller Datenträger, ungültiges Archiv, Benutzerabbruch oder
Providerfehler einstreuen.\
**Erwartung:** Kein Datenverlust, keine falsche Kompatibilitätsaussage,
keine halb installierte Datei; Fehler bleibt auf betroffene Operation
begrenzt. Vorzustand ist wiederherstellbar oder unverändert.\
**Nachweis:** Assertions für Datenbank, Dateisystem, Action Journal und
sichtbaren UI-Status.

## E2E-067

**Ziel:** Repräsentativer End-to-End-Fall für Kombination 67.\
**Vorbedingung:** HESPERIA Tool läuft, PS4-Modul ist initialisiert;
Provider- und Konsolenzustand werden als Fixture definiert.\
**Ablauf:** Modul öffnen → Zustand erfassen → Katalog/Inventar
synchronisieren → Kompatibilität berechnen → geplante Aktion in der
Vorschau prüfen → bei schreibender Aktion Checkpoint anlegen → Aktion
ausführen → Ergebnis verifizieren → Journal und UI aktualisieren.\
**Fehlerinjektion:** Je nach Test Netzwerkabbruch, Versionsabweichung,
voller Datenträger, ungültiges Archiv, Benutzerabbruch oder
Providerfehler einstreuen.\
**Erwartung:** Kein Datenverlust, keine falsche Kompatibilitätsaussage,
keine halb installierte Datei; Fehler bleibt auf betroffene Operation
begrenzt. Vorzustand ist wiederherstellbar oder unverändert.\
**Nachweis:** Assertions für Datenbank, Dateisystem, Action Journal und
sichtbaren UI-Status.

## E2E-068

**Ziel:** Repräsentativer End-to-End-Fall für Kombination 68.\
**Vorbedingung:** HESPERIA Tool läuft, PS4-Modul ist initialisiert;
Provider- und Konsolenzustand werden als Fixture definiert.\
**Ablauf:** Modul öffnen → Zustand erfassen → Katalog/Inventar
synchronisieren → Kompatibilität berechnen → geplante Aktion in der
Vorschau prüfen → bei schreibender Aktion Checkpoint anlegen → Aktion
ausführen → Ergebnis verifizieren → Journal und UI aktualisieren.\
**Fehlerinjektion:** Je nach Test Netzwerkabbruch, Versionsabweichung,
voller Datenträger, ungültiges Archiv, Benutzerabbruch oder
Providerfehler einstreuen.\
**Erwartung:** Kein Datenverlust, keine falsche Kompatibilitätsaussage,
keine halb installierte Datei; Fehler bleibt auf betroffene Operation
begrenzt. Vorzustand ist wiederherstellbar oder unverändert.\
**Nachweis:** Assertions für Datenbank, Dateisystem, Action Journal und
sichtbaren UI-Status.

## E2E-069

**Ziel:** Repräsentativer End-to-End-Fall für Kombination 69.\
**Vorbedingung:** HESPERIA Tool läuft, PS4-Modul ist initialisiert;
Provider- und Konsolenzustand werden als Fixture definiert.\
**Ablauf:** Modul öffnen → Zustand erfassen → Katalog/Inventar
synchronisieren → Kompatibilität berechnen → geplante Aktion in der
Vorschau prüfen → bei schreibender Aktion Checkpoint anlegen → Aktion
ausführen → Ergebnis verifizieren → Journal und UI aktualisieren.\
**Fehlerinjektion:** Je nach Test Netzwerkabbruch, Versionsabweichung,
voller Datenträger, ungültiges Archiv, Benutzerabbruch oder
Providerfehler einstreuen.\
**Erwartung:** Kein Datenverlust, keine falsche Kompatibilitätsaussage,
keine halb installierte Datei; Fehler bleibt auf betroffene Operation
begrenzt. Vorzustand ist wiederherstellbar oder unverändert.\
**Nachweis:** Assertions für Datenbank, Dateisystem, Action Journal und
sichtbaren UI-Status.

## E2E-070

**Ziel:** Repräsentativer End-to-End-Fall für Kombination 70.\
**Vorbedingung:** HESPERIA Tool läuft, PS4-Modul ist initialisiert;
Provider- und Konsolenzustand werden als Fixture definiert.\
**Ablauf:** Modul öffnen → Zustand erfassen → Katalog/Inventar
synchronisieren → Kompatibilität berechnen → geplante Aktion in der
Vorschau prüfen → bei schreibender Aktion Checkpoint anlegen → Aktion
ausführen → Ergebnis verifizieren → Journal und UI aktualisieren.\
**Fehlerinjektion:** Je nach Test Netzwerkabbruch, Versionsabweichung,
voller Datenträger, ungültiges Archiv, Benutzerabbruch oder
Providerfehler einstreuen.\
**Erwartung:** Kein Datenverlust, keine falsche Kompatibilitätsaussage,
keine halb installierte Datei; Fehler bleibt auf betroffene Operation
begrenzt. Vorzustand ist wiederherstellbar oder unverändert.\
**Nachweis:** Assertions für Datenbank, Dateisystem, Action Journal und
sichtbaren UI-Status.

## E2E-071

**Ziel:** Repräsentativer End-to-End-Fall für Kombination 71.\
**Vorbedingung:** HESPERIA Tool läuft, PS4-Modul ist initialisiert;
Provider- und Konsolenzustand werden als Fixture definiert.\
**Ablauf:** Modul öffnen → Zustand erfassen → Katalog/Inventar
synchronisieren → Kompatibilität berechnen → geplante Aktion in der
Vorschau prüfen → bei schreibender Aktion Checkpoint anlegen → Aktion
ausführen → Ergebnis verifizieren → Journal und UI aktualisieren.\
**Fehlerinjektion:** Je nach Test Netzwerkabbruch, Versionsabweichung,
voller Datenträger, ungültiges Archiv, Benutzerabbruch oder
Providerfehler einstreuen.\
**Erwartung:** Kein Datenverlust, keine falsche Kompatibilitätsaussage,
keine halb installierte Datei; Fehler bleibt auf betroffene Operation
begrenzt. Vorzustand ist wiederherstellbar oder unverändert.\
**Nachweis:** Assertions für Datenbank, Dateisystem, Action Journal und
sichtbaren UI-Status.

## E2E-072

**Ziel:** Repräsentativer End-to-End-Fall für Kombination 72.\
**Vorbedingung:** HESPERIA Tool läuft, PS4-Modul ist initialisiert;
Provider- und Konsolenzustand werden als Fixture definiert.\
**Ablauf:** Modul öffnen → Zustand erfassen → Katalog/Inventar
synchronisieren → Kompatibilität berechnen → geplante Aktion in der
Vorschau prüfen → bei schreibender Aktion Checkpoint anlegen → Aktion
ausführen → Ergebnis verifizieren → Journal und UI aktualisieren.\
**Fehlerinjektion:** Je nach Test Netzwerkabbruch, Versionsabweichung,
voller Datenträger, ungültiges Archiv, Benutzerabbruch oder
Providerfehler einstreuen.\
**Erwartung:** Kein Datenverlust, keine falsche Kompatibilitätsaussage,
keine halb installierte Datei; Fehler bleibt auf betroffene Operation
begrenzt. Vorzustand ist wiederherstellbar oder unverändert.\
**Nachweis:** Assertions für Datenbank, Dateisystem, Action Journal und
sichtbaren UI-Status.

## E2E-073

**Ziel:** Repräsentativer End-to-End-Fall für Kombination 73.\
**Vorbedingung:** HESPERIA Tool läuft, PS4-Modul ist initialisiert;
Provider- und Konsolenzustand werden als Fixture definiert.\
**Ablauf:** Modul öffnen → Zustand erfassen → Katalog/Inventar
synchronisieren → Kompatibilität berechnen → geplante Aktion in der
Vorschau prüfen → bei schreibender Aktion Checkpoint anlegen → Aktion
ausführen → Ergebnis verifizieren → Journal und UI aktualisieren.\
**Fehlerinjektion:** Je nach Test Netzwerkabbruch, Versionsabweichung,
voller Datenträger, ungültiges Archiv, Benutzerabbruch oder
Providerfehler einstreuen.\
**Erwartung:** Kein Datenverlust, keine falsche Kompatibilitätsaussage,
keine halb installierte Datei; Fehler bleibt auf betroffene Operation
begrenzt. Vorzustand ist wiederherstellbar oder unverändert.\
**Nachweis:** Assertions für Datenbank, Dateisystem, Action Journal und
sichtbaren UI-Status.

## E2E-074

**Ziel:** Repräsentativer End-to-End-Fall für Kombination 74.\
**Vorbedingung:** HESPERIA Tool läuft, PS4-Modul ist initialisiert;
Provider- und Konsolenzustand werden als Fixture definiert.\
**Ablauf:** Modul öffnen → Zustand erfassen → Katalog/Inventar
synchronisieren → Kompatibilität berechnen → geplante Aktion in der
Vorschau prüfen → bei schreibender Aktion Checkpoint anlegen → Aktion
ausführen → Ergebnis verifizieren → Journal und UI aktualisieren.\
**Fehlerinjektion:** Je nach Test Netzwerkabbruch, Versionsabweichung,
voller Datenträger, ungültiges Archiv, Benutzerabbruch oder
Providerfehler einstreuen.\
**Erwartung:** Kein Datenverlust, keine falsche Kompatibilitätsaussage,
keine halb installierte Datei; Fehler bleibt auf betroffene Operation
begrenzt. Vorzustand ist wiederherstellbar oder unverändert.\
**Nachweis:** Assertions für Datenbank, Dateisystem, Action Journal und
sichtbaren UI-Status.

## E2E-075

**Ziel:** Repräsentativer End-to-End-Fall für Kombination 75.\
**Vorbedingung:** HESPERIA Tool läuft, PS4-Modul ist initialisiert;
Provider- und Konsolenzustand werden als Fixture definiert.\
**Ablauf:** Modul öffnen → Zustand erfassen → Katalog/Inventar
synchronisieren → Kompatibilität berechnen → geplante Aktion in der
Vorschau prüfen → bei schreibender Aktion Checkpoint anlegen → Aktion
ausführen → Ergebnis verifizieren → Journal und UI aktualisieren.\
**Fehlerinjektion:** Je nach Test Netzwerkabbruch, Versionsabweichung,
voller Datenträger, ungültiges Archiv, Benutzerabbruch oder
Providerfehler einstreuen.\
**Erwartung:** Kein Datenverlust, keine falsche Kompatibilitätsaussage,
keine halb installierte Datei; Fehler bleibt auf betroffene Operation
begrenzt. Vorzustand ist wiederherstellbar oder unverändert.\
**Nachweis:** Assertions für Datenbank, Dateisystem, Action Journal und
sichtbaren UI-Status.

## E2E-076

**Ziel:** Repräsentativer End-to-End-Fall für Kombination 76.\
**Vorbedingung:** HESPERIA Tool läuft, PS4-Modul ist initialisiert;
Provider- und Konsolenzustand werden als Fixture definiert.\
**Ablauf:** Modul öffnen → Zustand erfassen → Katalog/Inventar
synchronisieren → Kompatibilität berechnen → geplante Aktion in der
Vorschau prüfen → bei schreibender Aktion Checkpoint anlegen → Aktion
ausführen → Ergebnis verifizieren → Journal und UI aktualisieren.\
**Fehlerinjektion:** Je nach Test Netzwerkabbruch, Versionsabweichung,
voller Datenträger, ungültiges Archiv, Benutzerabbruch oder
Providerfehler einstreuen.\
**Erwartung:** Kein Datenverlust, keine falsche Kompatibilitätsaussage,
keine halb installierte Datei; Fehler bleibt auf betroffene Operation
begrenzt. Vorzustand ist wiederherstellbar oder unverändert.\
**Nachweis:** Assertions für Datenbank, Dateisystem, Action Journal und
sichtbaren UI-Status.

## E2E-077

**Ziel:** Repräsentativer End-to-End-Fall für Kombination 77.\
**Vorbedingung:** HESPERIA Tool läuft, PS4-Modul ist initialisiert;
Provider- und Konsolenzustand werden als Fixture definiert.\
**Ablauf:** Modul öffnen → Zustand erfassen → Katalog/Inventar
synchronisieren → Kompatibilität berechnen → geplante Aktion in der
Vorschau prüfen → bei schreibender Aktion Checkpoint anlegen → Aktion
ausführen → Ergebnis verifizieren → Journal und UI aktualisieren.\
**Fehlerinjektion:** Je nach Test Netzwerkabbruch, Versionsabweichung,
voller Datenträger, ungültiges Archiv, Benutzerabbruch oder
Providerfehler einstreuen.\
**Erwartung:** Kein Datenverlust, keine falsche Kompatibilitätsaussage,
keine halb installierte Datei; Fehler bleibt auf betroffene Operation
begrenzt. Vorzustand ist wiederherstellbar oder unverändert.\
**Nachweis:** Assertions für Datenbank, Dateisystem, Action Journal und
sichtbaren UI-Status.

## E2E-078

**Ziel:** Repräsentativer End-to-End-Fall für Kombination 78.\
**Vorbedingung:** HESPERIA Tool läuft, PS4-Modul ist initialisiert;
Provider- und Konsolenzustand werden als Fixture definiert.\
**Ablauf:** Modul öffnen → Zustand erfassen → Katalog/Inventar
synchronisieren → Kompatibilität berechnen → geplante Aktion in der
Vorschau prüfen → bei schreibender Aktion Checkpoint anlegen → Aktion
ausführen → Ergebnis verifizieren → Journal und UI aktualisieren.\
**Fehlerinjektion:** Je nach Test Netzwerkabbruch, Versionsabweichung,
voller Datenträger, ungültiges Archiv, Benutzerabbruch oder
Providerfehler einstreuen.\
**Erwartung:** Kein Datenverlust, keine falsche Kompatibilitätsaussage,
keine halb installierte Datei; Fehler bleibt auf betroffene Operation
begrenzt. Vorzustand ist wiederherstellbar oder unverändert.\
**Nachweis:** Assertions für Datenbank, Dateisystem, Action Journal und
sichtbaren UI-Status.

## E2E-079

**Ziel:** Repräsentativer End-to-End-Fall für Kombination 79.\
**Vorbedingung:** HESPERIA Tool läuft, PS4-Modul ist initialisiert;
Provider- und Konsolenzustand werden als Fixture definiert.\
**Ablauf:** Modul öffnen → Zustand erfassen → Katalog/Inventar
synchronisieren → Kompatibilität berechnen → geplante Aktion in der
Vorschau prüfen → bei schreibender Aktion Checkpoint anlegen → Aktion
ausführen → Ergebnis verifizieren → Journal und UI aktualisieren.\
**Fehlerinjektion:** Je nach Test Netzwerkabbruch, Versionsabweichung,
voller Datenträger, ungültiges Archiv, Benutzerabbruch oder
Providerfehler einstreuen.\
**Erwartung:** Kein Datenverlust, keine falsche Kompatibilitätsaussage,
keine halb installierte Datei; Fehler bleibt auf betroffene Operation
begrenzt. Vorzustand ist wiederherstellbar oder unverändert.\
**Nachweis:** Assertions für Datenbank, Dateisystem, Action Journal und
sichtbaren UI-Status.

## E2E-080

**Ziel:** Repräsentativer End-to-End-Fall für Kombination 80.\
**Vorbedingung:** HESPERIA Tool läuft, PS4-Modul ist initialisiert;
Provider- und Konsolenzustand werden als Fixture definiert.\
**Ablauf:** Modul öffnen → Zustand erfassen → Katalog/Inventar
synchronisieren → Kompatibilität berechnen → geplante Aktion in der
Vorschau prüfen → bei schreibender Aktion Checkpoint anlegen → Aktion
ausführen → Ergebnis verifizieren → Journal und UI aktualisieren.\
**Fehlerinjektion:** Je nach Test Netzwerkabbruch, Versionsabweichung,
voller Datenträger, ungültiges Archiv, Benutzerabbruch oder
Providerfehler einstreuen.\
**Erwartung:** Kein Datenverlust, keine falsche Kompatibilitätsaussage,
keine halb installierte Datei; Fehler bleibt auf betroffene Operation
begrenzt. Vorzustand ist wiederherstellbar oder unverändert.\
**Nachweis:** Assertions für Datenbank, Dateisystem, Action Journal und
sichtbaren UI-Status.

## E2E-081

**Ziel:** Repräsentativer End-to-End-Fall für Kombination 81.\
**Vorbedingung:** HESPERIA Tool läuft, PS4-Modul ist initialisiert;
Provider- und Konsolenzustand werden als Fixture definiert.\
**Ablauf:** Modul öffnen → Zustand erfassen → Katalog/Inventar
synchronisieren → Kompatibilität berechnen → geplante Aktion in der
Vorschau prüfen → bei schreibender Aktion Checkpoint anlegen → Aktion
ausführen → Ergebnis verifizieren → Journal und UI aktualisieren.\
**Fehlerinjektion:** Je nach Test Netzwerkabbruch, Versionsabweichung,
voller Datenträger, ungültiges Archiv, Benutzerabbruch oder
Providerfehler einstreuen.\
**Erwartung:** Kein Datenverlust, keine falsche Kompatibilitätsaussage,
keine halb installierte Datei; Fehler bleibt auf betroffene Operation
begrenzt. Vorzustand ist wiederherstellbar oder unverändert.\
**Nachweis:** Assertions für Datenbank, Dateisystem, Action Journal und
sichtbaren UI-Status.

## E2E-082

**Ziel:** Repräsentativer End-to-End-Fall für Kombination 82.\
**Vorbedingung:** HESPERIA Tool läuft, PS4-Modul ist initialisiert;
Provider- und Konsolenzustand werden als Fixture definiert.\
**Ablauf:** Modul öffnen → Zustand erfassen → Katalog/Inventar
synchronisieren → Kompatibilität berechnen → geplante Aktion in der
Vorschau prüfen → bei schreibender Aktion Checkpoint anlegen → Aktion
ausführen → Ergebnis verifizieren → Journal und UI aktualisieren.\
**Fehlerinjektion:** Je nach Test Netzwerkabbruch, Versionsabweichung,
voller Datenträger, ungültiges Archiv, Benutzerabbruch oder
Providerfehler einstreuen.\
**Erwartung:** Kein Datenverlust, keine falsche Kompatibilitätsaussage,
keine halb installierte Datei; Fehler bleibt auf betroffene Operation
begrenzt. Vorzustand ist wiederherstellbar oder unverändert.\
**Nachweis:** Assertions für Datenbank, Dateisystem, Action Journal und
sichtbaren UI-Status.

## E2E-083

**Ziel:** Repräsentativer End-to-End-Fall für Kombination 83.\
**Vorbedingung:** HESPERIA Tool läuft, PS4-Modul ist initialisiert;
Provider- und Konsolenzustand werden als Fixture definiert.\
**Ablauf:** Modul öffnen → Zustand erfassen → Katalog/Inventar
synchronisieren → Kompatibilität berechnen → geplante Aktion in der
Vorschau prüfen → bei schreibender Aktion Checkpoint anlegen → Aktion
ausführen → Ergebnis verifizieren → Journal und UI aktualisieren.\
**Fehlerinjektion:** Je nach Test Netzwerkabbruch, Versionsabweichung,
voller Datenträger, ungültiges Archiv, Benutzerabbruch oder
Providerfehler einstreuen.\
**Erwartung:** Kein Datenverlust, keine falsche Kompatibilitätsaussage,
keine halb installierte Datei; Fehler bleibt auf betroffene Operation
begrenzt. Vorzustand ist wiederherstellbar oder unverändert.\
**Nachweis:** Assertions für Datenbank, Dateisystem, Action Journal und
sichtbaren UI-Status.

## E2E-084

**Ziel:** Repräsentativer End-to-End-Fall für Kombination 84.\
**Vorbedingung:** HESPERIA Tool läuft, PS4-Modul ist initialisiert;
Provider- und Konsolenzustand werden als Fixture definiert.\
**Ablauf:** Modul öffnen → Zustand erfassen → Katalog/Inventar
synchronisieren → Kompatibilität berechnen → geplante Aktion in der
Vorschau prüfen → bei schreibender Aktion Checkpoint anlegen → Aktion
ausführen → Ergebnis verifizieren → Journal und UI aktualisieren.\
**Fehlerinjektion:** Je nach Test Netzwerkabbruch, Versionsabweichung,
voller Datenträger, ungültiges Archiv, Benutzerabbruch oder
Providerfehler einstreuen.\
**Erwartung:** Kein Datenverlust, keine falsche Kompatibilitätsaussage,
keine halb installierte Datei; Fehler bleibt auf betroffene Operation
begrenzt. Vorzustand ist wiederherstellbar oder unverändert.\
**Nachweis:** Assertions für Datenbank, Dateisystem, Action Journal und
sichtbaren UI-Status.

## E2E-085

**Ziel:** Repräsentativer End-to-End-Fall für Kombination 85.\
**Vorbedingung:** HESPERIA Tool läuft, PS4-Modul ist initialisiert;
Provider- und Konsolenzustand werden als Fixture definiert.\
**Ablauf:** Modul öffnen → Zustand erfassen → Katalog/Inventar
synchronisieren → Kompatibilität berechnen → geplante Aktion in der
Vorschau prüfen → bei schreibender Aktion Checkpoint anlegen → Aktion
ausführen → Ergebnis verifizieren → Journal und UI aktualisieren.\
**Fehlerinjektion:** Je nach Test Netzwerkabbruch, Versionsabweichung,
voller Datenträger, ungültiges Archiv, Benutzerabbruch oder
Providerfehler einstreuen.\
**Erwartung:** Kein Datenverlust, keine falsche Kompatibilitätsaussage,
keine halb installierte Datei; Fehler bleibt auf betroffene Operation
begrenzt. Vorzustand ist wiederherstellbar oder unverändert.\
**Nachweis:** Assertions für Datenbank, Dateisystem, Action Journal und
sichtbaren UI-Status.

## E2E-086

**Ziel:** Repräsentativer End-to-End-Fall für Kombination 86.\
**Vorbedingung:** HESPERIA Tool läuft, PS4-Modul ist initialisiert;
Provider- und Konsolenzustand werden als Fixture definiert.\
**Ablauf:** Modul öffnen → Zustand erfassen → Katalog/Inventar
synchronisieren → Kompatibilität berechnen → geplante Aktion in der
Vorschau prüfen → bei schreibender Aktion Checkpoint anlegen → Aktion
ausführen → Ergebnis verifizieren → Journal und UI aktualisieren.\
**Fehlerinjektion:** Je nach Test Netzwerkabbruch, Versionsabweichung,
voller Datenträger, ungültiges Archiv, Benutzerabbruch oder
Providerfehler einstreuen.\
**Erwartung:** Kein Datenverlust, keine falsche Kompatibilitätsaussage,
keine halb installierte Datei; Fehler bleibt auf betroffene Operation
begrenzt. Vorzustand ist wiederherstellbar oder unverändert.\
**Nachweis:** Assertions für Datenbank, Dateisystem, Action Journal und
sichtbaren UI-Status.

## E2E-087

**Ziel:** Repräsentativer End-to-End-Fall für Kombination 87.\
**Vorbedingung:** HESPERIA Tool läuft, PS4-Modul ist initialisiert;
Provider- und Konsolenzustand werden als Fixture definiert.\
**Ablauf:** Modul öffnen → Zustand erfassen → Katalog/Inventar
synchronisieren → Kompatibilität berechnen → geplante Aktion in der
Vorschau prüfen → bei schreibender Aktion Checkpoint anlegen → Aktion
ausführen → Ergebnis verifizieren → Journal und UI aktualisieren.\
**Fehlerinjektion:** Je nach Test Netzwerkabbruch, Versionsabweichung,
voller Datenträger, ungültiges Archiv, Benutzerabbruch oder
Providerfehler einstreuen.\
**Erwartung:** Kein Datenverlust, keine falsche Kompatibilitätsaussage,
keine halb installierte Datei; Fehler bleibt auf betroffene Operation
begrenzt. Vorzustand ist wiederherstellbar oder unverändert.\
**Nachweis:** Assertions für Datenbank, Dateisystem, Action Journal und
sichtbaren UI-Status.

## E2E-088

**Ziel:** Repräsentativer End-to-End-Fall für Kombination 88.\
**Vorbedingung:** HESPERIA Tool läuft, PS4-Modul ist initialisiert;
Provider- und Konsolenzustand werden als Fixture definiert.\
**Ablauf:** Modul öffnen → Zustand erfassen → Katalog/Inventar
synchronisieren → Kompatibilität berechnen → geplante Aktion in der
Vorschau prüfen → bei schreibender Aktion Checkpoint anlegen → Aktion
ausführen → Ergebnis verifizieren → Journal und UI aktualisieren.\
**Fehlerinjektion:** Je nach Test Netzwerkabbruch, Versionsabweichung,
voller Datenträger, ungültiges Archiv, Benutzerabbruch oder
Providerfehler einstreuen.\
**Erwartung:** Kein Datenverlust, keine falsche Kompatibilitätsaussage,
keine halb installierte Datei; Fehler bleibt auf betroffene Operation
begrenzt. Vorzustand ist wiederherstellbar oder unverändert.\
**Nachweis:** Assertions für Datenbank, Dateisystem, Action Journal und
sichtbaren UI-Status.

## E2E-089

**Ziel:** Repräsentativer End-to-End-Fall für Kombination 89.\
**Vorbedingung:** HESPERIA Tool läuft, PS4-Modul ist initialisiert;
Provider- und Konsolenzustand werden als Fixture definiert.\
**Ablauf:** Modul öffnen → Zustand erfassen → Katalog/Inventar
synchronisieren → Kompatibilität berechnen → geplante Aktion in der
Vorschau prüfen → bei schreibender Aktion Checkpoint anlegen → Aktion
ausführen → Ergebnis verifizieren → Journal und UI aktualisieren.\
**Fehlerinjektion:** Je nach Test Netzwerkabbruch, Versionsabweichung,
voller Datenträger, ungültiges Archiv, Benutzerabbruch oder
Providerfehler einstreuen.\
**Erwartung:** Kein Datenverlust, keine falsche Kompatibilitätsaussage,
keine halb installierte Datei; Fehler bleibt auf betroffene Operation
begrenzt. Vorzustand ist wiederherstellbar oder unverändert.\
**Nachweis:** Assertions für Datenbank, Dateisystem, Action Journal und
sichtbaren UI-Status.

## E2E-090

**Ziel:** Repräsentativer End-to-End-Fall für Kombination 90.\
**Vorbedingung:** HESPERIA Tool läuft, PS4-Modul ist initialisiert;
Provider- und Konsolenzustand werden als Fixture definiert.\
**Ablauf:** Modul öffnen → Zustand erfassen → Katalog/Inventar
synchronisieren → Kompatibilität berechnen → geplante Aktion in der
Vorschau prüfen → bei schreibender Aktion Checkpoint anlegen → Aktion
ausführen → Ergebnis verifizieren → Journal und UI aktualisieren.\
**Fehlerinjektion:** Je nach Test Netzwerkabbruch, Versionsabweichung,
voller Datenträger, ungültiges Archiv, Benutzerabbruch oder
Providerfehler einstreuen.\
**Erwartung:** Kein Datenverlust, keine falsche Kompatibilitätsaussage,
keine halb installierte Datei; Fehler bleibt auf betroffene Operation
begrenzt. Vorzustand ist wiederherstellbar oder unverändert.\
**Nachweis:** Assertions für Datenbank, Dateisystem, Action Journal und
sichtbaren UI-Status.

## E2E-091

**Ziel:** Repräsentativer End-to-End-Fall für Kombination 91.\
**Vorbedingung:** HESPERIA Tool läuft, PS4-Modul ist initialisiert;
Provider- und Konsolenzustand werden als Fixture definiert.\
**Ablauf:** Modul öffnen → Zustand erfassen → Katalog/Inventar
synchronisieren → Kompatibilität berechnen → geplante Aktion in der
Vorschau prüfen → bei schreibender Aktion Checkpoint anlegen → Aktion
ausführen → Ergebnis verifizieren → Journal und UI aktualisieren.\
**Fehlerinjektion:** Je nach Test Netzwerkabbruch, Versionsabweichung,
voller Datenträger, ungültiges Archiv, Benutzerabbruch oder
Providerfehler einstreuen.\
**Erwartung:** Kein Datenverlust, keine falsche Kompatibilitätsaussage,
keine halb installierte Datei; Fehler bleibt auf betroffene Operation
begrenzt. Vorzustand ist wiederherstellbar oder unverändert.\
**Nachweis:** Assertions für Datenbank, Dateisystem, Action Journal und
sichtbaren UI-Status.

## E2E-092

**Ziel:** Repräsentativer End-to-End-Fall für Kombination 92.\
**Vorbedingung:** HESPERIA Tool läuft, PS4-Modul ist initialisiert;
Provider- und Konsolenzustand werden als Fixture definiert.\
**Ablauf:** Modul öffnen → Zustand erfassen → Katalog/Inventar
synchronisieren → Kompatibilität berechnen → geplante Aktion in der
Vorschau prüfen → bei schreibender Aktion Checkpoint anlegen → Aktion
ausführen → Ergebnis verifizieren → Journal und UI aktualisieren.\
**Fehlerinjektion:** Je nach Test Netzwerkabbruch, Versionsabweichung,
voller Datenträger, ungültiges Archiv, Benutzerabbruch oder
Providerfehler einstreuen.\
**Erwartung:** Kein Datenverlust, keine falsche Kompatibilitätsaussage,
keine halb installierte Datei; Fehler bleibt auf betroffene Operation
begrenzt. Vorzustand ist wiederherstellbar oder unverändert.\
**Nachweis:** Assertions für Datenbank, Dateisystem, Action Journal und
sichtbaren UI-Status.

## E2E-093

**Ziel:** Repräsentativer End-to-End-Fall für Kombination 93.\
**Vorbedingung:** HESPERIA Tool läuft, PS4-Modul ist initialisiert;
Provider- und Konsolenzustand werden als Fixture definiert.\
**Ablauf:** Modul öffnen → Zustand erfassen → Katalog/Inventar
synchronisieren → Kompatibilität berechnen → geplante Aktion in der
Vorschau prüfen → bei schreibender Aktion Checkpoint anlegen → Aktion
ausführen → Ergebnis verifizieren → Journal und UI aktualisieren.\
**Fehlerinjektion:** Je nach Test Netzwerkabbruch, Versionsabweichung,
voller Datenträger, ungültiges Archiv, Benutzerabbruch oder
Providerfehler einstreuen.\
**Erwartung:** Kein Datenverlust, keine falsche Kompatibilitätsaussage,
keine halb installierte Datei; Fehler bleibt auf betroffene Operation
begrenzt. Vorzustand ist wiederherstellbar oder unverändert.\
**Nachweis:** Assertions für Datenbank, Dateisystem, Action Journal und
sichtbaren UI-Status.

## E2E-094

**Ziel:** Repräsentativer End-to-End-Fall für Kombination 94.\
**Vorbedingung:** HESPERIA Tool läuft, PS4-Modul ist initialisiert;
Provider- und Konsolenzustand werden als Fixture definiert.\
**Ablauf:** Modul öffnen → Zustand erfassen → Katalog/Inventar
synchronisieren → Kompatibilität berechnen → geplante Aktion in der
Vorschau prüfen → bei schreibender Aktion Checkpoint anlegen → Aktion
ausführen → Ergebnis verifizieren → Journal und UI aktualisieren.\
**Fehlerinjektion:** Je nach Test Netzwerkabbruch, Versionsabweichung,
voller Datenträger, ungültiges Archiv, Benutzerabbruch oder
Providerfehler einstreuen.\
**Erwartung:** Kein Datenverlust, keine falsche Kompatibilitätsaussage,
keine halb installierte Datei; Fehler bleibt auf betroffene Operation
begrenzt. Vorzustand ist wiederherstellbar oder unverändert.\
**Nachweis:** Assertions für Datenbank, Dateisystem, Action Journal und
sichtbaren UI-Status.

## E2E-095

**Ziel:** Repräsentativer End-to-End-Fall für Kombination 95.\
**Vorbedingung:** HESPERIA Tool läuft, PS4-Modul ist initialisiert;
Provider- und Konsolenzustand werden als Fixture definiert.\
**Ablauf:** Modul öffnen → Zustand erfassen → Katalog/Inventar
synchronisieren → Kompatibilität berechnen → geplante Aktion in der
Vorschau prüfen → bei schreibender Aktion Checkpoint anlegen → Aktion
ausführen → Ergebnis verifizieren → Journal und UI aktualisieren.\
**Fehlerinjektion:** Je nach Test Netzwerkabbruch, Versionsabweichung,
voller Datenträger, ungültiges Archiv, Benutzerabbruch oder
Providerfehler einstreuen.\
**Erwartung:** Kein Datenverlust, keine falsche Kompatibilitätsaussage,
keine halb installierte Datei; Fehler bleibt auf betroffene Operation
begrenzt. Vorzustand ist wiederherstellbar oder unverändert.\
**Nachweis:** Assertions für Datenbank, Dateisystem, Action Journal und
sichtbaren UI-Status.

## E2E-096

**Ziel:** Repräsentativer End-to-End-Fall für Kombination 96.\
**Vorbedingung:** HESPERIA Tool läuft, PS4-Modul ist initialisiert;
Provider- und Konsolenzustand werden als Fixture definiert.\
**Ablauf:** Modul öffnen → Zustand erfassen → Katalog/Inventar
synchronisieren → Kompatibilität berechnen → geplante Aktion in der
Vorschau prüfen → bei schreibender Aktion Checkpoint anlegen → Aktion
ausführen → Ergebnis verifizieren → Journal und UI aktualisieren.\
**Fehlerinjektion:** Je nach Test Netzwerkabbruch, Versionsabweichung,
voller Datenträger, ungültiges Archiv, Benutzerabbruch oder
Providerfehler einstreuen.\
**Erwartung:** Kein Datenverlust, keine falsche Kompatibilitätsaussage,
keine halb installierte Datei; Fehler bleibt auf betroffene Operation
begrenzt. Vorzustand ist wiederherstellbar oder unverändert.\
**Nachweis:** Assertions für Datenbank, Dateisystem, Action Journal und
sichtbaren UI-Status.

## E2E-097

**Ziel:** Repräsentativer End-to-End-Fall für Kombination 97.\
**Vorbedingung:** HESPERIA Tool läuft, PS4-Modul ist initialisiert;
Provider- und Konsolenzustand werden als Fixture definiert.\
**Ablauf:** Modul öffnen → Zustand erfassen → Katalog/Inventar
synchronisieren → Kompatibilität berechnen → geplante Aktion in der
Vorschau prüfen → bei schreibender Aktion Checkpoint anlegen → Aktion
ausführen → Ergebnis verifizieren → Journal und UI aktualisieren.\
**Fehlerinjektion:** Je nach Test Netzwerkabbruch, Versionsabweichung,
voller Datenträger, ungültiges Archiv, Benutzerabbruch oder
Providerfehler einstreuen.\
**Erwartung:** Kein Datenverlust, keine falsche Kompatibilitätsaussage,
keine halb installierte Datei; Fehler bleibt auf betroffene Operation
begrenzt. Vorzustand ist wiederherstellbar oder unverändert.\
**Nachweis:** Assertions für Datenbank, Dateisystem, Action Journal und
sichtbaren UI-Status.

## E2E-098

**Ziel:** Repräsentativer End-to-End-Fall für Kombination 98.\
**Vorbedingung:** HESPERIA Tool läuft, PS4-Modul ist initialisiert;
Provider- und Konsolenzustand werden als Fixture definiert.\
**Ablauf:** Modul öffnen → Zustand erfassen → Katalog/Inventar
synchronisieren → Kompatibilität berechnen → geplante Aktion in der
Vorschau prüfen → bei schreibender Aktion Checkpoint anlegen → Aktion
ausführen → Ergebnis verifizieren → Journal und UI aktualisieren.\
**Fehlerinjektion:** Je nach Test Netzwerkabbruch, Versionsabweichung,
voller Datenträger, ungültiges Archiv, Benutzerabbruch oder
Providerfehler einstreuen.\
**Erwartung:** Kein Datenverlust, keine falsche Kompatibilitätsaussage,
keine halb installierte Datei; Fehler bleibt auf betroffene Operation
begrenzt. Vorzustand ist wiederherstellbar oder unverändert.\
**Nachweis:** Assertions für Datenbank, Dateisystem, Action Journal und
sichtbaren UI-Status.

## E2E-099

**Ziel:** Repräsentativer End-to-End-Fall für Kombination 99.\
**Vorbedingung:** HESPERIA Tool läuft, PS4-Modul ist initialisiert;
Provider- und Konsolenzustand werden als Fixture definiert.\
**Ablauf:** Modul öffnen → Zustand erfassen → Katalog/Inventar
synchronisieren → Kompatibilität berechnen → geplante Aktion in der
Vorschau prüfen → bei schreibender Aktion Checkpoint anlegen → Aktion
ausführen → Ergebnis verifizieren → Journal und UI aktualisieren.\
**Fehlerinjektion:** Je nach Test Netzwerkabbruch, Versionsabweichung,
voller Datenträger, ungültiges Archiv, Benutzerabbruch oder
Providerfehler einstreuen.\
**Erwartung:** Kein Datenverlust, keine falsche Kompatibilitätsaussage,
keine halb installierte Datei; Fehler bleibt auf betroffene Operation
begrenzt. Vorzustand ist wiederherstellbar oder unverändert.\
**Nachweis:** Assertions für Datenbank, Dateisystem, Action Journal und
sichtbaren UI-Status.

## E2E-100

**Ziel:** Repräsentativer End-to-End-Fall für Kombination 100.\
**Vorbedingung:** HESPERIA Tool läuft, PS4-Modul ist initialisiert;
Provider- und Konsolenzustand werden als Fixture definiert.\
**Ablauf:** Modul öffnen → Zustand erfassen → Katalog/Inventar
synchronisieren → Kompatibilität berechnen → geplante Aktion in der
Vorschau prüfen → bei schreibender Aktion Checkpoint anlegen → Aktion
ausführen → Ergebnis verifizieren → Journal und UI aktualisieren.\
**Fehlerinjektion:** Je nach Test Netzwerkabbruch, Versionsabweichung,
voller Datenträger, ungültiges Archiv, Benutzerabbruch oder
Providerfehler einstreuen.\
**Erwartung:** Kein Datenverlust, keine falsche Kompatibilitätsaussage,
keine halb installierte Datei; Fehler bleibt auf betroffene Operation
begrenzt. Vorzustand ist wiederherstellbar oder unverändert.\
**Nachweis:** Assertions für Datenbank, Dateisystem, Action Journal und
sichtbaren UI-Status.

## E2E-101

**Ziel:** Repräsentativer End-to-End-Fall für Kombination 101.\
**Vorbedingung:** HESPERIA Tool läuft, PS4-Modul ist initialisiert;
Provider- und Konsolenzustand werden als Fixture definiert.\
**Ablauf:** Modul öffnen → Zustand erfassen → Katalog/Inventar
synchronisieren → Kompatibilität berechnen → geplante Aktion in der
Vorschau prüfen → bei schreibender Aktion Checkpoint anlegen → Aktion
ausführen → Ergebnis verifizieren → Journal und UI aktualisieren.\
**Fehlerinjektion:** Je nach Test Netzwerkabbruch, Versionsabweichung,
voller Datenträger, ungültiges Archiv, Benutzerabbruch oder
Providerfehler einstreuen.\
**Erwartung:** Kein Datenverlust, keine falsche Kompatibilitätsaussage,
keine halb installierte Datei; Fehler bleibt auf betroffene Operation
begrenzt. Vorzustand ist wiederherstellbar oder unverändert.\
**Nachweis:** Assertions für Datenbank, Dateisystem, Action Journal und
sichtbaren UI-Status.

## E2E-102

**Ziel:** Repräsentativer End-to-End-Fall für Kombination 102.\
**Vorbedingung:** HESPERIA Tool läuft, PS4-Modul ist initialisiert;
Provider- und Konsolenzustand werden als Fixture definiert.\
**Ablauf:** Modul öffnen → Zustand erfassen → Katalog/Inventar
synchronisieren → Kompatibilität berechnen → geplante Aktion in der
Vorschau prüfen → bei schreibender Aktion Checkpoint anlegen → Aktion
ausführen → Ergebnis verifizieren → Journal und UI aktualisieren.\
**Fehlerinjektion:** Je nach Test Netzwerkabbruch, Versionsabweichung,
voller Datenträger, ungültiges Archiv, Benutzerabbruch oder
Providerfehler einstreuen.\
**Erwartung:** Kein Datenverlust, keine falsche Kompatibilitätsaussage,
keine halb installierte Datei; Fehler bleibt auf betroffene Operation
begrenzt. Vorzustand ist wiederherstellbar oder unverändert.\
**Nachweis:** Assertions für Datenbank, Dateisystem, Action Journal und
sichtbaren UI-Status.

## E2E-103

**Ziel:** Repräsentativer End-to-End-Fall für Kombination 103.\
**Vorbedingung:** HESPERIA Tool läuft, PS4-Modul ist initialisiert;
Provider- und Konsolenzustand werden als Fixture definiert.\
**Ablauf:** Modul öffnen → Zustand erfassen → Katalog/Inventar
synchronisieren → Kompatibilität berechnen → geplante Aktion in der
Vorschau prüfen → bei schreibender Aktion Checkpoint anlegen → Aktion
ausführen → Ergebnis verifizieren → Journal und UI aktualisieren.\
**Fehlerinjektion:** Je nach Test Netzwerkabbruch, Versionsabweichung,
voller Datenträger, ungültiges Archiv, Benutzerabbruch oder
Providerfehler einstreuen.\
**Erwartung:** Kein Datenverlust, keine falsche Kompatibilitätsaussage,
keine halb installierte Datei; Fehler bleibt auf betroffene Operation
begrenzt. Vorzustand ist wiederherstellbar oder unverändert.\
**Nachweis:** Assertions für Datenbank, Dateisystem, Action Journal und
sichtbaren UI-Status.

## E2E-104

**Ziel:** Repräsentativer End-to-End-Fall für Kombination 104.\
**Vorbedingung:** HESPERIA Tool läuft, PS4-Modul ist initialisiert;
Provider- und Konsolenzustand werden als Fixture definiert.\
**Ablauf:** Modul öffnen → Zustand erfassen → Katalog/Inventar
synchronisieren → Kompatibilität berechnen → geplante Aktion in der
Vorschau prüfen → bei schreibender Aktion Checkpoint anlegen → Aktion
ausführen → Ergebnis verifizieren → Journal und UI aktualisieren.\
**Fehlerinjektion:** Je nach Test Netzwerkabbruch, Versionsabweichung,
voller Datenträger, ungültiges Archiv, Benutzerabbruch oder
Providerfehler einstreuen.\
**Erwartung:** Kein Datenverlust, keine falsche Kompatibilitätsaussage,
keine halb installierte Datei; Fehler bleibt auf betroffene Operation
begrenzt. Vorzustand ist wiederherstellbar oder unverändert.\
**Nachweis:** Assertions für Datenbank, Dateisystem, Action Journal und
sichtbaren UI-Status.

## E2E-105

**Ziel:** Repräsentativer End-to-End-Fall für Kombination 105.\
**Vorbedingung:** HESPERIA Tool läuft, PS4-Modul ist initialisiert;
Provider- und Konsolenzustand werden als Fixture definiert.\
**Ablauf:** Modul öffnen → Zustand erfassen → Katalog/Inventar
synchronisieren → Kompatibilität berechnen → geplante Aktion in der
Vorschau prüfen → bei schreibender Aktion Checkpoint anlegen → Aktion
ausführen → Ergebnis verifizieren → Journal und UI aktualisieren.\
**Fehlerinjektion:** Je nach Test Netzwerkabbruch, Versionsabweichung,
voller Datenträger, ungültiges Archiv, Benutzerabbruch oder
Providerfehler einstreuen.\
**Erwartung:** Kein Datenverlust, keine falsche Kompatibilitätsaussage,
keine halb installierte Datei; Fehler bleibt auf betroffene Operation
begrenzt. Vorzustand ist wiederherstellbar oder unverändert.\
**Nachweis:** Assertions für Datenbank, Dateisystem, Action Journal und
sichtbaren UI-Status.

## E2E-106

**Ziel:** Repräsentativer End-to-End-Fall für Kombination 106.\
**Vorbedingung:** HESPERIA Tool läuft, PS4-Modul ist initialisiert;
Provider- und Konsolenzustand werden als Fixture definiert.\
**Ablauf:** Modul öffnen → Zustand erfassen → Katalog/Inventar
synchronisieren → Kompatibilität berechnen → geplante Aktion in der
Vorschau prüfen → bei schreibender Aktion Checkpoint anlegen → Aktion
ausführen → Ergebnis verifizieren → Journal und UI aktualisieren.\
**Fehlerinjektion:** Je nach Test Netzwerkabbruch, Versionsabweichung,
voller Datenträger, ungültiges Archiv, Benutzerabbruch oder
Providerfehler einstreuen.\
**Erwartung:** Kein Datenverlust, keine falsche Kompatibilitätsaussage,
keine halb installierte Datei; Fehler bleibt auf betroffene Operation
begrenzt. Vorzustand ist wiederherstellbar oder unverändert.\
**Nachweis:** Assertions für Datenbank, Dateisystem, Action Journal und
sichtbaren UI-Status.

## E2E-107

**Ziel:** Repräsentativer End-to-End-Fall für Kombination 107.\
**Vorbedingung:** HESPERIA Tool läuft, PS4-Modul ist initialisiert;
Provider- und Konsolenzustand werden als Fixture definiert.\
**Ablauf:** Modul öffnen → Zustand erfassen → Katalog/Inventar
synchronisieren → Kompatibilität berechnen → geplante Aktion in der
Vorschau prüfen → bei schreibender Aktion Checkpoint anlegen → Aktion
ausführen → Ergebnis verifizieren → Journal und UI aktualisieren.\
**Fehlerinjektion:** Je nach Test Netzwerkabbruch, Versionsabweichung,
voller Datenträger, ungültiges Archiv, Benutzerabbruch oder
Providerfehler einstreuen.\
**Erwartung:** Kein Datenverlust, keine falsche Kompatibilitätsaussage,
keine halb installierte Datei; Fehler bleibt auf betroffene Operation
begrenzt. Vorzustand ist wiederherstellbar oder unverändert.\
**Nachweis:** Assertions für Datenbank, Dateisystem, Action Journal und
sichtbaren UI-Status.

## E2E-108

**Ziel:** Repräsentativer End-to-End-Fall für Kombination 108.\
**Vorbedingung:** HESPERIA Tool läuft, PS4-Modul ist initialisiert;
Provider- und Konsolenzustand werden als Fixture definiert.\
**Ablauf:** Modul öffnen → Zustand erfassen → Katalog/Inventar
synchronisieren → Kompatibilität berechnen → geplante Aktion in der
Vorschau prüfen → bei schreibender Aktion Checkpoint anlegen → Aktion
ausführen → Ergebnis verifizieren → Journal und UI aktualisieren.\
**Fehlerinjektion:** Je nach Test Netzwerkabbruch, Versionsabweichung,
voller Datenträger, ungültiges Archiv, Benutzerabbruch oder
Providerfehler einstreuen.\
**Erwartung:** Kein Datenverlust, keine falsche Kompatibilitätsaussage,
keine halb installierte Datei; Fehler bleibt auf betroffene Operation
begrenzt. Vorzustand ist wiederherstellbar oder unverändert.\
**Nachweis:** Assertions für Datenbank, Dateisystem, Action Journal und
sichtbaren UI-Status.

## E2E-109

**Ziel:** Repräsentativer End-to-End-Fall für Kombination 109.\
**Vorbedingung:** HESPERIA Tool läuft, PS4-Modul ist initialisiert;
Provider- und Konsolenzustand werden als Fixture definiert.\
**Ablauf:** Modul öffnen → Zustand erfassen → Katalog/Inventar
synchronisieren → Kompatibilität berechnen → geplante Aktion in der
Vorschau prüfen → bei schreibender Aktion Checkpoint anlegen → Aktion
ausführen → Ergebnis verifizieren → Journal und UI aktualisieren.\
**Fehlerinjektion:** Je nach Test Netzwerkabbruch, Versionsabweichung,
voller Datenträger, ungültiges Archiv, Benutzerabbruch oder
Providerfehler einstreuen.\
**Erwartung:** Kein Datenverlust, keine falsche Kompatibilitätsaussage,
keine halb installierte Datei; Fehler bleibt auf betroffene Operation
begrenzt. Vorzustand ist wiederherstellbar oder unverändert.\
**Nachweis:** Assertions für Datenbank, Dateisystem, Action Journal und
sichtbaren UI-Status.

## E2E-110

**Ziel:** Repräsentativer End-to-End-Fall für Kombination 110.\
**Vorbedingung:** HESPERIA Tool läuft, PS4-Modul ist initialisiert;
Provider- und Konsolenzustand werden als Fixture definiert.\
**Ablauf:** Modul öffnen → Zustand erfassen → Katalog/Inventar
synchronisieren → Kompatibilität berechnen → geplante Aktion in der
Vorschau prüfen → bei schreibender Aktion Checkpoint anlegen → Aktion
ausführen → Ergebnis verifizieren → Journal und UI aktualisieren.\
**Fehlerinjektion:** Je nach Test Netzwerkabbruch, Versionsabweichung,
voller Datenträger, ungültiges Archiv, Benutzerabbruch oder
Providerfehler einstreuen.\
**Erwartung:** Kein Datenverlust, keine falsche Kompatibilitätsaussage,
keine halb installierte Datei; Fehler bleibt auf betroffene Operation
begrenzt. Vorzustand ist wiederherstellbar oder unverändert.\
**Nachweis:** Assertions für Datenbank, Dateisystem, Action Journal und
sichtbaren UI-Status.

## E2E-111

**Ziel:** Repräsentativer End-to-End-Fall für Kombination 111.\
**Vorbedingung:** HESPERIA Tool läuft, PS4-Modul ist initialisiert;
Provider- und Konsolenzustand werden als Fixture definiert.\
**Ablauf:** Modul öffnen → Zustand erfassen → Katalog/Inventar
synchronisieren → Kompatibilität berechnen → geplante Aktion in der
Vorschau prüfen → bei schreibender Aktion Checkpoint anlegen → Aktion
ausführen → Ergebnis verifizieren → Journal und UI aktualisieren.\
**Fehlerinjektion:** Je nach Test Netzwerkabbruch, Versionsabweichung,
voller Datenträger, ungültiges Archiv, Benutzerabbruch oder
Providerfehler einstreuen.\
**Erwartung:** Kein Datenverlust, keine falsche Kompatibilitätsaussage,
keine halb installierte Datei; Fehler bleibt auf betroffene Operation
begrenzt. Vorzustand ist wiederherstellbar oder unverändert.\
**Nachweis:** Assertions für Datenbank, Dateisystem, Action Journal und
sichtbaren UI-Status.

## E2E-112

**Ziel:** Repräsentativer End-to-End-Fall für Kombination 112.\
**Vorbedingung:** HESPERIA Tool läuft, PS4-Modul ist initialisiert;
Provider- und Konsolenzustand werden als Fixture definiert.\
**Ablauf:** Modul öffnen → Zustand erfassen → Katalog/Inventar
synchronisieren → Kompatibilität berechnen → geplante Aktion in der
Vorschau prüfen → bei schreibender Aktion Checkpoint anlegen → Aktion
ausführen → Ergebnis verifizieren → Journal und UI aktualisieren.\
**Fehlerinjektion:** Je nach Test Netzwerkabbruch, Versionsabweichung,
voller Datenträger, ungültiges Archiv, Benutzerabbruch oder
Providerfehler einstreuen.\
**Erwartung:** Kein Datenverlust, keine falsche Kompatibilitätsaussage,
keine halb installierte Datei; Fehler bleibt auf betroffene Operation
begrenzt. Vorzustand ist wiederherstellbar oder unverändert.\
**Nachweis:** Assertions für Datenbank, Dateisystem, Action Journal und
sichtbaren UI-Status.

## E2E-113

**Ziel:** Repräsentativer End-to-End-Fall für Kombination 113.\
**Vorbedingung:** HESPERIA Tool läuft, PS4-Modul ist initialisiert;
Provider- und Konsolenzustand werden als Fixture definiert.\
**Ablauf:** Modul öffnen → Zustand erfassen → Katalog/Inventar
synchronisieren → Kompatibilität berechnen → geplante Aktion in der
Vorschau prüfen → bei schreibender Aktion Checkpoint anlegen → Aktion
ausführen → Ergebnis verifizieren → Journal und UI aktualisieren.\
**Fehlerinjektion:** Je nach Test Netzwerkabbruch, Versionsabweichung,
voller Datenträger, ungültiges Archiv, Benutzerabbruch oder
Providerfehler einstreuen.\
**Erwartung:** Kein Datenverlust, keine falsche Kompatibilitätsaussage,
keine halb installierte Datei; Fehler bleibt auf betroffene Operation
begrenzt. Vorzustand ist wiederherstellbar oder unverändert.\
**Nachweis:** Assertions für Datenbank, Dateisystem, Action Journal und
sichtbaren UI-Status.

## E2E-114

**Ziel:** Repräsentativer End-to-End-Fall für Kombination 114.\
**Vorbedingung:** HESPERIA Tool läuft, PS4-Modul ist initialisiert;
Provider- und Konsolenzustand werden als Fixture definiert.\
**Ablauf:** Modul öffnen → Zustand erfassen → Katalog/Inventar
synchronisieren → Kompatibilität berechnen → geplante Aktion in der
Vorschau prüfen → bei schreibender Aktion Checkpoint anlegen → Aktion
ausführen → Ergebnis verifizieren → Journal und UI aktualisieren.\
**Fehlerinjektion:** Je nach Test Netzwerkabbruch, Versionsabweichung,
voller Datenträger, ungültiges Archiv, Benutzerabbruch oder
Providerfehler einstreuen.\
**Erwartung:** Kein Datenverlust, keine falsche Kompatibilitätsaussage,
keine halb installierte Datei; Fehler bleibt auf betroffene Operation
begrenzt. Vorzustand ist wiederherstellbar oder unverändert.\
**Nachweis:** Assertions für Datenbank, Dateisystem, Action Journal und
sichtbaren UI-Status.

## E2E-115

**Ziel:** Repräsentativer End-to-End-Fall für Kombination 115.\
**Vorbedingung:** HESPERIA Tool läuft, PS4-Modul ist initialisiert;
Provider- und Konsolenzustand werden als Fixture definiert.\
**Ablauf:** Modul öffnen → Zustand erfassen → Katalog/Inventar
synchronisieren → Kompatibilität berechnen → geplante Aktion in der
Vorschau prüfen → bei schreibender Aktion Checkpoint anlegen → Aktion
ausführen → Ergebnis verifizieren → Journal und UI aktualisieren.\
**Fehlerinjektion:** Je nach Test Netzwerkabbruch, Versionsabweichung,
voller Datenträger, ungültiges Archiv, Benutzerabbruch oder
Providerfehler einstreuen.\
**Erwartung:** Kein Datenverlust, keine falsche Kompatibilitätsaussage,
keine halb installierte Datei; Fehler bleibt auf betroffene Operation
begrenzt. Vorzustand ist wiederherstellbar oder unverändert.\
**Nachweis:** Assertions für Datenbank, Dateisystem, Action Journal und
sichtbaren UI-Status.

## E2E-116

**Ziel:** Repräsentativer End-to-End-Fall für Kombination 116.\
**Vorbedingung:** HESPERIA Tool läuft, PS4-Modul ist initialisiert;
Provider- und Konsolenzustand werden als Fixture definiert.\
**Ablauf:** Modul öffnen → Zustand erfassen → Katalog/Inventar
synchronisieren → Kompatibilität berechnen → geplante Aktion in der
Vorschau prüfen → bei schreibender Aktion Checkpoint anlegen → Aktion
ausführen → Ergebnis verifizieren → Journal und UI aktualisieren.\
**Fehlerinjektion:** Je nach Test Netzwerkabbruch, Versionsabweichung,
voller Datenträger, ungültiges Archiv, Benutzerabbruch oder
Providerfehler einstreuen.\
**Erwartung:** Kein Datenverlust, keine falsche Kompatibilitätsaussage,
keine halb installierte Datei; Fehler bleibt auf betroffene Operation
begrenzt. Vorzustand ist wiederherstellbar oder unverändert.\
**Nachweis:** Assertions für Datenbank, Dateisystem, Action Journal und
sichtbaren UI-Status.

## E2E-117

**Ziel:** Repräsentativer End-to-End-Fall für Kombination 117.\
**Vorbedingung:** HESPERIA Tool läuft, PS4-Modul ist initialisiert;
Provider- und Konsolenzustand werden als Fixture definiert.\
**Ablauf:** Modul öffnen → Zustand erfassen → Katalog/Inventar
synchronisieren → Kompatibilität berechnen → geplante Aktion in der
Vorschau prüfen → bei schreibender Aktion Checkpoint anlegen → Aktion
ausführen → Ergebnis verifizieren → Journal und UI aktualisieren.\
**Fehlerinjektion:** Je nach Test Netzwerkabbruch, Versionsabweichung,
voller Datenträger, ungültiges Archiv, Benutzerabbruch oder
Providerfehler einstreuen.\
**Erwartung:** Kein Datenverlust, keine falsche Kompatibilitätsaussage,
keine halb installierte Datei; Fehler bleibt auf betroffene Operation
begrenzt. Vorzustand ist wiederherstellbar oder unverändert.\
**Nachweis:** Assertions für Datenbank, Dateisystem, Action Journal und
sichtbaren UI-Status.

## E2E-118

**Ziel:** Repräsentativer End-to-End-Fall für Kombination 118.\
**Vorbedingung:** HESPERIA Tool läuft, PS4-Modul ist initialisiert;
Provider- und Konsolenzustand werden als Fixture definiert.\
**Ablauf:** Modul öffnen → Zustand erfassen → Katalog/Inventar
synchronisieren → Kompatibilität berechnen → geplante Aktion in der
Vorschau prüfen → bei schreibender Aktion Checkpoint anlegen → Aktion
ausführen → Ergebnis verifizieren → Journal und UI aktualisieren.\
**Fehlerinjektion:** Je nach Test Netzwerkabbruch, Versionsabweichung,
voller Datenträger, ungültiges Archiv, Benutzerabbruch oder
Providerfehler einstreuen.\
**Erwartung:** Kein Datenverlust, keine falsche Kompatibilitätsaussage,
keine halb installierte Datei; Fehler bleibt auf betroffene Operation
begrenzt. Vorzustand ist wiederherstellbar oder unverändert.\
**Nachweis:** Assertions für Datenbank, Dateisystem, Action Journal und
sichtbaren UI-Status.

## E2E-119

**Ziel:** Repräsentativer End-to-End-Fall für Kombination 119.\
**Vorbedingung:** HESPERIA Tool läuft, PS4-Modul ist initialisiert;
Provider- und Konsolenzustand werden als Fixture definiert.\
**Ablauf:** Modul öffnen → Zustand erfassen → Katalog/Inventar
synchronisieren → Kompatibilität berechnen → geplante Aktion in der
Vorschau prüfen → bei schreibender Aktion Checkpoint anlegen → Aktion
ausführen → Ergebnis verifizieren → Journal und UI aktualisieren.\
**Fehlerinjektion:** Je nach Test Netzwerkabbruch, Versionsabweichung,
voller Datenträger, ungültiges Archiv, Benutzerabbruch oder
Providerfehler einstreuen.\
**Erwartung:** Kein Datenverlust, keine falsche Kompatibilitätsaussage,
keine halb installierte Datei; Fehler bleibt auf betroffene Operation
begrenzt. Vorzustand ist wiederherstellbar oder unverändert.\
**Nachweis:** Assertions für Datenbank, Dateisystem, Action Journal und
sichtbaren UI-Status.

## E2E-120

**Ziel:** Repräsentativer End-to-End-Fall für Kombination 120.\
**Vorbedingung:** HESPERIA Tool läuft, PS4-Modul ist initialisiert;
Provider- und Konsolenzustand werden als Fixture definiert.\
**Ablauf:** Modul öffnen → Zustand erfassen → Katalog/Inventar
synchronisieren → Kompatibilität berechnen → geplante Aktion in der
Vorschau prüfen → bei schreibender Aktion Checkpoint anlegen → Aktion
ausführen → Ergebnis verifizieren → Journal und UI aktualisieren.\
**Fehlerinjektion:** Je nach Test Netzwerkabbruch, Versionsabweichung,
voller Datenträger, ungültiges Archiv, Benutzerabbruch oder
Providerfehler einstreuen.\
**Erwartung:** Kein Datenverlust, keine falsche Kompatibilitätsaussage,
keine halb installierte Datei; Fehler bleibt auf betroffene Operation
begrenzt. Vorzustand ist wiederherstellbar oder unverändert.\
**Nachweis:** Assertions für Datenbank, Dateisystem, Action Journal und
sichtbaren UI-Status.
