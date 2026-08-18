# QDM Finished-Lot-Yield-Dashboard Anforderungsvorlage

> Diese Vorlage wurde aus `D.CHQ.QDM Yield Dashboard Requirement .docx` abgeleitet.  
> Die urspruenglich eingebetteten Bilder wurden durch Textbeschreibungen ersetzt, damit die Vorlage fuer strukturierte Anforderungserhebung und Markdown-Generierung nutzbar ist.

## 1. Basisdokumentinformationen

| Feld | Wert |
| --- | --- |
| Vorlagenname | QDM Finished-Lot-Yield-Dashboard Anforderungsvorlage |
| Dokumentname | D.CHQ.QDM Finish Yield Dashboard Requirement |
| System / Modul | FinishedLot |
| Initiierende Abteilung | QDM |
| Autor / Anforderer | Ely Yi |
| Version | V1.0 |
| Erstellungsdatum | 2026-05-21 |
| Geschaeftsbereich | Manufacturing quality / finished lot yield / QDM dashboard |
| Status | Entwurf / In Pruefung / Freigegeben / In Entwicklung / Released |
| Zielrelease | [YYYY-MM-DD] |

## 2. Hintergrund und Ziele

### 2.1 Hintergrund

Das Dashboard dient als High-Level-Sicht auf aktuelle wichtige Yield-Metriken fuer verschiedene Produkte im Werk. Die Daten sollen per automatisiertem Zeitplan aktualisiert werden, standardmaessig taeglich, sofern der Data Owner keine andere Kadenz bestaetigt.

Das Dashboard muss unterstuetzen:

- Gesamten Yield-Trend und Drill-down nach Segmenten oder Produkten.
- Hierarchische Trends der Main Bins und kumulative Bins.
- Pareto-Analyse nach Loss Code und Loss Operation.
- Loss Attribution nach Root Cause oder verantwortlicher Abteilung.

### 2.2 Ziele

- Eine deutlich steilere Yield-Verbesserungskurve sichtbar machen.
- Produktionskosten schnell senken.
- Produktionsoutput ohne wesentliche Zusatzkosten erhoehen.
- Investitionskosten frueher amortisieren.

### 2.3 Erfolgskriterien

- Business Owner und Data Owner bestaetigen Metrikdefinitionen, Filter, Quelltabellen, Refresh-Kadenz und Abnahmeregeln.
- Nutzer erkennen auf dem ersten Screen den neuesten Finished-Lot-Yield, Output, Loss und wichtigste Defect-Treiber.
- Nutzer koennen vom Yield-Trend zu Defect-Code-Loss und verantwortlicher Abteilung drillen.
- Dashboardwerte stimmen unter repraesentativen Filtern mit freigegebenen Quellabfragen ueberein.

## 3. Seiten- / Funktionsdarstellung

### 3.1 Finished Lot Performance Overview Trend

| Element | Anforderung |
| --- | --- |
| Seitenname | Finished Lot Performance Overview Trend |
| Zweck | Finished Yield nach Zeitraum anzeigen und fuer die neueste Woche Output, Yield und NSQM Loss darstellen. |
| Oberer Bereich | Einheitliche Suchkriterien aus Abschnitt 4 verwenden. |
| Y-Achsen-Datenbereich | Das Hauptdiagramm zeigt standardmaessig pro Woche die Finished Product Yield Rate. Rechts werden standardmaessig Detaildaten der neuesten Woche gezeigt. Klicks auf linke Datenpunkte oder Balken wechseln die Detailansicht. |
| X-Achsen-Bereich | Das Hauptdiagramm zeigt standardmaessig Wocheninformationen; Detaildiagramme zeigen die Beschreibung der selektierten Daten. |

Textbeschreibung anstelle des urspruenglichen Screenshots:

