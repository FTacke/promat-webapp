# PROMAT – Data, UX & Publication Audit (2026-10-06)

Status: nicht-normativer Audit-Bericht. Aktive Regeln bleiben in `docs/spec/`. Dieser Bericht dokumentiert Befunde und Reparaturrichtungen; er ändert keine Spezifikation, keinen Code und keine Daten.

---

## 1. Executive Summary

**Gesamturteil:** Solider, ungewöhnlich gut dokumentierter Kern mit sauberer Datenschicht – aber **nicht publikationsreif**. Die Forschungsdaten sind in sich konsistent (Kataloge ↔ Alignments ↔ Audio ↔ Metadaten ohne einen einzigen verwaisten Verweis, `théâtre` überall korrekt). Die Schwächen liegen in der **öffentlichen Oberfläche**: Pflichtseiten liefern live HTTP 500, Seitentitel werden clientseitig überschrieben, die Zitierarchitektur ist praktisch nicht vorhanden, unfertige Seiten sind öffentlich, und im Dark Mode versagt der Kontrast an zentralen Stellen.

| Schweregrad | Anzahl |
|---|---|
| CRITICAL | 0 |
| HIGH | 9 |
| MEDIUM | 37 |
| LOW | 15 |

**Production-/Publication-Blocker: JA** – (a) Impressum und Datenschutzerklärung liefern auf Production HTTP 500 (PUBL-01); (b) öffentliche Platzhalter-Themenseiten mit Autor „NN“ (CONTENT-01); (c) das einzige Themenseiten-Zitat verweist auf die Domain-Wurzel (CITE-01). Kein Blocker ist das Fehlen eines DOI.

**Wichtigste Risiken:**
1. Rechtlich erforderliche Seiten live nicht erreichbar (PUBL-01).
2. `document.title` ist nach dem Laden auf jeder Seite konstant „Pronunciation Matters“ (METADATA-01) – verfälscht Tab, Lesezeichen, Verlauf, Zotero/Citavi und Screenreader-Ansage.
3. Mutmaßliche Namen in ID3-Tags der ausgelieferten MP3s (DATA-01) – Pseudonymisierung unvollständig.
4. Sprecher-Auswahl im Vergleich tauscht das gewählte Set implizit aus und legt serverseitig Kopien an (UX-01).
5. 5-MB-Icon-Font auf jeder Seite, keine Kompression (PERF-01/02) – auf 1,6 Mbit/s: 4,6 s (Login) bis 9,2 s (Themenseite) bis DOMContentLoaded, Icons fallen aus.
6. Dark-Mode-Kontrast: Primär-Buttons (Login) 2,24:1, Navigation für ausgeloggte Besucher:innen 1,55–1,87:1.

**Stärkste vorhandene Bereiche:** Datenintegrität der Korpora; DE/EN-Parität der i18n-Schicht (907/907 Keys, identische Platzhalter); generisches, lückenloses Auth-Gate (alle Research-Routen außer `design` redirecten vor dem Rendern, 8 Kombinationen × 14 Pfade); Audio-Architektur (ein einziges `Audio`-Objekt in der Matrix, `preload="none"`, Range-Requests funktionieren, keine Blob-Downloads, deterministische Zustände); native `<dialog>`-Dialoge mit Fokusfalle; Test-Suite (892 grün); governance-konforme Struktur.

---

## 2. Ausgangszustand

- **Branch / Commit:** `local/preservation-activation` @ `3c0bb8c` (Arbeitsbaum sauber bis auf ungetracktes `.claude/worktrees/`).
- **Stack:** Flask 3.1 Monolith (kein Next.js), Jinja-Templates, handgeschriebene ES-Module, Postgres (Dev: Docker, Port 54321), Gunicorn 2 sync Worker in Prod, nginx außerhalb des Repos.
- **Sprachbereiche:** Research `spanish` (24 Sessions), `french` (31), `english` (10), `german` (0 Sessions, Platzhalter); Teaching `spanish` (1 vollständiges Thema, 1 Scaffold, 2 nicht öffentliche Legacy-Stubs), `french` (3 Scaffolds), `english`/`german` (leere Hubs). UI-Sprachen `de`/`en`.
- **Umgebung:** lokal (Dev-Server `127.0.0.1:8000`, Dev-Postgres, Daten aus `data/`), Production `https://pronunciation-matters.de` nur per GET/HEAD und Browser-Smoke auf **öffentlichen** Seiten (~130 Requests, kein Login, keine Formulare). Production läuft älteren Code (Footer `v0.7`).
- **Geprüfte Routen:** lokal anonym 49 Routen (de+en: Landing, Projekt, Research-Hubs, `design`, Teaching-Hubs und -Themen, Impressum, Datenschutz, Login) × 3 Viewports (1440/820/390) × 2 Themes = 294 Ladevorgänge; lokal eingeloggt (Admin) 46 Routen (4 Korpora × Speakers/Comparison/Phenomena, Speaker-Profil, Player wordlist/text, Phänomene-Preset/Set) × 3 × 2 = 276; Production 12 Routen × 3 × 2 = 72.
- **Werkzeuge:** Playwright/Chromium (Overflow, Konsole, Netzwerk, Screenshots, Throttling per CDP), axe-core 4.14 (Desktop+Mobile), eigene Skripte für Unicode-/Referenz-/Dateiaudits, Kontrastberechnung aus Token, vier parallele Read-only-Teil-Audits (Daten; Content/i18n/Cross-Language; Publikation; Audio/Performance/CSS/A11y-Code).
- **Ausgeführte Checks:** `pytest app/tests` (Dev-DB per SQLite-URL umgangen): **892 passed, 1 failed** (`test_backup_and_restore_scripts_exist_are_executable_and_parse` – Windows-Umgebung: `bash` ist WSL-Stub, kein Befund); `scripts/ci_governance_checks.py` pass; `scripts/validate_teaching_content.py` pass; `validate_research_config.py --require-complete` ok; `validate_research_intake.py runtime-tree` über 65 Sessions: 0 Fehler.
- **Nicht geprüft:** echter Screenreader, echte iOS-/Android-Geräte, Authentifizierter Production-Zugang, nginx-Konfiguration (nicht im Repo), Postgres-Inhalt (nur Stichproben), Lighthouse/Bundle-Analyse (kein Bundler vorhanden).
- **Evidenzstufen im Bericht:** *[gemessen]* = im Browser/per Request von mir reproduziert; *[Code]* = aus Quelltext belegt; *[unverifiziert]* = plausibel, braucht Gerät/Browser-Lauf.

**Nebenwirkungen des Audits (Offenlegung):** Die UI-Läufe haben in der **lokalen Dev-DB** 8 private Draft-Sets (`research_sets`, `lifecycle=draft`, angelegt 2026-10-06 06:37–06:41 UTC, Folge von UX-01) und einen aktualisierten `last_login_at` für `admin_dev` erzeugt. Die Bereinigung der Drafts wurde vom Sicherheitsmechanismus der Sitzung abgelehnt und bewusst nicht erzwungen; Drafts besitzen ein Ablaufdatum. Im Repo wurden keine Dateien verändert (siehe §10).

---

## 3. Findings

Konsolidiert: Symptome gleicher Ursache sind zusammengefasst. Teilaudit-Agenten-Befunde, die ich selbst im Browser reproduziert habe, sind als *[gemessen]* markiert; **ein Agent-Befund wurde bei Gegenprüfung korrigiert** (siehe Hinweis bei UX-03).

### HIGH

#### PUBL-01 – HIGH – PUBLICATION – Impressum und Datenschutz liefern auf Production HTTP 500
- **Evidenz** *[gemessen]*: `curl` und Browser auf `https://pronunciation-matters.de/{de,en}/impressum`, `/{de,en}/privacy`, `/impressum` → `500 INTERNAL SERVER ERROR`. Footer-Links jeder Seite zeigen darauf.
- **Wahrscheinliche Ursache** *[Code/Git, durch Teil-Audit; Git-Abstammung von mir nicht erneut geprüft]*: Commit `7feaade` (2026-10-04) verschob `docs/plans/impressum_datenschutz.md` nach `content/legal/` und änderte `LEGAL_CONTENT_SOURCE` (`app/src/app/routes/public_content.py`). Production läuft älteren Code (`v0.7`), der Pfad `docs/plans/…` ist im Image nicht vorhanden (das Re-Entry-Audit vom 2026-10-04 hatte genau dieses Risiko „UNKNOWN“ markiert). Lokal rendert die Seite (200).
- **Auswirkung:** Pflichtangaben (Anbieterkennzeichnung, Datenschutz, einziger Urheberrechtshinweis) sind live nicht erreichbar.
- **Reparaturrichtung:** Stand mit `content/legal/` deployen (kein Code-Fix nötig, sofern der Branch gemergt wird); Legal-Render in `scripts/ci_image_smoke.py` und Post-Deploy-curl im Runbook.
- **Validierung:** 200 für alle fünf URLs; Image-Smoke rendert Legal-Seiten.

