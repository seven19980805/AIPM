# Vorlage fuer fachliche Anforderungen im Personalmanagement
> Zweck: fuer HR-Szenarien wie Mitarbeiterprofile, Recruiting und Onboarding, Anwesenheit und Schichtplanung, Payroll und Performance, Training und Entwicklung sowie Organisationsberechtigungen.  
> Verwendung: Ersetzen Sie die Hinweise in `[]` durch reale fachliche Inhalte; nicht relevante Punkte koennen entfernt werden.

## 1. Basisinformationen

| Feld | Inhalt |
| --- | --- |
| Vorlagenname | Vorlage fuer fachliche Anforderungen im Personalmanagement |
| Anforderungsname | [Beispiel: Optimierung des Mitarbeiterlebenszyklus] |
| Projekt | [Projektname eingeben] |
| Anforderungstyp | Neuentwicklung / Optimierung / Refactoring |
| Prioritaet | Hoch / Mittel / Niedrig |
| Anfordernde Abteilung | [Abteilung eingeben] |
| Anforderer | [Name eingeben] |
| Anforderungsdatum | [YYYY-MM-DD] |
| Version | V1.0 |

## 2. Fachlicher Hintergrund

### 2.1 Hintergrundbeschreibung

[Beschreiben Sie aktuellen HR-Betrieb, Mitarbeiterumfang, bestehende Prozesse und den Grund fuer den Aufbau dieser Faehigkeit.]

Beispiel: HR-Prozesse sind ueber Tabellen, E-Mail, Offline-Genehmigungen und mehrere Systeme verteilt. Mitarbeiterdaten sind uneinheitlich, Recruiting und Onboarding sind ineffizient, und Anwesenheit, Payroll und Performance sind schwer zu verbinden.

### 2.2 Aktuelle Schmerzpunkte

- [Beispiel: Mitarbeiterprofile werden an mehreren Stellen gepflegt und Aktualisierungen kommen verspaetet an]
- [Beispiel: Aufgaben von Einstellung bis Onboarding werden nicht einheitlich verfolgt]
- [Beispiel: Anwesenheits-, Urlaubs- und Ueberstundenregeln werden manuell geprueft]
- [Beispiel: Berechtigungen fuer Payroll- und Performance-Daten sind unklar]

## 3. Ziele

### 3.1 Fachliche Ziele

- [Beispiel: Einheitlichen Einstieg fuer HR-Prozesse schaffen]
- [Beispiel: Recruiting, Onboarding, Genehmigung und Employee Service effizienter machen]
- [Beispiel: Mitarbeiterstammdaten ueber den gesamten Lebenszyklus aufbauen]
- [Beispiel: Workforce Analytics und Managemententscheidungen verbessern]

### 3.2 Messbare Kennzahlen

- [Beispiel: Durchschnittliche Onboarding-Dauer um 50% reduzieren]
- [Beispiel: Vollstaendigkeit der Mitarbeiterprofile auf ueber 95% erhoehen]
- [Beispiel: Bearbeitungszeit fuer Anwesenheitsausnahmen um 40% verkuerzen]
- [Beispiel: Wiederholte HR-Dateneingabe um 60% reduzieren]

## 4. Fachlicher Umfang

### 4.1 Im Umfang enthalten

- Mitarbeiterprofilverwaltung
- Recruiting- und Onboarding-Prozess
- Anwesenheits-, Urlaubs- und Ueberstundenmanagement
- Zusammenarbeit von Payroll- und Performance-Daten
- Training- und Entwicklungsnachweise
- Organisations-, Positions- und Berechtigungsmanagement
- HR-Berichte und Analysen

### 4.2 Nicht im Umfang enthalten

- Komplexe Payroll-Berechnungsengine
- Sozialversicherungs- oder Benefit-Meldungen
- Tiefe Integration externer Headhunter-Plattformen
- Konzernweite Personalkostenprognose

## 5. Rollen und Kernszenarien

### 5.1 Zielrollen

- Mitarbeitende: sehen eigene Informationen und stellen Urlaubs-, Ueberstunden-, Korrektur- und Profilaenderungsantraege
- HR-Spezialisten: pflegen Mitarbeiterprofile und bearbeiten Lifecycle-Prozesse
- Recruiter: verwalten Kandidaten, Angebote und Onboarding-Aufgaben
- Fuehrungskraefte: genehmigen HR-Themen im Team und sehen Teamstatus
- Payroll- und Performance-Spezialisten: pflegen Payroll- und Performance-Daten
- Management: sieht Workforce-Kennzahlen und wichtige Indikatoren
- Systemadministratoren: pflegen Organisation, Positionen, Berechtigungen und Grundkonfiguration

