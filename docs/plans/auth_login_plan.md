---
tags: promat, webdesign, planung
---

auth_login_plan.md

# Auth und Login Implementierung

## Status und Zweck

Dieses Dokument legt die fachliche und technische Zielrichtung für Auth, Login, Zugangsanfrage, Account-Erstellung, Einladungslogik, Passwort-Setup, Passwort-Reset und accountbezogene Statusmeldungen in der PROMAT-Webapp fest.

Es dient als Referenz für die nächsten Umsetzungsruns rund um:

- Login-/Access-/Auth-UX-Polish
- Admin-seitige Account-Anlage
- automatisierten Einladungsversand
- Passwort-Setup und Passwort-Reset
- zeitlich befristete Zugänge
- Zugangsanfragen per Mail

Dieses Dokument ist zunächst ein Planungsdokument. Die aktiven bindenden Regeln sollen nach der Umsetzung in die Spezifikationen und ggf. in weitere Governance-Dokumente überführt werden.

## Ausgangslage

Die Research-Architektur der PROMAT-Webapp ist bereits so konsolidiert, dass außerhalb von `design` nur geschützte Research-Flächen existieren. Damit ist die grundlegende Access-Grenze fachlich bereits richtig gezogen.

Der nächste sinnvolle Schritt ist deshalb nicht mehr eine weitere große Strukturphase, sondern eine saubere, produktionsnahe Auth- und Login-Ausgestaltung, bevor echte Teilnehmerdaten, erste echte Intakes und die ersten realen Text-/Interview-Daten durch die App laufen.

Dabei gilt:

- Die Auth-Logik soll nach Möglichkeit auf dem bereits bewährten CORAPAN-Modell aufsetzen.
- Ein unnötiger Neubau soll vermieden werden.
- Die Nutzerführung muss klar, knapp, professionell und datenschutzsensibel sein.
- Die Login- und Zugangsanfrage-UX muss vor echten Forschungsdaten sauber und vertrauenswürdig wirken.

## Grundentscheidung

PROMAT erhält ein klar eingeschränktes Auth-Modell für eine geschützte Forschungsplattform.

Die Plattform ist **nicht** offen registrierbar.

Zugang wird nur an legitime Nutzer:innen aus Bildungs- und Forschungseinrichtungen vergeben, weil die Plattform neben Aufzeichnungen auch pseudonymisierte Daten von Lernenden enthält, die an der Studie teilgenommen haben und dem Datenschutz unterliegen.

Daraus folgen die Grundregeln:

- Login nur über **E-Mail + Passwort**
- keine Selbstregistrierung
- Accounts werden nur **admin-seitig** angelegt
- Passwort-Setup erfolgt über zeitlich begrenzten Einladungslink
- Passwort-Reset ist Teil des Auth-Modells
- Accounts können optional mit einem Ablaufdatum versehen werden
- Zugangsanfragen erfolgen vorerst **per mailto**, nicht über offene Selbstregistrierung

## Zielbild in einem Satz

PROMAT soll eine geschützte Forschungsplattform mit klarem E-Mail-Login, admin-seitig angelegten Accounts, automatisiertem Einladungsversand, Passwort-Setup/Reset per Token-Link und einer einfachen Zugangsanfrage per Rollenadresse erhalten.

## Fachliches Auth-Modell

## 1. Login

### Login-Identifier

Der Login erfolgt ausschließlich über:

- **E-Mail-Adresse**
- **Passwort**

Ein separater Benutzername wird nicht als Login-Identifier verwendet.

Die E-Mail-Adresse ist der kanonische Benutzername.

## 2. Registrierung

Es gibt:

- keine offene Registrierung
- keine `Sign up`-Seite
- keine Selbstfreischaltung
- kein Social Login

Die Plattform ist nur für autorisierte Nutzer:innen zugänglich.

## 3. Account-Anlage

Accounts werden ausschließlich durch Admins bzw. das autorisierte PROMAT-Team angelegt.

