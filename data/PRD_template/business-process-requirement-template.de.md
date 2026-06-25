# Vorlage fuer Geschaeftsprozess-Anforderungen
> Diese Vorlage dient dazu, vor Entwicklungsbeginn den Geschaeftsprozess, Datenanforderungen, Seitenverhalten, Berechtigungen, Integrationen, nicht-funktionale Anforderungen und Abnahmekriterien zu bestaetigen.  
> Ersetzen Sie Inhalte in `[]` durch projektspezifische Angaben und entfernen Sie nicht zutreffende Punkte.

## 1. Grundlegende Dokumentinformationen

| Feld | Inhalt |
| --- | --- |
| Vorlagenname | Vorlage fuer Geschaeftsprozess-Anforderungen |
| Dokumentname | [D.CHQ.QDM Geschaeftsprozess-Anforderung] |
| Dokument-ID | [Vorschlag: BRD-QDM-001] |
| Name des Geschaeftsprozesses | [Auszufuellen] |
| Business Owner | [Auszufuellen] |
| Process Owner / Product Owner | [Auszufuellen] |
| Autor | [Auszufuellen] |
| Erstellungsdatum | [YYYY-MM-DD] |
| Aktuelle Version | v0.1 Entwurf |
| Dokumentstatus | Entwurf / In Pruefung / Genehmigt |
| Ziel-Release / Meilenstein | [Auszufuellen] |
| Zugehoerige Systeme | [Upstream-, Downstream-, Workflow-, Reporting- und Authentifizierungssysteme] |
| Vertraulichkeitsstufe | Intern |

### 1.1 Versionshistorie

| Version | Datum | Autor | Aenderungszusammenfassung | Genehmiger |
| --- | --- | --- | --- | --- |
| v0.1 | [Datum] | [Autor] | Erste Anforderungsstruktur erstellt. | [Genehmiger] |
| v0.2 | [Datum] | [Autor] | [Aktualisierung nach Fachbereichspruefung] | [Genehmiger] |

## 2. Hintergrund und Ziele

### 2.1 Hintergrund

[Beschreiben Sie den aktuellen Prozesshintergrund, fachliche Probleme, operative Schmerzpunkte und warum der Prozess standardisiert oder systemseitig unterstuetzt werden muss.]

Beschreibung: Der Geschaeftsprozess benoetigt einen klaren und auditierbaren Workflow fuer Dateneingabe, Validierung, Genehmigung, Ausfuehrung, Nachverfolgung und Konfiguration. Dieses Dokument soll von fachlichen und technischen Stakeholdern vervollstaendigt werden.

### 2.2 Ziele

- End-to-end-Prozess und Verantwortlichkeiten je Schritt definieren.
- Datenquellen, Schluesselfelder, Validierungslogik und Datenqualitaetserwartungen klaeren.
- Benoetigte Seiten, Funktionen, Berechtigungen und Konfigurationen spezifizieren.
- Technische, Integrations-, nicht-funktionale und Abnahmeanforderungen dokumentieren.
- Offene Fragen und Genehmigungspunkte vor der Implementierung erfassen.

## 3. Umfang

| Bereich | Enthalten | Ausgeschlossen / Nicht im Umfang | Hinweise |
| --- | --- | --- | --- |
| Geschaeftsworkflow | [Auszufuellen] | [Auszufuellen] | Start, Pruefung, Genehmigung, Ablehnung, Ausnahme und Abschluss bestaetigen. |
| Datenmanagement | [Auszufuellen] | [Auszufuellen] | Datenverantwortung, Quelltabellen, Aktualisierungsregeln und Aufbewahrung erfassen. |
| Benutzeroberflaeche | [Auszufuellen] | [Auszufuellen] | Seitenliste, Rollen, Filter, Aktionen und Audit-Historie erfassen. |
| Reporting / Analytics | [Auszufuellen] | [Auszufuellen] | Dashboard-, Export- und operative Reporting-Anforderungen bestaetigen. |

## 4. Verantwortliche und Stakeholder

