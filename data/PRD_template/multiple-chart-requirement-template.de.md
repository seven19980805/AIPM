# Vorlage fuer Mehrfachchart-Anforderungen
> Diese Vorlage definiert eine responsive Mehrfachchart-Dashboard-Seite mit einer oder mehreren koordinierten QDM-Datenquellen.  
> Ersetzen Sie Inhalte in `[]` durch bestaetigte Projektinformationen.

## 1. Grundlegende Dokumentinformationen

| Feld | Wert |
| --- | --- |
| Vorlagenname | Vorlage fuer Mehrfachchart-Anforderungen |
| Dokumentname | D.CHQ.QDM Mehrfachchart-Anforderung |
| System / Modul | D.CHQ.QDM / Dashboard- und Chart-Darstellung |
| Business Owner | [Zu bestaetigen] |
| Product Owner | [Zu bestaetigen] |
| Autor | [Zu bestaetigen] |
| Version | V1.0 erweiterter Entwurf |
| Status | Entwurf zur Pruefung |
| Erstellungsdatum | [YYYY-MM-DD] |
| Letzte Aktualisierung | [YYYY-MM-DD] |
| Ziel-Release / Sprint | [Zu bestaetigen] |
| Genehmiger | [Zu bestaetigen] |

### 1.1 Versionshistorie

| Version | Datum | Owner | Aenderungsbeschreibung |
| --- | --- | --- | --- |
| V0.1 | [Datum] | Urspruenglicher Autor | Erste Struktur mit grundlegenden Mehrfachchart-Abschnitten. |
| V1.0 | [Datum] | [Autor] | Erweiterte Struktur, empfohlene Felder, Abnahmekriterien und Implementierungshinweise. |

## 2. Hintergrund und Ziele

### 2.1 Hintergrund

[Beschreiben Sie Bedarf, beteiligte Datenquellen, fachliche Fragestellungen und warum eine koordinierte Dashboard-Ansicht benoetigt wird.]

Beschreibung: Die Seite soll eine koordinierte Ansicht fuer mehrere Charts aus einer oder mehreren QDM-Datenquellen bieten. Benutzer muessen filtern, vergleichen, drill-down ausfuehren und chartbezogene Erkenntnisse exportieren koennen. Die Umsetzung soll leichtgewichtig, responsiv und konsistent mit dem AITC Enterprise UI Stil bleiben.

### 2.2 Ziele

- Eine responsive Dashboard-Seite mit mehreren verwandten Charts und konsistenten Filtern bereitstellen.
- Kennzahlen ueber Zeit, Kategorie, Status, Organisation oder andere genehmigte Dimensionen vergleichen.
- Drill-down und Cross-Filtering unterstuetzen, sofern Chart-Beziehungen fachlich definiert sind.
- Chart-Konfigurationsfelder standardisieren, damit kuenftige Charts mit weniger Neuentwicklung ergänzt werden koennen.
- Abnahmekriterien fuer Layout, Performance, Barrierefreiheit, Datengenauigkeit und Browser-Kompatibilitaet definieren.

## 3. Umfang

| Bereich | Im Umfang | Nicht im Umfang / Hinweise |
| --- | --- | --- |
| Seitenlayout | Dashboard-Container, Filterbereich, Mehrfachchart-Bereich, Detail-/Achsbeschreibungsbereich. | Globale Navigation und nicht verwandte Redesigns sind ausgeschlossen. |
| Charts | Linie, Balken, gestapelter Balken, Kreis/Donut, KPI-Karte, Heatmap und tabellenbasierte Detailansichten. | Erweiterte Spezialvisualisierungen nur nach Genehmigung. |
| Interaktionen | Filter, Reset, Refresh, Drill-down, Tabs, Tooltip, Legendentoggle, Export, Leer-/Fehlerzustaende. | Echtzeit-Kollaboration und nutzererstellte Charts sind ausgeschlossen. |
| Daten | Genehmigte QDM-Tabellen/-Views/-APIs und Feldmapping-Regeln. | Neue Upstream-Datenpipelines sind ausgeschlossen, sofern nicht erforderlich. |
| Lieferung | Responsives HTML + Bootstrap + JavaScript/jQuery mit sauberer Struktur und Kommentaren. | Komplexe Plug-ins oder schwere Chart-Abhaengigkeiten benoetigen Architekturpruefung. |