Der Zielzustand ist:

1. Admin legt in der Webapp einen neuen Account anhand der E-Mail-Adresse an.
2. System erzeugt einen zeitlich begrenzten Einladungs-/Passwort-Setup-Link.
3. System sendet automatisch eine Standardmail an die angelegte Nutzeradresse.
4. Admin kann der Mail optional eine persönliche Notiz ergänzen.
5. Nutzer:in setzt über den Link selbst ein Passwort gemäß Passwortregeln.

## 4. Passwort-Setup-Link

Der Einladungs-/Passwort-Setup-Link ist:

- tokenbasiert
- nur zeitlich begrenzt gültig
- nicht dauerhaft wiederverwendbar
- nach erfolgreicher Nutzung ungültig

### Gültigkeitsdauer

Festgelegt wird:

- **14 Tage** Gültigkeit

## 5. Passwort-Reset

Passwort-Reset gehört ausdrücklich zum Auth-Modell.

Der Zielzustand ist:

1. Nutzer:in klickt auf `Passwort vergessen?`
2. System versendet an die hinterlegte Account-E-Mail einen zeitlich begrenzten Reset-Link
3. Nutzer:in setzt ein neues Passwort
4. Link verfällt nach Ablauf oder Nutzung

Auch hier soll nach Möglichkeit auf die bereits in CORAPAN bewährte Logik zurückgegriffen werden statt einen neuen Reset-Mechanismus zu bauen.

## 6. Aktiv / Deaktiviert / Abgelaufen

Ein eigener Zustand `noch nicht freigeschaltet` wird nicht benötigt, solange Accounts nur dann angelegt werden, wenn sie bereits freigegeben sind.

Relevante Zustände sind stattdessen:

- aktiv
- deaktiviert
- abgelaufen

### Bedeutungen

#### aktiv

Der Account darf sich einloggen und geschützte Flächen nutzen.

#### deaktiviert

Der Account existiert, darf sich aber nicht mehr einloggen.

#### abgelaufen

Der Account war zeitlich begrenzt gültig und ist jetzt nicht mehr verwendbar.

## 7. Accounts mit Ablaufdatum

Accounts sollen optional mit einer zeitlichen Gültigkeitsbegrenzung versehen werden können.

Beispiel:

- Zugang gültig für 6 Monate

Dies ist insbesondere für externe Forschungs- oder Lehrzugänge sinnvoll.

### Folgen im System

- Login muss prüfen, ob ein Account abgelaufen ist.
- Abgelaufene Accounts dürfen sich nicht mehr einloggen.
- Es braucht eine klare Meldung.

Beispielhafte Meldung:

> Ihr Zugang ist abgelaufen. Bitte kontaktieren Sie das PROMAT-Team oder beantragen Sie erneut Zugang.

## Inhalt der Login-Seite

Die Login-Seite soll bewusst knapp und professionell bleiben.

### Sichtbare Elemente

- Feld: **E-Mail-Adresse**
- Feld: **Passwort**
- Button: **Anmelden**
- Link: **Passwort vergessen?**
- Hinweis zur Zugangsbeschränkung
- Link oder Button: **Zugang beantragen**

### Nicht sichtbar

- kein `Registrieren`
- kein `Konto erstellen`
- kein Self-Service-Signup
- kein unnötiger Werbe- oder Marketingsprech

## Hinweistext auf der Login-Seite

Auf der Login-Seite soll ein Hinweis stehen, dass die Forschungsplattform neben Aufzeichnungen auch pseudonymisierte Daten von Lernenden enthält, die an der Studie teilgenommen haben, und dass diese Daten dem Datenschutz unterliegen.

Die Formulierung soll klar, sachlich und professionell sein.

### Zielinhalt des Hinweises

Die Forschungsplattform enthält neben Sprachaufzeichnungen auch pseudonymisierte Daten von Lernenden, die an der Studie teilgenommen haben. Diese Daten unterliegen dem Datenschutz. Der Zugriff kann daher nur legitimen Nutzer:innen aus Bildungs- und Forschungseinrichtungen gewährt werden.