| Rolle | Name / Team | Verantwortung | Entscheidungsbefugnis | Kontakt |
| --- | --- | --- | --- | --- |
| Business Sponsor | [Auszufuellen] | Verantwortet Business Outcome, Finanzierung und Prioritaet. | Ja / Nein | [E-Mail/IM] |
| Business Owner | [Auszufuellen] | Definiert Prozessregeln und bestaetigt Anforderungsvollstaendigkeit. | Ja / Nein | [E-Mail/IM] |
| Prozessanwender | [Auszufuellen] | Fuehrt taegliche Prozessaktivitaeten aus und meldet operative Probleme. | Nein | [E-Mail/IM] |
| IT Owner | [Auszufuellen] | Verantwortet technisches Design, Lieferung und Deployment-Bereitschaft. | Ja / Nein | [E-Mail/IM] |
| Data Owner | [Auszufuellen] | Bestaetigt Quelltabellen, Felder, Datenqualitaet und Aufbewahrung. | Ja / Nein | [E-Mail/IM] |
| QA / Tester | [Auszufuellen] | Erstellt Testfaelle und prueft Abnahmekriterien. | Nein | [E-Mail/IM] |
| Security / Compliance | [Auszufuellen] | Prueft Berechtigungen, Audit, Datenschutz und Compliance. | Ja / Nein | [E-Mail/IM] |

## 5. Datenbeschreibung

### 5.1 Datenquellen

| Quelle | Typ | Owner | Aktualisierungsfrequenz | Nutzung im Prozess | Hinweise |
| --- | --- | --- | --- | --- | --- |
| XXX_Table | Datenbanktabelle | [Data Owner] | Echtzeit / Taeglich / Manuell | Primaere Quelle fuer Prozessdaten. | Tatsaechlichen Tabellennamen und Umgebung bestaetigen. |
| [Vorgeschlagene Quelle] | API / Datei / Manuelle Eingabe | [Owner] | [Frequenz] | [Nutzung] | [Hinweise] |

### 5.2 Schluesselfelder und Datenwoerterbuch

| Feldname | Fachliche Definition | Datentyp | Pflichtfeld | Validierung / Logik | Beispiel |
| --- | --- | --- | --- | --- | --- |
| XXX_Fields | [Fachliche Bedeutung beschreiben] | Text / Zahl / Datum | Ja / Nein | [Validierungsregel] | [Beispielwert] |
| Request ID | Eindeutige Kennung je Prozessinstanz. | Text | Ja | Systemgeneriert und eindeutig. | QDM-2026-0001 |
| Antragsteller | Benutzer, der den Prozess startet. | Benutzer | Ja | Muss aktiv und berechtigt sein. | [Benutzername] |
| Status | Aktueller Workflow-Status. | Text | Ja | Durch Workflow-Statusliste gesteuert. | Draft / Submitted / Approved / Rejected / Closed |
| Erstellt am | Zeitpunkt der Erstellung. | DateTime | Ja | Systemgeneriert. | 2026-05-20 09:30 |
| Zuletzt aktualisiert | Zeitpunkt der letzten Aktualisierung. | DateTime | Ja | Nach jeder Speicherung/Aktion systemgeneriert. | 2026-05-20 10:15 |

### 5.3 Datenlogik und Qualitaetsregeln

| Regel-ID | Regelbeschreibung | Ausloeser | Erwartetes Systemverhalten | Fehler- / Warnmeldung |
| --- | --- | --- | --- | --- |
| DQ-01 | Pflichtfelder muessen vor Einreichung ausgefuellt sein. | Submit | Einreichung blockieren und fehlende Felder markieren. | Bitte fuellen Sie alle Pflichtfelder aus. |
| DQ-02 | Nur gueltige Statusuebergaenge sind erlaubt. | Workflow-Aktion | Aktion nur bei passender Rolle und passendem Status zulassen. | Diese Aktion ist fuer den aktuellen Status nicht verfuegbar. |
| DQ-03 | [Vorgeschlagene Regel] | [Ausloeser] | [Verhalten] | [Meldung] |

## 6. Prozessbeschreibung

### 6.1 Flussdiagramm

[Fuegen Sie nach Prozessbestaetigung das finale Flussdiagramm ein.]

Empfohlene Notation: Start, Benutzeraktion, Systemvalidierung, Genehmigungsentscheidung, Ablehnungsschleife, Abschluss und Ausnahmeweg.

### 6.2 Workflow-Schrittmatrix