## 4. Verantwortliche und Stakeholder

| Rolle | Name | Verantwortung | Sign-off erforderlich |
| --- | --- | --- | --- |
| Business Owner | [Zu bestaetigen] | Bestaetigt Zweck, Prioritaet, KPIs und Chart-Bedeutung. | Ja |
| Product Owner / BA | [Zu bestaetigen] | Pflegt Anforderungen, klaert Umfangsfragen und koordiniert Reviews. | Ja |
| Data Owner | [Zu bestaetigen] | Bestaetigt Tabellen, Felder, Aktualisierung und Datenqualitaet. | Ja |
| UI/UX Reviewer | [Zu bestaetigen] | Prueft AITC-Konsistenz, Layout und Responsive Experience. | Empfohlen |
| Frontend Developer | [Zu bestaetigen] | Implementiert Dashboard, Chart-Komponenten und Interaktionen. | Nein |
| QA Tester | [Zu bestaetigen] | Testet Funktion, Daten, Kompatibilitaet, Barrierefreiheit und Regression. | Ja |
| Security / Compliance | [Zu bestaetigen] | Prueft Zugriff, Exportbeschraenkungen und sensible Daten. | Bei Bedarf |

## 5. Datenbeschreibung und Datenvertrag

### 5.1 Datenquellen

| Source ID | Tabelle / View / API | Fachliche Beschreibung | Datengranularitaet | Aktualisierung | Owner |
| --- | --- | --- | --- | --- | --- |
| DS-01 | XXX_Table | Primaerdatensatz fuer die Hauptchartgruppe. | [Zu bestaetigen] | [Zu bestaetigen] | [Zu bestaetigen] |
| DS-02 | XXX_Table2 | Unterstuetzender Datensatz fuer Vergleichs- oder Detailcharts. | [Zu bestaetigen] | [Zu bestaetigen] | [Zu bestaetigen] |
| DS-03 | Optionale Quelle | Nur nutzen, wenn benoetigte Kennzahlen nicht aus DS-01/DS-02 ableitbar sind. | [Zu bestaetigen] | [Zu bestaetigen] | [Zu bestaetigen] |

### 5.2 Erforderliche Datenfelder

| Feldname | Quelle | Typ | Pflicht | Fachliche Definition / Logik |
| --- | --- | --- | --- | --- |
| XXX_Field | XXX_Table | [Zu bestaetigen] | Ja | Primaere Kennzahl oder Dimension fuer ein oder mehrere Charts. |
| XXX_Field2 | XXX_Table2 | [Zu bestaetigen] | Ja | Feld fuer Vergleich, Segmentierung oder Tooltip-Detail. |
| Datum / Periode | Alle relevanten Quellen | Datum / Periode | Empfohlen | Erforderlich fuer Trend, Periodenvergleich oder Datumsfilter. |
| Organisation / Einheit | Alle relevanten Quellen | String / Code | Empfohlen | Erforderlich fuer Filter oder Vergleich nach Einheit, Standort, Kunde usw. |
| Status / Kategorie | Alle relevanten Quellen | String / Code | Empfohlen | Fuer gruppierte Charts, gestapelte Balken, Legenden und Statuszaehlung. |
| Messwert | Berechnet oder Quellfeld | Zahl | Empfohlen | Wert fuer KPI, Achse, Tooltip und Aggregation. |

### 5.3 Feldlogik und Datenregeln

- Join Key und Beziehung zwischen Datenquellen vor Entwicklungsbeginn definieren.
- Festlegen, ob Charts Rohdaten, aggregierte Daten oder vorberechnete Kennzahlen nutzen.
- Formeln, Filter, Ausschluesse, Nullbehandlung und Rundung in der Chart-Inventarliste dokumentieren.
- Gleiche Kennzahlen muessen dieselbe Berechnung nutzen, sofern keine Ausnahme dokumentiert ist.
- Labels, Einheiten und Legenden muessen genehmigter Fachterminologie entsprechen.

