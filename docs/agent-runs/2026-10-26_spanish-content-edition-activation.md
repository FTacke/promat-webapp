# Spanische Inhaltsfassung der sieben Spanisch-Themenseiten aktiviert (2026-10-26)

## Quelle und Umsetzung

- Lieferung: `pronunciation_matters_themenseiten_es_v1.md` (identisch in `pronunciation_matters_spanish_editions_v1.zip`, dort zusätzlich je Seite getrennt und mit Karten-Teasern), Übersetzung aus dem Export v2 (Commit `1196f58`), Status laut Lieferung: redaktionell vollständig, fachliche Durchsicht durch Ana Goás Pérez steht aus. Die Seiten sind deshalb nicht als von ihr geprüft gekennzeichnet.
- `content/teaching/spanish/{slug}/es.yaml` für alle sieben Seiten, Block für Block aus `de.yaml` erzeugt (`tmp/ui-qa/2026-10-26-spanish-editions/build_es.py`, nicht versioniert). Strikter Abgleich ohne Abweichung: Blocktypen und Reihenfolge, Fragen bzw. Aussagen (bei *el bebedor* bleibt die erklärende Aussage), Anzahl der Aufnahmen, Rollen, Untertitel, Hinweise, Wortfolge-Chips und Transkripte identisch mit den aufgenommenen Wortfolgen, Link-Ziele, Autorenschaft. Audio-Dateien, Slots, Hashes, Bilder, Embeds und Ressourcen-IDs unverändert aus `de.yaml`; `metadata.updated` 2026-10-26.
- Interne Links auf die sechs Nachbarseiten zeigen auf die spanische Fassung (zehn Links), werden auf der Seite auf die UI-Sprache der Lesenden umgeschrieben und tragen die Herkunft.
- `hubs/es.yaml`: Titel, Einleitung und Gruppen selbst übersetzt (in der Lieferung nicht enthalten), Karten-Titel und -Teaser aus den Seitendateien.
- Beschriftungen im Inhaltsbereich auf Spanisch (`i18n.TEACHING_CONTENT_LABELS["es"]`; Rollen „Hablante de referencia“/„Aprendiente“ wie in der Lieferung, „Secuencia“, „Mostrar/Ocultar solución“, „Autoría“, „Creado“/„Actualizado“, Datum TT/MM/JJJJ, „Cómo citar esta página temática“); Zitierform «…», „En:“, „ed.“. Eine Fassung geht nur mit vollständigem Beschriftungssatz online (neue Bedingung im Freigabe-Gate).
- Lieferdateien aus dem Repository-Root nach `tmp/ui-qa/2026-10-26-spanish-editions/incoming/` verschoben (nicht versioniert).

## Prüfungen

- Tests angepasst/ergänzt: echtes Repository mit veröffentlichter Fassung (sieben Seiten, Hub, Links, hreflang `de`/`en`/`es`, Canonical unter `/de/…/es/…`, keine deutschen/englischen Labels im Inhaltsbereich, interne Links in der Fassung), Französisch nur mit vollständigem Beschriftungssatz, Publikationsmetadaten (`es`-Seiten in der Canonical-/hreflang-Prüfung), Hardening (Fassungsdateien unter ihrer Route), Layout-Test, Browser-Smoke (hreflang mit Inhaltsfassungen).
- Browser-Pass (echte Inhalte, lokal): Übersicht und sieben Seiten unter DE- und EN-Navigation, Desktop/Mobil, Hell/Dunkel; 58/58 Player starten, Auflösungen klappen auf, keine fremdsprachigen Labels, kein Overflow, keine Konsolenfehler, keine fehlenden Ressourcen; „En español“ auf allen DE/EN-Seiten, „Auf Deutsch“/„In English“ auf der Fassung.
- ruff, Governance, Teaching-Validator, Slot-Check, Bild-Check, JS-Tests, Browser-Smoke, volle pytest-Suite grün.

## Offen

- Fachliche Durchsicht der spanischen Texte durch Ana Goás Pérez; Korrekturen direkt in den `es.yaml`.

## Nachtrag: Stil des Sprachlinks

- `En español` / `Auf Deutsch` / `In English` ohne Unterstreichung (auch nicht beim Hover): Akzentfarbe (`--pm-text-accent`), Globus-Icon, beim Hover leicht abgedunkelter bzw. aufgehellter Ton und eine zarte Akzent-Hinterlegung (9 %), Fokusring für Tastatur. Die Hinterlegung hat eine konstante Innenpolsterung, die ein negativer Rand ausgleicht (kein Verspringen); im Browser hell/dunkel, Desktop/Mobil geprüft, kein Overflow.