Dieser Hinweis muss mit einem klar sichtbaren Zugangsanfrage-Link verbunden sein.

## Zugang beantragen

## Grundentscheidung

Zugangsanfragen erfolgen **vorerst per `mailto`**.

Es wird zunächst **kein offenes Formular** in der Webapp gebaut.

### Begründung

Für die aktuelle Phase ist `mailto` die pragmatischste und zugleich ausreichend professionelle Lösung:

- schnell umsetzbar
- keine zusätzliche Route nötig
- keine neue Datenspeicherung für Anfragen
- kein Spam-/Missbrauchsproblem wie bei Formularen
- passt zu admin-seitig angelegten Accounts
- erlaubt manuelle Prüfung legitimer Anfragen

Ein Formular kann später ergänzt werden, wenn das Anfragevolumen steigt oder die Bearbeitung stärker standardisiert werden soll.

## Rollenadresse für Zugangsanfragen

Langfristig soll eine Rollenadresse verwendet werden:

- `access@pronunciation-matters.de`

Da diese Adresse aktuell noch nicht eingerichtet ist, gilt für die Entwicklung und Übergangsphase:

- `felix.tacke@uni-marburg.de`

### Zielregel

In Produktiv-UI und späterer Kommunikation soll die Rollenadresse verwendet werden, nicht dauerhaft die persönliche Mailadresse.

## Mailto-Ziel

Der Link `Zugang beantragen` soll direkt eine vorbefüllte Mail öffnen.

### Zieladresse

**Produktiv später:**

- `access@pronunciation-matters.de`

**Bis zur Einrichtung der Rollenadresse in Dev/Übergang:**

- `felix.tacke@uni-marburg.de`

## Vorgesehener Betreff

```text
Zugangsanfrage "Pronunciation Matters"
```

## Vorgesehene Textvorlage

```text
Ich möchte Zugang zur Forschungsplattform "Pronunciation Matters" beantragen.

Nachname:
Vorname:
Institution:
Rolle/Funktion:
Institutionelle E-Mail-Adresse:
Zweck der Nutzung:

Mir ist bekannt, dass die angegebene E-Mail-Adresse als Benutzername für den Zugang verwendet wird.
Ich verpflichte mich, die datenschutzrechtlichen Anforderungen beim Zugriff auf pseudonymisierte Forschungsdaten einzuhalten.
```

## Zusätzliche Hinweise bei der Zugangsanfrage

Die Zugangsanfrage soll zusätzlich klar machen:

- die angegebene E-Mail-Adresse wird später zum Login-Identifier
- mit der Anfrage erklärt die anfragende Person, dass sie die Datenschutzanforderungen beim Zugriff auf pseudonymisierte Forschungsdaten beachtet

### Juristisch sinnvoller Minimalhinweis

Es soll kein überladener Rechtsblock werden, aber der Hinweis sollte ernsthaft genug sein.

Sinnvoll ist eine knappe Formulierung wie:

> Mit der Anfrage bestätigen Sie, dass Sie die datenschutzrechtlichen Anforderungen beim Zugriff auf pseudonymisierte Forschungsdaten beachten und die Plattform nur im legitimen institutionellen Kontext nutzen.

Für eine finale juristische Feinformulierung kann später noch eine genauere Prüfung erfolgen.

## Admin-Seite für Account-Anlage

## Zielbild

Die Webapp soll eine Admin-Oberfläche erhalten oder vorhandene Auth/Admin-Funktionalität entsprechend nutzen, sodass Admins neue Accounts sauber anlegen und den Einladungsversand direkt aus der Webapp auslösen können.

### Minimaler Admin-Flow

1. Admin öffnet `Account anlegen`
2. Admin trägt ein:
   - E-Mail-Adresse
   - optional Name
   - optional Ablaufdatum
   - aktiv/deaktiviert