#### METADATA-01 – HIGH – METADATA/CITATION – Client-JS überschreibt `document.title` auf jeder Seite
- **Evidenz** *[gemessen, lokal + Production]*: Server-HTML hat korrekte Titel (`<title>Die Liaison · Pronunciation Matters</title>`), aber nach dem Laden ist `document.title === 'Pronunciation Matters'` auf **allen** 294+72 geprüften Seiten (u. a. `/de/teaching/spanish/which-pronunciation`).
- **Ursache** *[Code]*: `app/static/js/modules/navigation/page-title.js` setzt `const TITLE_TEXT = "Pronunciation Matters"; document.title = title;` bei Init, bei jeder DOM-Mutation in `<main>` (MutationObserver) und bei Navigationsereignissen (geladen über `modules/navigation/index.js`).
- **Auswirkung:** Tab-/Verlaufs-/Lesezeichen-Titel identisch; Referenzmanager, die den gerenderten DOM lesen, speichern „Pronunciation Matters“; Screenreader-Ansage und WCAG 2.4.2 verletzt; konkrete Themenseiten sind nicht über ihren Titel identifizierbar. Zusätzlich `console.log`-Rauschen bei jeder Mutation.
- **Reparaturrichtung:** `applyTitle()` darf den serverseitigen Titel nicht überschreiben (Modul entfernen oder nur bei Fragment-Navigation den neuen Server-Titel übernehmen).
- **Validierung:** Playwright-Test: `document.title` nach `networkidle` == Server-`<title>` für repräsentative Routen.

#### CITE-01 – HIGH – CITATION – Zitat der Themenseite verweist auf die Domain-Wurzel
- **Evidenz** *[Content/Live]*: `content/teaching/spanish/which-pronunciation/{de,en}.yaml:18-22`; live: `data-copy-text="Tacke, Felix (2026): „Welche Aussprache unterrichten? (Themenseite)“. In: Pronunciation Matters. Online: https://www.pronunciation-matters.de."`.
- **Probleme:** (a) URL ist nicht die Seite (`/de/teaching/spanish/which-pronunciation`), DE und EN teilen dieselbe URL; (b) Host `www.` ist nicht kanonisch (301 auf non-www; die Design-Seite zitiert non-www); (c) `/` ist ein 302 nach Accept-Language.
- **Auswirkung:** Wer die Seite zitiert, verweist auf die Startseite – zentraler Defekt für „Was zitiere ich, welche URL ist maßgeblich?“.
- **Reparaturrichtung:** Zitat aus Seitenmetadaten generieren; kanonische URL aus `PROMAT_PUBLIC_BASE_URL` + Route.
- **Validierung:** Test, dass die URL jedes Zitats gegen die Route-Map auflöst und curl ohne Redirect 200 liefert.

#### CONTENT-01 – HIGH – CONTENT/PUBLICATION – Unfertige Teaching-Themen sind öffentlich (Autor „NN“, Platzhaltertexte)
- **Evidenz** *[gemessen, lokal + Production]*: `/de/teaching/french/liaison`, `…/gleitlaute`, `…/nasalvokale`, `/*/teaching/spanish/r-am-silbenende` → 200; Hub zeigt „3 Themenseiten · Öffnen →“. Seiteninhalt: „Hier kann später ein kurzer erklärender Einstieg stehen…“, „Audio-Beispiele noch nicht hinterlegt“, Autor `NN` (8 YAMLs), `status: draft`. `spanish/r` mit `is_public: false` wird dagegen korrekt auf den Hub umgeleitet.
- **Ursache** *[Code]*: `teaching_content.py` (`_explicit_public_availability`, `topic_is_public`) wertet nur `is_available|is_public|published`; `status: draft` und `hub.status` wirken nicht. Der Validator prüft Platzhalter/`NN` nicht.
- **Auswirkung:** Platzhalterseiten bekommen stabile, indexierbare, zitierbare URLs mit Pseudo-Autor; Spec verlangt für geplante Themen kein Linkziel.
- **Reparaturrichtung:** `status: draft` wie `is_public: false` behandeln (oder Flag in den 5 Scaffolds setzen) + Regressionstest über den echten Content-Baum.
- **Validierung:** Test „Draft-Topic → Redirect/404 und nicht im Hub“; Validator-Regel gegen `NN` in öffentlichen Seiten.

#### DATA-01 – HIGH – DATA – Mutmaßliche Namen in ID3-Titeln der ausgelieferten MP3s
- **Evidenz** *[Teil-Audit, Stichprobe von mir bestätigt]*: Von 8.324 Runtime-MP3 tragen 5.143 einen ID3v2-`TIT2` aus den Quellaufnahmen, z. B. `Bender_Liste_ENG`, `Kober_Text_SPA`, `Probst_Wortliste`, `Minssen_Interview_SPA`, daneben interne Arbeitsnamen (`es_l_0011_wordlist_raw`). Von mir geprüft: `data/sessions/french/FR-L-0015-2026-S01/derived/interview.mp3` enthält `TIT2 = Probst_Wortliste`. 45 von 54 Sessions mit Audio betroffen; derselbe Nachname taucht korpusübergreifend auf. In ES-L-0001 und FR-L-0007 widerspricht die Tag-Sprache der Session.
- **Ursache:** ffmpeg-Konvertierung übernimmt Quell-Tags (`audio_conversion` ohne `-map_metadata -1`); nur `TSSE` (Lavf) ist sonst gesetzt.
- **Auswirkung:** Dateinamen sind IDs, die Dateien tragen aber Namen und sind für authentifizierte Nutzer:innen herunterladbar und in Prod-Paketen. **Zu bestätigen:** ob es sich um Teilnehmende oder Mitarbeitende handelt (Schluss aus dem Muster `<Nachname>_<Liste|Text>_<ENG|SPA>`).
- **Reparaturrichtung:** Tags bei Konvertierung strippen (`-map_metadata -1 -write_id3v2 0`), neu publizieren; Tag-Allowlist im Runtime-Tree-Validator und in Paketvalidatoren; Sprach-Mismatch-Sessions gegen Archiv prüfen.
- **Validierung:** Skript über `data/sessions/**/*.mp3`: 0 Dateien mit `TIT2/TPE1/TALB/COMM`.

#### UX-01 – HIGH – UX – Sprecher-Auswahl im Vergleich ersetzt das gewählte Set implizit und legt serverseitig Kopien an
- **Reproduktion** *[gemessen, lokal]*: `/de/research/spanish/comparison?set_id=3f70273a-…` (gespeichertes Custom-Set „PROMAT Testset (modifiziert 4) · custom“) öffnen → einen Sprecher anklicken. Ergebnis: Dropdown springt auf „PROMAT Testset · curated“, URL-`set_id` wechselt auf eine neue ID, Netzwerk: `POST /sets/<id>/private-copy`, `PUT /sets/<neu>/sessions`. Ebenso: Auswahl eines Presets im Set-Dropdown legt sofort eine neue private Draft-Kopie an (URL-`set_id` ≠ gewählte Option). Insgesamt 8 Draft-Zeilen aus ~6 Interaktionen.
- **Ursache** *[Code]*: `research-comparison.js` `updateSessions → ensureDraft()` forkt jedes nicht-Draft-Set per `/private-copy`; die Set-Auswahl wird über `matchedPresetId` neu aus Items abgeleitet (Fallback auf `source_preset_id`/erstes Preset mit gleichen Items).
- **Auswirkung:** Verletzt die Invariante „Auswahl verändert keine fachlich unabhängigen Filter/Sets implizit“; sichtbares Set wechselt, Nutzer:innen verlieren Bezug zu ihrem gespeicherten Set; DB-Wachstum durch unbeabsichtigte Kopien (laufen ab).
- **Reparaturrichtung:** Dropdown über stabile `source_set_id` abbilden bzw. erst beim ersten echten Edit forken, ohne die sichtbare Auswahl zu ändern.
- **Validierung:** Playwright-Regression: Set wählen → Sprecher togglen → `#pm-comparison-set-select.value` und Optionstext unverändert, kein `private-copy`-Request.
- Sauber verifiziert: Filter (L1/Level), Material-Tab (Wortliste/Text) und Sprecherliste verändern die Set-Auswahl nicht.

#### PERF-01 – HIGH – PERFORMANCE – 5,09-MB-Material-Symbols-Font auf jeder Seite
- **Evidenz** *[gemessen]*: Jede Seite (auch `/login`, `/en/research/french`) lädt `MaterialSymbolsRounded.woff2` (5.094.260 B; Production: Content-Type octet-stream) – größter Einzeltransfer (CSS+JS gesamt ≈ 0,6 MB). Gedrosselt auf 1,6 Mbit/s: DCL 4,6 s (Login) bzw. 9,2 s (Themenseite), dabei wurden auf der Themenseite 12 Icons per Fallback `display:none` gesetzt; auf 400 kbit/s: 15,2 s bis DCL auf `/login`.
- **Ursache** *[Code]*: `modules/navigation/index.js` → `initMaterialSymbolsFallback()` (`material-symbols-loader.js`) erzwingt `new FontFace(...).load()`; Header/Drawer/Player nutzen bereits SVG-Masken, der Font stützt nur ≈ 25 Ligaturen. Nach 2 s `Promise.race` werden Icons dauerhaft ausgeblendet, selbst wenn der Font später ankommt.
- **Auswirkung:** Erstbesuch auf Mobilfunk 5+ s langsamer; Icons verschwinden; unnötiger Traffic bei jedem neuen Besucher.
- **Reparaturrichtung:** Ligaturen durch Inline-SVG (Familie `pm-icon-mask` existiert) ersetzen oder Font auf ≈ 20–40 KB subsetten; mindestens unbedingtes `FontFace.load()` entfernen.
- **Validierung:** Cold-cache Netzwerkprofil `/en` und `/login` unter Fast-3G; keine Icons mit `display:none`.

