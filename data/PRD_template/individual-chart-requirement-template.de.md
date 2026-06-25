# Vorlage fuer Einzelchart-Anforderungen
> Diese Vorlage definiert fachlichen Bedarf, Datenvertrag, Chart-Verhalten, Entwicklungsumfang und Abnahmekriterien fuer ein einzelnes Chart oder Dashboard-Element.  
> Ersetzen Sie Inhalte in `[]` durch bestaetigte Projektinformationen.

## 1. Grundlegende Dokumentinformationen

| Feld | Wert / Beschreibung |
| --- | --- |
| Vorlagenname | Vorlage fuer Einzelchart-Anforderungen |
| Dokumentname | [D.CHQ.QDM Einzelchart-Anforderung] |
| Chart- / Seitenname | [Chart- oder Seitennamen eingeben] |
| Fachbereich | [CHQ / QDM / KMS / Sonstiges] |
| Anforderer | [Name / Team] |
| Business Owner | [Name / Team fuer fachliche Genehmigung] |
| Product Owner / BA | [Name] |
| Technical Owner | [Name] |
| Autor | [Name] |
| Version | v0.1 Entwurf |
| Status | Entwurf / In Pruefung / Genehmigt / In Entwicklung / Veröffentlicht |
| Prioritaet | Hoch / Mittel / Niedrig |
| Ziel-Release / Faelligkeit | [YYYY-MM-DD] |
| Zugehoeriges System / Modul | [Anwendung, Modul oder Menuepfad] |

## 2. Hintergrund und Ziele

### 2.1 Hintergrund

[Beschreiben Sie fachlichen Kontext, Schmerzpunkt, Entscheidungsszenario und warum dieses Chart benoetigt wird. Nennen Sie Zielnutzer und unterstuetzten Prozess.]

### 2.2 Ziele

- [Primaere Kennzahl] nach [Dimension / Zeitraum] klar visualisieren.
- Trends, Ausnahmen und Vergleichsluecken schnell erkennbar machen.
- Bei Bedarf Drill-down oder Detailpruefung der zugrunde liegenden Datensaetze ermoeglichen.
- Chart-Logik, Datenquelle und UI-Verhalten fuer Entwicklung und UAT standardisieren.

### 2.3 Erfolgskriterien

- Benutzer verstehen die Chart-Aussage ohne manuelle Datenabstimmung.
- Angezeigte Werte entsprechen vereinbarten Quelldaten und Berechnungsregeln.
- Filter, Sortierung, Export und Detailverhalten funktionieren konsistent ueber unterstuetzte Bildschirmbreiten.

## 3. Umfang

| Bereich | Beschreibung |
| --- | --- |
| Im Umfang | [Chart-Visualisierung, Filter, Detailtabelle, Export, Berechtigungen und UAT-Validierung.] |
| Nicht im Umfang | [Ausgeschlossene Funktionen, z. B. neue Datenerfassung, historische Rueckfuellung, komplexe Workflow-Genehmigung.] |
| Annahmen | [Verfuegbarkeit der Quelltabelle, Aktualisierungszeitpunkt, Rollen, Browserunterstuetzung.] |
| Abhaengigkeiten | [APIs, ETL-Jobs, Data Owner, UI-Assets, Plattformkomponenten.] |
| Einschraenkungen | [Performance, Sicherheit, Compliance, Layout oder technische Grenzen.] |

## 4. Verantwortliche und Stakeholder

| Rolle | Name / Team | Verantwortung |
| --- | --- | --- |
| Business Owner | [TBD] | Fachliche Definition, Prioritaet und finale Genehmigung. |
| Data Owner | [TBD] | Datenquelle, Felddefinitionen, Aktualisierungsfrequenz und Qualitaetsregeln. |
| Product Owner / BA | [TBD] | Umfang, Abnahmekriterien und Change Control. |
| UI / UX | [TBD] | Layout, Responsiveness, Lesbarkeit und Interaktion. |
| Frontend Developer | [TBD] | Layout, Chart-Rendering, Interaktion und Browser-Verhalten. |
| Backend / Data Engineer | [TBD] | API, Aggregationslogik, Datensicherheit und Performance. |
| QA / UAT Owner | [TBD] | Testfaelle, Ergebnisvalidierung und Defect-Erfassung. |

## 5. Datenbeschreibung

### 5.1 Datenquelle

