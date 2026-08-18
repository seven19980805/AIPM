# ABF Yield-Analyse Vorlage

> Diese Vorlage dient zur Definition eines ABF-Substratfertigungs-Dashboards fuer Yield-Analyse.  
> Ersetzen Sie die Angaben in `[]` durch bestaetigte Projektinformationen und entfernen Sie nicht zutreffende Punkte.

## 1. Basisinformationen

| Feld | Wert |
| --- | --- |
| Vorlagenname | ABF Yield-Analyse Vorlage |
| Dokumentname | [ABF Yield-Analyse Anforderung] |
| Analysethema / Seitenname | [Beispiel: ABF Yield-Analyse Dashboard] |
| Business-Domain | Fertigungsqualitaet / ABF / QDM |
| Anfragendes Team | [Abteilung / Team] |
| Business Owner | [Verantwortlich fuer Yield-Definition und Abnahme] |
| Data Owner | [Verantwortlich fuer Quelltabellen und Felddefinitionen] |
| Product Owner / BA | [Name] |
| Technical Owner | [Name] |
| Version | v0.1 Entwurf |
| Status | Entwurf / In Review / Freigegeben / In Entwicklung / Released |
| Zielrelease / Faelligkeit | [YYYY-MM-DD] |
| Relevante Systeme / Module | [MES / QMS / QDM / Datenplattform / Dashboard-Modul] |

## 2. Hintergrund und Ziele

### 2.1 Hintergrund

[Beschreiben Sie die aktuelle ABF-Yield-Steuerung, Pain Points, Nutzer, Entscheidungsszenarien und den Grund fuer diese Analyseseite.]

Beispiel: Die ABF-Fertigung laeuft ueber mehrere Prozess- und Pruefschritte. Die Fachseite muss schnell erkennen, ob Yield-Abweichungen aus Produkt, Lot, Panel, Prozessschritt, Equipment oder Defect-Kategorie stammen.

### 2.2 Analyseziele

- ABF-Yield nach Zeit, Produkt, Material, Lot, Panel, Prozessschritt, Equipment und Defect-Kategorie anzeigen.
- Hauptquellen von Yield-Loss nach Prozessschritt, Defect-Typ und Lot per Pareto identifizieren.
- Drill-down von Gesamt-Yield bis zu Lot-, Panel-, Step- und Defect-Details unterstuetzen.
- Yield-Definitionen, Datenquellen, Filterlogik und Abnahmekriterien standardisieren.
- Datenbasis fuer Alerts, Verantwortungszuordnung und Verbesserungsabschluss bereitstellen.

## 3. Analyseumfang

| Bereich | Beschreibung |
| --- | --- |
| Produktumfang | [ABF-Produktfamilie, Materialnummer, Kunde, Version oder Prozessplattform] |
| Prozessumfang | [Abgedeckte Prozessschritte, z. B. Exposure, Development, Plating, AOI, Test] |
| Datenumfang | [Historischer Start, Refresh-Takt, Lot-Status, Engineering/Pilot-Lots] |
| Chart-Umfang | KPI, Trend, Step-Loss, Defect-Pareto, Lot/Panel-Detail, Heatmap, Export |
| Nicht im Umfang | [Upstream-Datenerfassung, komplexe Prognosemodelle, automatische Task-Zuweisung] |
| Annahmen und Abhaengigkeiten | [Quellverfuegbarkeit, Feldmapping, Berechtigungen, Zielwerte, API-SLA] |

## 4. Verantwortliche und Stakeholder

| Rolle | Name / Team | Verantwortung |
| --- | --- | --- |
| Fertigung | [TBD] | Produktionsszenarien, Step-Verantwortung und Tagesnutzung bestaetigen. |
| Qualitaet | [TBD] | Yield-Definition, Defect-Taxonomie, Alert-Abschluss und Abnahme bestaetigen. |
| Prozess | [TBD] | Prozessverluste, Parameter und Verbesserungsmassnahmen erklaeren. |
| Equipment | [TBD] | Equipment-Dimension, Equipment-Auffaelligkeiten und Parameterbezug bestaetigen. |
| Daten | [TBD] | Quelltabellen, Felddefinitionen, Refresh-Takt und Datenqualitaet bestaetigen. |
| Product / BA | [TBD] | Scope, Prioritaet, Review und Change Control pflegen. |
| Entwicklung | [TBD] | APIs, Aggregationen, Seite und Chart-Interaktionen umsetzen. |
| QA / UAT | [TBD] | Testfaelle erstellen und Daten, Funktionen und Berechtigungen validieren. |

## 5. Yield-Definitionen und Business-Regeln