#### UX-02 – HIGH – UX/ACCESSIBILITY – Dark Mode: Primär-Buttons mit 2,24:1 (u. a. Login „Anmelden“)
- **Evidenz** *[gemessen: axe + Screenshot]*: `.pm-action-button--primary > .pm-action-button__label` `#f7fbff` auf `#77aee6` = **2,24:1** auf `/login`, `/de|en/access-request` (Dark) sowie auf „Neues Set“ in Phänomene. Der Screenshot `login-desktop-dark` zeigt weißen Text auf hellblauem Button. Ebenso Snackbar-Success (`--promat-on-primary` immer `#fff`, Token-Rechnung 2,28:1).
- **Ursache** *[Code]*: `--promat-on-primary` ist theme-unabhängig `#fff`, `--md-sys-color-primary` ist im Dark Mode hell (`#7ab0e8`). Genau die vom Auftrag genannte Fehlerklasse „nur in einem Theme lesbar“.
- **Reparaturrichtung:** `--promat-on-primary` pro Theme definieren.
- **Validierung:** axe `color-contrast` in Dark auf Login/Access-Request/Phänomene = 0.

#### UX-03 – HIGH – UX/ACCESSIBILITY – Nav-Einträge ausgeloggter Besucher:innen auf Korpus-Hubs nahezu unsichtbar
- **Evidenz** *[gemessen: axe, anonym]*: auf `/{de,en}/research/{french,spanish,english,german}` `.promat-panel__nav` / `.pm-nav-pill--muted`: `#c9c7c5` auf `#f7f6f3` = **1,55:1 (Light)**, `#46494f` auf `#1a1d22` = **1,87:1 (Dark)**. Es sind echte Links (Login-Umleitung), keine Disabled-Controls.
- **Ursache** *[Code]*: `--pm-text-muted-strong` (`color-mix(book-muted 28 %, paper 72 %)`) für `.pm-nav__item--muted`/`.pm-nav-pill--muted` bei `requires_research_auth and not is_authenticated`.
- **Hinweis zur Gegenprüfung:** Das Teil-Audit nannte „alle Research-Unterseiten-Links im Drawer“. Meine Stichprobe `a.pm-nav__item--muted` im Drawer ergab 6,56:1/13,9:1 – betroffen sind die Pill-/Panel-Nav der Korpus-Hub-Seiten (axe-belegt), nicht der Drawer insgesamt.
- **Reparaturrichtung:** Muted-Stil mit `--book-muted` (≥ 6,6:1) + Schloss-Icon; `muted-strong` nur für echtes `disabled`.
- **Validierung:** axe auf Korpus-Hub anonym, beide Themes.

### MEDIUM

**CONTENT / PUBLICATION**
- **CONTENT-02 – `design`-Seite ist für `french`/`german`/`english` ein Entwickler-Platzhalter** *[gemessen, Production]*. `public_content.py:552 if language_slug != "spanish"` liefert „…strukturell angelegt, inhaltlich aber noch nicht ausgebaut. Vorbereitung statt Endausbau Die Route existiert bereits mit dem finalen technischen Schlüssel…“ – die einzige öffentliche Research-Seite von drei Korpora. `research-capabilities.md:113` sagt „`design` is content-bearing for all corpora“; Tests prüfen nur `/spanish/design`. Zusätzlich zeigt der deutsche Korpus geschützte Platzhalterseiten, obwohl die Spec geschützte Planungsplatzhalter für retired erklärt. Fix: ehrlicher „Korpus im Aufbau“-Zustand bzw. datengetriebener Inhalt, Test je Korpus, Spec angleichen.
- **CONTENT-03 – Drittanbieter-Einbindungen und Analytics-Cookie nicht in der Datenschutzerklärung** *(juristisch zu prüfen)*. YouTube (nicht `-nocookie`, ohne Einwilligungsschicht) auf Projektseiten, Datawrapper (2 Iframes, zusätzlich Basemap-JSON und Roboto-Fonts von `dwcdn.net`, in Production gemessen) auf `which-pronunciation`; `pm_analytics_state`-Cookie auf allen HTML-Antworten; GoatCounter-Script. `content/legal/impressum_datenschutz.md` erwähnt weder YouTube noch Datawrapper noch dieses Cookie. Hinweis: Die Seite ist derzeit live nicht erreichbar (PUBL-01).
- **CONTENT-04 – Legacy-Stubs `spanish/r` und `soft-spanish-hard-german`**: DE mit 4 Legacy-Blöcken (`hero`, `credits`, `topic_grid`), EN `blocks: []`; auf dem öffentlichen Hub bleibt „Beschreibung folgt.“ als Karte sichtbar. `spanish/r-am-silbenende`: Abschnittsreihenfolge DE ≠ EN.
- **CONTENT-05 – Nutzer-sichtbare Entwicklersprache im Research-UI** (`i18n.py` u. a. „führen Sie scripts/dev-start.ps1 … aus“, „owner-gebundenen … zu leaken“, „in diesem Run … produktiv freigeschaltet“; DE/EN). Dazu Terminologiedrift (EN „Word list / word-list / Wordlist“; DE „Wortliste und Text“ vs. „Satzliste“).

**PUBLICATION / METADATA / CITATION**
- **PUBL-02 – Autor:innenschaft: zwei Modelle, Freitext, ohne Rollen/ORCID, Korpusverantwortung doppelt gepflegt.** Teaching: `metadata.authors` (Strings) und Legacy `credits.authors[{name,role,affiliation}]`, 8× `NN`, `peer_review: [null]`. Research: Verantwortliche als Python-Dict `LANGUAGES` (`public_content.py:42-135`) **und** erneut als Text in `PROJECT_PAGES_CONTENT["team"]`; die Schreibweisen weichen bereits ab („Theresa Fischer, Kathrin Siebold“ vs. „Theresa Fischer, M.A., Prof. Dr. Kathrin Siebold“). Positiv: Plattform-Branding wird nicht automatisch als Autor an Themenseiten gehängt. Es fehlt ein Ort für Herausgeber:in der Teaching-Sprachbereiche, strukturierte Korpus-Creators und sprachspezifische Mit-Autorschaft.
- **PUBL-03 – Lizenz-/Rechtelage fehlt bzw. widerspricht sich** *(Entscheidungsbedarf, siehe §7).* `app/LICENSE` MIT „Copyright 2025–2026 Felix Tacke“; Footer „© 2026 Philipps-Universität Marburg · Hispanistica @ Marburg · Felix Tacke“; Impressum „Inhalte unterliegen dem deutschen Urheberrecht… schriftliche Zustimmung“; keine Lizenzangabe für Teaching-Texte/-Audio/Forschungsdaten/Metadaten; öffentliches GitHub-Repo enthält `content/teaching/**` samt Medien ohne Lizenzdatei; CO.RA.PAN-Audio nur mit Quellenlink.
- **PUBL-04 – Keine Version/kein Datenstand der Korpora.** Upload-Manifest nur `upload_id/built_at/sessions/files`; App kennt nur `APP_VERSION`/Release-Tag (`v0.7`); `research_sets.version` ist eine Set-Revision. Nutzende können nicht angeben, mit welchem Korpusstand sie gearbeitet haben. Kleine Vorstufe: statisches `corpus_version`/`data_as_of` je Korpus, angezeigt und im Zitat.
- **PUBL-05 – Stabile Identität hängt nur am Slug; unbekannte Slugs liefern 302 statt 404.** Keine Ressourcen-ID, keine Alias-Tabelle; Umbenennung leitet zitierte URLs still auf den Hub; gemischte Slug-Politik (`gleitlaute`, `nasalvokale`, `r-am-silbenende` deutsch, `which-pronunciation` englisch; Spec Z. 125 erlaubt sprachspezifische Slugs, `AGENTS.md` verlangt englische technische Slugs). Stabil und gut: Research-IDs (`ES-L-0001-2026-S01`, `person_id`).
- **METADATA-02 – Kein canonical, kein hreflang, Parametervarianten identisch erreichbar.** `?utm_x=1` → 200 gleiche Seite; `?lang=en` auf `/de/…` → 200 deutscher Inhalt; der Sprachumschalter erzeugt selbst `…?lang=en`-URLs; `/de/teaching/` (Slash) → 404; DE/EN-`equivalents` nicht maschinenlesbar verknüpft. OK: `www`→non-www und http→https (301).
- **METADATA-03 – Keine maschinenlesbaren wissenschaftlichen Metadaten.** Head enthält nur charset, viewport, title, application-name, description, theme-color. Kein JSON-LD, Dublin Core, `citation_*`, OpenGraph, `meta author`, `robots`; `created`/`updated` nur als `<span>` (DE `13.05.2026`, EN ISO), kein `<time datetime>`. Autor:in/Datum liegen im YAML bereits vor.
- **METADATA-04 – Eine globale **deutsche** Meta-Description für alle Seiten und Sprachen** *[gemessen]*: `/en` zeigt „Pronunciation Matters ordnet Projektkommunikation, Forschung und Unterricht in einer textzentrierten PROMAT-Oberfläche.“ (`base.html:8`, `branding.py`), auch bei `lang="en"` und auf Themenseiten, obwohl YAML `summary` liefert. Landing-`<title>` doppelt („Pronunciation Matters · Pronunciation Matters“); Platzhalter-`design`-Seiten heißen alle „Design“ ohne Korpuskontext.
- **CITE-02 – Zitat-Titel und -Format driften vom Seitentitel.** EN-Titel „Which pronunciation should you teach?“ vs. Zitat „Which pronunciation should be taught? (topic page)“; DE-Zitat endet mit Punkt, EN nicht; Jahr fest `2026`; `citation.text`/`copy_text` frei getippt.
- **CITE-03 – Kein zentrales „Wie zitieren“; Strukturfeld ungenutzt.** Zitatangebot existiert nur auf einer Themenseite und der Spanisch-Design-Seite; nicht für Plattform, Korpus, Teaching-Sprachbereich, Speaker, Set, Audio. Der Loader kennt `citation.{doi,url}` (das Re-Entry-Audit sprach von „structured citation with DOI field“), aber kein Inhalt nutzt sie, Autor/Titel/Jahr stehen als Freitext, DOI würde als Text statt Link gerendert, der Validator prüft `metadata`/`citation` nicht. UI-Baustein (Admonition `citation` + Copy-Button) ist vorhanden, es fehlen die Daten.

