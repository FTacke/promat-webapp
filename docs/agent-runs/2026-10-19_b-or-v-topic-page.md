# Themenseite „B oder V? Wenn die Schrift mitredet“ (2026-10-19)

## Ziel

Die bereits angelegte Seite `/{de|en}/teaching/spanish/b-or-v` nach dem Blueprint (`Pronunciation_Matters_Blueprint_Themenseiten_2026-10-19.md`) und dem Vorbild *Weiches Spanisch, hartes Deutsch* vollständig ausarbeiten (DE/EN), mit authentischen Hörvergleichen und zentral austauschbaren Lernendenaufnahmen.

## Consulted Sources

- Blueprint 2026-10-19, `docs/spec/platform-data-files.md`, `docs/runbooks/teaching-corpus-audio.md`, `docs/agent-runs/2026-10-11_soft-spanish-hard-german-revision.md`
- Digitales Lehrbuch (`orthographie`, `fehlerlinguistik`, `aussprache`; dort auch die Transkriptionen und Aussagen zu *spelling pronunciation* aus Tacke 2020). Tacke (2020) selbst war nicht abrufbar: Die Aussagen der Seite stützen sich auf die Lehrbuchkapitel und sind vorsichtig formuliert („mitunter“, „kann“).

## Seitenstruktur (DE/EN gleichwertig)

1. Kurzer Orientierungstext.
2. **Hörvergleich *bienes – vienes*** (W92) mit zwei Referenzstimmen (Mexiko, Chile) und aufklappbarer Auflösung (einzige Auflösung der Seite).
3. **Zwei Buchstaben, ein Laut**: Erklärung (Graphem, Phonem /b/, lateinische Herkunft, Homophone), typografische Zeile ⟨b⟩ / ⟨v⟩ → /b/, Infokasten „Zwei Buchstaben, ein Laut – auch Erstsprachler:innen sind manchmal unsicher“ (3 Sätze, ohne Mengenangaben, ohne Kontaktgebiete).
4. **Wenn zwei Buchstaben zu zwei Lauten werden**: Hörvergleich *barón – varón* (MAR.ELE, Referenz und Lernende), kurzer Text mit den Transkriptionen, ergänzend Hörvergleich *vienes* (Pronunciation Matters, W92; Lernendenaufnahme **vorläufig**), kurzer Allophonie-Absatz mit Verweis auf die Themenseite *Weiche Konsonanten: b, d und g* (kein eigener Abschnitt, kein zusätzlicher Hörvergleich).
5. Impulse für den Unterricht (3, mit der umgekehrten Rechtschreibproblematik, *Fater*/*Vater* als Illustration, *tubo*/*tuvo*).
6. Vertiefung: drei Lehrbuchkapitel (mit Ankern) und Tacke (2020) mit DOI; Zitation automatisch (Autorschaft unverändert Felix Tacke, Ana Goás Pérez nicht Mitautorin dieser Seite).

Titel/Teaser wie vorgegeben; EN: „B or V? When spelling has a say“. Die Verweistitel auf der Seite *Weiche Konsonanten* und die Tests wurden auf den neuen Titel umgestellt. Entfallen: „Auf einen Blick“, Variationsbox zum Katalanischen, die Boxen *vino*/*vida*/*lavar* (samt 10 alten MP3 und Registereinträgen).

## Audioquellen und Freigaben (`--release-report`, Stand 2026-10-19)

| Sprecher-ID | Item | Rolle | Verwendung | Einwilligung (Teaching) | `needs_review` | Sprechertyp | Ergebnis |
|---|---|---|---|---|---|---|---|
| ES-N-0004-2026-S01 | wl_092 | reference | p4-bienes-vienes · integrated | yes | False | native_speaker | OK |
| ES-N-0005-2026-S01 | wl_092 | reference | p4-bienes-vienes · integrated | yes | False | native_speaker | OK |
| ES-L-0019-2026-S01 | wl_092 | learner | p4-bienes-vienes · integrated | yes | False | learner | OK |
| ES-L-0006-2026-S01 | wl_092 | learner | p4-vienes-reserve-0006 · reserve (not integrated) | yes | False | learner | OK |
| ES-L-0007-2026-S01 | wl_092 | learner | p4-vienes-reserve-0007 · reserve (not integrated) | yes | False | learner | OK |
| ES-N-0003-2026-S01 (Ecuador) | – | reference | nicht verwendet (`EXCLUDED_SESSIONS`) | no | False | native_speaker | BLOCKED: keine Teaching-Freigabe |

