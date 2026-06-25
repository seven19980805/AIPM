# Vorlage fuer fachliche Anforderungen an Logistik und Lager
> Fuer WMS/TMS-Zusammenarbeit, Inbound-Einlagerung, Lagerprozesse, Bestandsverwaltung, Outbound-Versand, Lieferung, Ausnahmen und operative Analysen.  
> Ersetzen Sie die Hinweise in `[]` durch reale fachliche Inhalte; nicht relevante Punkte koennen entfernt werden.

## 1. Basisinformationen

| Feld | Inhalt |
| --- | --- |
| Vorlagenname | Vorlage fuer fachliche Anforderungen an Logistik und Lager |
| Anforderungsname | [Aufbau eines integrierten Logistik- und Lagersystems] |
| Projekt | [Projektnamen eingeben] |
| Anforderungstyp | Neubau / Optimierung / Refactoring |
| Prioritaet | Hoch / Mittel / Niedrig |
| Anfordernde Abteilung | [Anfordernde Abteilung eingeben] |
| Anforderer | [Anforderer eingeben] |
| Anforderungsdatum | [YYYY-MM-DD] |
| Version | V1.0 |

## 2. Fachlicher Hintergrund

### 2.1 Hintergrundueberblick

[Beschreiben Sie Lagerlogistik-Hintergrund, aktuelle Prozesse und Grund fuer den Systemaufbau]

Beschreibung: Inbound, Einlagerung, Bestand, Kommissionierung, Pruefung, Versand und Lieferung stuetzen sich derzeit auf mehrere Systeme und manuelle Tabellen. Bestandsgenauigkeit, Arbeitseffizienz und Logistiktransparenz sind unzureichend. Ein einheitliches Logistik-Lagersystem soll Lagerprozesse, Warehouse-Delivery-Zusammenarbeit, Ausnahmen und Analysen unterstuetzen.

### 2.2 Aktuelle Schmerzpunkte

- [Inbound-Termin, Wareneingang und Einlagerung haben keine einheitliche Arbeitsfuehrung]
- [Bestandsdifferenzen sind schwer rechtzeitig zu erkennen und nachzuverfolgen]
- [Kommissionierung, Pruefung, Verpackung und Versand beruhen auf manueller Kommunikation]
- [Liefertracking, Ausnahmen und Zustellnachweis werden nicht einheitlich verfolgt]

## 3. Fachliche Ziele

### 3.1 Fachliche Ziele

- [Einheitliche Verwaltung fuer Lager, Zonen, Plaetze, Bestand und Chargen aufbauen]
- [Effizienz und Genauigkeit von Inbound, Lager, Outbound und Lieferung verbessern]
- [Informationsfluss zwischen Bestellung, Lager, Carrier und Kunde verbinden]
- [Daten zu Umschlag, Arbeitseffizienz, Lieferzeit und Ausnahmen sammeln]

### 3.2 Messbare Kennzahlen

- [Bestandsgenauigkeit auf 99% bringen]
- [Outbound-Genauigkeit auf 99.5% bringen]
- [Durchschnittliche Picking-Effizienz um 30% steigern]
- [Bearbeitungszeit fuer Lieferausnahmen um 40% reduzieren]

## 4. Fachlicher Umfang

### 4.1 Im Umfang

- Inbound-Termin, Wareneingang, Qualitaetspruefung und Einlagerung
- Lagerzonen, Plaetze, Bestand, Chargen, Sperre und Inventur
- Wellen, Picking, Pruefung, Verpackung und Outbound-Uebergabe
- Carrier, Frachtbriefe, Liefertracking und Zustellnachweis
- Retouren-Inbound, Ausnahmen, Schaden/Verlust und Claims
- Lagerlogistik-Dashboards und Operationsberichte

### 4.2 Nicht im Umfang

- Eigenentwicklung von Steuerungssystemen fuer automatische Lagertechnik
- Beschaffung von Fahrzeugtracking-Hardware
- Grenzueberschreitende Zollabfertigung und internationale Line-Haul-Transporte
- Umbau komplexer Finanzabrechnungssysteme

## 5. Rollen und Kernszenarien

### 5.1 Zielrollen