**DATA**
- **DATA-02 – Kanonische Kataloge nicht in Git und nicht in CI.** `data/config/**` ist gitignored (Spec Z. 372 „intentionally not versioned“); CI führt `validate_research_config.py` nicht aus; versionierte Test-Fixtures verwenden dieselben Item-IDs mit anderen Texten (`wl_059`: „think“ vs. „wolf“). Sieben ignorierte Upload-Pakete (2,3 GB) enthalten ältere Kataloge (z. B. French `t_42` abweichend) – Regressionsrisiko beim Re-Upload; `french/wordlist.json` hat gemischte Zeilenenden.
- **DATA-03 – Spanische Design-Seite pflegt 142 Item-Texte hart codiert** (`public_page_content_data.py` ≈ 776–960). Heute 142/142 identisch mit den Katalogen, aber zweite Pflegestelle (Fehlerklasse `théâtre`).
- **DATA-04 – Sprecher-/Session-Metadaten doppelt, DB-Spiegel ohne Leser.** App liest nur `metadata.json`; `research_metadata.py` (DB-Tabellen) wird nur von Import-Skripten genutzt; Feldnamen weichen ab (`exposure_entries[].type` vs. `exposure_type`).
- **DATA-05 – Korpus-Registry und Task-/Level-Vokabulare in vielen Literalen.** ≥ 9 unabhängige Korpus-Registries (`data_conventions.py`, `LANGUAGES`, `admin.py`, `analytics.py TRACKED_CORPORA`, `ACTIVE_RESEARCH_CORPORA` (unbenutzt), `language_config.py`, DB-CHECK u. a.; Reihenfolgen differieren: Research spanish/french/german/english, Teaching spanish/english/french/german); `("wordlist","text")` 9× in `research_player_runtime.py` und in `research-comparison.js:224,1159`; Level-`<select>` A1–B2 (`research_comparison.html:46-50`) vs. `LEVEL_ORDER` A1–C2 und Spec „direct level chips“. Widerspricht `research-capabilities.md:11,126`.
- **DATA-06 – Französischer Text-Katalog: Apostroph-Inkonsistenz und wahrscheinliche Tippfehler.** `t_46` „N'écoutez“ mit ASCII-Apostroph (restliche 836 mit U+2019), kopiert in 11 Session-Alignments; `t_08` „sept insects.“ (in allen 21 FR-Text-Sessions); `t_07` „C'est un drôle d'histoire“. **Editorielle Bestätigung nötig** (Vorlagentext liegt nicht im Repo), kein Auto-Fix.
- **DATA-07 – 11 Sessions nur mit `metadata.json`, ohne Daten.** EN-L-0010, FR-L-0008, FR-L-0022…0029, FR-N-0002 (`tasks: []`); `validate_runtime_tree` besteht; Sprecherkarten ohne abspielbares Material; EN-L-0010 mit `research_consent_signed` null.

**AUDIO / PERFORMANCE**
- **AUDIO-01 – Clip-Ende nur über `timeupdate` (≈ 250 ms): Überlauf** *[Code + Datencheck]*. `research-player.js:1047-1059`. Wortliste/Text-Lücken ≥ 400 ms (Überlauf in Stille), im Interview 13 von 35 Lücken < 250 ms → nächstes Segment hörbar. Validierung: `currentTime` im `pause`-Event im Interview-Modus.
- **AUDIO-02 – `play()` nach asynchroner Arbeit außerhalb der User-Geste** *[unverifiziert, potenziell HIGH auf iOS Safari]*. Player: `ensureAudioMetadata().then(…play())`; Comparison: `await fetchClipUrl` (HEAD) vor `audio.play()`. Nur Chromium validiert. Prüfen: erster Tap auf echtem iPhone.
- **AUDIO-03 – Fehler-/Lade-/Stall-Rückmeldung unzureichend.** Player: kein `error`/`stalled`/`waiting`-Handler, `play()`-Fehler werden verschluckt (`.catch(() => false)`), kein Ladezustand – 404 oder abgelaufene Session (Login-HTML als Audio) wirkt wie „nichts passiert“. Comparison *[gemessen]*: bei 404 erscheint im Feedback-Element der **rohe Text „Not Found“** (nicht der lokalisierte Key `research.comparison.clip_unavailable`), das Element ist weder `role=status` noch `aria-live`.
- **PERF-02 – Keine Kompression, jede statische Datei wird bei jeder Navigation revalidiert** *[gemessen, Production]*. CSS (`30_components.css` 257 KB), JS, Fonts, SVG ohne `Content-Encoding` (nur HTML gzip); `Cache-Control: no-cache` auf allen statischen Dateien (ETag/304 funktioniert) → ≈ 35–40 bedingte Requests je Navigation. Repo-CSS 434 KB roh / 66 KB gzip. nginx liegt außerhalb des Repos (Operator-Task); `base.html` nutzt `url_for('static')` statt des vorhandenen `static_asset()` (`?v=<mtime>`).
- **PERF-03 – Landing-Bilder überdimensioniert** *[gemessen]*: `unterricht_01.png` 1525×1097, 2,2 MB, ohne `width/height`, `loading`, `decoding`; kein WebP/AVIF.
- **PERF-04 – 1,5 MB unsubsettete Variable-Fonts, kein Preload** *[gemessen]*: Inter 352 KB + Source Serif 4 429 KB Pflicht zum First Paint, Italics weitere ≈ 735 KB.
- **PERF-05 – Comparison-HTML baut Session-Katalog ohne Cache** *[lokal gemessen]*: `research_views.py:1514-1526` lädt alle Sessions × 2 Tasks unzwischengespeichert: 575 ms warm / 814 ms kalt (Spanisch, 48 Bundles); Prod (Linux) wahrscheinlich schneller, gleiche Größenordnung.

