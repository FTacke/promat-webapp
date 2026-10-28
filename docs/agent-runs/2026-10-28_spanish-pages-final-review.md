# Spanisch-Themenseiten: Finalisierung nach der fachlichen Begutachtung (2026-10-28)

Grundlage: Durchsicht durch Ana Goás Pérez und die daraus getroffenen redaktionellen Entscheidungen. DE, EN und ES synchron; Slugs, Routen, Illustrationen und die 15 Platzhalterseiten (Englisch, Französisch, Deutsch) unverändert.

## 1. Geänderte und neue Hörvergleiche

| Seite | Hörvergleich | Änderung | Referenz | Lernende:r |
|---|---|---|---|---|
| *Europa klingt auf Spanisch anders* | *sueño* (W40) | Lernendenaufnahme ersetzt | ES-N-0001 (unverändert) | **ES-L-0015**, `wl_040` |
| *Europa klingt auf Spanisch anders* | *álbum* (W44) | ersetzt *mismo – álbum* | MAR.ELE-*álbum*-Clip wie bisher (siehe 2) | **ES-L-0015**, `wl_044` |
| *B oder V?* | *bienes – vienes* (W92, Referenz vs. Lernende:r) | Lernendenaufnahme ersetzt | ES-N-0004 (unverändert) | **ES-L-0017**, `wl_092` |
| *b, d und g* | *el baile elegante del evento* (D8) | neu, nach *con agua* | **ES-N-0004**, `d_08` (Ausschnitt) | **ES-L-0020**, `d_08` (Ausschnitt) |
| *b, d und g* | *cuidado* (D21) | neu, nach *el bebedor* | **ES-N-0004**, `d_21` (Ausschnitt) | **ES-L-0020**, `d_21` (Ausschnitt) |
| *Das spanische r* | *reloj* (W2) | Lernendenaufnahme ersetzt | ES-N-0005 (unverändert) | **ES-L-0019**, `wl_002` |

Unverändert: *Europa*, *deuda*, *viuda*; der Referenzsprechervergleich *bienes – vienes* und *barón – varón* (MAR.ELE); *vida*, *lavar*, *con agua*, *el bebedor*; *pero – perro*, *caro*, *carro*, *reír* (beide r-Seiten); auf *Das r am Wortende* keine Audioänderung (*flor*, *lavar*, *enfermo*, *reír*).

## 2. Herkunft der neuen Aufnahmen

- Wortlisten-Items (W40, W44, W92, W2): unveränderte Item-MP3 der Sessions (`items/wordlist/wl_NNN.mp3`), Item-Text im Alignment geprüft (*sueño*, *álbum*, *bienes – vienes*, *reloj*). Das *álbum*-Item heißt im Korpus `wl_044`.
- *álbum*-Referenz: der bisher verwendete MAR.ELE-Clip (Quelle `items/inf-L1-ES_es_049_álbum.mp3`, Schnitt 480–1135 ms, Quell-SHA im Register). Da das MAR.ELE-Backup auf diesem Rechner nicht vorliegt, wurde er verlustfrei aus der bisherigen Montage gewonnen: MP3-Frame-Kopie ohne Neukodierung ab 0,85 s (in der 300-ms-Pause vor *álbum*) bis zum Ende; 718 ms, nur *álbum*. In `origin.extracted_from` dokumentiert (Datei und SHA-256 der Montage, Verfahren). Die Montage-Dateien `p7-mismo-album-{ref,learner}.mp3` wurden gelöscht (keine andere Verwendung); keine Seite nutzt mehr eine Montage.

## 3. Ausschnitte D8 und D21

Schnittpunkte auf der Zeitachse der Item-MP3 aus Spektrogramm und Energieverlauf (nicht aus den Alignment-Zeiten). Die Item-MP3 beginnen 273 ms vor dem Alignment-Item (Kreuzkorrelation gegen die Session-Aufnahme); danach liegen die Token-Grenzen korrekt.

| Datei | Quelle | Schnitt (ms) | Fades | Inhalt |
|---|---|---|---|---|
| `p5-baile-ref.mp3` | ES-N-0004 `d_08` | 1500–3210 | 35/30 | *el baile elegante del evento*; Einsatz im o-e-Übergang, da *acompañó el* ohne Pause verbunden ist |
| `p5-baile-learner.mp3` | ES-L-0020 `d_08` | 2900–6100 | 15/30 | *el baile elegante del evento* (Pause davor) |
| `p5-cuidado-ref.mp3` | ES-N-0004 `d_21` | 745–1135 | 10/25 | *cuidado*, ab dem /k/-Verschluss bis vor das /s/ von *se* |
| `p5-cuidado-learner.mp3` | ES-L-0020 `d_21` | 960–1785 | 10/25 | *cuidado*, ebenso |