| Schritt | Akteur / Rolle | Eingabe | Aktivitaet | Systemausgabe | Naechster Status |
| --- | --- | --- | --- | --- | --- |
| 1 | Antragsteller | Geschaeftsdaten und Anhaenge | Prozessantrag erstellen und Entwurf speichern. | Entwurfsdatensatz erstellt. | Draft |
| 2 | Antragsteller | Vollstaendiger Antrag | Antrag zur Pruefung einreichen. | Validierungsergebnis und Workflow-Aufgabe. | Submitted |
| 3 | Genehmiger / Reviewer | Eingereichter Antrag | Details, Kommentare und Belege pruefen. | Entscheidung aufgezeichnet. | Approved / Rejected |
| 4 | System | Genehmigter Antrag | Status aktualisieren, Audit-Historie schreiben und Benutzer informieren. | Abgeschlossener Prozessdatensatz. | Closed / Completed |
| 5 | Antragsteller | Abgelehnter Antrag | Ueberarbeiten und erneut einreichen oder abbrechen. | Aktualisierter Antrag und Historie. | Draft / Cancelled |
| 6 | [Vorgeschlagene Rolle] | [Eingabe] | [Ausnahmebehandlung / Eskalation] | [Ausgabe] | [Status] |

## 7. Geschaeftsregeln

| Regel-ID | Geschaeftsregel | Owner | Prioritaet | Bemerkungen |
| --- | --- | --- | --- | --- |
| BR-01 | Der Prozess muss eine vollstaendige Audit-Spur fuer Erstellung, Einreichung, Genehmigung, Ablehnung, Zuweisung und Abschluss fuehren. | Business / IT | Hoch | Audit-Historie soll auf der Detailseite sichtbar sein. |
| BR-02 | Nur berechtigte Benutzer duerfen starten, pruefen, genehmigen, konfigurieren oder Berechtigungen verwalten. | Business / Security | Hoch | Mit der Berechtigungsmatrix abgleichen. |
| BR-03 | Abgelehnte Antraege muessen Reviewer-Kommentare behalten und Korrektur erlauben. | Business | Mittel | Klaeren, ob erneute Einreichung dieselbe Request ID nutzt. |
| BR-04 | [Vorgeschlagene Regel] | [Owner] | Hoch / Mittel / Niedrig | [Bemerkungen] |

## 8. Seiten- / Funktionsdarstellung

| Seite / Funktion | Zweck | Schluesselelemente | Hauptaktionen | Zugriffsrolle |
| --- | --- | --- | --- | --- |
| Prozessstartseite | Berechtigte Benutzer erstellen und reichen Prozessantraege ein. | Formular, Pflichtfelder, Anhaenge, Entwurf, Submit. | Speichern, Einreichen, Abbrechen | Antragsteller |
| Prozess-To-do-Liste | Zeigt Aufgaben mit Handlungsbedarf. | Aufgabenliste, Filter, Status, Faelligkeit, Owner, Schnellzugriff. | Oeffnen, Genehmigen, Ablehnen, Zuweisen | Reviewer / Genehmiger |
| Prozessdetails und Historie | Zeigt Prozessdetails und Audit-Spur. | Kopfdaten, Datenfelder, Kommentare, Zeitachse, Anhaenge. | Kommentieren, Exportieren, Drucken | Berechtigte Rollen |
| Konfiguration | Pflegt konfigurierbare Prozesswerte. | Statusliste, Routing-Regeln, Schwellenwerte, Benachrichtigungsvorlagen. | Hinzufuegen, Bearbeiten, Deaktivieren | Admin |
| Berechtigungsverwaltung | Verwaltet rollenbasierten Zugriff. | Benutzer-Rollen-Zuordnung, Funktionszugriff, Datenscope. | Gewaehren, Entziehen, Auditieren | Security / Admin |
| [Reporting-Seite] | Bietet operative Sichtbarkeit und Export. | Filter, KPI-Uebersicht, Tabelle, Export. | Suchen, Exportieren | [Rolle] |

### 8.1 UI-Verhalten und Layoutanforderungen

