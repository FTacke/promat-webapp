# 2026-04-28 · I18n Shared UI Remediation

## Scope

Remediation-Schritt 2/4 mit Fokus auf sichtbare UI-Copy in bereits produktiven Shared- und Research-Oberflächen:

- zentrale Erweiterung von `app/src/app/i18n.py`
- Footer-Lokalisierung in `app/templates/partials/footer.html`
- HTML-Error-Seiten `401`, `403`, `404`, `500`
- produktive Research-Templates `research_recordings`, `research_speakers`, `research_speaker_profile`
- zentrale sichtbare Label-Schicht in `app/src/app/research_views.py`
- fokussierte Regressionen in `app/tests/test_auth_phase1.py` und `app/tests/test_research_sessions.py`

Nicht Teil dieses Schritts:

- Layout-/CSS-Neugestaltung
- CI-/GitHub-Härtung
- vollständige Bereinigung aller verbleibenden Auth-/Account-Templates
- größere Public-/Sample-/Player-Stub-Aufräumarbeiten außerhalb der direkten Shared-i18n-Slice

## Ausgangsbefund

Die zentrale Übersetzungsinfrastruktur war bereits vorhanden, wurde aber auf mehreren fertigen Oberflächen nicht konsistent genutzt.

Konkrete Defekte vor der Bereinigung:

- Footer enthielt sichtbare Hardcodings für `Rechtliches`, `Impressum`, `Datenschutz`
- HTML-Error-Seiten enthielten Titel, Meldungen und Aktionslabels direkt im Template
- Research-Templates enthielten sichtbare `if ui_lang == ... else ...`-Branches für ARIA-Labels und Headings
- `app/src/app/research_views.py` trug sichtbare DE/EN-Texte in lokalen Mapping-Konstanten und Builder-Branches

## Justierung aus Schritt 1/4

Schritt 1/4 hat Auth-/Session-Verhalten und die Error-Handler-Registrierung bereits auf einen kanonischen Pfad zusammengezogen.

Schritt 2/4 setzt darauf auf und räumt nun die sichtbare Copy-Schicht derselben Oberflächen auf:

- keine neue i18n-Infrastruktur
- keine neue UI-Familie
- keine Routing- oder Access-Änderung
- stattdessen konsequente Nutzung der bestehenden `translate(...)`-/`t(...)`-Schicht

## Geänderte Dateien

- `app/src/app/i18n.py`
- `app/src/app/research_views.py`
- `app/templates/partials/footer.html`
- `app/templates/errors/401.html`
- `app/templates/errors/403.html`
- `app/templates/errors/404.html`
- `app/templates/errors/500.html`
- `app/templates/pages/research_recordings.html`
- `app/templates/pages/research_speakers.html`
- `app/templates/pages/research_speaker_profile.html`
- `app/tests/test_auth_phase1.py`
- `app/tests/test_research_sessions.py`

## Neue oder geänderte i18n-Keys

Neue bzw. erweiterte Key-Gruppen in `app/src/app/i18n.py`:

- `common.labels.*` für wiederverwendete Research-/Profile-Labels wie `gender`, `speaker_type`, `recording_date`, `recording_year`, `associated_sessions`, `profile_data`, `level_at_recording`
- `common.actions.*` für `apply_filters`, `reset_filters`, `show_filters`, `home`, `reload_page`
- `common.options.*` und `common.values.*` für `all`, `yes`, `no`, `not_recorded`, `mixed`
- `footer.*` für Footer-Linktexte
- `errors.*` für 401/403/404/500 Seitentitel, Überschriften und Meldungen
- `research.shared.*` für Sprechergruppen, Geschlechter, Standardvarietäten, Herkunftsländer, Exposure-Typen, Monatsformate und Recording-Link-ARIA
- `research.recordings.*`, `research.speakers.*`, `research.profile.*` für Introtexte, Empty-States, ARIA-Texte und Profiltitel

## Bereinigte Templates

Bereinigt wurden die produktiven Shared-/Research-Templates, die in dieser Slice sichtbare lokale Copy oder lokale Sprach-Branches trugen:

- Footer nutzt jetzt `t('section.legal')`, `t('footer.imprint')`, `t('footer.privacy')`
- Error-Seiten nutzen jetzt `t('errors.*')` plus gemeinsame Actions wie `t('common.actions.home')`, `t('common.actions.back')`, `t('common.actions.reload_page')`
- Research-Templates nutzen jetzt zentrale `t(...)`-Keys für ARIA-Labels und sichtbare Profilnavigation statt lokaler `if ui_lang`-Branches

## Bereinigte Python-Builder

`app/src/app/research_views.py` wurde von lokaler sichtbarer DE/EN-Copy auf zentrale Keys umgestellt:

- frühere sichtbare Mapping-Konstanten wurden auf Key-Mappings umgestellt
- Filter-Labels, Optionen, Active-Filter-Chips, Empty-States und Statuslabels laufen nun über `_t(...)`/zentral definierte Keys
- Profil-, Aufzeichnungs- und Sprecher-Builder ziehen sichtbare Labels nicht mehr aus lokalen `if ui_lang`-Branches
- in der Datei bleiben keine `if ui_lang == "de"`-Branches mehr für diese sichtbare Copy-Schicht übrig

## Bewusst nicht geänderte Bereiche

In dieser minimalen Step-2-Slice bewusst offengelassen:

- `app/templates/auth/account_profile.html`
- `app/templates/auth/account_delete.html`
- weitere zuvor identifizierte Randbereiche wie `research_player_stub`-/Public-Folgesurfaces, sofern sie nicht Teil der direkt produktiven Shared-/Research-Slice waren

Diese Bereiche waren bereits als i18n-Schulden sichtbar, wurden hier aber nicht mitgezogen, um Schritt 2/4 auf die höchste gemeinsame UI-Schicht zu begrenzen.

## Tests

Ergänzt wurden fokussierte Regressionen für:

- lokalisierte Footer-Legal-Links in Deutsch und Englisch
- englische HTML-Error-Seiten für `401`, `403`, `404`, `500`
- englische Research-Builder-Labels für Recordings, Speakers und Profile
- gerenderte ARIA-/Action-Labels in den englischen Research-Templates

Ausgeführt:

- `python -m pytest app/tests/test_auth_phase1.py -q`
- `python -m pytest app/tests/test_research_sessions.py -q`

Ergebnis:

- `37 passed`
- `180 passed`

## Grep-/Regressionsergebnisse

Gezielte Nachkontrollen nach der Änderung:

- keine verbleibenden Treffer für `if ui_lang == "de"` in `app/src/app/research_views.py`
- keine verbleibenden Hardcodings der fokussierten Footer-/Error-/Research-Template-Texte in den berührten Templates
- Editor-Diagnostik für alle geänderten Dateien: keine Fehler

Gezielte Folgepunkt-Greps bestätigten weiterhin verbleibende sichtbare Auth-Account-Copy in:

- `app/templates/auth/account_profile.html`
- `app/templates/auth/account_delete.html`

## Offene Folgepunkte für Schritt 3/4 oder 4/4

- Auth-Account-Oberflächen auf dieselbe zentrale i18n-Schicht ziehen
- restliche productive Templates mit sichtbarer lokaler Copy systematisch nachziehen
- verbleibende Public-/Stub-Surfaces mit direkter UI-Copy prüfen und entscheiden, ob produktiv oder entnormt