- Lagerkraft: Wareneingang, Einlagerung, Umlagerung, Inventur und Bestandskorrektur
- Picker: Picking-Aufgaben nach Welle oder Auftrag abschliessen
- Reviewer: Produkt, Menge, Charge pruefen und Differenzen behandeln
- Packer: Verpacken, Wiegen, Label drucken und Outbound uebergeben
- Disponent: Carrier zuweisen, Transport verfolgen und Ausnahmen bearbeiten
- Fahrer/Carrier: Frachtbriefe empfangen, abholen, transportieren und Zustellung rueckmelden
- Operations-Leiter: Bestand, Effizienz, Lieferzeit und Ausnahmen einsehen

### 5.2 Kernszenarien

1. Lieferant oder Upstream-System erstellt Inbound-Termin, Lager empfaengt nach Termin.
2. Lagerkraft prueft Ware, erstellt Einlagerungsaufgabe und legt Ware in Zielplatz.
3. System erstellt Wellen und Picking-Aufgaben aus Bestellungen; Picker arbeitet nach Route.
4. Reviewer prueft Ware und Menge; Differenzen gehen in Ausnahmeprozess.
5. Packer wiegt, druckt Label, uebergibt an Carrier und System synchronisiert Frachtbrief/Tracking.
6. Leiter sieht Bestandsgenauigkeit, Outbound-Effizienz, Lieferzeit und Ausnahmen.

## 6. Funktionale Anforderungen

### 6.1 Funktionsueberblick

[Fassen Sie die Kernfaehigkeiten des Logistik-Lagersystems zusammen]

Beschreibung: Diese Anforderung umfasst sieben Faehigkeitsgruppen: Inbound, Lagerbestand, Picking und Pruefung, Outbound-Versand, Transportlieferung, Reverse-Ausnahmen und Analysen.

### 6.2 Funktionsdetails

#### 6.2.1 Inbound-Termin und Einlagerung

- Beschreibung: Verwaltet Termine, Ankunft, Wareneingang, Qualitaetspruefung und Einlagerungsaufgaben.
- Ausloeser: Upstream erstellt Inbound-Auftrag oder Lieferant meldet Lieferung an.
- Fachliche Regeln / Logik:
-   Unterstuetzt Terminzeit, Lieferant, Kartons, SKU und Charge
-   Unterstuetzt Wareneingangsdifferenzen, Pruefergebnis und Ausnahmeerfassung
-   Erzeugt Einlagerungsaufgaben nach Platzstrategie
- Eingaben: Inbound-Auftrag, Lieferant, SKU, Charge, Menge, Pruefergebnis
- Ausgaben: Wareneingang, Einlagerungsaufgabe, Bestandserhoehung
- Ausnahmen: Ueberlieferung, Minder-/Mehrmenge, Pruefung nicht bestanden, Platzmangel

#### 6.2.2 Bestand und Lagerprozesse

- Beschreibung: Pflegt Lager, Zonen, Plaetze, Bestand, Chargen, Sperre und Inventur.
- Ausloeser: Bestandsbewegung, Inventurplan oder Umlagerung.
- Fachliche Regeln / Logik:
-   Unterstuetzt verfuegbaren, gesperrten, unterwegs- und Chargenbestand
-   Unterstuetzt Umlagerung, Nachschub, Anpassung, Sperre/Entsperrung und Bewegungsjournal
-   Unterstuetzt Vollinventur, Bewegungsinventur, Zyklusinventur und Differenzen
- Eingaben: Lager, Platz, SKU, Charge, Bestandsstatus, Inventurauftrag
- Ausgaben: Bestandskonto, Bewegungsjournal, Inventurdifferenz
- Ausnahmen: Bestandsabweichung, Sperre, Charge abgelaufen, Platzkapazitaet unzureichend

#### 6.2.3 Wellenpicking und Pruefung

- Beschreibung: Erzeugt Wellen, Picking-Aufgaben, Pruefaufgaben und Differenzbearbeitung aus Bestellungen.
- Ausloeser: Bestellung ist versandbereit oder Operator erstellt Welle.
- Fachliche Regeln / Logik:
-   Unterstuetzt Wellen nach Lager, Carrier, SLA und Produktattribut
-   Unterstuetzt Pickingroute, Vollkarton/Einzelstueck, Fehlmenge und Ersatz
-   Unterstuetzt Scan-Pruefung, Differenz und Zweitpruefung
- Eingaben: Bestellung, SKU, Platz, Wellenregel, Picking-Aufgabe
- Ausgaben: Pickliste, Pruefergebnis, Differenzdatensatz
- Ausnahmen: Fehlmenge, Falschpick, Charge falsch, Pruefung fehlgeschlagen