| Quelle / Tabelle / API | Owner | Aktualisierungsfrequenz | Datengranularitaet | Hinweise |
| --- | --- | --- | --- | --- |
| XXX_Table | [Data Owner] | Echtzeit / Taeglich / Woechentlich / Monatlich | [Eine Zeile pro ...] | [Verfuegbarkeit, SLA, bekannte Grenzen] |
| [Weitere Quelle] | [Owner] | [Frequenz] | [Granularitaet] | [Join Key / Abhaengigkeit] |

### 5.2 Schluesselfelder und fachliche Definitionen

| Feldname | Fachliche Definition | Datentyp | Pflicht | Quellenmapping / Logik |
| --- | --- | --- | --- | --- |
| XXX_Field_1 | [Fachliche Bedeutung] | String / Zahl / Datum | J / N | [Quellspalte oder Formel] |
| XXX_Field_2 | [Fachliche Bedeutung] | String / Zahl / Datum | J / N | [Quellspalte oder Formel] |
| Dimensionsfeld | [Gruppierung fuer Achse, Legende oder Filter] | String / Datum | J / N | [Mapping / Hierarchie] |
| Kennzahlenfeld | [Im Chart angezeigte Kennzahl] | Zahl | J | [Aggregation, Rundung, Nullbehandlung] |
| Statusfeld | [Farbe, Statussplit oder Ausnahmeindikator] | String | N | [Gueltige Werte und Mapping] |

### 5.3 Berechnungs- und Logikregeln

- Kennzahlenformel: [Zaehler, Nenner, Aggregation, Rundung und Einheit definieren].
- Filterlogik: [Ein- und Ausschluesse vor Aggregation definieren].
- Datumslogik: [Datumsfeld, Zeitzone, Fiskalkalender und Periodengrenze definieren].
- Nullbehandlung: [Ausschliessen, als Unknown gruppieren oder als 0 behandeln].
- Deduplizierung: [Eindeutigen Schluessel und Dublettenbehandlung definieren].

## 6. Seiten- und Chart-Darstellung

### 6.1 Seitenlayout

| Bereich | Inhalt / Verhalten |
| --- | --- |
| Oben: Filterbereich | Filter, Suche, Reset/Apply und Default-Auswahlregeln. |
| Mitte: Chartbereich | Einzelchart mit Titel, Legende, Achsen, Tooltip, Leer-/Lade-/Fehlerzustand. |
| Unten: Detaildaten | Detailtabelle hinter dem Chart, inkl. Paginierung und Export falls erforderlich. |

### 6.2 Chart-Spezifikation

| Feld | Wert / Beschreibung |
| --- | --- |
| Chart-Typ | Linie / Balken / Kreis / Donut / Kombi / KPI / Sonstiges |
| Primaere Kennzahl | [Name und Einheit] |
| X-Achse / Kategorie | [Dimension, Zeitraum oder Kategorie] |
| Y-Achse / Wert | [Kennzahl und Einheit] |
| Legende / Serie | [Serienfeld, falls vorhanden] |
| Sortierung | Aufsteigend / Absteigend / Fachliche Reihenfolge |
| Standardzeitraum | [Aktueller Monat / Letzte 12 Monate / Sonstiges] |
| Tooltip-Inhalt | [Wert, Prozent, Dimension, Zeitraum, Quellenhinweis] |
| Drill-down | Kein / Detailtabelle / Navigation / Modal |
| Leerzustand | [Meldung bei keinen Daten] |
| Lade- / Fehlerzustand | [Spinner, Retry-Meldung, Fallback-Text] |

### 6.3 Filter und Abfragebedingungen

| Filterfeld | Kontrolltyp | Standardwert | Pflicht | Abhaengigkeit / Hinweis |
| --- | --- | --- | --- | --- |
| Datumsbereich | Date Picker | Aktuelle Periode | J / N | Zeitzone, Maximalbereich, Fiskalregel |
| Organisation / Region | Einfach- / Mehrfachauswahl | Benutzerscope / Alle | J / N | Berechtigungsbasierte Optionen |
| Status | Dropdown / Checkboxgruppe | Alle | N | Gueltige Statusliste |
| Stichwort | Suchfeld | Leer | N | Suchbare Felder und Match-Regel |

### 6.4 Detailtabellenfelder