## 6. Seiten- / Funktionslayout

Das Layout wird anhand fachlicher Prioritaet, Datendichte und Bildschirmgroesse gewaehlt. Fuer Analyse-Seiten ist Primary-Detail / Hero empfohlen; Uniform Grid ist der Fallback fuer Monitoring-Dashboards.

| Layoutoption | Beschreibung | Bester Einsatzfall | Empfehlung |
| --- | --- | --- | --- |
| Uniform Grid | Alle Chartcontainer gleich gross und konsistent ausgerichtet. | Monitoring-Dashboard und gleichrangiger KPI-Vergleich. | Wenn alle Charts gleich wichtig sind. |
| Primary-Detail / Hero | Ein Hero-Chart nimmt den Hauptbereich ein, Hilfscharts daneben oder darunter. | Analyse-Seiten mit dominanter Trendfrage. | Standardempfehlung, sofern nicht anders bestaetigt. |
| Nested / Drill-down | Auswahl eines Charts aktualisiert oder filtert ein anderes. | Explorative Analyse und Kategorie-Drill-down. | Nur bei klar definierten Chart-Beziehungen. |
| Tabbed | Mehrere Charts teilen einen Container und wechseln per Tab. | Homogene Daten wie Tag / Woche / Monat. | Platzsparend, aber kritische Charts nicht verstecken. |
| Masonry / Waterfall | Karten haben gleiche Breite, aber variable Hoehe. | Mixed-Media-Berichte oder mobile Feeds. | Nicht fuer Kern-Dashboards empfohlen. |

## 7. Seiten- / Funktionsdarstellung

| Feld | Anforderung |
| --- | --- |
| Seitenname | Mehrfachchart-Dashboard - exakter Menue-Name zu bestaetigen |
| Seitenzweck | Mehrere QDM-Kennzahlen in einer koordinierten, filterbaren und exportierbaren Ansicht anzeigen. |
| Oberer Bereich | Filter: Zeitraum, Organisation, Kategorie/Status, Datenquelle und rollenspezifische Filter. |
| Mittlerer Bereich | Chartbereich mit gewaehltem Layout, Titeln, Legenden, Tooltip, Lade-/Leer-/Fehlerzustand. |
| Unterer Bereich | Detaildaten, Achsbeschreibung, Kennzahlendefinitionen, letzte Aktualisierung und Quellenhinweise. |
| Diagramm / Illustration | Finales Wireframe oder Screenshot nach UX-Review einfuegen. |

## 8. Chart-Inventar und Konfiguration

### 8.1 Chart-Inventar

| Chart ID | Chartname | Typ | Primaere Kennzahl | Dimension / Gruppierung | Datenquelle | Interaktion |
| --- | --- | --- | --- | --- | --- | --- |
| CH-01 | Gesamttrend | Linie / Flaeche | [Zu bestaetigen] | Datum / Periode | DS-01 | Tooltip; Klick filtert Detailtabelle |
| CH-02 | Zusammensetzung | Kreis / Donut | [Zu bestaetigen] | Status / Kategorie | DS-01 oder DS-02 | Legendentoggle; Klick filtert verwandte Charts |
| CH-03 | Vergleich nach Einheit | Balken / gestapelter Balken | [Zu bestaetigen] | Organisation / Einheit | DS-01 | Sortierung; Tooltip; Export |
| CH-04 | Detailtabelle | Tabelle | Rohdaten oder aggregierte Details | Aktive Filter | DS-01 + DS-02 | Paginierung; Sortierung; Export |

### 8.2 Chart-Konfigurationsfelder

