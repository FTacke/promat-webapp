# Französisch „Die Liaison“: Liaisonkonsonanten über einen zusammenhängenden Hörtext (2026-11-10)

Didaktische Idee: Janina Reinhardt. Überarbeitet wurde nur der Abschnitt „Drei Konsonanten: [z], [t] und [n]“ in `content/teaching/french/liaison/{de,en,fr}.yaml`. Als einzige Folgeänderung außerhalb des Abschnitts wurde der dritte Unterrichtsimpuls angepasst. Die Seite ging direkt online, damit Janina Reinhardt sie dort begutachten kann.

## 1. Gewählte Aufnahme

- Quelle: französisches Korpus, Lesetext („Petit Chaperon rouge“). Sprecher-ID FR-N-0001 (`FR-N-0001-2026-S01`), Item T63 (`text/t_63`).
- Teaching-Freigabe: `teaching_consent_signed: yes`, `needs_review: False`, Ergebnis im `--release-report`: OK.
- Datei: `corpus/fr1-c-etait-un-chat.mp3`, Registry-Eintrag `fr1-hoertext`.
- Zuschnitt: ungeschnittene Item-MP3 (2808 ms). Gesprochen wird von etwa 310 bis 2555 ms, davor und danach liegt digitale Stille. Die Satzgrenzen entsprechen der durchgehenden Textaufnahme `derived/text.mp3`; kein Laut ist abgeschnitten.
- „N1-T1“ ist als Sprecher FR-N-0001 mit dem Lesetext aufgelöst. Der Satz T1 allein (*Il était une fois le Petit Chaperon rouge, étudiante à l’université de Marbourg.*) enthält nur eine Liaisonstelle, *était‿une* mit [t], dazu das *enchaînement* *étudiante à*. Für die Aufgabe reicht das nicht.

## 2. Transkript und Markierung

*C’était un chat, vous en avez entendu parler ?* Im Quelltext steht `C’étai**t** un chat, vou**s** e**n** ave**z** entendu parler ?`.

- Markiert ist jeweils der geschriebene Endkonsonant vor einem vokalisch anlautenden Wort. Alle vier Stellen sehen gleich aus (Markdown `**…**`).
- Wortpaare lassen sich nicht markieren, weil *vous en avez* zwei überlappende Übergänge enthält (*vous‿en*, *en‿avez*).
- Keine weiteren Stellen markiert: *chat, vous* (vor Konsonant und nach Pause), *un chat* (vor Konsonant), *entendu parler* (vor Konsonant).

## 3. Akustischer Befund (Spektrogramm, Energie, Stimmhaftigkeit; nicht abgehört)

| Stelle | Befund | Messung (Item-Zeitachse) |
|---|---|---|
| *c’était‿un* | Liaison [t] | zweiter Verschluss 590–635 ms (−50 bis −57 dB) mit Lösung bei 640–650 ms vor *un*; davor der *t*-Verschluss von *était* bei 480–500 ms |
| *vous‿en* | Liaison [z] | Friktion 1470–1505 ms, Hochfrequenzanteil bis 0,44, stimmhaft (Autokorrelation 0,34–0,53) |
| *en‿avez* | Liaison [n] | Nasalmurmel 1585–1615 ms: Schwerpunkt fällt von etwa 700 Hz (Nasalvokal) auf etwa 260 Hz, Energie −25 dB, danach [a] |
| *avez entendu* | keine Liaison | [e] → [ɑ̃] ohne Einbruch und ohne Friktion, 1770–1830 ms |

- Kein bloßes *enchaînement* im Satz. Liaison und *enchaînement* werden in der Auflösung entsprechend unterschieden.
- Am sichersten ist der Befund für [t] und [z]. Bei [n] (*en‿avez*) ist er akustisch plausibel, und die Liaison ist an dieser Stelle obligatorisch.

## 4. Geänderte Inhaltsblöcke (DE/EN/FR)

