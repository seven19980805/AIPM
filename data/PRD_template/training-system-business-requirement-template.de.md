# Vorlage fuer fachliche Anforderungen an ein Schulungssystem
> Fuer Schulungssysteme wie Kursverwaltung, Schulungsplanung, Anmeldung und Freigabe, Online-Lernen, Pruefungen, Zertifikate, Lernprofile und Analysen.  
> Ersetzen Sie die Hinweise in `[]` durch reale fachliche Inhalte; nicht relevante Punkte koennen entfernt werden.

## 1. Basisinformationen

| Feld | Inhalt |
| --- | --- |
| Vorlagenname | Vorlage fuer fachliche Anforderungen an ein Schulungssystem |
| Anforderungsname | [Aufbau einer Unternehmens-Schulungsplattform] |
| Projekt | [Projektnamen eingeben] |
| Anforderungstyp | Neubau / Optimierung / Refactoring |
| Prioritaet | Hoch / Mittel / Niedrig |
| Anfordernde Abteilung | [Anfordernde Abteilung eingeben] |
| Anforderer | [Anforderer eingeben] |
| Anforderungsdatum | [YYYY-MM-DD] |
| Version | V1.0 |

## 2. Fachlicher Hintergrund

### 2.1 Hintergrundueberblick

[Beschreiben Sie den Schulungshintergrund, den aktuellen Prozess und den Grund fuer den Systemaufbau]

Beschreibung: Schulungsplaene, Kursanmeldungen, Lernnachweise, Pruefungsergebnisse und Zertifikate sind derzeit ueber E-Mail, Tabellen und mehrere Plattformen verteilt. Schulungsadministratoren koennen die Umsetzung schwer verfolgen, Lernende haben keinen einheitlichen Einstieg, und dem Management fehlen auswertbare Daten zur Schulungswirkung.

### 2.2 Aktuelle Schmerzpunkte

- [Veroeffentlichung von Schulungsplaenen und Anmeldung beruhen auf manuellen Benachrichtigungen]
- [Kursressourcen sind verteilt und Lernfortschritt ist schwer einheitlich nachzuverfolgen]
- [Pruefungsergebnisse, Zertifikate und Lernprofile werden nicht automatisch archiviert]
- [Schulungsdaten sind uneinheitlich definiert und Reporting erfordert viel Handarbeit]

## 3. Fachliche Ziele

### 3.1 Fachliche Ziele

- [Einen einheitlichen Einstieg fuer Schulungsplaene, Kurse und Lernen schaffen]
- [Anmeldung, Lernen, Pruefung und Zertifikat geschlossen verwalten]
- [Effizienz der Schulungsdurchfuehrung und Genauigkeit der Lernnachweise verbessern]
- [Auswertbare Schulungsdaten fuer Talententwicklungsentscheidungen aufbauen]

### 3.2 Messbare Kennzahlen

- [Bearbeitungszeit fuer Kursanmeldungen um 50% reduzieren]
- [Genauigkeit der Abschlussstatistik auf 98% bringen]
- [90% der Zertifikate automatisch erzeugen und archivieren]
- [Manuelle Reporting-Arbeit um 60% reduzieren]

## 4. Fachlicher Umfang

### 4.1 Im Umfang

- Kurs- und Inhaltsverwaltung
- Veroeffentlichung von Schulungsplaenen
- Anmeldung und Freigabe fuer Lernende
- Online-Lernen und Fortschrittsverfolgung
- Pruefungen, Bewertungen und Ergebnisverwaltung
- Zertifikate und Lernprofile
- Schulungsberichte und Analysen

### 4.2 Nicht im Umfang

- Eigenentwicklung der zugrunde liegenden Live-Classroom-Engine
- Komplexe LMS-Marktplatztransaktionen
- Tiefgehender Inhalteinkauf von externen Hochschulplattformen
- KI-basierte Empfehlung personalisierter Lernpfade

## 5. Rollen und Kernszenarien

### 5.1 Zielrollen

- Lernende: Kurse durchsuchen, Schulungen buchen, Inhalte lernen, Pruefungen ablegen und Zertifikate einsehen
- Trainer: Unterrichtsmaterialien pflegen, Teilnehmerlisten einsehen und Feedback pruefen
- Schulungsadministrator: Plaene erstellen, Anmeldungen verwalten, Pruefungen und Zertifikate konfigurieren
- Abteilungsverantwortliche: Teamanmeldungen freigeben und Lernfortschritt des Teams einsehen
- Management: Abdeckung, Abschlussquote, Bestehensquote und Wirksamkeit der Schulung einsehen
- Systemadministrator: Berechtigungen, Kategorien, Woerterbuecher und Grundkonfiguration pflegen

