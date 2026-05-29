# 2026-05-29 — Analytics-Inflation: Diagnose und Korrekturen

## Ausgangslage

Admin-Analytics zeigte inflationäre Werte gegenüber GoatCounter (~321 interne „eindeutige Besucher:innen" vs. ~57 GoatCounter-Visits bei wenigen Aktivitätstagen). Diagnoseauftrag: Ursachen finden, Korrekturen ohne neue Feature-Branch.

## DB-Diagnose (read-only)

```
analytics_daily: 27 Zeilen, 2026-04-13 bis 2026-05-28
  SUM(unique_visitors) = 976
  SUM(page_views)      = 5.452

Aufällige Tage:
  2026-05-11: unique=273, page_views=408  → UV/PV-Ratio 0.67
  2026-05-12: unique=207, page_views=466  → UV/PV-Ratio 0.44
  2026-05-11 teaching/english: unique=45, page_views=47  → fast 1:1 (Bot-Signatur)

analytics_language_area_daily: 52 Zeilen, SUM(unique_visitors)=913
```

Normales Verhältnis (echte Nutzer:innen) liegt bei 0.02–0.10 UV/PV. Werte nahe 1:1 belegen Crawler.

## Identifizierte Ursachen

### 1. Bot-Traffic ohne Cookie-Persistenz (Hauptursache)
`_is_trackable_response()` hatte keine User-Agent-Filterung. Bots speichern keinen Cookie → jeder Bot-Request zählt als neuer „Unique Visitor". Die Spikes vom 05-11/12 sind typische Crawler-Muster.

**Fix:** `_BOT_UA_KEYWORDS`-Tuple hinzugefügt, UA-Check am Ende von `_is_trackable_response()`.

### 2. Falsch beschriftete Gesamt-Unique-Metrik (sekundär)
`summarize_analytics()` addierte `unique_visitors` über alle Tage: `sum(row.unique_visitors ...)`. Eine Person, die an N Tagen kommt, wird N-mal gezählt. Labelwar „Eindeutige Besucher:innen" — irreführend.

Da die DB nur Aggregattabellen enthält (kein Rohlog, privacy-by-design), ist echter Zeitraum-Unique rückwirkend nicht rekonstruierbar.

**Fix:** Key in `totals`-Dict umbenannt von `unique_visitors` → `visitor_day_sum`. Neue i18n-Schlüssel `auth.admin_analytics.visitor_day_sum` (DE/EN) und `auth.admin_analytics.visitor_day_sum_note` (methodische Erläuterung). Template aktualisiert.

### 3. Cookie-Tracking-Logik (keine Änderung nötig)
Per-Day-Unique-Zählung im Cookie ist korrekt: dieselbe Person am selben Tag wird nur einmal gezählt. Cookie-Attribute (Path=/, SameSite=Lax, secure via SESSION_COOKIE_SECURE) sind korrekt gesetzt.

### 4. Ausschlussregeln (bereits korrekt)
`/admin`, `/auth`, `/api/`, Healthchecks, HTMX-Requests, Static waren bereits ausgeschlossen. `_describe_request()` filtert zudem auf `TRACKED_ROOT_SECTIONS = {"project", "research", "teaching"}`, sodass Routen außerhalb dieser Bereiche nie gezählt werden.

## Geänderte Dateien

| Datei | Änderung |
|-------|----------|
| `app/src/app/analytics.py` | `_BOT_UA_KEYWORDS` + UA-Check in `_is_trackable_response()`; `totals["unique_visitors"]` → `totals["visitor_day_sum"]` |
| `app/src/app/i18n.py` | Neue Keys `visitor_day_sum` und `visitor_day_sum_note` in DE + EN |
| `app/templates/pages/admin_analytics.html` | Totals-Karte auf `visitor_day_sum` umgestellt, Methodenhinweis-Note hinzugefügt |
| `app/tests/test_analytics.py` | 21 neue Tests: Bot-UA-Filter, ausgeschlossene Routen, Unique-Counting-Logik, visitor_day_sum-Key |

## Testlauf

```
641 passed, 0 failed (84 s)
```

## Was rückwirkend nicht korrigierbar ist

Die bereits gespeicherten `analytics_daily.visitors`-Werte enthalten Zählungen von Bot-Requests. Eine rückwirkende Bereinigung wäre nur möglich, wenn bekannte Tage mit Bot-Spikes manuell zurückgesetzt werden (z. B. 05-11: 273→ Schätzwert). Das ist ein manueller Schritt und wurde in diesem Run nicht durchgeführt, da keine Datenänderungen ohne explizite Freigabe vorgesehen waren.

## Akzeptanzkriterien erfüllt

- [x] Ursache der Aufblähung identifiziert (Bot-Traffic + falsche Summierung)
- [x] Interne Zahlen korrekt umbenannt (visitor_day_sum statt unique_visitors im Gesamt-Aggregat)
- [x] Login/Auth/Admin/API/Static weiterhin ausgeschlossen
- [x] Unique-Definition im UI dokumentiert (Hinweistext)
- [x] Admin-Analytics-UI zeigt keine irreführende Gesamt-Unique-Zahl mehr
- [x] Tests decken korrigierte Logik ab
- [x] Keine Datenänderung ohne Backup/Freigabe
- [x] Kein neuer Feature-Branch