**UX / ACCESSIBILITY / RESPONSIVE**
- **RESPONSIVE-01 – Mobile (390 px): Inhalte laufen aus dem Viewport** *[gemessen]*. Phänomene-Preset/Set (`/research/spanish/phenomena/presets|sets/…`): Overflow 275 px, der „Weitere/…“-Toggle (`pm-comparison-more-filters`) liegt außerhalb des Viewports (Screenshot: Overflow-Aktion rechts außerhalb der Kartenbreite); Player (wordlist/text): 73–75 px (`pm-info-tip` Set-Hilfe + `pm-comparison-filter-select`); Comparison: 11 px (Rate-Slider). Jeweils Light und Dark, de und en. Anonyme Seiten und Production-Smoke: kein Overflow.
- **ACCESSIBILITY-01 – Fokusindikator schwach/fehlend** *[Code/Token-Rechnung, nicht im Browser verifiziert]*: `.pm-action-button/.pm-nav-pill/.pm-cta-link` `outline: 3px solid color-mix(accent-2 38 %, transparent)` ≈ 1,46:1 (Light) / 1,95:1 (Dark) und überschreibt die globale 2-px-Regel; `.promat-panel__language-link:focus-visible { outline:none }` ohne Ersatz.
- **ACCESSIBILITY-02 – Speakers-Filterformular doppelt gerendert, doppelte IDs** *[gemessen]*: `pm-filter-level`, `-l1`, `-target_country_stay`, `-gender` je 2× im DOM (mobiles `<details>` + Desktop, `research_speakers.html:22,26`); Labels binden an das erste (versteckte) Element.
- **ACCESSIBILITY-03 – Vergleichsmodus im Player: Sprecher nicht unterscheidbar** *[Code]*: Spaltenköpfe `aria-hidden`, Seek-Buttons nur mit Item-Text benannt; aktives Item ohne `aria-current`. Comparison-Matrix: alle Buttons „Clip abspielen“/„Zeile abspielen“ ohne Item-/Sprecher-Kontext (berechneter Label ungenutzt).
- **ACCESSIBILITY-04 – Statusmeldungen nicht als Live-Region** *[gemessen/Code]*: `data-comparison-feedback`/`-status-text` ohne `role`/`aria-live` (bestätigt: `role=null`, `aria-live=null`); Snackbar erzeugt Live-Region mit Inhalt zusammen; Snackbar-Texte „Schließen“/„OK“ hart deutsch.
- **ACCESSIBILITY-05 – Fokusverlust nach Re-Render und In-Place-Navigation** *[Code]*: Comparison rendert Sprecher-/Materiallisten per `innerHTML` neu; Player `replaceWith` ohne Fokus-Rückgabe; aktives Material als `disabled` + `aria-pressed="true"` (nicht fokussierbar, widersprüchlich).
- **ACCESSIBILITY-06 – Kein `lang` auf fremdsprachigem Material** *[Code/Live]*: spanische/französische/englische Items und Transkripte ohne `lang` (WCAG 3.1.2; Live-Themenseite: 0 Treffer).
- **ACCESSIBILITY-07 – Set-Dropdown navigiert bei `change`** *[Code]* (`research-player.js:160-166`; WCAG 3.2.2): in Chrome/Edge löst jeder Pfeiltastendruck einen Seitenwechsel aus.
- **ACCESSIBILITY-08 – axe „serious“ `label-content-name-mismatch`** *[gemessen: 188 lokale/40 Production-Seiten]*: `.promat-site-title` und `.promat-panel__language-link` – `aria-label` enthält nicht den sichtbaren Text (WCAG 2.5.3, Sprachsteuerung).
- **UX-04 – Akzent-/Statusfarben haben keine Dark-Entsprechung** *[axe + Token]*: `--pm-text-accent` `#a15a95` auf Dark 3,27–3,55:1 (Bereichsnavigation, Segmented-Control, Material-Choice, Filter-Chips, Badges), Light 3,94–4,4:1; Native-Teal `#18677a` Badge auf Dark 2,24:1; `.pm-profile-session__selected` 2,12:1; Teaching-Karten-Aktion Dark 4,44:1; Light-Karten `.pm-card__title/__text` 3,85:1 (Teaching-Hub French); Teaching-Audio-Token `#777` auf Weiß 4,47:1.
- **UX-05 – Undefinierte CSS-Variablen brechen Stile still** *[Code]*: `--book-danger` nie definiert (26 Stellen fallen auf `#b54747`, im Dark 3,10:1); `--md-sys-color-tertiary-container` (Copy-Success `!important` → transparent), `--pm-accent-rose-strong`, `--pm-ink` (6 Schatten), `--pm-space-md` u. a. Fehlerklasse „nur in einem Theme korrekt“.

### LOW

- **UX-06 – Themenumschaltung:** `color-scheme: light dark` fix, `theme.js` ignoriert OS-Präferenz (Default `light`), Scrollbars/Select-Popups folgen dem OS statt dem Toggle *[Code, unverifiziert]*.
- **UX-07 – Sprechergruppen-Chip verwirft gruppenspezifische Filter** (`level`, `l1`, … beim Wechsel Lernende↔Native; nicht wiederhergestellt) *[Code/Test-Client; Produktentscheidung]*.
- **UX-08 – Player-In-Place-Navigation nutzt `replaceState`** (Zurück verlässt den Player); kein Mitscrollen der aktiven Zeile bei langen Listen; Dauer `0:00`/Slider disabled bis zum ersten Play (`preload="none"`) *[Code]*.
- **UX-09 – „Aktive Zeile/Token“-Hervorhebung nur schwach und farbgebunden** (`rgba(24,103,122,.09)` 1,06–1,13:1, kein `aria-current`) *[Code, braucht visuelle Prüfung]*.
- **AUDIO-04 – Schnelle Doppelklicks während Metadaten laden** können zwei konkurrierende Clip-Sessions erzeugen (`clearClipPlayback` vor `clipCleanup`) *[Code]*. Im Browser nicht reproduziert: 6 schnelle Klicks in der Comparison enden deterministisch mit einem Clip, ein `Audio`-Objekt.
- **AUDIO-05 – Comparison-Row-Play: je Clip HEAD + GET seriell** (`cache:"no-store"`, hörbare Lücken); jeder `render()` (auch Tippen in der Suche, ohne Debounce) stoppt die Wiedergabe; `beforeunload`-Listener verhindert bfcache in Firefox. Server: mp3 mit `Cache-Control: no-cache, max-age=0`, ohne ETag (`etag=False`), Dateien 20–35 KB → vernachlässigbar.
- **AUDIO-06 – Player-Leaks bei In-Place-Navigation:** `desktopMedia`-Listener nie entfernt, verwaiste `playClip`-Promises; Teaching-Mini-Player ohne `error`-Handler, englische Fallback-Labels fest (`Play audio`).
- **PERF-06 – Speakers-Hover-Prewarm** baut je gehovertem Eintrag den Player-Seite-Build (50–260 ms) ohne Hover-Intent/Concurrency-Limit *[Code, potenziell relevant]*.
- **PERF-07 – Totes/ungenutztes Gewicht:** `htmx.min.js` (85 KB) auf jeder Seite ohne `hx-*`-Nutzung; `GET /auth/session` auf jeder Seite ohne Konsument; tote JS-Dateien (`auth/password_reset.js` mit spanischen Strings, `como-citar.js`, `corpus-guia.js`, `modules/auth/login.js`, jQuery 163 KB); ungenutzte Bilder im Repo/Image (`forschung_01.png` 1,08 MB u. a.); 9 render-blockierende Stylesheets.
- **ACCESSIBILITY-09 – Kleinere Punkte** *[axe/Code]*: doppelte Banner-/unbenannte Landmarks (`header#top-app-bar` + `role=banner`, axe `landmark-*` auf allen Seiten); `heading-order` (Teaching-Admonitions h1→h3, Comparison h2→h4); `aria-allowed-role` (`role=navigation` auf Drawer); verschachtelte interaktive Elemente im Player (`div[role=button]` mit `button`); Slider ohne `aria-valuetext`; `role="menu"` ohne Pfeiltasten; Toggles ändern Zustand **und** Namen; `.pm-info-tip__trigger` 16 px; Reduced-Motion nur teilweise; kein Skip-Link; hartcodierte deutsche `aria-label`/Texte (`Pfad`, `Schnellzugriffe`, `Sprachbereiche`).
- **DATA-08 – Herkunftsländer/Vokabulare nicht lokalisiert:** `ORIGIN_COUNTRY_LABEL_KEYS` kennt nur `spain`/`mexico` – DE-Profil zeigt „Herkunftsland: France“ **und** „Standardvarietät: Frankreich“; Freitext-Länder (`Marocco`, `USA`), `additional_languages` (`CA`, `QU`) unvalidiert; 7 Legacy-Variety-Aliasse ohne Daten.
- **DATA-09 – Alignment-Auffälligkeiten:** FR-L-0005 Text: 8 Items mit Span und MP3, aber 0 Tokens; 7 Interview-Segment-Überlappungen von 1 ms; 1 NFD-Token (FR-L-0002 seg_010), 1 ZWSP (ES-L-0014 seg_012); EN-L-0008 `t_01` bewusst ausgelassen (nur im Importer-Code dokumentiert).
- **DATA-10 – Tote/Legacy-Pfade gegen Spec/`AGENTS.md`:** unbenutzte Funktionen/Keys (40 ungenutzte i18n-Keys, `_research_feature_cards`, `project_url=https://example.invalid/promat`), Legacy-Routen (`/auth/konto`, `/auth/reset-password/*`, `/auth/change-password`, `/datenschutz`), Logout per GET; `ensure_curated_test_set` (Spanisch fest) in Produktionsmodul; `organize_batch_working_tree.py` in zwei divergierenden Fassungen (getrackt vs. ignoriert); `phenomena_presets.json` (legacy) mit ASCII-transliteriertem Deutsch.
- **DATA-11 – `validate_teaching_content.py` zu schwach:** prüft nur Manifest/Hub/Medien/Equivalents, nicht DE/EN-Parität, verwaiste Medien (4 Dateien öffentlich ausgeliefert, davon 2 mit Session-ID `es-n-0004-2026-s01` im Dateinamen, Einwilligung `yes`), Platzhalter, `NN`, `status: draft` oder Front-Matter.
- **CONTENT-06 – Kleinteiliges Content-Inkonsistenzen:** Hub-Titelmuster uneinheitlich („Spanisch: Themenseiten“ vs. „Englisch: Aussprache unterrichten“), `lead` vs. `overview_intro`; Navigationsreihenfolgen Research/Teaching abweichend; „curated/custom/Draft/Preset“ in DE-UI englisch; MAR.ELE-Datierung „2024–2025“ (About) vs. „2023–2024“ (Literaturangabe) vor externer Zitierung klären.

