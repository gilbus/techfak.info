# **UNMAINTAINED**

This repository is an excerpt of my work as System Administrator for the Faculty of
Technology, Bielefeld University. Specific details have been removed and therefore this
software is not functional as is.

# techfak.info

[``techfak.info``](https://techfak.info) ist die Status-Seite der RBG auf welcher aktuelle Störungen
und Ankündigungen unsererseits angezeigt werden.

Bis auf ``status`` greifen alle Skripte auf eine globale Konfigurationsdatei
zurück. Diese ist auf der status-Maschine unter
`/usr/local/etc/techfak_info.conf` zu finden und enthält alle Optionen (Pfade
zu Ordnern, Mail-Inhalte, etc.)

Für die lokale Weiterentwicklung bzw Debugging siehe [hier](Hacking.md).

## Konfiguration

Alle Einstellungen sind innerhalb einer einzelnen Datei ``techfak_info.conf``
gespeichert. Diese ist im INI-Format gespeichert und wird von dem
``configparser``-Modul im
[``Extended Interpolation``-Modus](https://docs.python.org/3/library/configparser.html?highlight=configparser#configparser.ExtendedInterpolation)
geparst.

## Struktur

### Einträge

Der gesamte Inhalt der Seite bzw. alle Einträge sind in einer Datei
gespeichert, welche sich standardmäßig unter
``/srv/www/status/techfak_info.json`` findet. Das Format ist das eines [JSON
Feed](https://jsonfeed.org/version/1) (bis auf die Daten, aber niemand arbeitet
gerne mit Zeitzonen...), damit sowohl ein Abonnieren mit Hilfe eines Feed
Readers als auch eine simple Verarbeitung (siehe Verwendung von ``jq``) möglich
ist.

Ein valider Eintrag sieht wie folgt aus

```json
{
		"_tf_params": {
				"begin": "2018-05-10T10:00:00",
				"eta": "2018-05-10T18:00:00",
				"severity": "green",
				"state": "active"
		},
		"content_html": "Da Infrastruktur gewartet werden muss, kann das GZI am Mittwoch nachmittag nicht genutzt werden. Bei vorzeitiger Beendigung wird dieser Eintrag entsprechend aktualisiert.",
		"date_modified": "2018-04-15T16:18:36",
		"date_published": "2017-05-31T17:22:45",
		"id": "8e2433a-d1e7-56e7-a38-9c0a33bf223b",
		"summary": "Da Infrastruktur gewartet werden muss, kann das GZI am Mittwoch nachmittag nicht genutzt werden.",
		"title": "GZI wegen Wartungsarbeiten nicht nutzbar"
},
```

Abgesehen von ``id`` und ``date_modified`` können alle Inhalte von Clients
beeinflusst werden, für weitere Informationen siehe ``techfak_info-add``.

## ``status``

Ruft die anderen Skripte auf und ist auch das Einzige, welches als Benutzer
aufgerufen werden muss.

### ``status edit``

1. Lädt die aktuellen Einträge von ``status.techfak.net`` herunter und startet
``techfak_info-enty`` mit diesen, welches dem Nutzer eine REPL bietet um einen
Eintrag zu modifizieren. Am Ende wird ein Eintrag im JSON-Format in einer
temporären Datei gespeichert.
2. Dieser Eintrag wird ``techfak_info-add`` auf der status-Maschine als String
übergeben, welches ihn auf Korrektheit überprüft und ihn dann in die bereits
genannte Datei einträgt.
3. ``techfak-info_build`` baut auf der Grundlage dieser Einträge zwei Dateien
und kopiert sie in das Verzeichnis des Webservers

### ``status show``

Zeigt mit Hilfe von ``jq`` die aktuellen aktiven Einträge an.

### ``status search <query>``

Sucht mit Hilfe von ``jq`` innerhalb aller textuellen Attribute eines Eintrag
nach dem gesuchten Inhalt (case sensitive(!))

## ``techfak_info-entry``

```
usage: techfak_info-entry [-h] [-l [LOCAL_ENTRIES]] [-o OUTPUT_FILE]
                          [--error-on-abort]

Runs the REPL of techfak.info locally and outputs the collected entries to
STDOUT

optional arguments:
  -h, --help            show this help message and exit
  -l [LOCAL_ENTRIES], --local-entries [LOCAL_ENTRIES]
                        Loads the entries from the local file if given and
                        uses no existing entries if not.
  -o OUTPUT_FILE, --output_file OUTPUT_FILE
                        Path to file to write the output to.
  --error-on-abort      Do not exit with code 0 if terminated via Ctrl+c

GPLv3 @ tl
```

Es kann immer nur ein Eintrag bearbeitet werden, für mehrere Schritte muss
``status`` entsprechend häufig aufgerufen werden.

## ``techfak_info-add``

```
usage: techfak_info-add [-h] [-l [LOCAL_FILE]] entry

Accepts one JSON-formatted entry and either adds it as a new one or, in case
the entry already contains an id, replaces an existing one.

positional arguments:
  entry                 JSON-formatted entry

optional arguments:
  -h, --help            show this help message and exit
  -l [LOCAL_FILE], --local-file [LOCAL_FILE]
                        Path to local jsonfeed-file to modify instead of the
                        one defined in the config file. Use - for stdout and
                        to simulate no existent entries. (default:
                        share/dummy_data.json)

GPLv3 @ tl
```

Nimmt Einträge im JSON-Format entgegen, überprüft diese auf Korrektheit und
fügt sie anschließend in ``techfak_info.json`` ein. Falls der übergebene
Eintrag eine existierende ``id`` besitzt wird der entsprechen Eintrag mit
Übergebenen ersetzt, wann immer ein Eintrag geändert wird aktualisiert sich
``date_modified``.

### Pflicht-Inhalte

- ``title``:
  Titel des Eintrags
- ``summary``:
  Kurze Zusammenfassung des Inhalts, welche auf den Info-Monitoren angezeigt
wird
- ``_tf_params.severity``:
  Kategorie/Schwere des Eintrages: ``green``, ``yellow`` oder ``red``
- Minimalbeispiel:
	```json
	{
		"summary": "Auf Grund der Störung des SMB/CIFS Services kommt es zu Beeinträchtigungen bei der Nutzung des Windows Terminal-Servers.",
		"_tf_params": {
			"severity": "yellow"
		},
		"title": "Windows Terminal-Server nur eingeschränkt verfügbar"
	}
	```

### Optionale Inhalt mit Default-Werten

Im Fall von invaliden Werten werden diese ignoriert.

- ``content_html``:
  Der vollständige Eintrag, falls ``summary`` nicht ausreicht. Wird statt der
  ``summary`` auf der Info-Seite angezeigt falls vorhanden. Default ``''``
- ``_tf_params.state``:
  Ob der Eintrag aktiv (``active``), versteckt (``hidden``) oder archiviert
  (``archive``) ist. Default ``active``
- ``begin``:
  Wann der im Eintrag beschriebene Inhalt beginnt. Default ``today as
  YYYY-MM-DD``
- ``eta``:
  Wann der im Eintrag beschriebene Inhalt ended. Default ``null``
- ``date_published``
  Wann der Eintrag das Erste mal verfasst wurde. Default ``date_modified``

Ein vollständiges Beispiel findet sich am Anfang der Seite.

### Integration

Die primäre Idee ist, dass der Input von ``techfak_info-entry`` generiert wird,
theoretisch kann aber jede andere Methode ebenfalls verwendet werden. Dem
Interessierten seien hierbei die verwendeten ``jq``-Skripte empfohlen.

## ``techfak_info-build``

```
usage: techfak_info-build [-h] [-l LOCAL_FILE] [-o OUTPUT] [--hide-all]
                          [-p {infopage,monitor,all}]

Builds static websites from a jsonfeed formatted file. If called without
arguments all targets are build and moved according to config.

optional arguments:
  -h, --help            show this help message and exit
  -l LOCAL_FILE, --local-file LOCAL_FILE
                        Path to jsonfeed file containing the entries to render
                        (default: share/dummy_data.json)
  -o OUTPUT, --output OUTPUT
                        Output file or `-` for stdout (default: None)
  --hide-all            Treat all active entries as hidden. Useful to simulate
                        such simulation with having to edit the entries.
                        (default: False)
  -p {infopage,monitor,all}, --page {infopage,monitor,all}
                        Which page to build. In case of `all` output files are
                        taken from config. (default: all)

GPLv3 @ tl
```

Verwendet [``jinja2``](http://jinja.pocoo.org/) um aus der JSON-Datei mit
Einträgen die Infoseiten zu bauen. Eine für den regulären Aufruf aus einem
beliebigen Browser (auch mobil), welche direkt unter ``https://techfak.info``
angezeigt wird.
Die zweite ist für den Einsatz auf den Info-Bildschirmen im CITEC gedacht und
zeigt reduzierte Inhalte an, zu finden unter
``https://techfak.info/monitor.htlm``.

## ``techfak-info_check``

```
usage: techfak_info-check [-h] [-l LOCAL_FILE] [-r] [-n]

Expected to be executed every hour by an external mechanism (cron/systemd-
timer). Moves expired entries to archive and sends reminders concerning
entires without an ETA. Intervals are specified inside the config file.

optional arguments:
  -h, --help            show this help message and exit
  -l LOCAL_FILE, --local-file LOCAL_FILE
                        Path to local jsonfeed-file to use instead of the one
                        defined in the config file. (default:
                        share/dummy_data.json)
  -r, --send-reminder   Send reminder independent of current time. (default:
                        False)
  -n, --no-move         Do not move expired entries to the archive (default:
                        False)

GPLv3 @ tl

```

Führt zwei Aktionen und informiert über diese via Mail
1. Der ETA eines Eintrags ist abgelaufen woraufhin dieser ins Archiv verschoben
wird.
2. Erinnerung bezüglich Einträge ohne ETA.