| Feld | Pflicht? | Hinweise |
| --- | --- | --- |
| Chart-Titel | Ja | Kurze fachliche Formulierung, keine technischen Tabellennamen. |
| X-/Y-Achse | Ja fuer Achsencharts | Labels, Einheiten, Sortierung, Datumsgranularitaet und Min/Max definieren. |
| Legende | Bei Bedarf | Reihenfolge, Farbmapping und Verhalten beim Ausblenden definieren. |
| Tooltip | Ja | Wert, Einheit, Periode/Kategorie und Berechnungshinweise anzeigen. |
| Leerzustand | Ja | Klare Meldung bei keinen Daten; kein defektes Chart anzeigen. |
| Ladezustand | Ja | Leichter Loader oder Skeleton beim Datenabruf. |
| Fehlerzustand | Ja | Benutzerfreundliche Meldung und technische Details loggen. |
| Export | Empfohlen | Bild-, CSV- oder Detailtabellenexport je Rolle definieren. |

## 9. Filter und Benutzerinteraktionen

| Filter | Kontrolltyp | Standardwert | Gilt fuer | Hinweise |
| --- | --- | --- | --- | --- |
| Datumsbereich / Periode | Date Picker oder Segmentauswahl | Neueste verfuegbare Periode | Alle Charts, sofern nicht ausgeschlossen | Erforderlich fuer Trend und Vergleich. |
| Organisation / Einheit | Dropdown / Suche | Benutzer-Default-Scope | Relevante Charts | Berechtigungsscope beachten. |
| Kategorie / Status | Dropdown / Mehrfachauswahl | Alle | Kategorie-, Status- und Zusammensetzungscharts | Genehmigte Fachlabels nutzen. |
| Datenquelle | Dropdown / versteckter Parameter | Primaere Quelle | Quellenspezifische Charts | Nur anzeigen, wenn Benutzer wechseln muessen. |
| Reset | Button | N/A | Ganze Seite | Genehmigten Default wiederherstellen. |

### 9.1 Interaktionsregeln

- Filteraenderungen aktualisieren betroffene Charts ohne Vollseitenreload, sofern technisch machbar.
- Ausgewaehlte Chartsegmente zeigen aktiven Zustand und sichtbaren aktiven Filter.
- Tooltips sind am Desktop lesbar; auf Touch-Geraeten ggf. tap-freundliches Detailverhalten.
- Interaktive Legenden muessen per Tastatur erreichbar sein.
- Exporte folgen Datenberechtigungen und enthalten soweit moeglich Filterkontext.

## 10. UI- und visuelle Anforderungen

| UI-Bereich | Anforderung |
| --- | --- |
| Farbsystem | Hintergrund #f6f8fb / #f3f5f7, Panels #ffffff, Primaerblau #2563eb, Hover #1d4ed8, Border #d9e1e7, Text #111315 / #17202a. Gruen oder Violett nicht als Primaerfarben einfuehren. |
| Typografie | Arial Nova falls verfuegbar, danach Plus Jakarta Sans, Arial und passende Fallbacks. Keine negativen Zeichenabstaende. |
| Spacing / Radius | 8px-Spacingsystem, 8px Radius, 6px fuer kompakte Controls. |
| Karten / Panels | Weisse Chartpanels mit klaren Titeln, konsistentem Padding und nur leichter Elevation. |
| Responsiveness | Desktop priorisiert Vergleich, Tablet Lesbarkeit, Mobile stapelt Charts vertikal; horizontales Scrollen nur fuer echte Tabellen. |
| Zustaende | Lade-, Leer-, Fehler-, deaktivierte, aktive, Hover-, Fokus- und Auswahlzustaende definieren. |

## 11. Technische Spezifikationen

| Kategorie | Anforderung |
| --- | --- |
| Frontend-Stack | HTML + Bootstrap + JavaScript/jQuery; sauber, strukturiert, kommentiert und erweiterbar. |
| Chart-Bibliothek | Genehmigte leichte Chartbibliothek oder Projektstandard verwenden. |
| Responsiveness | Desktop-, Tablet- und Mobile-Breakpoints unterstuetzen, feste Breiten vermeiden. |
| Performance | Shell schnell rendern; Charts asynchron laden; Ziel fuer Chart-Refresh 3 Sekunden bei normalem Volumen. |
| Browser | Genehmigte Chrome- und Edge-Versionen unterstuetzen. |
| Wartbarkeit | Datenmapping, Chartkonfiguration und Rendering trennen. |
| Sicherheit | Rollenbasierten Datenzugriff beachten und unerlaubten Export verhindern. |