#### 6.2.4 Verpackung, Outbound und Uebergabe

- Beschreibung: Schliesst Verpackung, Wiegen, Label, Outbound-Bestaetigung und Carrier-Uebergabe ab.
- Ausloeser: Nach bestandener Pruefung beginnt Verpackung.
- Fachliche Regeln / Logik:
-   Unterstuetzt Paket-Split/Merge, Wiegen, Material und Labeldruck
-   Unterstuetzt Outbound-Uebergabe, Abholbestaetigung und Bestandsabzug
-   Unterstuetzt Bestellnotiz, Spezialverpackung und Gefahrguthinweis
- Eingaben: Pruefergebnis, Paket, Gewicht, Label, Carrier
- Ausgaben: Outbound-Auftrag, Paketnummer, Frachtbrief, Uebergabe
- Ausnahmen: Labeldruck fehlgeschlagen, Gewicht abnormal, Carrier verweigert, Outbound rueckgaengig

#### 6.2.5 Transport und Tracking

- Beschreibung: Verwaltet Carrier, Frachtbriefe, Tracking-Knoten, Zustellung und Lieferausnahmen.
- Ausloeser: Nach Outbound wird Frachtbrief erstellt und Carrier uebergeben.
- Fachliche Regeln / Logik:
-   Unterstuetzt Carrier-Routing, Frachttarife und Laufzeitregeln
-   Unterstuetzt Tracking-Abo, Knotenrueckmeldung, Zustellbild und elektronischen Beleg
-   Unterstuetzt Verzoegerung, Annahmeverweigerung, Verlust und Schaden
- Eingaben: Frachtbrief, Carrier, Paket, Tracking-Knoten, Zustellung
- Ausgaben: Tracking, Zustellergebnis, Ausnahme
- Ausnahmen: Tracking-Verzug, Zustellung fehlgeschlagen, Verlust, Schaden, Adresse unerreichbar

#### 6.2.6 Reverse Logistics und Ausnahmen

- Beschreibung: Behandelt Retouren, Annahmeverweigerung, Umtausch, Ausnahmen, Claims und Bestandsrueckschreibung.
- Ausloeser: Kunde retourniert, Carrier verweigert oder Lager findet Ausnahme.
- Fachliche Regeln / Logik:
-   Unterstuetzt Retourentermin, Annahme, Pruefung, Wiedereinlagerung oder Verschrottung
-   Unterstuetzt Ausnahmeerfassung, Verantwortlichkeit, Claim und Frist
-   Verknuepft After-Sales, Frachtbrief, Bestand und Finanzstatus
- Eingaben: Retourenauftrag, Grund, Pruefergebnis, Verantwortlicher, Ergebnis
- Ausgaben: Retouren-Inbound, Ausnahmenregister, Claim
- Ausnahmen: Retour ohne Originalauftrag, Ware beschaedigt, Verantwortung unklar, Frist verpasst

## 7. Seiten und Prozesse

| Seite / Einstieg | Einstieg | Schluesselinhalte | Hauptaktionen | Ablauf |
| --- | --- | --- | --- | --- |
| Lager-Arbeitsplatz | Lagerarbeit-Einstieg | Wareneingang, Einlagerung, Picking, Pruefung, Ausnahmen | Aufgabe nehmen, scannen, Ergebnis senden, Ausnahme ansehen | Mitarbeiter nehmen Aufgaben und schliessen Lagerarbeit ab. |
| Inbound-Verwaltung | Lager-Backend | Termine, Inbound-Auftraege, Wareneingang, Pruefung, Einlagerung | Termin erstellen, empfangen, pruefen, Einlagerung erzeugen, schliessen | Lagerkraft empfaengt nach Termin und lagert ein. |
| Bestandsverwaltung | Lager-Backend | Bestandskonto, Plaetze, Chargen, Sperren, Inventur | Suchen, umlagern, sperren, inventarisieren, korrigieren | Leiter sieht Bestand und behandelt Differenzen. |
| Outbound-Arbeit | Lagerarbeit-Einstieg | Wellen, Picklisten, Pruefung, Pakete, Labels | Welle erzeugen, picken, pruefen, packen, uebergeben | System erzeugt Aufgaben und schliesst Outbound-Uebergabe ab. |
| Transporttracking | Logistik-Backend | Frachtbriefe, Tracking, Zustellung, Ausnahmen, Carrier | Carrier zuweisen, Tracking suchen, Ausnahme behandeln, Bericht exportieren | Disponent verfolgt Lieferung und behandelt Ausnahmen. |
| Warehouse-Delivery-Dashboard | Management-Einstieg | Bestandsgenauigkeit, Outbound-Effizienz, Lieferzeit, Ausnahmequote | Filtern, Drilldown, Export, Abonnement | Management sieht Qualitaet der Lager- und Lieferprozesse. |