`source_sha256` und `sha256` im Register; Export mit `scripts/teaching_audio_slots.py --export`. Fokus der Karten: /g/ in *elegante*; die beiden /d/ in *cuidado* gemeinsam. **Nicht abgehört.**

## 4. Textänderungen

- *Europa*: Einleitung des Vokalabschnitts auf /u/ [u] vs. [ʊ] und *álbum*; Erklärung von [i] vs. [ɪ] bleibt schriftlich (*vino* [i] gegenüber *bitten* [ɪ] und *bieten* [iː]); Hörfrage „Wie unterscheidet sich die Aussprache des *u* in *álbum* zwischen den beiden Aufnahmen?“; Unterrichtsimpuls angepasst.
- *B oder V?*: Infokasten mit Semikolon und „este es un ejemplo de *spelling pronunciation* …“ (ES verbindlich), DE/EN entsprechend; Kurzbelege „(vgl./cf./véase Tacke 2020)“ im Fließtext entfernt, der Vertiefungslink bleibt.
- *b, d und g*: Übergang vor *el baile elegante del evento* und vor *cuidado*; dritter Unterrichtsimpuls ohne „Allophonie“/„alofonía“ (ES verbindlich, DE/EN entsprechend).
- *Das spanische r*: „lenguas de herencia“ in Infokastentitel, Infokasten, drittem Impuls und Vertiefungstitel (ES); zweiter Impuls „Reconocer dónde se articula la r“ (ES verbindlich), DE „Erkennen, wo das r gebildet wird“, EN „Recognise where the r is produced“ mit der konkreten Übung zu *claro*.
- *Das r am Wortende*: Auflösung zu *flor* mit konkreter Zungenbewegung; Einführung zur deutschen R-Vokalisierung auf die vorgegebene Fassung gekürzt (ohne [ɐ̯]/[ɐ], Vater-Schwa und IPA der deutschen Beispiele); Übergänge geprüft, *enfermo* und *reír* unverändert.

## 5. Autorenschaft

Ana Goás Pérez Mitautorin (nach Felix Tacke) auf *Weiches Spanisch, hartes Deutsch* (bestehend), *Europa klingt auf Spanisch anders*, *b, d und g* und *Das r am Wortende*, in DE, EN und ES; Zitation „Tacke, Felix & Goás Pérez, Ana (2026)“. Die übrigen drei Seiten: Felix Tacke allein. `metadata.updated` der fünf geänderten Seiten: 2026-10-28.

## 6. Freigaben

`--release-report`: ES-L-0015 (`wl_040`, `wl_044`), ES-L-0017 (`wl_092`), ES-L-0019 (`wl_002`), ES-N-0004 und ES-L-0020 (`d_08`, `d_21`) mit `teaching_consent_signed: yes`, `needs_review: False`, passendem Sprechertyp und Item im Alignment: alle OK. ES-L-0014 und ES-N-0003 nicht verwendet. Reserven bereinigt (jetzt integrierte ES-L-0015/ES-L-0019 und die *mismo*-Reserven entfernt).

## 7. Prüfungen

- Neue Tests `app/tests/test_teaching_review_2026_10_28.py` (Autorenschaft auf genau vier Seiten in allen Fassungen, gleiche Aufnahmen und Reihenfolge in DE/EN/ES, neue Karten, verbindliche spanische Formulierungen, unveränderte Karten); bestehende Regressionstests auf die neue Soll-Lage gebracht (u. a. Kuratierung, Ausschnitte, *álbum* statt Montage, Montage-Regeln an einer konstruierten Deklaration).
- 1604 Tests, ruff, Governance, Teaching-Validator, `--check` mit Runtime, Bildcheck, JS-Tests, Browser-Smoke grün.
- Browser (lokal): die fünf geänderten Seiten in DE, EN und ES, Desktop/Mobil, Hell/Dunkel: 60 Aufrufe mit 200, kein Overflow, keine Konsolenfehler, alle 138 Player starten.

## 8. Offen

- Die neuen Ausschnitte und Lernendenaufnahmen sind nur akustisch (Spektrogramm, Energie) geprüft, nicht abgehört.
- Für eine spätere Neuerzeugung des *álbum*-Referenzclips aus dem Original wird das MAR.ELE-Backup benötigt (`--marele-root`); der jetzige Clip ist bitgleich mit dem bisher veröffentlichten Montageteil.