- Header: `QUALITY OPERATION CENTER - Weekly Finished Lot Performance Overview`.
- Rechts oben: Wochenauswahl, z. B. `W 202621`, und Export-/Download-Aktion.
- Hauptbereich: grosses Diagramm `Weekly Finished Lot Performance Overview Trend`.
- Die X-Achse zeigt Perioden wie `202612` bis `202621`.
- Das Diagramm kombiniert Balken und Linien: Wochenwerte werden als Balken gezeigt, Linien zeigen Target-, Output- oder Yield-Kontext.
- Die selektierte Woche wird visuell hervorgehoben; ein Hinweis erklaert, dass ein Klick auf den Weekly-Yield-Balken die Defect Analysis darunter aktualisiert.
- Rechte KPI-Karten zeigen Yield / Target, Finished Count, NSQM oder NSOM Output und NSQM oder NSOM Loss.
- Beispielwerte aus der Quelle: Yield / Target `96.83%`, Target `94.81%`, Finished Count `159 Lots`, Output `1,335.57`, Loss `63.55`.
- Das finale Label `NSQM` oder `NSOM` muss bestaetigt werden, da die Quelle inkonsistent wirkt.

### 3.2 Loss Ratio By Defect Code

| Element | Anforderung |
| --- | --- |
| Seitenname | Loss Ratio By Defect Code |
| Zweck | Top 10 bis Top 20 Defect Loss Ratio nach Defect Code und Defect-Code-Trend anzeigen. |
| Oberer Bereich | Einheitliche Suchkriterien aus Abschnitt 4 verwenden. |
| Y-Achsen-Datenbereich | Das Hauptdiagramm zeigt Top 10 bis Top 20 Defect Loss Ratio. Rechts werden Trend und Ursachenabteilung fuer den selektierten Defect Code angezeigt. |
| X-Achsen-Bereich | Das Hauptdiagramm zeigt Defect-Code-Informationen; das rechte Pie-/Donut-Diagramm zeigt Department-Informationen. |

Textbeschreibung anstelle des urspruenglichen Screenshots:

- Header bleibt `QUALITY OPERATION CENTER - Weekly Finished Lot Performance Overview`.
- Eine horizontale Periodenauswahl zeigt Wochen wie `202612` bis `202621`.
- Der Analysebereich heisst `Loss Ratio By Defect Code`.
- Toggle-Steuerungen erlauben `Loss Ratio` und `Core Loss Ratio` ein- oder auszublenden.
- Das Hauptdiagramm ist ein sortiertes horizontales Balkendiagramm, z. B. `202621 Top 10 Loss Ratio By Defect Code`.
- Rote Balken stehen fuer total loss ratio, blaue Balken fuer core loss ratio.
- Beispiel-Defect-Codes: `ED25 - Short in inner layer`, `ED21 - High resistance short`, `AP09 - Component tilting`, `BM31 - Base material dent`, `GE01 - Scratches`, `SM94 - Solder mask thickness`, `SM41 - Soldermask discoloration`, `ED55 - Short bridge die region`, `HO31 - Via not completely filled`.
- Die Auswahl eines Defect Codes aktualisiert die rechten Detailkarten.
- Das rechte Trenddiagramm, z. B. `ED25 Weekly Overview Trend`, vergleicht Core Defect Loss und Defect Loss Ratio ueber die Zeit.
- Das rechte Donut-Diagramm zeigt Department Attribution. Beispielsegmente: `Etching + AOI 59%`, `Assembly 23%`, `Final Check 11%`, `Material 7%`, mit Mittelwert `26.26%`.

## 4. Abfragebedingungen und Nutzerinteraktionen

### 4.1 Filter

Textbeschreibung anstelle des Filter-Screenshots:

- Der Filterbereich nutzt zwei Zeilen und drei Spalten.
- Zeile 1 enthaelt `Customer`, `Plant`, `Date Type`.
- Zeile 2 enthaelt `Lot Type`, `Unit Type`, `Project Type`.
- Alle Controls sind Dropdowns mit sichtbarem Pfeil.
- Standardwerte: `Customer = All selected`, `Plant = All selected`, `Date Type = Weekly`, `Lot Type = HVM`, `Unit Type = NSQM`, `Project Type = Overall`.

| Filter | Control-Typ | Standardwert | Gilt fuer |
| --- | --- | --- | --- |
| Customer | Dropdown | All selected | Alle passenden Charts |
| Plant | Dropdown | All selected | Alle passenden Charts |
| Date Type | Dropdown | Weekly | Alle passenden Charts |
| Lot Type | Dropdown | HVM | Alle passenden Charts |
| Unit Type | Dropdown | NSQM | Alle passenden Charts |
| Project Type | Dropdown | Overall | Alle passenden Charts |