| Bereich | Anforderung | Prioritaet |
| --- | --- | --- |
| Responsiveness | Seiten muessen Desktop und gaengige Tablet-Breiten ohne horizontales Ueberlaufen unterstuetzen. | Hoch |
| Formularvalidierung | Pflicht-, Format- und Fachregelmeldungen erscheinen nahe am betroffenen Feld. | Hoch |
| Suche und Filter | Listenseiten sollen bei Bedarf Suche, Status-, Owner- und Datumsfilter unterstuetzen. | Mittel |
| Audit-Sichtbarkeit | Detailseite zeigt Zeit, Akteur, Aktion, Kommentare und Ergebnisstatus. | Hoch |
| Leer- / Fehlerzustaende | Seiten bieten klare Leer-, Lade- und Fehlerzustaende. | Mittel |

## 9. Berechtigungen und Kontrollen

| Funktion | Antragsteller | Reviewer | Genehmiger | Admin | Security |
| --- | --- | --- | --- | --- | --- |
| Antrag erstellen | Erstellen | Anzeigen | Anzeigen | Anzeigen | Anzeigen |
| Antrag einreichen | Eigenen einreichen | Nein | Nein | Nein | Nein |
| Antrag pruefen | Eigenen anzeigen | Pruefen | Genehmigen / Ablehnen | Anzeigen | Anzeigen |
| Konfiguration bearbeiten | Nein | Nein | Nein | Bearbeiten | Anzeigen |
| Berechtigungen verwalten | Nein | Nein | Nein | Anzeigen | Bearbeiten |
| Daten exportieren | [Bestaetigen] | [Bestaetigen] | [Bestaetigen] | [Bestaetigen] | [Bestaetigen] |

## 10. Audit- und Compliance-Anforderungen

- Jede Workflow-Aktion mit Akteur, Zeitstempel, altem Status, neuem Status, Kommentaren und Quellseite protokollieren.
- Sensible Daten nach Rolle und Datenscope beschraenken.
- Aufbewahrungsdauer und Archivierungsansatz vor Go-live definieren.
- Klaeren, ob Datenexport Genehmigung, Maskierung oder Wasserzeichen benoetigt.

## 11. Entwicklungsanforderungen

### 11.1 Technische Spezifikation

[Wenn der Standard-Stack der Vorlage gilt, mit HTML, Bootstrap, JavaScript und jQuery entwickeln. Code soll sauber strukturiert, sinnvoll kommentiert, responsiv und gut erweiterbar sein. Leichte Hover-, Fade- und Sticky-Interaktionen nur einsetzen, wenn sie die Bedienbarkeit verbessern.]

Wenn ein anderer Stack bestaetigt wurde, ist dieser Stack massgeblich; funktionale, UI-, Berechtigungs-, Audit- und Abnahmeanforderungen bleiben erhalten.

### 11.2 Farbsystem

| Token | Wert | Nutzung |
| --- | --- | --- |
| Background | #f6f8fb / #f3f5f7 | Anwendungshintergruende. |
| Panel | #ffffff | Karten, Panels und Formulare. |
| Hover surface | #eef2f4 | Hover- und sekundaere Interaktionszustaende. |
| Soft blue panel | #f0f6ff | Dezente Informationsbereiche. |
| Primary text | #111315 | Haupttext und Labels. |
| KMS text | #17202a | KMS-nahe Hervorhebung. |
| Secondary text | #424a55 / #647280 | Hilfstext und Metadaten. |
| Border | #d9e1e7 / rgba(17,19,21,0.17) | Standardrahmen und Trenner. |
| Active border | rgba(17,19,21,0.28) | Fokus und Auswahl. |
| Primary blue | #2563eb | Hauptaktionen und aktive Indikatoren. |
| Primary hover | #1d4ed8 | Hover fuer Hauptaktionen. |
| Danger / error / warning | #c2413b / #b43636 / #a56313 | Fehler-, Warn- und Risikoanzeigen. |

## 12. Integrations- und Schnittstellenanforderungen

| Schnittstelle | Richtung | Daten / Payload | Frequenz | Fehlerbehandlung | Owner |
| --- | --- | --- | --- | --- | --- |
| [API / Tabelle] | Eingehend / Ausgehend | [Payload] | [Frequenz] | Retry / Alarm / manuelle Korrektur | [Owner] |
| Authentifizierung / SSO | Eingehend | Benutzeridentitaet und Rollenattribute | Beim Login | Zugriff verweigern und Berechtigungsmeldung anzeigen. | IT / Security |
| Benachrichtigungsdienst | Ausgehend | Aufgaben, Genehmigungsergebnis, Ablehnungskommentare | Ereignisbasiert | Fehler loggen und erneutes Senden erlauben. | IT |