| Kennzahl | Formel / Definition | Granularitaet | Hinweis |
| --- | --- | --- | --- |
| Gesamt-Yield | [Good Quantity / Input Quantity] | Produkt / Lot / Periode | Definieren, ob Rework-Pass enthalten ist. |
| Step-Yield | [Step Pass Quantity / Step Input Quantity] | Step / Equipment / Lot | Step-Eintritt und -Austritt definieren. |
| First-Pass-Yield | [Direkt bestandene Menge ohne Rework / Input Quantity] | Produkt / Step | Zeigt versteckte Rework-Kosten. |
| Scrap-Rate | [Scrap Quantity / Input Quantity] | Defect / Step | Separat von Rework, Hold und Pending Disposition. |
| Yield-Loss-Beitrag | [Loss Quantity fuer Defect oder Step / Total Loss Quantity] | Defect / Step | Basis fuer Pareto. |

Regeln:

- Zaehler, Nenner, Input, Good, Defect, Scrap und Rework Quantity eindeutig definieren.
- Engineering Lots, Pilot Lots, Hold Lots, Retest, Rework und stornierte Lots explizit einschliessen oder ausschliessen.
- Zeitzuordnung festlegen: Input Time, Step Completion Time, Test Completion Time oder Warehouse Time.
- KPI, Trend, Detailtabelle und Export muessen dieselbe Berechnungslogik verwenden.
- Prozentgenauigkeit, Einheiten, Rundung und Nullwertbehandlung fixieren.

## 6. Datenbeschreibung und Datenvertrag

| Quelle | Tabelle / View / API | Beschreibung | Grain | Refresh | Owner |
| --- | --- | --- | --- | --- | --- |
| DS-01 | [MES Lot/Step Records] | Lot, Step, Input/Output, Step-Zeit. | Lot + Step | [Realtime / stuendlich / taeglich] | [TBD] |
| DS-02 | [QMS / Defect Inspection] | Defect Code, Kategorie, Disposition. | Panel / Defect | [TBD] | [TBD] |
| DS-03 | [Testsystem] | Electrical, Final oder Reliability Test. | Panel / Unit | [TBD] | [TBD] |
| DS-04 | [Work Order / Product Master] | Produkt, Material, Kunde, Version, Ziel-Yield. | Produkt / Auftrag | [TBD] | [TBD] |
| DS-05 | [Equipment / Parameter Logs] | Equipment, Maschine, Parameter, Alarme. | Equipment / Zeit | [TBD] | [TBD] |

| Feld | Quelle | Typ | Pflicht | Business-Definition |
| --- | --- | --- | --- | --- |
| lot_id | MES | String | Ja | Eindeutige Lot-ID. |
| panel_id | MES / QMS | String | Empfohlen | Eindeutige Panel-ID fuer Drill-down. |
| product_code / material_no | Stammdaten | String | Ja | Produkt- oder Materialdimension. |
| process_step | MES | String | Ja | Prozessschritt oder Operation. |
| equipment_id | MES / Equipment Logs | String | Empfohlen | Equipment- oder Liniendimension. |
| defect_code / defect_type | QMS | String | Empfohlen | Defect-Code und Kategorie. |
| input_qty / pass_qty / fail_qty / scrap_qty / rework_qty | MES / QMS | Number | Ja | Basis fuer Yield- und Loss-Berechnung. |
| event_time | Alle Quellen | DateTime | Ja | Periodenfilter und Refresh-Pruefung. |

Datenqualitaetsregeln:

- Cross-System-Keys definieren: lot_id, panel_id, work_order, process_step, equipment_id.
- Duplikate, verspaetete Daten, fehlende Steps, fehlende Defect Codes und Pending Disposition behandeln.
- Refresh-SLA und Anzeige des letzten Refresh-Zeitpunkts festlegen.
- Abstimmung gegen Quellsysteme und erlaubte Toleranz definieren.
- Auswirkungen von Backfill, Neuberechnung und Definitionsaenderungen dokumentieren.

## 7. Analysedimensionen und Filter

| Dimension | Beispiel | Zweck |
| --- | --- | --- |
| Zeit | Tag / Woche / Monat / Schicht | Trend, Vergleich, Anomalieortung. |
| Produkt | Produktfamilie / Material / Kunde / Version | Yield-Vergleich und Zielsteuerung. |
| Prozess | Step / Linie / Equipment | Prozessverlust lokalisieren. |
| Lot | Work Order / Lot / Panel | Detailtracking und Review auffaelliger Lots. |
| Defect | Kategorie / Code / Disposition | Pareto und Root Cause. |