### 4.2 Interaktionsregeln

- Filteraenderungen sollen alle betroffenen Charts aktualisieren, ohne die ganze Seite neu zu laden, sofern technisch machbar.
- Selektierte Chartsegmente muessen einen sichtbaren aktiven Zustand haben und den aktiven Filterkontext erkennbar machen.
- Tooltips muessen auf Desktop gut lesbar sein; auf Touchgeraeten soll bei Bedarf ein tap-freundliches Detailverhalten verwendet werden.
- Interaktive Legenden muessen per Tastatur erreichbar sein.
- Exportaktionen muessen Datenberechtigungen beachten und nach Moeglichkeit den angewendeten Filterkontext enthalten.

## 5. Datenbeschreibung und Datenvertrag

### 5.1 Datenquellen

| Source ID | Tabelle / View / API | Beschreibung | Datengranularitaet | Refresh-Kadenz | Owner |
| --- | --- | --- | --- | --- | --- |
| DS-01 | `[QDMProductionDB].[IDA].[Yield_Dashboard_FinishedLotSummaryData_Internal]` | Hauptquelle fuer berechneten Finished-Lot-Yield. | Weekly / Quarterly / Monthly | Weekly oder bestaetigte Kadenz | QDM |
| DS-02 | `[QDMProductionDB].[IDA].[Yield_Dashboard_FinishedLotSummaryDefectData_Internal]` | Zusatzdaten fuer Defect-Code-Vergleich und Detailcharts. | Weekly / Quarterly / Monthly | Weekly oder bestaetigte Kadenz | QDM |

### 5.2 Erforderliche Datenfelder

| Feldname | Quelle | Typ | Pflicht | Business-Definition / Logik |
| --- | --- | --- | --- | --- |
| `ATSDate` | DS-01 | Date / period | Ja | Fuer Trend, Periodenvergleich und Datumsfilter. |
| `DateType` | DS-01 | Date / period | Ja | Definiert weekly, monthly oder quarterly Grain. |
| `LotType` | DS-01 | String / code | Ja | Fuer Filterung oder Vergleich nach Lot Type. |
| `Project Type` | DS-01 | String / code | Ja | Fuer Filterung oder Vergleich nach Project Type. |
| `Yield` | DS-01 | Number / percent | Ja | Zentrale Finished-Yield-Metrik. |
| `Output_NSQM` | DS-01 | Number | Ja | Zentrale Output-Metrik. |
| `DefectCode` | DS-02 | String / code | Ja | Fuer Defect-Code-Ranking und Drill-down. |
| `DefectQty` | DS-02 | Number | Ja | Zentrale Defect Quantity oder Loss Value. |
| `Department` | DS-02 | String / code | Ja | Fuer Loss Attribution nach Department. |

### 5.3 Zu bestaetigende Datenregeln

- Klaeren, ob die Aktualisierung weekly, daily oder beides ist; die Quelle nennt Daily Automation und zugleich Weekly Cadence.
- Gueltige Periodengranularitaet und `DateType` Werte bestaetigen.
- Klaeren, ob `Customer`, `Plant`, `LotType`, `UnitType`, `ProjectType` direkt in DS-01/DS-02 liegen oder ueber Referenztabellen kommen.
- Klaeren, ob Output und Loss NSQM, Lots, Units oder mehrere Unit-Modi verwenden.
- Nullwerte, Nenner 0, Rundung und Prozentformat definieren.
- Berechtigungsumfang fuer Customer, Plant, Product und exportierbare Detaildaten definieren.

## 6. Yield-Berechnungslogik

### 6.1 Finished Yield Definition

Finished Yield, auch Product Yield, ist der Prozentsatz der Einheiten, die den gesamten Fertigungsprozess erfolgreich durchlaufen und als Fertigware fuer ein bestimmtes Lot oder eine bestimmte Woche ausgeliefert werden. Er beschreibt die gesamte Yield-Leistung der Linie.

Kernlogik: Multiplikation der Output/Input-Verhaeltnisse aller wichtigen Prozessschritte, also das Produkt der einzelnen Process Yields.

### 6.2 Formeltext anstelle der Formelbilder