## 13. Nicht-funktionale Anforderungen

| Kategorie | Anforderung | Ziel / Messung | Prioritaet |
| --- | --- | --- | --- |
| Performance | Listen- und Detailseiten laden bei normalem Volumen innerhalb der vereinbarten Zeit. | [z. B. <= 3 Sekunden] | Hoch |
| Verfuegbarkeit | System ist in definierten Geschaeftszeiten und Wartungsfenstern verfuegbar. | [Auszufuellen] | Hoch |
| Sicherheit | Zugriff ist rollenbasiert und entspricht der Berechtigungsmatrix. | Keine unberechtigten Zugriffe im Test. | Hoch |
| Usability | Standardablauf Submit/Review ohne erneute manuelle Dateneingabe. | In UAT validiert. | Mittel |
| Wartbarkeit | Konfigurationswerte moeglichst ohne Codeaenderung wartbar. | Admin-konfigurierbar. | Mittel |

## 14. Abnahmekriterien und Tests

| AC ID | Abnahmekriterium | Testmethode | Owner | Status |
| --- | --- | --- | --- | --- |
| AC-01 | Antragsteller kann Antrag erstellen, speichern, einreichen und anzeigen; Pflichtfelder werden validiert. | Funktionstest / UAT | QA / Business | Nicht gestartet |
| AC-02 | Genehmiger koennen genehmigen oder ablehnen; Kommentare werden in Audit-Historie gespeichert. | Funktionstest / UAT | QA / Business | Nicht gestartet |
| AC-03 | Berechtigungsregeln verhindern unberechtigten Zugriff. | Sicherheitstest | QA / Security | Nicht gestartet |
| AC-04 | Datenfelder und Validierungslogik entsprechen dem genehmigten Datenwoerterbuch. | Datenvalidierung | QA / Data Owner | Nicht gestartet |

## 15. Risiken, Abhaengigkeiten und offene Fragen

### 15.1 Risiken und Abhaengigkeiten

| ID | Typ | Beschreibung | Auswirkung | Massnahme / Naechster Schritt | Owner |
| --- | --- | --- | --- | --- | --- |
| R-01 | Anforderung | Geschaeftsregeln sind vor Entwicklungsbeginn nicht vollstaendig bestaetigt. | Rework und UAT-Verzoegerung. | Stakeholder-Review und Sign-off abschliessen. | Business Owner |
| D-01 | Abhaengigkeit | Quelltabellen und Felder sind noch offen. | Datenmapping kann nicht finalisiert werden. | Datenquelle und Feldwoerterbuch bestaetigen. | Data Owner |
| R-02 | Sicherheit | Berechtigungsmatrix unvollstaendig. | Zugriffskontrollfehler. | Rollen vor Build mit Security pruefen. | Security |

### 15.2 Offene Fragen

| Frage-ID | Frage | Owner | Zieldatum | Klaerung |
| --- | --- | --- | --- | --- |
| Q-01 | Wer ist der bestaetigte Process Owner und finale Genehmiger? | [Owner] | [Datum] | [Klaerung] |
| Q-02 | Was sind finale Quelltabellen, Schluesselfelder und Aktualisierungsfrequenz? | [Owner] | [Datum] | [Klaerung] |
| Q-03 | Welche Status und Uebergaenge sind erlaubt? | [Owner] | [Datum] | [Klaerung] |

## 16. Empfohlene Abschluss-Checkliste

| Punkt | Pruefung | Status |
| --- | --- | --- |
| Dokumentinformationen | Owner, Autor, Version, Status und Genehmiger sind vollstaendig. | Offen |
| Umfang | In-Scope und Out-of-Scope sind abgestimmt. | Offen |
| Daten | Quellen, Datenwoerterbuch und Datenregeln sind bestaetigt. | Offen |
| Workflow | Flussdiagramm, Schrittmatrix, Status und Ausnahmen sind bestaetigt. | Offen |
| Seiten | Seitenliste, Aktionen, Wireframes und Rollen sind bestaetigt. | Offen |
| Tests | Abnahmekriterien und UAT-Verantwortliche sind bestaetigt. | Offen |