- Geprüft: `metadata.json` der Session (Flags, Sprechertyp), Item-MP3, Alignment-Eintrag mit *bienes – vienes*. Keine Aufnahme aus Ecuador; ES-N-0001/ES-N-0002 sind für das MAR.ELE-Material reserviert und nicht im Leitbeispiel verwendet.
- **MAR.ELE *barón – varón*:** `baron_varon_l1.mp3` (Referenz, `5154d399dc05…`) und `baron_varon_ele.mp3` (Lernende, `6d3a8741de5d…`) aus dem Lehrbuch-Repository (Quelle: Lehrbuchabschnitt „Aussprache von ⟨b⟩ und ⟨v⟩“, Zielaussprache [baˈɾon] – [baˈɾon], Lernendenaussprache [baˈʁon] – *[vaˈʁon]), **byte-identisch kopiert** (`origin` im Slot-Register, kein Re-Encoding, Original unverändert). Die Freigabe wurde im Auftrag vom 2026-10-19 durch den Projektverantwortlichen bestätigt; sie ersetzt keine Prüfung weiterer Nachweise (Einwilligungsdokumente der MAR.ELE-Sprecher:innen liegen nicht im Repository). **Identitätsabgleich** mit ES-N-0001/ES-N-0002 war mit den vorhandenen Daten nicht belastbar möglich (die Wörter stehen nicht in der Pronunciation-Matters-Wortliste); deshalb **keine Zuordnung** zu PM-IDs, die Provenienz bleibt „MAR.ELE“.

## Zuschnitte und Zusammenschnitte

Keine. Statt eines Zusammenschnitts nutzt das Leitbeispiel zwei Karten desselben Hörvergleichs (jeweils die unveränderte Wortlisten-Aufnahme *bienes – vienes* einer Referenzstimme): Sprecher:innen bleiben erkennbar, es gibt keine künstliche Pause, keine Schnittstelle und je Stimme einen eigenen austauschbaren Slot. Die Wortfolge-Chips zeigen die tatsächlich gespielte Passage.

## Akustische Prüfung (Spektrogramm/Energie, **nicht abgehört**)

- Beide Referenzstimmen: *bienes* und *vienes* mit gleichem Anlautmuster, ohne labiodentale Reibung → Aussage der Auflösung („gleich aus“) akustisch plausibel.
- ES-L-0019 (vorläufiger Lernendenkandidat): auffällig anderer Anlaut in *vienes* (hoher Rauschanteil im Anlaut gegenüber *bienes*); im Text wird **nichts** über die konkrete Realisierung behauptet (neutrale Hörfrage, keine Auflösung).
- MAR.ELE-Lernende: *barón* mit unmittelbarem stimmhaftem Einsatz, *varón* mit längerem schwachem Reibe-/Stimmanlauf – stimmt mit der Lehrbuch-Transkription [vaˈʁon] überein; die Seite beschreibt genau diese Aussage.
- **Ausstehende manuelle Hörabnahme:** alle sechs Player (die Wiedergabe wurde im Browser ausgelöst und die Chips wechselten auf `playing`, ein Abhören fand nicht statt).

## Vorläufige Lernendenaufnahmen / Hörliste für Ana Goás Pérez

1. `p4-bienes-vienes`, Slot `learner`: **ES-L-0019 (A2), W92 – vorläufig**; Reserven im Register: ES-L-0006 (B1) und ES-L-0007 (B1) (`reserves`, ebenfalls freigegeben laut Gate). Austausch: Session in `audio-slots.yaml` ändern, `--export`, ggf. Untertitel der Karte (L1 Deutsch) prüfen; Texte bleiben unberührt.
2. Referenzstimmen `ref-mx` (ES-N-0004) und `ref-cl` (ES-N-0005): Gleichlautung beider Wörter bestätigen.
3. MAR.ELE *barón – varón*: Hörabnahme der Lehrbuchaufnahmen (Referenz, Lernende) für die Beschreibung auf der Seite.

## Entscheidungen / Abweichungen

- Zwei Karten statt Zusammenschnitt (s. o.); Schriftbild wird nicht nach dem ersten Hören eingeblendet (der Wortfolge-Chip ist per Vorgabe zwingend; eine neue Interaktion wurde nicht gebaut).
- Der Link zur Nachbarseite trägt deren tatsächlichen Titel *Weiche Konsonanten: b, d und g* (der im Auftrag genannte Titel „Zu hart gesprochen? …“ existiert nicht).
- Sprecher-Untertitel nennen bei den Referenzstimmen die Region (damit die zwei Stimmen unterscheidbar sind); bei einem Austausch ist der Untertitel mit anzupassen.
- Autorschaft: unverändert `felix-tacke` (keine Mitautorschaft von Ana für diese Seite ohne gesonderte Entscheidung).