| Formel | Textversion |
| --- | --- |
| Lot Product Yield | `Lot Product Yield = (PAOI Output / PAOI Input) x (E-test Output / E-test Input) x (CCAOI Output / CCAOI Input) x (Bump AOI Output / Bump AOI Input) x (FVI Output / FVI Input)` |
| Weekly Product Yield | `Weekly Product Yield = Produkt der woechentlichen shipped output/input ratios je Prozess`, z. B. `(Total Weekly Shipped PAOI Output / Total Weekly Shipped PAOI Input) x (Total Weekly Shipped E-test Output / Total Weekly Shipped E-test Input) x ...` |
| Erweiterungsregel | Wenn der freigegebene Prozesspfad `Inline`, `Others` oder weitere Schritte enthaelt, muessen deren Yield Ratios ebenfalls multipliziert werden. |

### 6.3 Berechnungsschritte und Beispiel

Prinzip: `Output / Input = Process Yield`, danach werden alle Process Yields sequenziell multipliziert.

| Process | Input | Output | Losses | Yield |
| --- | ---: | ---: | ---: | ---: |
| PAOI | 50000 | 49700 | 300 | 99.4% |
| E-test | 49700 | 49500 | 200 | 99.5% |
| CCAOI | 49250 | 48900 | 350 | 99.29% |
| Bump | 48600 | 48300 | 300 | 99.38% |
| FVI | 48300 | 47900 | 400 | 99.17% |
| Inline | 49500 | 49250 | 250 | 99.49% |
| Others | 48900 | 48600 | 300 | 99.39% |

Beispielausdruck aus der Quelle:

`GTY = 99.4% x 99.5% x 99.29% x 99.38% x 99.17% x 99.49% x 99.39%`

## 7. Seiten- / Funktionslayout

Die Seite soll je nach Business-Prioritaet, Datendichte und Bildschirmgroesse ein passendes Layout verwenden. Empfohlen ist Primary-Detail / Hero fuer analytische Seiten; Uniform Grid ist Fallback fuer Monitoring-Dashboards.

| Layoutoption | Beschreibung | Bester Einsatzfall | Empfehlung |
| --- | --- | --- | --- |
| Primary-Detail / Hero | Ein grosses Hero-Chart im Hauptbereich, unterstuetzende KPI-Karten und Charts seitlich oder darunter. | Analyseseiten mit einer dominanten Businessfrage. | Standardempfehlung, sofern Business Owner nichts anderes bestaetigt. |
| Nested / Drill-down | Auswahl in einem Chart aktualisiert oder filtert ein anderes Chart. | Explorative Analyse und Kategorien-Drill-down. | Nur verwenden, wenn Chart-Beziehungen klar definiert sind. |
| Uniform Grid | Charts haben konsistente Kartengroessen und aehnliche Prioritaet. | Monitoring-Dashboards mit vergleichbaren Metriken. | Fallback, wenn kein dominantes Chart existiert. |

## 8. Chart-Inventar und Konfiguration

Jedes Chart sollte vor Entwicklungsbeginn spezifiziert werden.

| Chart ID | Chartname | Typ | Primaere Metrik | Dimension / Gruppierung | Datenquelle | Interaktion |
| --- | --- | --- | --- | --- | --- | --- |
| CH-01 | Finished Overall Trend | Linien- und Balken-Kombination | Yield / target / output | Weekly / Quarterly / Monthly | DS-01 | Hover Tooltip; Klick auf Wochenbalken oder Punkt filtert Detailtabelle und Defect Analysis. |
| CH-02 | Defect Loss Ratio | Gestapeltes oder gruppiertes horizontales Balkendiagramm | Defect loss ratio / core loss ratio | Top 10 bis Top 20 defect codes | DS-02 | Legendenumschaltung; Klick auf Defect Code aktualisiert Trend und Department Attribution. |
| CH-03 | Rechtes Detail-Chart | Tabelle / Linie / Pie oder Donut | Details basierend auf linker Auswahl | Aktuelle Periode, selektierter Defect, Filter | DS-01 + DS-02 | Pagination, Sorting, Tooltip, Auswahlverknuepfung, Export. |

## 9. Verantwortliche und Stakeholder