3. System erzeugt Setup-Token mit 14 Tagen Gültigkeit
4. System erzeugt Standard-Einladungsmail
5. Admin kann optional eine persönliche Freitext-Notiz ergänzen
6. System versendet Mail direkt an die Nutzeradresse

## Einladungsmail

Die Einladungsmail soll standardisiert, sachlich und knapp sein.

### Inhaltlich mindestens enthalten

- kurze Information, dass ein Zugang zur Plattform eingerichtet wurde
- Hinweis, dass über den Link ein Passwort gesetzt werden kann
- Hinweis, dass der Link 14 Tage gültig ist
- Link zum Passwort-Setup
- optional persönliche Notiz des Admins

### Mögliche Struktur

- Betreff
- Standardtext
- persönlicher Zusatz des Admins
- Setup-Link
- Gültigkeitshinweis
- Signatur / Teamhinweis

## Passwortregeln

Die Passwortlogik soll nach Möglichkeit von CORAPAN übernommen werden, wenn sie dort bereits produktiv und bewährt ist.

### Zielregeln

Mindestens:

- Mindestlänge: 8 Zeichen
- mindestens ein Großbuchstabe
- mindestens ein Kleinbuchstabe
- mindestens eine Zahl

Je nach bereits vorhandenem CORAPAN-Modell kann geprüft werden, ob zusätzliche Regeln übernommen werden sollen.

## Entscheidung zur technischen Umsetzung

### Grundsatz

Wenn die Auth-/Einladungs-/Reset-Logik in CORAPAN bereits produktiv und zuverlässig läuft, soll sie **nicht neu erfunden**, sondern möglichst übernommen oder in PROMAT sauber vervollständigt werden.

### Vorgehen

1. Prüfen, welche Teile des CORAPAN-Auth-Stacks bereits in PROMAT übernommen wurden.
2. Prüfen, ob Setup-Link-, Reset-Link-, Aktiv-/Deaktiviert- und Expiry-Logik schon vorhanden oder teilweise vorhanden sind.
3. Fehlende Teile gezielt aus CORAPAN übernehmen oder angleichen.
4. Nur dort neu implementieren, wo eine direkte Übernahme nicht sinnvoll möglich ist.

### Begründung

Ein unnötiger Neubau ist schlechter als die Übernahme eines bereits produktiv bewährten Flows.

Ziel ist:

- geringeres Risiko
- schnellere Stabilität
- konsistentes Verhalten zwischen verwandten Projekten

## Meldungen und Fehlerzustände

## 1. Falsche Zugangsdaten

Beispiel:

> Die eingegebenen Zugangsdaten sind ungültig.

Keine unnötig verräterischen Detailangaben.

## 2. Deaktivierter Account

Beispiel:

> Ihr Konto ist derzeit nicht aktiv. Bitte kontaktieren Sie das PROMAT-Team.

## 3. Abgelaufener Zugang

Beispiel:

> Ihr Zugang ist abgelaufen. Bitte kontaktieren Sie das PROMAT-Team oder beantragen Sie erneut Zugang.

## 4. Abgelaufener oder ungültiger Setup-Link

Beispiel:

> Dieser Einladungslink ist ungültig oder abgelaufen. Bitte wenden Sie sich an das PROMAT-Team.

## 5. Abgelaufener oder ungültiger Reset-Link

Beispiel:

> Dieser Link zum Zurücksetzen des Passworts ist ungültig oder abgelaufen. Bitte fordern Sie einen neuen Link an.

## UX-Ziele für den nächsten Login-/Access-/Auth-Polish-Run

Der nächste Run soll nicht die komplette Auth-Verwaltung in einem Schritt fertigstellen, sondern zuerst die vorhandenen und jetzt fachlich festgezogenen Flows sichtbar und funktional sauber machen.

## Konkret soll der Run leisten

### 1. Login-Seite layouten und härten

- saubere Typografie
- gute Abstände
- klare Hierarchie
- gute Fokuszustände
- gute Formularfehler
- `de`/`en` sauber

