# Vorlage fuer fachliche Anforderungen im Finanzmanagement
> Zweck: fuer Finanzmanagement-Szenarien wie Spesenabrechnung, Budgetkontrolle, Zahlungsantraege, Rechnungsmanagement, Debitoren/Kreditoren und Finanzanalyse.  
> Verwendung: Ersetzen Sie die Hinweise in `[]` durch reale fachliche Inhalte; nicht relevante Punkte koennen entfernt werden.

## 1. Basisinformationen

| Feld | Inhalt |
| --- | --- |
| Vorlagenname | Vorlage fuer fachliche Anforderungen im Finanzmanagement |
| Anforderungsname | [Beispiel: Optimierung des Spesenabrechnungsmanagements] |
| Projekt | [Projektname eingeben] |
| Anforderungstyp | Neuentwicklung / Optimierung / Refactoring |
| Prioritaet | Hoch / Mittel / Niedrig |
| Anfordernde Abteilung | [Abteilung eingeben] |
| Anforderer | [Name eingeben] |
| Anforderungsdatum | [YYYY-MM-DD] |
| Version | V1.0 |

## 2. Fachlicher Hintergrund

### 2.1 Hintergrundbeschreibung

[Beschreiben Sie den aktuellen Betrieb des Finanzprozesses, die fachliche Groesse, bestehende Ablaeufe und den Grund fuer den Aufbau dieser Faehigkeit.]

Beispiel: Aktuelle Finanzprozesse sind ueber Excel, E-Mail, ERP und manuelle Genehmigungen verteilt. Datenwege sind uneinheitlich, Genehmigungen dauern lange und die Budgetkontrolle erfolgt zu spaet. Mit wachsendem Geschaeft reicht der bestehende Prozess nicht mehr fuer differenziertes Management und Audit-Compliance aus.

### 2.2 Aktuelle Schmerzpunkte

- [Beispiel: Spesenantraege laufen offline und Genehmigungszyklen sind lang]
- [Beispiel: Budgetausfuehrung wird nicht in Echtzeit geprueft]
- [Beispiel: Zahlungsstatus ist schwer nachvollziehbar, Rechnungen und Vertraege sind verteilt]
- [Beispiel: Finanzstatistiken nutzen unterschiedliche Definitionen und Monatsabstimmung dauert zu lange]

## 3. Ziele

### 3.1 Fachliche Ziele

- [Beispiel: Einheitlichen Einstieg fuer Finanzprozesse schaffen]
- [Beispiel: Effizienz von Genehmigung, Pruefung und Zahlung erhoehen]
- [Beispiel: End-to-End-Budgetkontrolle vor, waehrend und nach Ausgaben ermoeglichen]
- [Beispiel: Datennachvollziehbarkeit verbessern und Audit-Anforderungen erfuellen]

### 3.2 Messbare Kennzahlen

- [Beispiel: Durchschnittliche Genehmigungsdauer fuer Abrechnungen um 50% reduzieren]
- [Beispiel: Budgetueberschreitungsrate um 80% senken]
- [Beispiel: Monatliche Abstimmungszeit um 30% verkuerzen]
- [Beispiel: Bearbeitungseffizienz von Zahlungsantraegen um 40% verbessern]

## 4. Fachlicher Umfang

### 4.1 Im Umfang enthalten

- Spesenantraege
- Abrechnungsfreigabe
- Rechnungsupload und Validierung
- Budgetreservierung und Kontrolle
- Zahlungsantraege und Nachverfolgung
- Finanzbuch und Berichtswesen

### 4.2 Nicht im Umfang enthalten

- Hauptbuchhaltung
- Steuererklaerung
- Direkte Bankanbindung
- Konsolidierte Berichte

## 5. Rollen und Kernszenarien

### 5.1 Zielrollen

- Mitarbeitende: reichen Spesen-, Abrechnungs- und Zahlungsantraege ein und verfolgen den Bearbeitungsstatus
- Abteilungsverantwortliche: fuehren fachliche Freigaben und Budgetbestaetigungen durch
- Finanzspezialisten: pruefen Belege, bearbeiten Zahlungen und pflegen Ledger-Daten
- Finanzmanager: fuehren Nachpruefung, Budgetmanagement und Finanzanalyse durch
- Management: sieht operative und finanzielle Zusammenfassungen
- Systemadministratoren: pflegen Workflows, Berechtigungen und Grundkonfiguration

### 5.2 Zentrale Geschaeftsszenarien