| Filter | Control | Default | Pflicht | Hinweis |
| --- | --- | --- | --- | --- |
| Zeitraum | Date Picker | Letzte 30 Tage / letzter Zeitraum | Ja | Maximale Abfrageweite begrenzen. |
| Produkt / Material | Suchbarer Select | Alle oder Nutzerbereich | Nein | Bei Bedarf nach Berechtigung filtern. |
| Lot / Panel | Suche | Leer | Nein | Exakte Suche unterstuetzen. |
| Prozessschritt | Multi-Select | Alle | Nein | Charts und Details verknuepfen. |
| Defect-Kategorie | Multi-Select | Alle | Nein | Pareto und Detail verknuepfen. |
| Equipment / Linie | Multi-Select | Alle | Nein | Equipment-bezogene Auffaelligkeiten lokalisieren. |

## 8. Kennzahlensystem

| Kennzahl | Beschreibung | Darstellung | Ziel / Schwellwert |
| --- | --- | --- | --- |
| Input Quantity | Gesamtmenge im Analyseumfang. | KPI / Detail | [TBD] |
| Good Quantity | Pass-Menge nach genehmigter Definition. | KPI / Detail | [TBD] |
| Defect Quantity | Fail-, Scrap- oder Pending-Menge. | KPI / Pareto | [TBD] |
| Overall Yield | Kernkennzahl. | KPI / Trend | [Ziel-Yield] |
| Step Yield | Yield je Prozessschritt. | Matrix / Balken | [Step-Ziel] |
| Defect Contribution | Beitrag einzelner Defects zum Yield-Loss. | Pareto | Top N |
| Abnormal Lot Count | Lots unter Schwellwert oder mit auffaelliger Bewegung. | KPI / Detail | [Warnlinie] |

## 9. Seiten- und Chart-Darstellung

| Bereich | Inhalt / Verhalten |
| --- | --- |
| Filterbereich | Datum, Produkt, Lot, Step, Defect, Equipment; Query, Reset, Export. |
| KPI-Bereich | Overall Yield, Target Gap, Input, Good, Loss, auffaellige Lots. |
| Trendbereich | Yield-Trend, Ziellinie, Periodenvergleich, Anomalie-Marker. |
| Analysebereich | Step-Yield-Matrix, Defect-Pareto, Produktvergleich, Equipmentvergleich. |
| Detailbereich | Lot, Panel, Step, Defect, Equipment, Menge und Status. |

| Chart ID | Name | Typ | Kernkennzahl | Dimension | Interaktion |
| --- | --- | --- | --- | --- | --- |
| CH-01 | ABF Overall Yield Trend | Liniendiagramm | Overall Yield / Target Yield | Datum | Klick auf Anomalie filtert Details. |
| CH-02 | Process Step Yield Loss | Balken / Heatmap | Step Yield / Loss Quantity | Step | Klick auf Step drillt in Defects und Lots. |
| CH-03 | Defect Pareto | Pareto | Defect Contribution / Defect Quantity | Defect | Klick filtert Details. |
| CH-04 | Product / Material Comparison | Balken | Yield / Input Quantity | Produkt / Material | Sortieren und Export. |
| CH-05 | Lot / Panel Detail | Tabelle | Yield, Menge, Status | Lot / Panel | Paging, Sortierung, Drill-down. |

## 10. Drill-down und Root-Cause-Analyse

| Pfad | Beschreibung | Ergebnis |
| --- | --- | --- |
| Produkt -> Lot | Low-Yield-Lots je Produkt anzeigen. | Lotliste, Lot-Yield, Target Gap. |
| Lot -> Panel | Panel-Verteilung im Lot anzeigen. | Panel-Yield, Defect Count, Status. |
| Panel -> Step | Panel-Leistung je Step verfolgen. | Step Pass/Fail, Zeit, Equipment. |
| Step -> Defect | Wichtigste Defects im Step anzeigen. | Defect-Pareto und Details. |
| Defect -> Equipment / Parameter | Konzentration nach Equipment oder Parameter pruefen. | Equipmentvergleich, Parameternotizen, Verbesserungsdatensatz. |

## 11. Alerts und Verbesserungsabschluss

| Alert | Trigger | Schweregrad | Empfaenger | SLA |
| --- | --- | --- | --- | --- |
| Gesamt-Yield unter Ziel | [Overall Yield < Target - Tolerance] | High / Medium | Quality / Manufacturing | [TBD] |
| Step-Yield auffaellig | [Step Yield unter Schwellwert oder Periodenabfall] | High / Medium | Process / Equipment | [TBD] |
| Defect-Spike | [Defect Share ueber Schwellwert] | Medium | Quality / Process | [TBD] |
| Refresh auffaellig | [Refresh ueber SLA] | Medium | Data Owner | [TBD] |