| Spalte | Quellfeld | Anzeigeformat | Sortierbar | Hinweise |
| --- | --- | --- | --- | --- |
| [Spalte 1] | [Quellfeld] | Text / Zahl / Datum | J / N | Maskierung, Link oder Statusstil |
| [Spalte 2] | [Quellfeld] | Text / Zahl / Datum | J / N | Format und Ausrichtung |

## 7. Interaktion, Berechtigungen und Export

| Anforderung | Erwartetes Verhalten |
| --- | --- |
| Responsives Layout | Keine abgeschnittenen Labels oder ueberlappenden Controls auf vereinbarten Breakpoints. |
| Hover / Klick | Tooltip bei Hover; Klick folgt der definierten Drill-down-Regel. |
| Export | Kein Export / Chart-Bild / Detail-CSV oder Excel; Export folgt aktiven Filtern. |
| Berechtigungen | Benutzer sehen nur Daten ihres autorisierten Organisations-, Rollen- oder Datenscopes. |
| Audit / Logging | [Definieren, ob Zugriff, Export oder Drill-down geloggt werden muss.] |
| Barrierefreiheit | Farbe nicht als einziger Statusindikator; Labels, Kontrast und Tastaturzugriff beachten. |

## 8. Entwicklungsanforderungen

- Mit HTML, Bootstrap, JavaScript und jQuery entwickeln, sofern die Zielplattform keinen anderen genehmigten Stack vorgibt.
- Sauberen, strukturierten und wartbaren Code mit Kommentaren fuer nicht offensichtliche Logik schreiben.
- Responsiv, leichtgewichtig und fuer Folgeentwicklung geeignet umsetzen.
- API-Vertrag, Request-Parameter, Response-Schema, Fehlercodes und Paginierung vor Entwicklung bestaetigen.

### 8.1 Performance und Sicherheit

| Kategorie | Anforderung |
| --- | --- |
| Performance | [Ladezeit, maximale Zeilen, Aggregation, Cache-Regel und Timeout definieren.] |
| Sicherheit | [Authentifizierung, Autorisierung, Maskierung, Exportbeschraenkung und sensible Felder definieren.] |
| Kompatibilitaet | [Unterstuetzte Browser, Bildschirmbreiten und Plattformgrenzen definieren.] |
| Fehlerbehandlung | [Benutzerfreundliche Fehlermeldungen und Fallback bei API-/Datenfehlern definieren.] |

## 9. Farbsystem

| Token | Genehmigter Wert |
| --- | --- |
| Background | #f6f8fb / #f3f5f7 |
| Panel | #ffffff |
| Hover Surface | #eef2f4 |
| Soft Blue Panel | #f0f6ff |
| Primary Text | #111315 |
| KMS Text | #17202a |
| Secondary Text | #424a55 / #647280 |
| Border | #d9e1e7 / rgba(17,19,21,0.17) |
| Primary Blue | #2563eb |
| Danger / Error / Warning | #c2413b / #b43636 / #a56313 |

## 10. Abnahmekriterien und UAT-Checkliste

| ID | Abnahmekriterium | Owner | Status |
| --- | --- | --- | --- |
| AC-01 | Chart-Werte entsprechen Quelldaten und Berechnungsregeln. | QA / Data Owner | Pending |
| AC-02 | Alle Filter funktionieren korrekt und setzen auf dokumentierte Defaults zurueck. | QA | Pending |
| AC-03 | Tooltip, Legende, Achsenlabels sowie Leer-/Lade-/Fehlerzustaende werden korrekt angezeigt. | QA / UI | Pending |
| AC-04 | Detailtabelle passt zum ausgewaehlten Chartsegment und aktiven Filtern. | QA / Data Owner | Pending |
| AC-05 | Export folgt aktiven Filtern und Berechtigungsscope. | QA / Security | Pending |
| AC-06 | Seite ist responsiv ohne Clipping, Ueberlappung oder unlesbare Labels. | QA / UI | Pending |

## 11. Offene Fragen und Aenderungsprotokoll

| Nr. | Frage | Owner | Faelligkeit | Klaerung |
| --- | --- | --- | --- | --- |
| 1 | Quelltabelle und finales Feldmapping bestaetigen. | TBD | YYYY-MM-DD | Offen |
| 2 | Chart-Typ und Drill-down-Verhalten bestaetigen. | TBD | YYYY-MM-DD | Offen |
| 3 | Berechtigungsscope und Exportregel bestaetigen. | TBD | YYYY-MM-DD | Offen |