### 5.2 Zentrale Geschaeftsszenarien

1. HR erstellt und pflegt Mitarbeiterprofile; Mitarbeitende aktualisieren erlaubte persoenliche Daten per Self-Service.
2. Nach Angebotsannahme startet das System Onboarding-Aufgaben fuer Dokumente, Accounts und Schulungen.
3. Mitarbeitende stellen Urlaubs-, Ueberstunden- oder Korrekturantraege; das System prueft Anwesenheitsregeln.
4. Fuehrungskraefte genehmigen Team-Antraege und sehen Anwesenheits- und Performance-Status.
5. Management analysiert Headcount, Fluktuation, Recruiting-Fortschritt, Performance-Verteilung und Personalkosten.

## 6. Funktionale Anforderungen

### 6.1 Funktionsuebersicht

[Beschreiben Sie die Kernfaehigkeiten, die fuer diese HR-Anforderung aufgebaut werden sollen.]

Beispiel: Die Anforderung umfasst Mitarbeiterprofile, Recruiting und Onboarding, Anwesenheit und Urlaub, Payroll und Performance, Training und Entwicklung sowie HR Analytics. Ziel ist die Verbindung zentraler HR-Prozesse mit Mitarbeiterstammdaten.

### 6.2 Funktionsdetails

#### Funktion 1: Mitarbeiterprofilverwaltung

- Beschreibung: Pflege von Basisdaten, Beschaeftigungsdaten, Vertragsdaten und Anhaengen.
- Ausloeser: HR erstellt Mitarbeitende oder Mitarbeitende beantragen Profilaenderungen.
- Verarbeitungslogik:
  - Eindeutige Mitarbeiternummer automatisch erzeugen und pruefen
  - Statuswechsel wie Onboarding, aktiv, ausgetreten und deaktiviert unterstuetzen
  - Aenderungshistorie fuer wichtige Felder und Genehmigungen speichern
- Eingaben: Name, Organisation, Position, Eintrittsdatum, Vertragsdaten, Anhaenge
- Ausgaben: Mitarbeiterprofil, Aenderungsprotokoll, Statushistorie
- Ausnahmefaelle: doppelte Mitarbeiternummer, fehlende Pflichtdaten, ungueltiges Anhangformat

#### Funktion 2: Recruiting und Onboarding

- Beschreibung: Prozess von Angebotsbestaetigung bis Abschluss des Onboardings verwalten.
- Ausloeser: Recruiter bestaetigt Angebotsannahme.
- Verarbeitungslogik:
  - Onboarding-Checkliste und Aufgaben automatisch erzeugen
  - Dokumentensammlung, Account-Erstellung, Geraetevorbereitung und Training unterstuetzen
  - Nach Abschluss offizielles Mitarbeiterprofil erzeugen
- Eingaben: Kandidatendaten, Eintrittsdatum, Positionsdaten, Onboarding-Dokumente
- Ausgaben: Onboarding-Aufgaben, Onboarding-Status, Mitarbeiterprofil
- Ausnahmefaelle: fehlende Dokumente, geaendertes Eintrittsdatum, ueberfaellige Aufgaben

#### Funktion 3: Anwesenheit und Urlaub

- Beschreibung: Urlaub, Ueberstunden, Korrekturen, Dienstreisen und weitere Anwesenheitsantraege unterstuetzen.
- Ausloeser: Mitarbeitende stellen Antrag oder das System synchronisiert eine Ausnahme.
- Verarbeitungslogik:
  - Nach Organisation, Schicht, Urlaubssaldo und Genehmigungsregeln pruefen
  - Erinnerungen und geschlossene Bearbeitung von Ausnahmen unterstuetzen
  - Ergebnisse in Anwesenheitsstatistiken synchronisieren
- Eingaben: Antragstyp, Zeitraum, Grund, Anhang, Genehmigungskommentar
- Ausgaben: Antrag, Genehmigungsprotokoll, Anwesenheitsergebnis
- Ausnahmefaelle: unzureichender Urlaubssaldo, Zeitkonflikt, fehlender Genehmiger

#### Funktion 4: Payroll- und Performance-Zusammenarbeit

- Beschreibung: Autorisierte Anzeige und Bestaetigung von Payroll- und Performance-Ergebnissen mit Mitarbeiterstammdaten verbinden.
- Ausloeser: Payroll- oder Performance-Spezialist importiert oder aktualisiert Daten.
- Verarbeitungslogik:
  - Ergebnisse je Periode pflegen
  - Sensible Felder nach Rolle und Datenumfang autorisieren
  - Einsicht und Bestaetigungsnachweise fuer Mitarbeitende unterstuetzen