### 5.2 Kernszenarien

1. Ein Schulungsadministrator veroeffentlicht einen Schulungsplan und oeffnet die Anmeldung fuer die Zielgruppe.
2. Ein Lernender waehlt im Schulungsportal einen Kurs, sendet die Anmeldung ab und erhaelt Benachrichtigungen.
3. Ein Abteilungsverantwortlicher genehmigt Teamanmeldungen, und das System aktualisiert den Anmeldestatus.
4. Ein Lernender schliesst Online-Lernen ab und nimmt an einer Bewertung teil.
5. Das System erzeugt gemaess Abschlussregeln ein Zertifikat und speichert das Lernprofil.
6. Das Management prueft Abschlussquote, Bestehensquote und Kursfeedback.

## 6. Funktionale Anforderungen

### 6.1 Funktionsueberblick

[Fassen Sie die Kernfaehigkeiten des Schulungssystems zusammen]

Beschreibung: Diese Anforderung umfasst sieben Faehigkeitsgruppen: Kursressourcen, Schulungsplaene, Anmeldefreigabe, Lernfortschritt, Pruefungen und Bewertungen, Zertifikate und Lernprofile sowie Analysen.

### 6.2 Funktionsdetails

#### 6.2.1 Kurs- und Inhaltsverwaltung

- Beschreibung: Pflegt Kurskategorien, Kursinformationen, Lerninhalte, Trainer und Zielgruppen.
- Ausloeser: Ein Schulungsadministrator erstellt oder aktualisiert einen Kurs.
- Fachliche Regeln / Logik:
-   Unterstuetzt Veroeffentlichen, Zurueckziehen, Kategorien, Tags und Zielrollen
-   Unterstuetzt Videos, Dokumente, Aufgaben und weitere Inhaltsanhaenge
-   Unterstuetzt Kursversionen und Aenderungsverlauf
- Eingaben: Kursname, Kategorie, Trainer, Inhalte, Zielgruppe
- Ausgaben: Kursdetail, Katalog, Inhaltsliste
- Ausnahmen: Doppelte Kurse, fehlende Inhalte, Loeschen blockiert wenn durch Plan referenziert

#### 6.2.2 Schulungsplaene und Anmeldefreigabe

- Beschreibung: Veroeffentlicht Schulungsplaene und verwaltet Anmeldung, Freigabe, Kontingente und Benachrichtigungen.
- Ausloeser: Ein Plan wird erstellt oder eine Anmeldung eingereicht.
- Fachliche Regeln / Logik:
-   Unterstuetzt Anmeldung nach Organisation, Rolle oder benannten Personen
-   Unterstuetzt Kontingente, Wartelisten, Stornierung und Freigabeablaeufe
-   Unterstuetzt Benachrichtigungen fuer Anmeldung, Freigabe und Kursstart
- Eingaben: Planname, Kurs, Zeitplan, Kontingent, Zielgruppe, Freigeber
- Ausgaben: Schulungsplan, Anmeldeliste, Freigabeergebnis
- Ausnahmen: Kontingent voll, Frist abgelaufen, doppelte Anmeldung, Freigabe ueberfaellig

#### 6.2.3 Online-Lernen und Fortschrittsverfolgung

- Beschreibung: Bietet einen einheitlichen Lerneinstieg und zeichnet Lernfortschritt auf.
- Ausloeser: Ein Lernender startet das Lernen in einem Kurs.
- Fachliche Regeln / Logik:
-   Unterstuetzt Kurskatalog, Lernfortschritt, Dauer und Abschlussstatus
-   Unterstuetzt Fortsetzen, Pflicht-/Wahlkennzeichen und Erinnerungen
-   Unterstuetzt Mahnungen fuer ueberfaellige Lernaufgaben
- Eingaben: Lernender, Kurs, Inhalt, Dauer, Abschlussstatus
- Ausgaben: Lernnachweis, Fortschrittsstatistik, Abschlussnachweis
- Ausnahmen: Wiedergabefehler, Fortschrittsmeldung fehlgeschlagen, doppelte Datensaetze zusammenfuehren

#### 6.2.4 Pruefungen, Bewertungen und Ergebnisverwaltung