**Anmerkung Zählung:** Die Tabelle in §1 zählt die oben als eigene Überschriften geführten Findings (HIGH 9, MEDIUM 37, LOW 15; insgesamt 61); LOW-Sammelpunkte (ACCESSIBILITY-09, PERF-07 etc.) zählen als je ein Finding.

---

## 4. Data Integrity Matrix

| Datenklasse | Kanonische Quelle | Verbraucher | Validierung vorhanden? | Bekannte Inkonsistenz | Drift-Risiko | Handlungsbedarf |
|---|---|---|---|---|---|---|
| Task-Items (IDs, Texte, Reihenfolge) | `data/config/research_player/{lang}/task_catalogs/*.json` (gitignored) | Player, Comparison, Sets, Phänomene, Alignment-Erzeugung | Loader + manuell `validate_research_config.py` (nicht in CI) | `t_46` Apostroph, `t_08` „insects“, `t_07`, gemischte Zeilenenden | hoch (nicht versioniert, alte Pakete) | DATA-02, DATA-06 |
| Itemtexte auf Spanisch-Design-Seite | Duplikat in `public_page_content_data.py` | Design-Seite | keine | heute 142/142 identisch | mittel | DATA-03 |
| Itemtexte in Alignments | Kopie je Session `alignment/{task}.json` | Player | `validate_runtime_tree` nur Pfade | keine (0 Textabweichungen) | mittel (Fix = Datenmigration) | beobachten |
| Sets | Postgres `research_sets` + `research_set_items` (nur Item-ID) | Phänomene, Comparison, Player | Item-Referenzprüfung beim Laden | keine Katalogrevision gespeichert; UX-01 erzeugt Kopien | mittel | UX-01 |
| Phänomene-Presets | `phenomena_presets.json` (legacy, ungenutzt) | nur Tests | Loader+Tests | ASCII-transliteriertes Deutsch | niedrig | DATA-10 |
| Person-/Session-Metadaten | `data/sessions/**/metadata.json` | Speakers, Player, Comparison | `_validate_session_identity` (zur Laufzeit) | `CA`/`QU`, Länder/Regionen frei, 11 Sessions ohne Daten | mittel | DATA-07/08 |
| Person-/Session-Metadaten (DB-Spiegel) | `research_people/_sessions/_session_exposures` | nur Importer | Payload-Validierung | `type` vs. `exposure_type` | mittel | DATA-04 |
| Vokabulare (Varietäten, L1, Tasks, Level) | `config/data_conventions.py`, `research_capabilities.py` | Importer, Runtime, Views, JS, Templates | Workbook-Reader; Runtime teilweise | Template/JS-Literale, Level-Select A1–B2, Legacy-Aliasse | mittel | DATA-05 |
| Korpus-/Sprachnamen, Teams | `public_content.LANGUAGES` + ≥ 8 weitere Literale | Seiten, Admin, Analytics | keine | Team-Schreibweisen driften schon | mittel | DATA-05, PUBL-02 |
| Audio | `data/sessions/**/*.mp3` | Player, Prod-Paket | `validate_runtime_tree` (Namen/Suffixe) | **ID3-Titel mit Namen** | hoch (Datenschutz) | DATA-01 |
| Teaching-Content/-Metadaten | `content/teaching/**/*.yaml` | Teaching-Seiten | `validate_teaching_content.py` (CI) | Autorenschema, `NN`, `status` wirkungslos, Zitat-Titel | niedrig-mittel | CONTENT-01, DATA-11 |
| i18n-Strings | `i18n.py TRANSLATIONS` | alle Templates | Schlüsselparität (907/907, nicht in CI) | ungenutzte Keys, Legacy-Variety-Keys | niedrig | CONTENT-05 |
| Bibliographische Daten | Teaching-`citation`, Design-Seite (Python), `LANGUAGES` | Seiten | keine | www vs. non-www, Titeldrift | mittel (DOI-Vorbereitung) | CITE-01..03 |
| Rechtstexte | `content/legal/impressum_datenschutz.md` | `/impressum`, `/privacy` | Markdown-Splitter validiert Überschriften | Production 500 | – | PUBL-01 |

---

## 5. Cross-Language Matrix

Nur reale strukturelle Unterschiede; inhaltliche Unterschiede (Umfang der Korpora, Sprachen) sind kein Befund.

| Aspekt | spanish | french | german | english |
|---|---|---|---|---|
| Routing | generisch `/{ui}/research/{corpus}/…` + gleiches Gate | identisch | identisch | identisch |
| Research `design` (öffentlich) | vollständiger Inhalt | **Platzhalter** (CONTENT-02) | **Platzhalter** | **Platzhalter** |
| Research Speakers/Comparison/Phenomena | produktiv (24 Sessions) | produktiv (31), Phänomene-Seite erreichbar, keine Presets | **Platzhalter** (0 Sessions, keine Player-Config) | produktiv (10), keine Natives |
| Teaching | Hub + 1 fertig, 1 Scaffold (öffentlich), 2 Legacy-Stubs (nicht öffentlich) | Hub + 3 Scaffolds öffentlich (CONTENT-01) | Hub, leerer Zustand | Hub, leerer Zustand |
| Datenmodell | 24 Sessions (19 L/5 N), `es/ec/mx/cl_std` | 31 (29/2), `fr_std`, Herkunft „France“ unlokalisiert (DATA-08) | – | 10 (10/0), keine Varietät/Herkunft |
| Player | gemeinsame Capability-Schicht | identisch | nicht testbar | identisch |
| Sets | generisch; Spanisch-Testset-Seed fest codiert (`research_sets.py:1462`) | generisch | Phänomene benötigen Kataloge (fehlen) | generisch |
| Navigation | gleiche vier Seiten/Reihenfolge; Teaching-Reihenfolge hart (spanish, english, french, german) ≠ Research-Reihenfolge | wie spanish | wie spanish | wie spanish |
| Metadaten/Verantwortliche | Karte + Team-Seite doppelt gepflegt | wie spanish | wie spanish | wie spanish; DE-Summary enthält „intelligibility“ |
| Zitation | nur Teaching-Thema (falsche URL) + Design-Seite | keine | keine | keine |
| UX-Grundfunktionen | gleiche Komponenten; Mobile-Overflow in Player/Phänomene/Comparison (RESPONSIVE-01) in allen Korpora identisch | identisch | – | identisch |

Strukturelle Sonderfälle im Code: `public_content.py:552` (Design-Inhalt nur `spanish`), `research_capabilities.py:234` (`== "spanish"`, laut Spec sanktioniert), `research_sets.py:1462` (Spanish-Testset), Teaching-Reihenfolge `public_content.py:414-419`. Templates/JS enthalten keine Korpus-Verzweigungen. Auth-/Public-Grenze identisch für alle Korpora (verifiziert).

---

## 6. UX / Accessibility Matrix

Legende: ✔ geprüft ok · ⚠ Befund · – nicht anwendbar/nicht geprüft. Kontext: lokal Chromium; Screenreader nicht getestet.

| Komponente | Desktop | Mobile (390) | Light | Dark | Keyboard | Semantik/SR | Status/Feedback |
|---|---|---|---|---|---|---|---|
| Header / Navigations-Drawer | ✔ (44 px) | ✔ | ⚠ Hub-Nav 1,55:1 (UX-03) | ⚠ 1,87:1 | ⚠ Language-Link ohne Fokus (A11Y-01) | ⚠ doppelte Banner, `label-content-name-mismatch` (A11Y-08/09) | – |
| Sprachumschalter DE/EN | ✔ | ✔ | ✔ | ✔ | ⚠ Fokus (A11Y-01) | ✔ `lang`, `aria-current` | – |
| Theme-Toggle | ✔ | ✔ | ✔ | ✔ | ✔ | ⚠ Zustand+Name doppelt | ✔ persistiert, kein FOUC |
| Login / Access-Request | ✔ | ✔ | ✔ | ⚠ Primär-Button 2,24:1 (UX-02) | ✔ | ✔ Labels; Fehler nicht `aria-describedby` | ✔ `role=alert` |
| Speakers-Liste/Filter | ✔ | ⚠ Filter doppelt (A11Y-02) | ✔ | ⚠ Chips/Badges (UX-04) | ⚠ Fokusverlust nach Toggle | ⚠ doppelte IDs | ✔ Leerzustände |
| Comparison (Sprecher-/Set-/Filterwahl) | ✔ | ⚠ 11 px Overflow | ✔ | ⚠ Akzentfarben | ⚠ Fokusverlust | ⚠ Heading-Order, Buttons ohne Kontext | ⚠ Set-Wechsel implizit (UX-01); Fehler nicht Live (A11Y-04) |
| Comparison-Matrix/Play-Row | ✔ ein Audio-Objekt, deterministisch | ✔ | ✔ | ✔ | ✔ | ⚠ identische Button-Namen | ⚠ 404 → roher Text „Not Found“ |
| Player (Wortliste/Text/Interview) | ✔ | ⚠ 73–75 px Overflow | ✔ | ⚠ Material-Choice 3,4:1 | ⚠ Select `change`-Navigation | ⚠ Slider ohne `aria-valuetext`, kein `lang` | ⚠ kein Error/Loading (AUDIO-03), `0:00` bis Play |
| Phänomene-Editor/Preset/Set | ✔ | ⚠ 275 px Overflow, Overflow-Aktion außerhalb | ✔ | ⚠ „Neues Set“ 2,24:1; Badges | ✔ native Dialoge | – | ✔ |
| Dialoge | ✔ native `<dialog>`, Fokusfalle, Esc, Fokus zurück | ✔ | ✔ | ✔ | ✔ | ✔ | – |
| Teaching-Blöcke (Admonition, Expandable, Fußnoten) | ✔ | ✔ | ⚠ Hub-Karten 3,85:1 | ⚠ Karten-Aktion 4,44:1 | ✔ | ⚠ Admonition-`aside`-Landmarks, Heading h1→h3, kein `lang` | ✔ |
| Teaching-Mini-Player | ✔ `preload=none` | ✔ | ⚠ Token 4,47:1 | ✔ | ✔ | ⚠ kein `aria-valuetext` | ⚠ kein Error-Handler |
| Status-/Empty-/Placeholder-Seiten | ⚠ Entwicklersprache (CONTENT-02/05) | ⚠ | – | – | – | – | ⚠ |