- Eingaben: Payroll-Periode, Performance-Periode, Ergebnisdaten, Bestaetigungsstatus
- Ausgaben: Payroll-/Performance-Datensaetze, Bestaetigungen, Statistiken
- Ausnahmefaelle: uneinheitliche Daten, unzureichende Rechte, Importfehler

#### Funktion 5: Training und Entwicklung

- Beschreibung: Trainingsplaene, Anmeldung, Abschlussnachweise und Entwicklungsprofile verwalten.
- Ausloeser: HR veroeffentlicht Training oder Mitarbeitende melden sich an.
- Verarbeitungslogik:
  - Veroeffentlichung, Anmeldung, Pruefung und Teilnahmeprotokolle unterstuetzen
  - Abschlussdaten im Entwicklungsprofil speichern
  - Trainingserfolg statistisch auswerten
- Eingaben: Thema, Zielgruppe, Zeit und Ort, Anmeldedaten, Abschlussresultat
- Ausgaben: Trainingsplan, Anmeldeliste, Abschlussnachweise
- Ausnahmefaelle: Plaetze fehlen, Bedingungen nicht erfuellt, Nachweise fehlen

#### Funktion 6: HR-Berichte und Analysen

- Beschreibung: Analyse von Headcount, Organisation, Fluktuation, Recruiting-Fortschritt und Anwesenheitsausnahmen.
- Ausloeser: Nutzer fragt Berichte ab oder das System erstellt geplante Zusammenfassungen.
- Verarbeitungslogik:
  - Filter nach Organisation, Position, Status und Zeitraum unterstuetzen
  - Kennzahlenkarten, Trenddiagramme und Detailtabellen bereitstellen
  - Excel-Export unterstuetzen
- Eingaben: Suchbedingungen, Statistikdimensionen, Zeitraum
- Ausgaben: HR-Berichte, Trenddiagramme, Exportdateien
- Ausnahmefaelle: Daten fehlen, Definitionen sind uneinheitlich, Exportfehler

## 7. Geschaeftsregeln

- Mitarbeiterstammdaten muessen eine eindeutige Mitarbeiternummer haben und mit Organisation, Position, Level und Status verknuepft sein.
- Onboarding darf erst abgeschlossen werden, wenn alle Pflichtdokumente und Aufgaben erledigt sind.
- Urlaubs-, Ueberstunden- und Korrekturantraege muessen Organisationsregeln folgen.
- Sensible Felder wie Payroll, Performance und Vertrag muessen nach Rolle und Datenumfang autorisiert werden.
- Nach Austritt sollen Systemrechte automatisch entzogen und Auditdaten behalten werden.
- Aenderungen an Organisation, Position und Berichtslinie muessen historisiert werden.

## 8. Seiten- und Interaktionsvorschlaege

#### Seite 1: Mitarbeiterprofilliste

- Einstiegspunkt: Personalmanagement / Mitarbeiterprofile
- Seitenelemente: Filter, Mitarbeiterliste, Statuslabel, Import-/Exportbuttons
- Schaltflaechenaktionen: Mitarbeitenden hinzufuegen, Details anzeigen, bearbeiten, importieren, exportieren

#### Seite 2: Mitarbeiterprofildetail

- Einstiegspunkt: Klick aus der Mitarbeiterprofilliste
- Seitenelemente: Basisdaten, Beschaeftigungsdaten, Vertragsdaten, Anhaenge, Aenderungshistorie
- Schaltflaechenaktionen: Bearbeiten, Aenderung einreichen, Anhang hochladen, Logs anzeigen

#### Seite 3: Recruiting- und Onboarding-Board

- Einstiegspunkt: Recruiting / Onboarding
- Seitenelemente: Kandidatenliste, Onboarding-Aufgaben, Knotenstatus, Verantwortliche
- Schaltflaechenaktionen: Angebot bestaetigen, Onboarding-Aufgabe erstellen, erinnern, als erledigt markieren

#### Seite 4: Anwesenheits- und Urlaubs-Workbench

- Einstiegspunkt: Employee Service / Anwesenheit und Urlaub
- Seitenelemente: Antragsformular, Urlaubssaldo, Genehmigungsprotokoll, Ausnahmeliste
- Schaltflaechenaktionen: Antrag einreichen, zurueckziehen, genehmigen, exportieren

#### Seite 5: HR-Berichtsseite

