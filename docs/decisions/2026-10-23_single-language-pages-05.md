# ADR: Seitenbezogene Sprachverfügbarkeit (einsprachige Seiten)

Status: accepted

Datum: 2026-10-23

## Kontext

Die Plattform war für alle Seiten außerhalb von Teaching zweisprachig (`de`, `en`). Der Design-Aufsatz des englischen Korpus (Rolf Kreyer) erscheint nur auf Englisch. Eine deutsche Ersatz- oder Leerseite darf es nicht geben, und die Lösung soll für spätere einsprachige Seiten wiederverwendbar sein, auch für rein deutsche.

## Entscheidung

- Eine zentrale, deklarative Registry `app/src/app/page_languages.py::PAGE_UI_LANGUAGES` ordnet einem exakten Seitenpfad (unterhalb von `/{ui_lang}`) die vorhandenen UI-Sprachen zu. Nicht eingetragene Seiten bleiben zweisprachig.
- Eine Anfrage in einer fehlenden Sprache wird im `before_request` des Public-Blueprints mit `302` auf die vorhandene Fassung umgeleitet. `302` wie bei Teaching-Editionen, damit eine spätere zweite Fassung nicht an gecachten `301`-Antworten scheitert.
- Der Sprachumschalter zeigt die fehlende Sprache deaktiviert. `hreflang` nennt nur vorhandene Fassungen, Navigationslinks zeigen direkt auf die vorhandene Fassung.
- Teaching behält sein eigenes Editionsmodell.

## Auswirkungen

- Neue einsprachige Seiten brauchen nur einen Registry-Eintrag und keine Sonderfälle in Routen oder Templates.
- Die Sprachverfügbarkeit ist pfadbasiert und hängt nicht von Korpus oder Navigationszweig ab. Sie gilt für die exakte Seite, nicht für Unterpfade.
- Betroffen: `routes/public.py` (Redirect, Meta, Links), `__init__.py` (Umschalter-URLs), `_ui_lang_switch.html`, `30_components.css`.

## Alternativen

- Flag im Seiten-Payload (`available_ui_langs`): verworfen, weil Umschalter, Navigationslinks auf anderen Seiten und die Weiterleitung die Verfügbarkeit kennen müssen, bevor die Zielseite gebaut wird.
- Sprachverfügbarkeit pro Korpus: verworfen, weil die übrigen englischen Korpusseiten zweisprachig bleiben.
- Deutsche Seite mit Hinweis „nur auf Englisch“: verworfen, weil sie eine inhaltsleere, indexierbare Ersatzseite wäre.

## Referenzen

- `docs/agent-runs/2026-10-23_english-design-article.md`
- `docs/spec/platform-data-files.md` (*Routing rules*, *Active App Shell*)
- `docs/spec/research-access.md`