Trennung der A11y-Befunde: **automatisch belegt (axe):** color-contrast, label-content-name-mismatch, landmark-*, heading-order, aria-allowed-role (aria-prohibited-attr auf Speakers). **Manuell/Code nachvollziehbar:** A11Y-01..07, UX-01. **Theoretisch (nicht als Befund gezählt):** `forced-colors`, redundantes `aria-modal` auf `<dialog>`, `aria-current="false"` auf Nav-Links.

---

## 7. Publication Readiness Matrix

Skala: ja / teilweise / nein.

| Ebene | eindeutige Identität | Autor:in | Titel | Jahr | stabile URL | strukturierte Metadaten | Version | Zitation möglich |
|---|---|---|---|---|---|---|---|---|
| Gesamtplattform | teilweise (Name/Domain; kein formaler Titel/Untertitel, Laufzeit „2026–“ nicht definiert) | teilweise (Projektleitung im Impressum – live 500; Footer „Felix Tacke“; kein Autor/Editor-Modell) | teilweise (Landing-`<title>` doppelt; Client überschreibt Titel – METADATA-01) | teilweise (`footer_meta_year` fest „2026“) | teilweise (`/de`, `/en` stabil; `/` = 302) | nein | teilweise (App-Tag `v0.7`) | nein |
| Research-Sprachkorpus (spanish) | teilweise (Slug, Session-IDs, keine Korpus-ID) | teilweise (Karten + Team-Seite doppelt, driftend) | teilweise (UI-Label „Spanisch-Korpus“; Design-Seite mit Titel) | teilweise (nur Aufnahmejahr in Session-ID) | ja für `design`; Rest login-geschützt | nein | nein (PUBL-04) | teilweise (Design-Seite mit Zitat, Jahr fest; Daten nein) |
| Research-Sprachkorpus (french / english / german) | wie spanish | Karten/Team-Seite | nein (Design-Seite „Design“-Platzhalter) | nein | ja (Platzhalter) | nein | nein | nein |
| Teaching-Sprachbereich (spanish/french/english/german) | teilweise (`/{ui}/teaching/{lang}`; Manifest ohne Titel/Verantwortliche) | nein (kein Herausgeber auf Hub-Ebene) | teilweise („Spanisch: Themenseiten“) | nein | ja | nein | nein | nein |
| Themenseite `which-pronunciation` | teilweise (Slug + `equivalents`, keine Ressourcen-ID) | ja (Felix Tacke, Freitext, ohne Rolle/ORCID) | ja (Server) / **nein** (nach JS, METADATA-01) | ja (`created`/`updated` sichtbar; Zitatjahr fest) | ja (Slash → 404; unbekannt → 302) | teilweise (YAML strukturiert; HTML nur `<span>`) | nein | teilweise (Zitat vorhanden, **URL falsch**, Titel driftet) |
| Themenseite Entwurf (`NN`) | teilweise | nein (`NN`) | ja | teilweise | ja (sollte nicht öffentlich sein) | nein | nein | nein (CONTENT-01) |
| Design-Seite Spanisch | teilweise | ja im Zitat (Text im Python-Dict) | ja | teilweise (Zitatjahr 2026) | ja | nein | nein | ja (lebende URL ohne Version) |
| Sprecherprofil | ja (`person_id`) | n/a (pseudonymisiert) | nein | nein | stabil, geschützt | DB-/JSON-Felder, nicht publikationsreif | nein | nein |
| Session / Player | ja (`session_id`) | `recorded_by` intern, nicht angezeigt | nein | Aufnahmejahr in ID | stabil, geschützt | `metadata.json` strukturiert | nein | nein |
| Set / Vergleich | ja (`set_id`, ownergebunden) | Owner | Label | `published_at` | geschützt | DB | Set-Revision ohne Korpusbezug | nein |
| Audio-Item | ja (Session+Task+Item-ID) | nein | Item-Label | nein | stabil, geschützt | `alignment/*.json` | nein | nein |

**Zitierarchitektur-Bewertung (D1–D8):** Die Hierarchie Plattform → Sprachkorpus/Teaching-Bereich → Ressource ist **konzeptionell durch die Routen bereits angelegt**, aber **nicht in Metadaten abgebildet**: weder Plattform- noch Bereichsebene hat einen strukturierten Datensatz, und nur die Ressourcenebene hat (ungeprüfte, falsche) Zitierangaben. Autor:innenschaft vs. Plattformherausgeberschaft lassen sich im Teaching-YAML trennen (positiv), es fehlt aber ein Ort für Bereichs-Verantwortliche und Rollen. DOI-Bereitschaft: Teaching-Loader ist additiv erweiterbar (unbekannte Keys werden ignoriert), die Design-Seite als Python-Dict und die Korpora ohne Versionsmodell müssten vorher strukturiert werden.

**Empfohlene kleine Metadatenarchitektur (Richtung, nicht umgesetzt):** Eine Quelle (`resource_id`, `resource_type`, `creators[]`, `editor_platform`, `version`/`date_published`/`date_modified`, `license`, `canonical_url`, `is_part_of[]`) – im Plan `docs/plans/storage_preservation_architecture_plan.md` §11 bereits skizziert und in `docs/spec/` zu übernehmen; je Ebene ein kleiner Block (Plattform, Sprachressource, Einzelressource); **ein** Partial für `<head>` mit: serverseitig korrektem `<title>`, lokalisierter `description`, `canonical`, `hreflang` nur bei vorhandenem Äquivalent, `noindex` für Entwürfe, **ein** JSON-LD-Block (schema.org), `<time datetime>`; Zitat **generiert** statt getippt; optional minimale `citation_*` nur für Themen-/Design-Seiten nach Zotero-Test. **Nicht empfohlen:** zusätzlich Dublin Core (Doppelpflege), Microdata/RDFa, OAI-PMH, Twitter-Cards, DataCite als Laufzeitmodell (erst als Export beim Deposit), `CITATION.cff` für Webseiten.

**Versionierung (D6) – benötigter Grad:** `version` + `date_modified` je Ressource, `data_as_of` je Korpus; Plattform-Tag bleibt App-Version. Keine weitere Infrastruktur nötig.

**Lizenz-Entscheidungsbedarf (nicht entschieden):** (1) Rechteinhaber/Publisher: Universität vs. Person (Footer/LICENSE/Impressum widersprechen sich); (2) Code (`app/`, MIT) und Abgrenzung zu `content/`; (3) Teaching-Texte; (4) Teaching-Audio (Eigenaufnahmen vs. CO.RA.PAN-Auszüge, Einwilligungen); (5) Forschungsdaten (Audio/Alignments/Metadaten): Zugang bleibt geschützt, Lizenz/Zugangsklausel hängt an Einwilligung und Re-Identifikationsrisiko; (6) separate Metadatenlizenz; (7) Sichtbarkeit von `content/teaching/**` im öffentlichen GitHub-Repo ohne Lizenzdatei.

---

## 8. Priorisierung

### P0 – vor weiterer öffentlicher / produktiver Nutzung beheben
- PUBL-01 Legal-Seiten 500 (Deploy).
- CONTENT-01 Draft-/`NN`-Themen öffentlich.
- CITE-01 Zitat-URL der einzigen zitierbaren Themenseite.
- METADATA-01 Titelüberschreibung (Voraussetzung für Zitierbarkeit/WCAG 2.4.2).
- DATA-01 ID3-Namen – zunächst Klärung (Teilnehmende?), dann Strippen vor weiterem Datenzugang/Paketexport.