- Einstiegspunkt: Workforce Analytics / Berichtszentrum
- Seitenelemente: Kennzahlenkarten, Filter, Trenddiagramme, Detailtabelle
- Schaltflaechenaktionen: Suchen, exportieren, Dimension wechseln

### 8.1 Interaktionsablauf

1. Nutzer startet einen HR-Antrag oder HR erstellt eine mitarbeitendenbezogene Aufgabe.
2. Das System prueft Basisdaten, Anhaenge und Regelbedingungen.
3. Verantwortliche Personen erledigen Genehmigungen oder Bearbeitungsaufgaben.
4. Nach Abschluss werden Mitarbeiterstammdaten, Status und Datensaetze aktualisiert.
5. Daten werden in Berichte und externe Abhaengigkeitssysteme synchronisiert.

## 9. Daten und Abhaengigkeiten

### 9.1 Schluesseldaten

- Mitarbeiternummer
- Name
- Organisation und Abteilung
- Position und Level
- Eintritts- und Austrittsdatum
- Mitarbeiterstatus
- Vertragsdaten
- Anwesenheit und Urlaubssaldo
- Payroll- und Performance-Periodendaten
- Bediener, Erstellungszeit, Aktualisierungszeit

### 9.2 Externe Abhaengigkeiten

- Organisationsstrukturdaten
- Identity- und Access-Management-System
- OA-Genehmigungssystem
- Zeiterfassungsgeraete oder Zeiterfassungssystem
- Payroll-System
- E-Mail- oder Benachrichtigungssystem

## 10. Berechtigungs- und Risikokontrolle

- Mitarbeitende koennen nur eigene Informationen und Antraege sehen.
- Fuehrungskraefte koennen Teammitglieder und Genehmigungsthemen sehen.
- HR kann Mitarbeiterdaten im Verantwortungsbereich sehen und pflegen.
- Payroll- und Performance-Daten benoetigen strengere feldbezogene Berechtigungen.
- Alle wichtigen Aktionen muessen fuer Audit und Compliance protokolliert werden.
- Austritt, Versetzung und Payroll-Aenderung sollen Pruefung oder starke Hinweise ausloesen.

## 11. Nicht-funktionale Anforderungen

- Seitenantwortzeit darf 3 Sekunden nicht ueberschreiten.
- Unterstuetzung von mindestens [Anzahl eingeben] gleichzeitigen Online-Nutzern.
- Uebertragung und Speicherung sensibler HR-Daten muessen verschluesselt werden.
- Zielverfuegbarkeit von 99,9% unterstuetzen.
- Genehmigung und Employee Self-Service auf PC und mobilen Geraeten unterstuetzen.

## 12. Abnahmekriterien

- Mitarbeiterprofil-, Onboarding-, Anwesenheits-, Genehmigungs- und Berichtsprozesse laufen Ende-zu-Ende.
- Mitarbeiterstammdaten stimmen mit Organisations- und Positionsdaten ueberein.
- Sensible Feldberechtigungen sind korrekt isoliert und unberechtigter Zugriff wird blockiert.
- Anwesenheits- und Urlaubsregelpruefung entspricht den fachlichen Erwartungen.
- Berichtsdefinitionen stimmen mit Geschaeftsdaten ueberein.
- Alle wichtigen Workflow-Knoten haben Operationslogs.

## 13. Risiken und offene Fragen

### 13.1 Risiken

- Unvollstaendige oder uneinheitliche historische Mitarbeiterdaten koennen Migration und Reporting beeinflussen.
- Unklare Berechtigungsgrenzen koennen sensible HR-Daten gefaehrden.
- Komplexe Anwesenheits-, Payroll- und Performance-Regeln koennen die Launch-Qualitaet beeinflussen.

### 13.2 Offene Fragen

- Muessen bestehende OA-, IAM-, Payroll-Systeme oder Zeiterfassungsgeraete integriert werden?
- Sollen Payroll- und Performance-Daten nur Ergebnisse anzeigen oder Berechnungsprozesse unterstuetzen?
- Welche Self-Service-Felder duerfen Mitarbeitende selbst bearbeiten?
- Ist eine einmalige Migration historischer Mitarbeiterprofile erforderlich?

## 14. Meilensteinplan

| Phase | Datum |
| --- | --- |
| Anforderungsbestaetigung | [YYYY-MM-DD] |
| Prototyp-Review | [YYYY-MM-DD] |
| Entwicklung abgeschlossen | [YYYY-MM-DD] |
| Test abgeschlossen | [YYYY-MM-DD] |
| UAT-Abnahme | [YYYY-MM-DD] |
| Produktivsetzung | [YYYY-MM-DD] |