| Rolle | Name / Team | Verantwortung | Sign-off erforderlich |
| --- | --- | --- | --- |
| Business Owner | Yield team | Bestaetigt Businesszweck, Prioritaet und Chart-Bedeutung. | Ja |
| Product Owner / BA | QDM | Pflegt Anforderungen, klaert Scope-Fragen, koordiniert Review. | Ja |
| Data Owner | Yield team | Bestaetigt Quelltabellen, Felder, Refresh-Kadenz und Datenqualitaet. | Ja |
| UI/UX Reviewer | Yield team | Prueft AITC-Konsistenz, Layoutverhalten und Responsive Experience. | Empfohlen |
| Frontend Developer | QDM | Implementiert Dashboard, Charts, Interaktionen und Responsiveness. | Nein |
| QA Tester | Yield team | Fuehrt Funktions-, Daten-, Kompatibilitaets-, Accessibility- und Regressionstests aus. | Ja |

## 10. UI- und visuelle Designanforderungen

Die Implementierung soll dem AITC Enterprise UI Stil folgen: sauber, operativ, vertrauenswuerdig, dicht aber lesbar, mit neutralen Flaechen und Blau als primaerer Aktionsfarbe.

| UI-Bereich | Anforderung |
| --- | --- |
| Farbsystem | Background `#f6f8fb` / `#f3f5f7`, Panels `#ffffff`, Primary Blue `#2563eb`, Hover `#1d4ed8`, Border `#d9e1e7`, Text `#111315` / `#17202a`. Gruen oder Violett nicht als primaere Markenfarben verwenden. |
| Typografie | Arial Nova falls verfuegbar, sonst Plus Jakarta Sans, Arial und chinesische Fallback-Fonts. Keine zu schweren Schriftgewichte oder negative Laufweite. |
| Abstand und Radius | 8px Spacing Rhythmus, 8px allgemeiner Radius, 6px fuer kompakte Controls. |
| Karten / Panels | Weisse Chart-Panels mit klaren Titeln, konsistentem Padding und nur bei Bedarf leichter Elevation. |
| Responsives Layout | Desktop priorisiert Vergleich; Tablet behaelt Chart-Lesbarkeit; Mobile stapelt Charts vertikal, horizontales Scrollen nur fuer echte Tabellen. |
| Zustaende | Loading, Empty, Error, Disabled, Active, Hover, Focus und Selected States definieren. |

## 11. Technische Spezifikationen

| Kategorie | Anforderung |
| --- | --- |
| Frontend Stack | HTML + Bootstrap + JavaScript/jQuery. Code soll klar, strukturiert, bei Bedarf kommentiert und leicht weiterentwickelbar sein. |
| Chart-Bibliothek | Freigegebene leichte Chart-Bibliothek oder bestehenden Projektstandard verwenden. Komplexe Plugins nur nach Architekturfreigabe. |
| Responsiveness | Desktop-, Tablet- und Mobile-Breakpoints unterstuetzen. Responsive Grids verwenden und feste Breiten vermeiden, die Overflow verursachen. |
| Performance | Page Shell schnell rendern; Charts moeglichst asynchron laden. Ziel fuer Chart Refresh bei normalem Datenvolumen: 3 Sekunden, abhaengig von API-Performance. |
| Browser Support | Aktuelle unternehmensfreigegebene Chrome- und Edge-Versionen unterstuetzen. Weitere Browseranforderungen bestaetigen. |
| Wartbarkeit | Datenmapping, Chart-Konfiguration und Rendering trennen, damit neue Charts moeglichst konfigurierbar ergaenzt werden koennen. |
| Sicherheit | Rollenbasierte Datenzugriffe beachten, unberechtigten Export verhindern und keine sensiblen Rohfelder im Client offenlegen. |

## 12. Nicht-funktionale Anforderungen