## 8. Fachliche Regeln und Daten

### 8.1 Fachliche Regeln / Logik

- Jede Bestandsbewegung muss einen Bestandseintrag erzeugen und mit dem Quelldokument verknuepft sein.
- Verfuegbarer Bestand darf erst nach bestandener Outbound-Pruefung abgezogen und Paket erzeugt werden.
- Gleiche Chargen werden nach FIFO oder definierten Chargenregeln gepickt.
- Ausnahmen muessen Verantwortlichen, Ergebnis und Frist erfassen.
- Tracking und Zustellnachweis brauchen Retry und manuelle Nachpflege bei Callback-Fehlern.

### 8.2 Wichtige Datenobjekte

- Lager: Code, Name, Zone, Platz, Kapazitaet, Status
- Bestand: SKU, Charge, Platz, verfuegbar, gesperrt, unterwegs, reserviert
- Inbound-Auftrag: Lieferant, SKU, Menge, Termin, Pruefergebnis
- Outbound-Auftrag: Bestellung, Welle, Picking, Pruefung, Paket, Frachtbrief
- Frachtbrief: Carrier, Paket, Tracking, Zustellung, Ausnahme
- Ausnahmefall: Typ, Grund, Verantwortlicher, Bearbeiter, Ergebnis

## 9. Nichtfunktionale Anforderungen

- Performance: Scan-Prozesse und Bestandsabfragen muessen schnell reagieren; haeufige Aktionen innerhalb von 2 Sekunden.
- Genauigkeit: Bestand, Inbound, Outbound und Frachtbriefstatus brauchen Nachverfolgbarkeit und finale Konsistenz.
- Mobile Arbeit: Handheld-Seiten muessen Scannen, schwaches Netz und Offline-Nachsendung unterstuetzen.
- Audit: Bestandsanpassungen, Ausnahmen und manuelle Frachtbriefpflege muessen protokolliert werden.
- Sicherheit: Lager-, Owner- und Carrier-Daten muessen nach Berechtigung getrennt sein.

## 10. Integrationen und Abhaengigkeiten

- Bestellsystem / ERP
- Shop oder Vertriebskanaele
- Carrier-Schnittstellen
- Barcode-/Label-Druckservice
- Handheld / PDA
- Unternehmens-DWH / BI

## 11. Risiken und offene Fragen

### 11.1 Risiken

- Bestandsdifferenzen beeinflussen Verkaufs- und Fulfillment-Zusagen.
- Instabile Carrier-Callbacks beeintraechtigen Kundenabfragen.
- Zu komplexe Lagerprozesse reduzieren Frontline-Effizienz.
- Unklare Chargen-, MHD- und Sperrregeln erzeugen Falschversand- oder Ablauf-Risiken.

### 11.2 Offene Fragen

- Sollen mehrere Lager, mehrere Eigentuemer und Temperaturzonen unterstuetzt werden?
- Erfolgt Bestandsabzug bei Bestellung, Zahlung oder Outbound?
- Priorisiert Picking Welle, Auftrag, Zone oder Charge?
- Kommt Carrier-Tracking per API-Abo oder manueller Import?
- Sind PDA-Scanning, Offline-Arbeit und elektronischer Zustellnachweis erforderlich?

## 12. Meilensteine und Abnahme

| Meilenstein | Zieldatum | Abnahmekriterien |
| --- | --- | --- |
| Anforderungsbestaetigung | T+1 Woche | Warehouse-Delivery-Umfang, Bestandsregeln, Prozesse und Carrier-Schnittstellen bestaetigen |
| Prototyp-Review | T+3 Wochen | Inbound-, Bestand-, Outbound-, Transport- und Dashboard-Prototypen abschliessen |
| Entwicklung und Integration | T+8 Wochen | Bestellung, Lager, Carrier und Druck integrieren |
| Pilotstart | T+10 Wochen | Ein Lager oder eine Geschaeftslinie pilotieren |
| Produktivstart | T+12 Wochen | Multi-Lager-Rollout, Schulung und Abnahme abschliessen |