### 2. Access-Gates sauber darstellen

- geschützte Research-Ziele leiten sauber auf Login
- `next` bleibt erhalten
- nach Login sauberer Rücksprung
- kein Flackern oder halb sichtbare Workbench vor Redirect

### 3. Zugangsanfrage-Link sauber integrieren

- Hinweistext auf Datenschutz und geschützten Zugang
- direkter `mailto`-Link
- saubere Link-/Button-Gestaltung
- dev/prod-konfigurierbare Zieladresse

### 4. Passwort-Reset sauber im UI sichtbar machen

- Link `Passwort vergessen?`
- spätere Einbindung des Reset-Flows
- saubere Meldungszustände

### 5. Statusmeldungen vorbereiten

- falsche Zugangsdaten
- deaktiviert
- abgelaufen
- Link ungültig/abgelaufen

## Was im nächsten Run noch nicht zwingend fertig sein muss

Nicht alles muss sofort voll umgesetzt werden.

Ein sinnvoller gestufter Weg ist:

### Stufe 1

- Login-Seite und Access-UX sauber
- `mailto`-Zugangsanfrage sauber
- Fehlermeldungen sauber
- `next`-Redirect sauber

### Stufe 2

- Admin-Accountanlage mit Einladungsmail
- Setup-Link-Flow
- Passwort-Reset-Flow
- Ablaufdaten und Statusmeldungen produktiv

### Stufe 3

- spätere optionale Umstellung von `mailto` auf Formular, falls nötig
- ggf. erweiterte Admin-Verwaltung

## Zusammenhang mit den nächsten Daten- und Player-Schritten

Diese Auth-Planung ist nicht Selbstzweck. Sie ist Vorbereitung für den nächsten Realitätscheck der Plattform.

Sinnvolle Reihenfolge danach:

1. Login-/Access-/Auth-UX-Polish
2. Intake-Readiness mit kleinem echten Datensatz
3. `text`/Satzliste mit realen Audios und `alignment/text.json`
4. Interview zunächst nur als technischer Test-/Smoke-Pfad
5. abschließender Harmonisierungslauf mit realen Daten durch Player, Comparison und Phenomena

## Offene Punkte

Einige Punkte sind fachlich schon klar, aber technisch noch im Umsetzungscheck:

### 1. CORAPAN-Übernahmegrad prüfen

Es muss geprüft werden:

- welche Auth-/Reset-/Invite-Logik in PROMAT bereits vorhanden ist
- welche Teile vollständig aus CORAPAN übernehmbar sind
- welche Teile nur angepasst oder aktiviert werden müssen

### 2. Produktive Rollenadresse einrichten

- `access@pronunciation-matters.de` muss noch technisch eingerichtet werden
- bis dahin Dev-/Übergangsadresse nutzen

### 3. Exakte Mailtexte finalisieren

- Einladungsmail
- Reset-Mail
- Zugangsanfrage-Mailto
- Statusmeldungen in `de/en`

### 4. Juristische Feinformulierung optional nachziehen

Die Datenschutzformulierung ist fachlich klar, kann später aber noch juristisch präzisiert werden.

## Schlussformel

PROMAT soll keine offene Plattform mit Selbstregistrierung werden, sondern eine klar geschützte Forschungsplattform mit institutionell legitimiertem Zugang.

Die Auth-Implementierung folgt daher diesen Leitlinien:

- Login nur über E-Mail + Passwort
- keine Selbstregistrierung
- Accounts nur durch Admin/Team
- Zugangsanfrage per `mailto`
- Passwort-Setup und Passwort-Reset über zeitlich begrenzte Token-Links
- Accounts optional mit Ablaufdatum
- möglichst Nutzung der bereits in CORAPAN bewährten Logik statt unnötigem Neubau

Damit ist die Grundlage geschaffen, um die Login-/Access-/Auth-UX sauber umzusetzen und anschließend echte Daten sicher in die Plattform zu bringen.