## 12. Nicht-funktionale Anforderungen

| Typ | Ziel / Regel | Validierung |
| --- | --- | --- |
| Datengenauigkeit | Werte muessen fuer gleiche Filter mit genehmigten Quellen uebereinstimmen. | QA vergleicht mit Source Query oder Referenzbericht. |
| Performance | Filter- oder Chart-Refresh innerhalb vereinbarter SLA, Ziel 3 Sekunden. | Browser Timing und API-Logs. |
| Barrierefreiheit | Tastaturzugriff, sichtbarer Fokus, Kontrast und keine reinen Farbcodes. | Manuelle Tastatur- und Kontrastpruefung. |
| Zuverlaessigkeit | Fehler in einem Chart duerfen die Seite nicht brechen. | Simulierter API-Fehler. |
| Kompatibilitaet | Layout bleibt auf genehmigten Breiten lesbar. | Responsive Browserpruefung. |
| Auditierbarkeit | Letzte Aktualisierung und Filterkontext sichtbar oder in Export-Metadaten verfuegbar. | Funktionstest und Exportpruefung. |

## 13. Abnahmekriterien

- Business Owner bestaetigt Chartliste, Kennzahlendefinitionen, Filterliste, Default-Ansicht und Layout.
- Data Owner bestaetigt Quellen, Feldmapping, Aktualisierung, Join-Logik und Berechnungen.
- Alle Charts rendern fuer Default-Filter und mindestens drei repraesentative Filterkombinationen korrekt.
- Lade-, Leer-, Fehler-, aktive, Hover-, Fokus- und deaktivierte Zustaende sind konsistent umgesetzt.
- Seite ist auf Desktop, Tablet und Mobile responsiv ohne Clipping, Ueberlappung oder unlesbare Labels.
- Export folgt genehmigten Berechtigungen und enthaelt ggf. Filterkontext.
- QA prueft Datengenauigkeit gegen Quellen oder genehmigten Referenzbericht.

## 14. Offene Fragen und Entscheidungen

| ID | Frage / Entscheidung | Owner | Zieldatum | Status |
| --- | --- | --- | --- | --- |
| Q-01 | Welches Layout ist Default: Primary-Detail / Hero, Uniform Grid, Tabbed oder anderes? | Business Owner / Product Owner | [Zu bestaetigen] | Offen |
| Q-02 | Was sind finale Tabellen/Views/APIs und Join Keys? | Data Owner | [Zu bestaetigen] | Offen |
| Q-03 | Welche Charts sind fuer Release 1 Pflicht, welche optional? | Business Owner | [Zu bestaetigen] | Offen |
| Q-04 | Welche Rollen duerfen Chartbilder oder Rohdaten exportieren? | Security / Business Owner | [Zu bestaetigen] | Offen |
| Q-05 | Welche Aktualisierungsfrequenz und Daten-SLA sind genehmigt? | Data Owner | [Zu bestaetigen] | Offen |

## 15. Empfohlene Zusatzfelder

| Feldgruppe | Empfohlene Felder | Nutzen |
| --- | --- | --- |
| Dokument-Governance | Owner, Genehmiger, Versionshistorie, Status, Zielrelease, Change Log | Verantwortung klaeren und Drift verhindern. |
| Fachliche Definition | Persona, Businessziel, KPI, Erfolgskennzahl, Prioritaet | Sicherstellen, dass Charts echte Fragen beantworten. |
| Datenvertrag | Quelle, Feldtyp, Granularitaet, Aktualisierung, Join Key, Nullbehandlung, Formel | Zahlendifferenzen und QA-Rework vermeiden. |
| Chart-Konfiguration | Typ, Kennzahl, Dimension, Achsen, Legende, Tooltip, Sortierung, Defaultfilter | Konsistente Umsetzung und spaetere Erweiterung. |
| Interaktion | Drill-down, Cross-Filtering, Tabs, Export, Reset, Active State, Error State | Bedienverhalten klar definieren. |
| Qualitaet und Release | Abnahmekriterien, Tests, Browser, Accessibility, Performance, Sign-off | Release messbar und pruefbar machen. |