- Beschreibung: Konfiguriert Fragenbank, Pruefungsbogen, Pruefungstermine, Bewertung und Ergebnisstatistiken.
- Ausloeser: Ein Plan erfordert eine Pruefung oder ein Administrator veroeffentlicht eine.
- Fachliche Regeln / Logik:
-   Unterstuetzt Fragenbank, Pruefungsbogen, Pruefungszeit und Bestehensgrenze
-   Unterstuetzt automatische Bewertung, manuelle Bewertung und Wiederholungen
-   Unterstuetzt Ergebnisabfrage, Bestehensquoten und Export
- Eingaben: Fragen, Pruefungsbogen, Pruefungseinrichtung, Antwortdatensaetze
- Ausgaben: Ergebnisliste, Bestehensstatus, Pruefungsstatistik
- Ausnahmen: Zeitueberschreitung, doppelte Abgabe, Betrugsmarkierung, fehlende Wiederholungsberechtigung

#### 6.2.5 Zertifikate und Lernprofile

- Beschreibung: Erzeugt Zertifikate basierend auf Abschluss und Pruefungsergebnissen und baut Lernprofile auf.
- Ausloeser: Ein Lernender erfuellt die Ausgabebedingungen.
- Fachliche Regeln / Logik:
-   Unterstuetzt Zertifikatsvorlagen, Nummernregeln und Gueltigkeitsdauer
-   Unterstuetzt Erzeugung, Download, Widerruf und Ablaufhinweise
-   Aggregiert Lern- und Zertifikatsdaten je Mitarbeiter
- Eingaben: Abschlussdatensatz, Ergebnis, Zertifikatsvorlage, Mitarbeiterdaten
- Ausgaben: Zertifikat, Lernprofil, Zertifikatsregister
- Ausnahmen: Fehler bei Zertifikatserzeugung, Ablauf, Audit Trail fuer Widerruf

#### 6.2.6 Schulungsberichte und Analysen

- Beschreibung: Stellt Statistiken zu Umsetzung, Lernwirkung und Ressourcennutzung bereit.
- Ausloeser: Ein Manager oder Schulungsadministrator ruft Berichte auf.
- Fachliche Regeln / Logik:
-   Unterstuetzt Abdeckung und Abschluss nach Organisation, Kurs, Zeit und Rolle
-   Unterstuetzt Bestehensquote, Kursbewertung und Feedbackzusammenfassung
-   Unterstuetzt Export und geplante Zustellung
- Eingaben: Anmeldungen, Lernnachweise, Ergebnisse, Feedback
- Ausgaben: Schulungsdashboard, Statistikbericht, Exportdatei
- Ausnahmen: Datenverzug, fehlende Berechtigung, Hinweis bei Aenderung der Definitionen

## 7. Seiten und Prozesse

| Seite / Einstieg | Einstieg | Schluesselinhalte | Hauptaktionen | Ablauf |
| --- | --- | --- | --- | --- |
| Startseite Schulungsportal | Einstieg fuer Lernende | Empfohlene Kurse, offene Aufgaben, Zertifikate, Benachrichtigungen | Kurse suchen, anmelden, Lernen fortsetzen, Zertifikate ansehen | Ein Lernender meldet sich an, prueft Aufgaben und oeffnet einen Kurs. |
| Kursverwaltung | Administrationskonsole | Kursliste, Kursdetail, Inhalte, Trainer, Zielgruppe | Kurs anlegen, Inhalte bearbeiten, veroeffentlichen/zurueckziehen, Kurs kopieren | Ein Administrator pflegt einen Kurs und veroeffentlicht ihn fuer die sichtbare Zielgruppe. |
| Schulungsplanverwaltung | Administrationskonsole | Planliste, Anmeldeliste, Freigabestatus, Benachrichtigungen | Plan veroeffentlichen, Kontingent anpassen, Anmeldungen anzeigen, Liste exportieren | Ein Administrator erstellt einen Plan, das System oeffnet Anmeldung nach Zielgruppe und sendet Nachrichten. |
| Pruefungs- und Zertifikatsverwaltung | Administrationskonsole | Fragenbank, Pruefungsbogen, Pruefungseinrichtung, Ergebnisse, Zertifikatsvorlagen | Pruefung konfigurieren, bewerten, Zertifikat erzeugen, Zertifikat widerrufen | Nach Pruefungsende fasst das System Ergebnisse zusammen und erzeugt Zertifikate nach Regel. |
| Schulungsanalyse-Dashboard | Management-Einstieg | Abdeckung, Abschluss, Bestehensquote, Kursbewertung, Trends | Filtern, Drilldown, Export, Abonnement | Management prueft Schulungswirkung nach Organisation und Zeitraum. |

