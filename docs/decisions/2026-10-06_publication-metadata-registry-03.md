# ADR: Publikationsmetadaten aus einer Registry

Status: accepted

Datum: 2026-10-06

## Kontext

Bibliographische Angaben lagen an mehreren Stellen: Personen der Korpora in `LANGUAGES` und noch einmal als Text auf der Team-Seite (mit bereits abweichenden Schreibweisen), Autor:innen der Themenseiten als Freitext im YAML, Zitate als getippte Zeichenketten in YAML und Python, eine globale deutsche Meta-Description, kein canonical, kein `hreflang`, keine maschinenlesbaren Metadaten. Plattform, Sprachressource und Einzelressource waren nur über Routen unterscheidbar; die Herausgeberrolle der Plattform ließ sich von der Autor:innenschaft einer Ressource nicht trennen.

## Entscheidung

- Eine Registry `content/publication/resources.yaml` ist die einzige Quelle für Plattformtitel, Herausgeber, Publisher, Personen und die Sprachressourcen (Korpus, Design-Artikel, Teaching-Bereich) mit `resource_id`, Status, Creators, Contributors, Daten, Version, Datenstand, Lizenz und DOI.
- Ein Modul `app/src/app/publication.py` leitet daraus Ressourcen, Zitate, schema.org JSON-LD und `citation_*`-Tags ab und validiert die Registry. Es hat keine Flask-Abhängigkeit.
- Fünf Ressourcentypen: `platform`, `research_corpus`, `teaching_resource`, `research_design`, `teaching_topic`.
- Eine Head-Komponente (`partials/_page_meta.html`) rendert Description, canonical, `hreflang`, robots, Autor-/Zitat-Tags und JSON-LD.
- Zitate werden generiert; getippte Zitate sind kein Inhalt mehr.
- Unbekannte und unveröffentlichte Themen antworten mit 404; Redirects nur für fehlende UI-Sprachfassung und explizite `aliases`.
- Unentschiedene Werte (Lizenz, DOI, Version, Datenstand, ORCID) bleiben `null`.

## Auswirkungen

- Personen und Titel werden an einer Stelle gepflegt; Korpuskarten, Team-Seite, Metadaten und Zitate können nicht mehr auseinanderlaufen.
- Ein DOI, eine Lizenz oder eine Korpusversion ist später ein einzelner Registry-Wert, ohne Template- oder Zitatumbau.
- Eine neue Themenseite braucht für die Veröffentlichung `resource_id`, `metadata.creators` (Personen-IDs) und `metadata.created`; der Validator erzwingt das.
- Zuvor erreichbare Entwurfs-URLs liefern 404 statt einer Weiterleitung auf den Hub.

## Alternativen

- Metadaten je Template oder je Python-Dict weiterpflegen: verworfen, erzeugt genau die bestehende Drift.
- DataCite- oder Dublin-Core-Schema als Laufzeitmodell: verworfen; ein Repository-Datensatz ist ein späterer Export.
- Vollständige YAML-Migration des spanischen Design-Artikels: verworfen, für die Metadatenarchitektur nicht nötig.

## Referenzen

- `docs/agent-runs/2026-10-06_publication-metadata-run4.md`
- `docs/spec/platform-data-files.md`, Abschnitt „Publication Metadata“