1. Mitarbeitende starten Ausgaben- oder Zahlungsantraege; das System prueft Pflichtangaben und Budgetsaldo automatisch.
2. Abteilungsverantwortliche schliessen die fachliche Genehmigung ab und ergaenzen Kommentare oder lehnen ab.
3. Finance prueft Belege, Rechnungen und Vertragsanhaenge auf Einhaltung der Finanzregeln.
4. Freigegebene Antraege gehen in den Zahlungsprozess; Finance verfolgt Zahlungsergebnisse und archiviert Nachweise.
5. Abgeschlossene Belege fliessen automatisch in Ledger und Berichte fuer Analyse und Audit.

## 6. Funktionale Anforderungen

### 6.1 Funktionsuebersicht

[Beschreiben Sie die Kernfaehigkeiten, die fuer diese Finanzmanagement-Anforderung aufgebaut werden sollen.]

Beispiel: Die Anforderung umfasst Antragstellung, Genehmigung, Budgetkontrolle, Rechnungs-/Belegmanagement, Zahlungsmanagement und Reporting. Ziel ist ein durchgaengiger Finanzprozess mit hoeherer Standardisierung und Effizienz.

### 6.2 Funktionsdetails

#### Funktion 1: Antragsmanagement

- Beschreibung: Unterstuetzt Spesen-, Abrechnungs- und Zahlungsantraege durch Mitarbeitende.
- Ausloeser: Nutzer klickt im System auf "Neuer Antrag".
- Verarbeitungslogik:
  - Entwurf speichern, einreichen, zurueckziehen und kopieren
  - Pflichtfelder, Betragsformat und Vollstaendigkeit von Anhaengen pruefen
  - Antragsnummer automatisch erzeugen
- Eingaben:
  - Antragstyp
  - Abteilung
  - Kostenkategorie
  - Betrag
  - Projekt-/Vertrags-/Lieferanteninformationen
  - Anhaenge
- Ausgaben:
  - Antragsformular
  - Antragsstatus
  - Vorgangsprotokoll
- Ausnahmefaelle:
  - Pflichtfelder fehlen
  - Betragsformat ist ungueltig
  - Anhaenge fehlen

#### Funktion 2: Genehmigungsmanagement

- Beschreibung: Unterstuetzt Genehmigungsablaeufe nach Organisationsstruktur und Geschaeftsregeln.
- Ausloeser: Nach Einreichung gelangt der Antrag automatisch in den Genehmigungsfluss.
- Verarbeitungslogik:
  - Mehrstufige Genehmigung, Mitzeichnung, Zusatzfreigabe und Ablehnung unterstuetzen
  - Genehmigungsergebnisse steuern Status und Weiterleitung
  - Erinnerungen bei ueberfaelligen Genehmigungen ausloesen
- Eingaben:
  - Genehmigungsknotenkonfiguration
  - Genehmigungskommentar
  - Genehmigungsergebnis
- Ausgaben:
  - Genehmigungsprotokoll
  - Workflow-Status
  - Benachrichtigungen
- Ausnahmefaelle:
  - Genehmiger fehlt
  - Genehmigung ist ueberfaellig
  - Workflow-Konfiguration ist fehlerhaft

#### Funktion 3: Budgetkontrolle

- Beschreibung: Fuehrt Budgetpruefung und Reservierung in Antragstellung und Finanzpruefung aus.
- Ausloeser: Bei Einreichung oder Finanzpruefung eines Antrags.
- Verarbeitungslogik:
  - Budget nach Abteilung, Projekt und Kostenkategorie pruefen
  - Budgetreservierung, Freigabe und Ausfuehrungsstatistik unterstuetzen
  - Budgetueberschreitungen in Sonderfreigabe oder Warnprozess leiten
- Eingaben:
  - Budgetdimension
  - Budgetbetrag
  - Aktueller Antragsbetrag
- Ausgaben:
  - Budgetpruefergebnis
  - Budgetreservierung
  - Budgetwarnung
- Ausnahmefaelle:
  - Budget nicht konfiguriert
  - Budgetsaldo unzureichend
  - Budgetdimension passt nicht

#### Funktion 4: Rechnungs- und Belegmanagement

- Beschreibung: Unterstuetzt Verwaltung von Rechnungen, Vertraegen, Zahlungsbelegen und weiteren Anhaengen.
- Ausloeser: Beim Upload von Belegen oder bei Finanzpruefung.
- Verarbeitungslogik:
  - Rechnungserfassung, Anhang-Upload und Belegverknuepfung unterstuetzen
  - Dublettenpruefung und Vollstaendigkeitspruefung unterstuetzen
  - Belegstatus pflegen