## 8. Fachliche Regeln und Daten

### 8.1 Fachliche Regeln / Logik

- Nach Ablauf der Frist ist Anmeldung standardmaessig geschlossen; Administratoren koennen mit Berechtigung nacherfassen.
- Ein Lernender darf fuer denselben Schulungsplan nur einen aktiven Anmeldedatensatz haben.
- Kursabschluss kann von Fortschritt, Dauer, Aufgabenabgabe und bestandener Pruefung abhaengen.
- Zertifikatsnummern muessen global eindeutig sein und duerfen nach Widerruf nicht wiederverwendet werden.
- Aenderungen an Ergebnissen und Zertifikaten muessen auditierbar sein.

### 8.2 Wichtige Datenobjekte

- Kurs: Code, Name, Kategorie, Trainer, Inhalte, Zielgruppe, Status
- Schulungsplan: Code, Kurs, Zeitplan, Kontingent, Zielgruppe, Freigaberegeln
- Anmeldedatensatz: Lernender, Plan, Status, Freigeber, Freigabezeit
- Lernnachweis: Lernender, Kurs, Fortschritt, Dauer, Abschlussstatus, Abschlusszeit
- Pruefungsergebnis: Pruefung, Lernender, Punktzahl, Bestehensstatus, Bewertungsstatus
- Zertifikat: Nummer, Lernender, Kurs/Plan, Ausgabezeit, Gueltigkeit, Status

## 9. Nichtfunktionale Anforderungen

- Berechtigungen: Sichtbarkeit und Aktionen nach Rolle, Organisation und Datenbereich steuern.
- Performance: Haeufige Listenabfragen innerhalb von 3 Sekunden; Berichte koennen asynchron erzeugt werden.
- Benutzbarkeit: Wichtige Anmelde- und Lernablaeufe benoetigen Wiederholung und klare Fehlermeldungen.
- Audit: Anmeldefreigabe, Ergebnisbearbeitung und Zertifikatserzeugung/-widerruf muessen protokolliert werden.
- Sicherheit: Pruefungsantworten, Ergebnisse und Zertifikatsdaten als sensible Daten behandeln.

## 10. Integrationen und Abhaengigkeiten

- Organisations- und Mitarbeiterstammdaten
- Zentrale Identitaet / SSO
- Benachrichtigungsdienst
- Elektronisches Siegel oder Zertifikatsdienst
- Unternehmens-DWH / BI

## 11. Risiken und offene Fragen

### 11.1 Risiken

- Uneinheitliche historische Schulungsdaten koennen die Migrationsqualitaet beeinflussen.
- Unterschiedliche Inhaltsformate und Wiedergabefaehigkeiten koennen die Lernerfahrung beeintraechtigen.
- Anforderungen an Betrugsschutz bei Pruefungen und Zertifikats-Compliance muessen frueh bestaetigt werden.
- Unklare Berechtigungsgrenzen zwischen Organisationen koennen Datenisolierung beeintraechtigen.

### 11.2 Offene Fragen

- Sollen Schulungsplaene firmenuebergreifende oder externe Anmeldungen unterstuetzen?
- Sollen Abschlussregeln je Kurs, Plan oder Rolle unterschiedlich konfigurierbar sein?
- Benoetigen Zertifikate elektronisches Siegel, QR-Pruefung oder Gueltigkeitsdauer?
- Benoetigen Pruefungen Zeitlimit, Zufallsbogen, Betrugsschutz und Wiederholungsregeln?
- Welche Schulungsmodule brauchen eigene Seiten im Endprodukt?

## 12. Meilensteine und Abnahme

| Meilenstein | Zieldatum | Abnahmekriterien |
| --- | --- | --- |
| Anforderungsbestaetigung | T+1 Woche | Umfang, Rollen, Kernablaeufe und Reportingdefinitionen bestaetigen |
| Prototyp-Review | T+3 Wochen | Hauptseiten-Prototypen und Prozessreview abschliessen |
| Entwicklung und Integration | T+8 Wochen | Kernfunktionen und externe Integrationen abschliessen |
| Pilotstart | T+10 Wochen | Pilotorganisation starten und Pilotprobleme schliessen |
| Produktivstart | T+12 Wochen | Gesamtrelease, Schulung und Abnahme abschliessen |