1. `section_heading`: „Die drei Liaison-Konsonanten“ / „The three liaison consonants“ / „Les trois consonnes de liaison“.
2. `text`: Hinführung nach Vorgabe, ohne Nennung der Konsonanten.
3. `audio_examples`: „Hörbeispiel: Liaison im Zusammenhang“ mit Hörfrage nach Vorgabe; ein Beispiel (Transkript wie oben, Hinweis „Frankreich · T63“).
4. `solution` (anfangs geschlossen):
   - Befund mit den drei realisierten Liaisons und den Konsonanten.
   - *avez entendu* als mögliche, nicht realisierte Liaison.
   - Kein *enchaînement* ohne Liaison.
   - Allgemeiner Teil nach Vorgabe, einschließlich des optionalen Satzes zu [z]. Keine Prozentangaben und keine Siebenerliste.
5. Entfernt: die bisherige Einleitung (mit unbelegter Angabe „etwa die Hälfte entfällt auf [z]“), drei Einzelbeispiele und Schlusstext; deren Aussagen stehen jetzt in der Auflösung.
6. Dritter Unterrichtsimpuls verweist jetzt auf das zusammenhängende Hörbeispiel; der Zweck ist unverändert.

Die Medien `fr1-z-des-heures.mp3`, `fr1-t-est-allee.mp3` und `fr1-n-un-aspect.mp3` wurden nirgends sonst verwendet. Sie sind samt Registry-Einträgen gelöscht. Die übrigen Medien sind nach `--export` bitgleich.

Hinweis: Der Infokasten „Woher kommt die Liaison?“ vor dem Abschnitt nennt bereits [z] (für *s*) und [t] (für *d*). Er bleibt nach Vorgabe unverändert.

## 5. Darstellung

- Neue allgemeine Regel `.pm-teaching-audio-example__text strong` in `app/static/css/30_components.css`: neutrale, leicht getönte Markierung über `--pm-text-accent` (18 %), fett, gleich für alle Stellen, ohne Linkfarbe.
- Wirkt nur auf Hervorhebungen in Beispieltranskripten von `audio_examples`. Andere Seiten verwenden dort kein `**…**`; das spanische `***los otros***` steht im Transkript von `audio_contrast` und ist nicht betroffen.
- Spec ergänzt (`docs/spec/platform-data-files.md`, `audio_examples`). Außerdem die veraltete Liste angekündigter französischer Seiten entfernt; die Seiten wurden im vorigen Run gelöscht.

## 6. Prüfungen

- Teaching-Validator, `--language french --check` und `--release-report`, spanische Registry `--check`.
- `app/tests/test_teaching_liaison.py` erweitert:
  - gleiche Abschnittsstruktur in DE/EN/FR;
  - gleiche Aufnahme und gleiches Transkript;
  - genau vier markierte Übergänge;
  - vor der Auflösung keine Konsonanten und kein ‿;
  - Auflösung mit den drei realisierten Liaisons und *avez entendu*;
  - keine Prozentangabe und keine Siebenerliste;
  - Impuls aktualisiert;
  - gerenderte Markierungen und geschlossene Auflösung.
- Ergebnisse:
  - 1608 Python-Tests grün;
  - ruff und Governance grün;
  - JS-Tests 69/69;
  - Browser-Smoke 277/277.
- Browser lokal (DE/EN/FR × Desktop/Mobil × Hell/Dunkel):
  - Player spielt;
  - Auflösung anfangs geschlossen;
  - Markierungen gut lesbar;
  - Umbruch mobil sauber;
  - kein Overflow, keine Konsolenfehler.

## 7. Alternativen

- Bester Alternativkandidat ist derselbe Satz T63 von FR-N-0002. Bei *vous‿en* ist [z] deutlich realisiert. Bei *c’était un* fehlt dagegen der zweite Verschluss, also keine [t]-Liaison, und *en‿avez* ist akustisch unklar.
- Weitere Fundstellen bei FR-N-0001:
  - T43 *ils‿ont‿entendu une explosion* mit [z], optionalem [t] und dem Sonderfall *neuf heures*;
  - T41 *griller un‿agneau* mit [n] und möglichem [ʁ] nach Infinitiv, das nur in gehobener Rede vorkommt;
  - T16/T17 mit optionalem [t].
- T64 *les‿a* ([z], obligatorisch) ist akustisch schwach ausgeprägt; *bottes et* und *jetées à* sind ohne Liaison gesprochen.
- *aller à* (T55) wurde nicht als [ʁ]-Kontext verwendet.

## 8. Offen

Hörabnahme durch Janina Reinhardt: Auswahl der Aufnahme, Markierung der Endkonsonanten statt Wortpaare, Formulierungen der Auflösung.