- Eingaben:
  - Rechnungsnummer
  - Rechnungsbetrag
  - Ausstellungsdatum
  - Anhangdatei
  - Zugehoerige Vertragsnummer
- Ausgaben:
  - Belegdatensatz
  - Dublettenpruefergebnis
  - Pruefstatus
- Ausnahmefaelle:
  - Doppelte Rechnung
  - Rechnungsdaten passen nicht zum Antragsbetrag
  - Beleganhang ist defekt oder fehlt

#### Funktion 5: Zahlungsmanagement

- Beschreibung: Unterstuetzt Zahlungspruefung, Zahlungsausfuehrung und Ergebnisverfolgung.
- Ausloeser: Startet nach bestandener Finanzpruefung.
- Verarbeitungslogik:
  - Empfaengerinformationen und Zahlungsbedingungen pruefen
  - Zahlungsstatus und Belege dokumentieren
  - Rueckschreibung und Archivierung nach Zahlung abschliessen
- Eingaben:
  - Empfaengerinformationen
  - Zahlungsbetrag
  - Zahlungskonto
  - Zahlungsnotiz
- Ausgaben:
  - Zahlungsauftrag
  - Zahlungsstatus
  - Zahlungsbeleg
- Ausnahmefaelle:
  - Empfaengerinformationen fehlen
  - Zahlung fehlgeschlagen
  - Risiko doppelter Zahlung

#### Funktion 6: Reporting und Analyse

- Beschreibung: Bietet Analyse nach Ausgaben-, Budget-, Zahlungs- und weiteren Dimensionen.
- Ausloeser: Nutzer fragt Berichte ab oder das System erstellt geplante Zusammenfassungen.
- Verarbeitungslogik:
  - Filter nach Zeit, Abteilung, Projekt und Kostenkategorie unterstuetzen
  - Excel-Export unterstuetzen
  - Zusammenfassungen fuer Management bereitstellen
- Eingaben:
  - Suchbedingungen
  - Statistikdimensionen
  - Zeitraum
- Ausgaben:
  - Ausgabenbericht
  - Budgetausfuehrungsbericht
  - Zahlungsfortschrittsbericht
- Ausnahmefaelle:
  - Daten fehlen
  - Definitionen sind uneinheitlich
  - Export fehlgeschlagen

## 7. Geschaeftsregeln

- Jeder Antrag muss Kostenkategorie, Abteilung, Leistungsdatum und weitere Basisinformationen enthalten.
- Budgetueberschreitungen duerfen nicht direkt genehmigt werden und muessen in Sonderfreigabe oder Warnprozess gehen.
- Rechnungen, Vertraege und Zahlungsbelege muessen mit Antraegen verknuepft und archiviert werden.
- Finanzpruefung startet erst nach Genehmigung; Zahlung startet erst nach Finanzpruefung.
- Eine Ablehnung durch Finance muss einen Grund enthalten und protokolliert werden.
- Derselbe Geschaeftsantrag darf nicht mehrfach zur Zahlung eingereicht werden.
- Nach Zahlung muss der Status automatisch auf Bezahlt oder einen gleichwertigen Status wechseln.

## 8. Seiten- und Interaktionsvorschlaege

#### Seite 1: Antragsliste

- Einstiegspunkt: Finanzmanagement-Startseite / Meine Antraege
- Seitenelemente: Filterbereich, Antragsliste, Statuslabel, Exportbutton
- Schaltflaechenaktionen: Antrag erstellen, Details anzeigen, zurueckziehen, exportieren

#### Seite 2: Antragsdetail

- Einstiegspunkt: Klick aus der Antragsliste
- Seitenelemente: Basisinformationen, Kostendetails, Anhangbereich, Genehmigungsprotokoll, Budgetpruefergebnis
- Schaltflaechenaktionen: Einreichen, Entwurf speichern, bearbeiten, Anhang hochladen

#### Seite 3: Genehmigungsseite

- Einstiegspunkt: Aufgaben-Center / Genehmigungsaufgaben
- Seitenelemente: Antragsinformationen, Anhanginformationen, Kommentarfeld, Budgethinweis, Workflow-Knoten
- Schaltflaechenaktionen: Genehmigen, ablehnen, weiterleiten, zusaetzlichen Genehmiger hinzufuegen

#### Seite 4: Zahlungsbearbeitung

- Einstiegspunkt: Finance Workbench / Offene Zahlungen
- Seitenelemente: Zahlungsinformationen, Empfaengerinformationen, Beleg-Upload, Zahlungsstatus
- Schaltflaechenaktionen: Zahlung bestaetigen, Beleg hochladen, als fehlgeschlagen markieren