Abschlussfelder: verantwortliche Abteilung, Ursache, Sofortmassnahme, langfristige Massnahme, Faelligkeit, Abschlussbedingung, Review-Notiz.

## 12. Interaktionen, Berechtigungen und Export

| Anforderung | Erwartetes Verhalten |
| --- | --- |
| Verknuepfte Filter | Klick auf Trendpunkt, Step, Defect oder Produkt aktualisiert passende Charts und Details. |
| Tooltip | Kennzahl, Zaehler/Nenner, Target Gap, Periode, Filter und Definitionshinweis anzeigen. |
| Detail-Drill-down | Detailtabelle muss aktuelle Filter und Berechtigungen einhalten. |
| Export | Chart-Bild oder CSV/Excel fuer aktuelle Filter exportieren; Filterkontext im Export erhalten. |
| Berechtigungen | Nutzer sehen nur autorisierte Produkte, Linien, Kunden oder Werke. |
| Audit | Export, sensitive Details, Alert-Abschluss und Massnahmenaenderungen protokollieren. |

## 13. Technische Spezifikationen und nicht-funktionale Anforderungen

| Kategorie | Anforderung |
| --- | --- |
| API / Aggregation | Request-Parameter, Response, Paging, Sortierung, Aggregationsebene und Fehlercodes definieren. |
| Performance | Erstscreen im Default-Filterziel innerhalb von 3 Sekunden; grosse Abfragen mit Hinweis oder Async Export. |
| Datenkorrektheit | KPI, Charts, Details und Export muessen bei gleichen Filtern konsistent sein. |
| Zuverlaessigkeit | Ein Chart-Fehler darf die Seite nicht brechen; Chart-Level-Error und Retry anzeigen. |
| Sicherheit | Rollenrechte beachten und Kunden-, Produkt- oder Prozessdaten beim Export schuetzen. |
| Barrierefreiheit | Status nicht nur ueber Farbe ausdruecken; Charts brauchen Titel, Einheiten und lesbare Labels. |
| Wartbarkeit | Yield-Formeln, Ziele und Chart-Konfiguration moeglichst konfigurierbar halten. |

## 14. Abnahmekriterien

| ID | Kriterium | Owner | Status |
| --- | --- | --- | --- |
| AC-01 | Yield-Formeln, Zaehler, Nenner, Ausschluesse, Rework/Retest-Regeln sind freigegeben. | Business / Daten | Pending |
| AC-02 | KPI, Trend, Step, Defect-Pareto und Details stimmen im Default-Filter mit Quellabfragen ueberein. | QA / Daten | Pending |
| AC-03 | Datum, Produkt, Lot, Step, Defect und Equipment Filter funktionieren und koennen zurueckgesetzt werden. | QA | Pending |
| AC-04 | Nach Drill-down behalten Charts, Details und Export denselben Kontext. | QA / Produkt | Pending |
| AC-05 | Berechtigungen, sensitive Felder und Exportregeln erfuellen Sicherheitsanforderungen. | Security / QA | Pending |
| AC-06 | Loading, Empty, Error, Alert und Last-Refresh werden korrekt angezeigt. | QA / UI | Pending |
| AC-07 | Zielbrowser und Hauptbreiten zeigen keine Ueberlappung, Trunkierung oder unlesbare Labels. | QA / UI | Pending |

## 15. Offene Fragen und Aenderungsprotokoll

| ID | Frage | Owner | Faelligkeit | Entscheidung |
| --- | --- | --- | --- | --- |
| Q-01 | Enthaelt die finale Yield-Definition Mengen, die nach Rework bestehen? | Quality / Manufacturing | [YYYY-MM-DD] | Open |
| Q-02 | Werden Engineering, Pilot und Hold Lots in der Standardanalyse beruecksichtigt? | Business Owner | [YYYY-MM-DD] | Open |
| Q-03 | Welches System pflegt Ziel-Yield und Warnschwellen? | Daten / Quality | [YYYY-MM-DD] | Open |
| Q-04 | Sollen Alerts automatische Benachrichtigungen ausloesen oder nur im Dashboard sichtbar sein? | Product / Business | [YYYY-MM-DD] | Open |
| Q-05 | Muss der Detailexport nach Kunde, Material oder Rolle maskiert werden? | Security / Business | [YYYY-MM-DD] | Open |

| Version | Datum | Autor | Aenderung |
| --- | --- | --- | --- |
| v0.1 | [YYYY-MM-DD] | [Name] | ABF Yield-Analyse Vorlage initialisiert. |