| Typ | Ziel / Regel | Validierung |
| --- | --- | --- |
| Datengenauigkeit | Angezeigte Werte muessen unter gleichen Filtern mit freigegebenen Quellabfragen uebereinstimmen. | QA vergleicht Stichproben mit Quellabfrage oder validiertem Report. |
| Performance | Normale Filter- oder Chart-Aktualisierung erfuellt SLA, Ziel 3 Sekunden bei Standarddatenvolumen. | Browser Timing und API-Logs. |
| Barrierefreiheit | Tastaturerreichbare Controls, sichtbarer Fokus, ausreichender Kontrast und Status nicht nur ueber Farbe. | Manuelle Tastatur- und Kontrastpruefung. |
| Zuverlaessigkeit | Ausfall eines Charts darf nicht die ganze Seite brechen; Chart-Level-Error anzeigen. | Simulierter API-Fehler. |
| Kompatibilitaet | Layout bleibt auf freigegebenen Desktop-, Tablet- und Mobile-Breiten lesbar. | Responsive Browserpruefung. |
| Auditierbarkeit | Letzter Refresh und Filterkontext sind sichtbar oder in Exportmetadaten verfuegbar. | Funktionstest und Exportpruefung. |

## 13. Abnahmekriterien

1. Business Owner bestaetigt Chart-Liste, Metrikdefinitionen, Filterliste, Default View und Layoutmuster.
2. Data Owner bestaetigt Quelltabellen / Views / APIs, Feldmapping, Refresh-Kadenz, Join-Logik und Berechnungsregeln.
3. Alle Charts rendern korrekt fuer Default-Filter und mindestens drei repraesentative Filterkombinationen.
4. Loading, Empty, Error, Active, Hover, Focus und Disabled States sind implementiert und visuell konsistent.
5. Die Seite ist auf Desktop, Tablet und Mobile responsiv, ohne abgeschnittenen Text, ueberlappende Controls oder unlesbare Chartlabels.
6. Exportverhalten folgt den Datenberechtigungen und enthaelt, wo zutreffend, Filterkontext.
7. QA verifiziert Datengenauigkeit gegen Quellabfragen oder freigegebenen Referenzreport.
8. Die finale Seite folgt dem freigegebenen Farbsystem und fuehrt keine nicht freigegebenen Primaerfarben oder schwere Dekoration ein.

## 14. Offene Fragen und Entscheidungen

| ID | Frage / Entscheidung | Owner | Zieltermin | Status |
| --- | --- | --- | --- | --- |
| Q-01 | Welches Layout ist Default: Primary-Detail / Hero, Uniform Grid, Tabbed oder ein anderes Muster? | Business Owner / Product Owner | Zu bestaetigen | Open |
| Q-02 | Was sind die finalen Quelltabellen / Views / APIs und Join-Keys? | Data Owner | Zu bestaetigen | Open |
| Q-03 | Welche Charts sind im ersten Release verpflichtend, welche optional? | Business Owner | Zu bestaetigen | Open |
| Q-04 | Welche Rollen duerfen Chart-Bilder oder Rohdaten exportieren? | Security / Business Owner | Zu bestaetigen | Open |
| Q-05 | Was ist die freigegebene Refresh-Kadenz und Datenverfuegbarkeits-SLA? | Data Owner | Zu bestaetigen | Open |
| Q-06 | Soll das finale Label fuer Output / Loss KPI-Karten NSQM oder NSOM sein? | Business Owner / Data Owner | Zu bestaetigen | Open |
| Q-07 | Soll die Product-Yield-Formel neben PAOI, E-test, CCAOI, Bump AOI und FVI auch Inline und Others enthalten? | Data Owner | Zu bestaetigen | Open |

## 15. Anhang A. Farbsystem

| Token | Wert / Regel |
| --- | --- |
| Background | `#f6f8fb` / `#f3f5f7` |
| Panel | `#ffffff` |
| Hover Surface | `#eef2f4` |
| Soft Blue Panel | `#f0f6ff` |
| Primary Text | `#111315` |
| KMS Text | `#17202a` |
| Secondary Text | `#424a55` / `#647280` |
| Border | `#d9e1e7` / `rgba(17,19,21,0.17)` |
| Active Border | `rgba(17,19,21,0.28)` |
| Primary Blue | `#2563eb` |
| Primary Hover | `#1d4ed8` |
| Primary Soft Background | `#e8f1ff` |
| Accent Blue | `#60a5fa` |
| Accent Soft Background | `rgba(96,165,250,0.17)` |
| Danger / Error / Warning | `#c2413b` / `#b43636` / `#a56313` |
| Shadow | `0 14px 34px rgba(38, 55, 70, 0.1)`, nur leichte Elevation |