### P1 – zeitnah
- UX-01 (Set-Fork bei Sprecherwahl), UX-02/UX-03 (Dark-/Hub-Kontrast), PERF-01/PERF-02 (Font, Kompression/Caching; nginx-Operator), RESPONSIVE-01 (Mobile-Overflow), CONTENT-02 (Platzhalter-`design`), CONTENT-03 (Datenschutz ↔ Drittanbieter/Cookie – nach rechtlicher Prüfung), AUDIO-03 (Fehlerfeedback), ACCESSIBILITY-02/04/08 (doppelte IDs, Live-Regionen, Name-Mismatch), METADATA-02/03/04 + PUBL-02/CITE-02/03 (kleine Metadatenarchitektur inkl. Autorenmodell und generiertem Zitat), DATA-02 (Katalog-Versionierung/CI), DATA-06 (editorielle Klärung).

### P2 – sinnvoll, nicht dringend
Rest der MEDIUM/LOW: PUBL-03 (Lizenzentscheidung – Projektseite), PUBL-04/05, DATA-03/04/05/07, AUDIO-01/02 (nach Gerätetest), PERF-03/04/05, ACCESSIBILITY-01/03/05/06/07, UX-04/05, alle LOW.

### Kein Handlungsbedarf (geprüft, belastbar in Ordnung)
- **Daten:** 6 Kataloge (eindeutige IDs, sequentiell, NFC, kein BOM/NBSP/ZW); Catalog ↔ 54+54 Alignments ↔ Item-MP3s ↔ Metadaten ohne unbekannte/verwaiste IDs oder Textabweichungen; alle 65 Person-/Session-IDs formgerecht, L/N ↔ `speaker_type`, Jahr, Korpus-Code ok; keine verbotenen Dateitypen (WAV/TextGrid/XLSX) in `data/sessions`; MP3 durchgehend MPEG-1 L3 160 kbit/s CBR 48 kHz mono, keine 0-Byte-Dateien, keine Hash-Duplikate; **`théâtre`-Fehlerklasse: 0 Vorkommen von `théatre`/NFD/`theatre` in `data/`, `app/`, `content/`, Dev-PG-Verzeichnis**; Accent-Strip-Near-Duplicates nur legitime Minimalpaare.
- **i18n:** 907/907 Keys, identische Platzhalter, keine Umlaut-Transliteration, keine fehlenden referenzierten Keys; Legal-Markdown de/en strukturgleich; Projekt-/Design-Seiten-Dicts vollständig.
- **Routing/Auth:** `design` + Korpus-Root öffentlich, alle übrigen Research-/Player-/Audio-Routen redirecten für alle 4 Korpora × 2 Sprachen vor dem Rendern auf `/login?next=…`; `/teaching-media` weist `..`/unbekannte Typen ab; http→https, www→non-www 301.
- **Audio:** ein `Audio`-Objekt für N×M Matrix; kein eager Preload; Range 206 mit `Accept-Ranges`; keine Blobs; exklusive Wiedergabe; Row-Play wechselt sequenziell Sprecher, Toggle stoppt, Clip unterbricht Row; Navigation beendet Wiedergabe sauber; 6 schnelle Klicks → ein deterministischer Clip; kein Overflow/Layoutfehler auf anonymen Seiten und Production-Smoke.
- **A11y-Basis:** `<html lang>`, native Dialoge, Breadcrumbs `aria-current`, Auth-Alerts, Tabellen-`scope`, Expandables/Fußnoten, Alt-Texte, keine unbeschrifteten Formularfelder.
- **Themen:** Admonition-/Teaching-Flächen kippen im Dark Mode korrekt (≥ 10,9:1); kein FOUC.
- **Tests:** 892 von 893 grün; Governance- und Teaching-Validator grün.

---

## 9. Repair Plan

Fünf klar abgegrenzte Runs; Reihenfolge nach Risiko.

**Run R1 – Production-Hotfix & Titel/Zitat-Basis** *(Sonnet 5.5 Low)*
- Scope: Deploy-Stand mit `content/legal/` (PUBL-01) + Post-Deploy-Smoke/Image-Smoke; `page-title.js` entfernen/entschärfen (METADATA-01); `status: draft` ↔ Öffentlichkeit (CONTENT-01) bzw. `is_public: false` in 5 Scaffolds; Zitat-URL in `which-pronunciation` korrigieren (CITE-01, interimistisch, ohne Generator).
- Validierung: curl 200 auf Legal; Playwright-Titeltest; Test über Content-Baum; Test „Zitat-URL löst auf“.

**Run R2 – Daten-/Audio-Hygiene** *(Sonnet 5.5 Medium)*
- Scope: ID3-Strippen (Konvertierung + Re-Publish, Validator-Allowlist) nach inhaltlicher Klärung (DATA-01); Katalog-Lint (Apostroph/Rechtschreibung → Liste für editorielle Prüfung, kein Auto-Fix), `validate_research_config.py` in CI gegen Golden-Copy bzw. Katalog-Revision im Paketmanifest (DATA-02, DATA-06); Metadaten-only-Sessions explizit markieren/ausschließen und Consent prüfen (DATA-07).
- Validierung: Tag-Scan = 0; CI-Job grün; Session-Liste ohne leere Sprecherkarten.

**Run R3 – UI-Korrekturen (Theme, Mobile, A11y, Comparison-Set)** *(Sonnet 5.5 High)*
- Scope: Tokens (`--promat-on-primary`, `--pm-text-accent`, Native-Teal, `--book-danger`, Muted-Nav, Fokusringe, undefinierte Variablen: UX-02..05, A11Y-01); Mobile-Overflow (RESPONSIVE-01); doppelte Filterform-IDs, Live-Regionen, Namen/`lang`-Attribute, Select-`change`-Navigation (A11Y-02..08); UX-01: Set-Auswahl stabil + Fork erst beim ersten Edit; AUDIO-03: lokalisierte Fehler-/Ladezustände, `error`-Handler im Player.
- Beachte `AGENTS.md` UI Change Discipline: DE+EN, Browser-Pass mit Screenshots, Regressionstests für exakte Reihenfolge/Labels, Regression-Check einer unveränderten Seite derselben Komponentenfamilie.
- Validierung: axe (beide Themes, DE/EN, Desktop/Mobile) ohne `serious`; Playwright-Regressionen (Set bleibt, kein `private-copy`); Screenshot-Durchgang.

**Run R4 – Performance-Basis** *(Sonnet 5.5 Medium; nginx-Teil durch Operator)*
- Scope: Material-Symbols-Ligaturen → SVG oder Font-Subset, unbedingtes `FontFace.load()` entfernen (PERF-01); `static_asset()` in `base.html`; nginx-Vorgaben dokumentieren (gzip/brotli, `font/woff2`, `immutable` für fingerprinted Assets) im Deploy-Runbook (PERF-02); Landing-Bilder (PERF-03); Fonts subsetten/preloaden (PERF-04); Cache für Comparison-Katalog (PERF-05); htmx/`/auth/session`/tote JS-Dateien entfernen (PERF-07).
- Validierung: Cold-cache Netzwerkprofil, Fast-3G-DCL, Anzahl bedingter Requests; Comparison-Timing kalt/warm.

**Run R5 – Zitier-/Metadatenarchitektur** *(Opus 5.5 Medium – nur weil Datenmodell-/Publikationsentscheidungen offen sind: Rechteinhaber/Lizenz, Autorenmodell/Rollen/ORCID, Ressourcen-ID/Aliasse, `data_as_of`)*
- Scope: Entscheidungen aus §7 treffen und in `docs/spec/platform-data-files.md` festschreiben; danach Umsetzung (sinnvoll als Sonnet 5.5 High): zentrale Personen-/Ressourcenquelle, Partial `_page_meta.html` (canonical, hreflang, lokalisierte description, JSON-LD, `<time>`, `noindex` Drafts), generierter Zitatblock inkl. Plattform/Korpus/Teaching-Bereich, 404 statt 302 für unbekannte Slugs, Dopplungen `LANGUAGES`/Team-Seite beseitigen (PUBL-02..05, METADATA-02..04, CITE-02/03, DATA-03/05); `validate_teaching_content.py` um Front-Matter/Parität/Orphans erweitern (DATA-11).
- Validierung: curl-Skript (jede öffentliche URL genau ein selbstreferenzielles canonical, reziproke hreflang), Zotero-Test, Test „Zitat enthält exakten Seitentitel“.

Separat, ohne Code-Run: **CONTENT-03/PUBL-03** juristisch/organisatorisch klären (Datenschutz-Abgleich Drittanbieter/Cookie, Lizenz-/Rechteinhaberfrage) – Voraussetzung für R5. **AUDIO-01/02** erst mit einem iPhone-/Interview-Test belegen, dann entscheiden.

---

## 10. Hygiene und Abschluss

- Alle temporären Skripte, Screenshots, `axe`-Installation und Ergebnisdateien liegen ausschließlich im Session-Scratchpad außerhalb des Repos (`…\scratchpad\audit\`); im Repo wurden keine Auditskripte angelegt.
- `git status` am Ende: siehe Agent-Run-Eintrag `docs/agent-runs/2026-10-06_data-ux-publication-audit.md`; Änderungen sind auf diesen Bericht und den Run-Eintrag beschränkt.
- Nicht zurückgesetzt: 8 lokale Dev-DB-Drafts (siehe §2).
