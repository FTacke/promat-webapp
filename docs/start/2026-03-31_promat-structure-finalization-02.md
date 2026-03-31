# PROMAT Structure Finalization 02

Datum: 2026-03-31

## Ziel

Zweite Bereinigungs- und Finalisierungsrunde nach dem ersten Strukturabgleich auf die Spezifikation in `docs/PROMAT_ Plattform-, Daten- und Filestruktur.md`.

## Umgesetzter Stand

- Alle verbliebenen alten Public-Redirect-Routen für `/projekt`, `/forschung`, `/unterricht`, `/sample` und `/sprachen` wurden entfernt.
- Die Public-Routingstruktur akzeptiert nur noch die finalen technischen Slugs unter `/{ui_lang}/project`, `/{ui_lang}/research`, `/{ui_lang}/teaching` und `/{ui_lang}/sample`.
- Die Legacy-Kanonisierung alter deutscher Sprach- und Seitenslugs wurde aus der Public-Content-Konfiguration entfernt.
- Die öffentliche Runtime-Grenze wurde vollständig von `PROMAT_MEDIA_ROOT` auf `PROMAT_PUBLIC_ROOT` umgestellt.
- Die Dev-Postgres-Ablage wurde von `data/db/restricted/postgres_dev` nach `data/db/postgres_dev` verschoben.
- Aktive Repo-Instruktionen, Compose-Dateien, Setup-Skripte, CI und README wurden auf den finalen Zustand aktualisiert.
- Der versionierte Legacy-Ordner `media/` wurde aus dem Repo-Stand entfernt.

## Verbleibende bewusste Grenzen

- `app/` bleibt der versionierte Webapp-Source-Root.
- Die UI bleibt vorerst deutsch, obwohl die technische Struktur bereits sprachneutral vorbereitet ist.
- Restricted-/Auth-Zugriffe für forschungsnahe Detailseiten bleiben weiterhin strukturell vorbereitet, aber nicht final ausgebaut.

## Verifikation

- Routingdateien und Runtime-Konfiguration wurden auf verbliebene Legacy-Routen, alte Slugs und alte Runtime-Variablen geprüft.
- Die Dev- und CI-Konfiguration referenzieren jetzt denselben öffentlichen Rootnamen und denselben Dev-Postgres-Pfad.