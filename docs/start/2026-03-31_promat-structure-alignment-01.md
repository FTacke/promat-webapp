# PROMAT Structure Alignment 01

Datum: 2026-03-31

## Ziel

Struktureller Abgleich des bestehenden PROMAT-Repos auf die Spezifikation in `docs/PROMAT_ Plattform-, Daten- und Filestruktur.md`.

## Umgesetzter Stand

- Öffentliches Routing auf ui-lang-prefixte Pfade mit englischen technischen Slugs umgestellt.
- Zentrale Public-Content-Konfiguration auf englische interne Keys und getrennte UI-Labels refaktoriert.
- Spanischer Forschungsbereich in das neue Schema `/de/research/spanish/...` überführt.
- Vorbereitete Platzhalter für `french`, `german` und `english` in Forschung und Unterricht angelegt.
- Unterricht auf das reduzierte Minimalset `/{ui_lang}/teaching/{language}`, `phenomena`, `materials` konsolidiert.
- Root-Struktur um `public/`, `secure/` und `data/sessions/` ergänzt.
- Beispielhafte Session unter `data/sessions/spanish/ES-L-DE-B2-24-001/` angelegt.
- Technische Datenkonventionen zentral unter `app/src/app/config/data_conventions.py` dokumentiert.
- Root-`scripts/` um vorbereitete Pipeline-Unterordner für Import, Session-Setup, Audio-Konvertierung, Item-Split und Export nach `public/` ergänzt.

## Ersetzte Altstrukturen

- Frühere öffentliche Hauptpfade `/projekt`, `/forschung` und `/unterricht` sind nur noch Redirects auf `/de/project`, `/de/research` und `/de/teaching`.
- Frühere deutsche Sprach-Slugs wie `spanisch`, `franzoesisch`, `deutsch-als-fremdsprache` und `englisch` werden auf `spanish`, `french`, `german` und `english` kanonisiert.
- Frühere Seitenslugs wie `forschungsdesign`, `sprecherinnen`, `aufnahmen`, `phaenomene` und `einstieg-unterricht` werden auf die neuen technischen Slugs umgeleitet.

## Bewusst nur vorbereitet

- Restricted-/Auth-Logik für `speakers`, `recordings`, `comparison` und `phenomena` ist nicht final implementiert.
- Öffentliche Medienauslieferung aus `public/` ist strukturell vorbereitet, aber noch nicht als eigene Mediapipeline umgesetzt.
- Englische UI-Texte sind noch nicht produktiv aktiviert; die Struktur ist nur vorbereitet.

## Technische Abweichungen zur Spezifikation

- `app/` bleibt als bestehender versionierter Webapp-Source-Root erhalten und wurde nicht künstlich auf Root-Ebene umgebaut.
- Die damals noch vorhandenen Übergangsentscheidungen zu Redirects, `PROMAT_MEDIA_ROOT`, `media/` und `data/db/restricted/postgres_dev` wurden im nachfolgenden Finalisierungslauf wieder entfernt.

## Verifikation

- Relevante Python-Dateien für Routing und Content-Konfiguration wurden ohne Fehler geprüft.
- Die HTML-Shell wurde nach dem Routing-Umbau auf Templatefehler geprüft; nur ein bestehender Browser-Kompatibilitätshinweis zu `theme-color` blieb unverändert.