#### Seite 5: Finanzberichte

- Einstiegspunkt: Finanzanalyse / Berichtszentrum
- Seitenelemente: Filter, Kennzahlenkarten, Diagramme, Detailtabelle
- Schaltflaechenaktionen: Suchen, exportieren, Statistikdimension wechseln

### 8.1 Interaktionsablauf

1. Nutzer erstellt und reicht einen Antrag ein.
2. Das System prueft Pflichtfelder, Budget und Vollstaendigkeit der Anhaenge.
3. Genehmiger schliessen die Genehmigung ab, danach fuehrt Finance die Pruefung durch.
4. Nach bestandener Pruefung geht der Antrag in die Zahlung und das finale Ergebnis wird zurueckgeschrieben.
5. Daten werden in Berichte und Ledger synchronisiert.

## 9. Daten und Abhaengigkeiten

### 9.1 Schluesseldaten

- Antragsnummer
- Antragsteller
- Abteilung
- Kostenkategorie
- Projektname
- Betrag
- Rechnungsinformationen
- Vertragsnummer
- Budgetbetrag und Restsaldo
- Genehmigungsstatus
- Zahlungsstatus
- Erstellungszeit, Aktualisierungszeit, Bediener

### 9.2 Externe Abhaengigkeiten

- Organisationsstrukturdaten
- Mitarbeiterdaten
- Budgetstammdaten
- Lieferanten- und Empfaengerstammdaten
- Externe ERP-/OA-/HR-Systeme

## 10. Berechtigungs- und Risikokontrolle

- Mitarbeitende koennen nur eigene Antragsdaten sehen und bearbeiten.
- Abteilungsverantwortliche koennen relevante offene und genehmigte Daten ihrer Abteilung sehen.
- Finanzmitarbeitende koennen alle Finanzbelege sehen und bearbeiten.
- Management kann Zusammenfassungen sehen, aber keine Geschaeftsbelege aendern.
- Alle wichtigen Aktionen muessen fuer Audit-Zwecke protokolliert werden.
- Hohe Risiken wie unzureichendes Budget, doppelte Rechnungen oder doppelte Zahlungen muessen blockiert oder deutlich gewarnt werden.

## 11. Nicht-funktionale Anforderungen

- Seitenantwortzeit darf 3 Sekunden nicht ueberschreiten.
- Unterstuetzung von mindestens [Anzahl eingeben] gleichzeitigen Online-Nutzern.
- Uebertragung und Speicherung wichtiger Daten muessen verschluesselt werden.
- Zielverfuegbarkeit von 99,9% unterstuetzen.
- Genehmigung auf PC und mobilen Geraeten unterstuetzen.

## 12. Abnahmekriterien

- Antrag, Genehmigung, Pruefung, Zahlung und Archivierung laufen Ende-zu-Ende.
- Budgetprueflogik entspricht den fachlichen Erwartungen.
- Rechnungsdublettenpruefung und Anhangvalidierung sind wirksam.
- Berichtsdaten stimmen mit den Geschaeftsbelegen ueberein.
- Berechtigungstrennung ist korrekt und unberechtigter Zugriff wird blockiert.
- Alle wichtigen Knoten besitzen Audit-Protokolle.

## 13. Risiken und offene Fragen

### 13.1 Risiken

- Uneinheitliche historische Finanzdaten koennen Migration und Abstimmung beeinflussen.
- Komplexe Genehmigungsregeln koennen den Rollout beeinflussen, wenn sie nicht frueh geklaert werden.
- Instabile externe Schnittstellen koennen Budget- oder Zahlungssynchronisierung beeinflussen.

### 13.2 Offene Fragen

- Wird eine bidirektionale Echtzeitsynchronisierung mit ERP benoetigt?
- Sollen Budgetueberschreitungen blockiert oder ueber Sonderfreigaben behandelt werden?
- Muss Rechnungsvalidierung an externe Prueffaehigkeiten angebunden werden?
- Folgen Berichtskennzahlen der Finanz- oder der Fachdefinition?

## 14. Meilensteinplan

| Phase | Datum |
| --- | --- |
| Anforderungsbestaetigung | [YYYY-MM-DD] |
| Prototyp-Review | [YYYY-MM-DD] |
| Entwicklung abgeschlossen | [YYYY-MM-DD] |
| Test abgeschlossen | [YYYY-MM-DD] |
| UAT-Abnahme | [YYYY-MM-DD] |
| Produktivsetzung | [YYYY-MM-DD] |
