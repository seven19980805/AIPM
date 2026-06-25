# Vorlage fuer fachliche Anforderungen an einen Online-Shop
> Fuer Shop-Szenarien wie Produktverwaltung, Warenkorb, Checkout, Zahlung, Aktionen, Kundenmitgliedschaft, After-Sales, Bestandsabgleich und Commerce-Analysen.  
> Ersetzen Sie die Hinweise in `[]` durch reale fachliche Inhalte; nicht relevante Punkte koennen entfernt werden.

## 1. Basisinformationen

| Feld | Inhalt |
| --- | --- |
| Vorlagenname | Vorlage fuer fachliche Anforderungen an einen Online-Shop |
| Anforderungsname | [Aufbau eines Marken-Online-Shops] |
| Projekt | [Projektnamen eingeben] |
| Anforderungstyp | Neubau / Optimierung / Refactoring |
| Prioritaet | Hoch / Mittel / Niedrig |
| Anfordernde Abteilung | [Anfordernde Abteilung eingeben] |
| Anforderer | [Anforderer eingeben] |
| Anforderungsdatum | [YYYY-MM-DD] |
| Version | V1.0 |

## 2. Fachlicher Hintergrund

### 2.1 Hintergrundueberblick

[Beschreiben Sie Commerce-Hintergrund, Vertriebskanaele und Grund fuer den Shop-Aufbau]

Beschreibung: Produktverkauf erfolgt derzeit ueber Filialen, Communities und manuelle Bestellungen. Produktinformationen, Bestand, Rabatte, Bestellungen und After-Sales werden getrennt verwaltet. Ein einheitlicher Online-Shop soll Produktdarstellung, Mitgliedskauf, Online-Zahlung, Fulfillment, After-Sales und Analysen unterstuetzen.

### 2.2 Aktuelle Schmerzpunkte

- [Produktinformationen und Preise sind verteilt und zwischen Frontend und Backend uneinheitlich]
- [Bestellung, Zahlung, Bestandsabzug und Versand bilden keinen geschlossenen Ablauf]
- [Aktionen werden manuell konfiguriert und abgerechnet und sind fehleranfaellig]
- [After-Sales, Kundenservice und operative Daten werden nicht einheitlich verfolgt]

## 3. Fachliche Ziele

### 3.1 Fachliche Ziele

- [Ein einheitliches System fuer Produkt, SKU, Preis und Bestand aufbauen]
- [Warenkorb, Bestellung, Zahlung, Versand und After-Sales zu einem Transaktionsablauf verbinden]
- [Gutscheine, Mengenrabatte, Flash Sales, Mitgliederpreise und Kampagnen unterstuetzen]
- [Kunden-, Bestell-, Konversions- und Wiederkaufsdaten fuer Operations sammeln]

### 3.2 Messbare Kennzahlen

- [Checkout-Konversion um 15% steigern]
- [Zahlungserfolgsquote auf 98% bringen]
- [Durchschnittliche After-Sales-Bearbeitungszeit um 40% reduzieren]
- [Aktionskonfigurationszeit um 60% reduzieren]

## 4. Fachlicher Umfang

### 4.1 Im Umfang

- Produktkategorien, SPU/SKU, Preis- und Listing-Verwaltung
- Suche, Filter, Produktdetail, Warenkorb und Checkout
- Bestellerstellung, Zahlung, Storno, Versand und Empfangsbestaetigung
- Gutscheine, Mengenrabatte, Flash Sales, Mitgliederpreise und Kampagnenseiten
- Mitgliederprofil, Adresse, Merkliste, Browsing und Kundenbetrieb
- Rueckerstattung/Rueckgabe, Service-Zusammenarbeit und Commerce-Dashboards

### 4.2 Nicht im Umfang

- Grenzueberschreitende Zoll- und internationale Steuerberechnung
- Komplexes Marketplace-Haendler-Onboarding und Settlement
- Umbau des Offline-POS
- Eigenentwicklung einer Live-Commerce-Engine

## 5. Rollen und Kernszenarien

### 5.1 Zielrollen

- Besucher: Produkte browsen, suchen, Kampagnen ansehen und anmelden
- Mitglied: Warenkorb, Bestellung, Zahlung, Bestellungen ansehen und After-Sales beantragen
- Operator: Produkte, Kampagnen, Empfehlungen und Inhaltsseiten pflegen
- Kundenservice: Anfragen, Bestellfehler, Rueckgaben und Beschwerden behandeln
- Lagerpersonal: Bestellungen empfangen, kommissionieren, versenden und Tracking synchronisieren
- Finanzen: Zahlungen, Rueckerstattungen, Abstimmung und Rechnungsdaten ansehen
- Systemadministrator: Berechtigungen, Woerterbuecher, Zahlung und Shop-Parameter pflegen

### 5.2 Kernszenarien

1. Ein Operator listet Produkte und konfiguriert Bestand, Preise und Kampagnentags.
2. Ein Nutzer sucht Produkte, oeffnet die Detailseite, legt Artikel in den Warenkorb und sendet eine Bestellung ab.
3. Das System berechnet Rabatte, Versand und Zahlbetrag; der Nutzer bezahlt online.
4. Das Lager empfaengt Versandauftraege, kommissioniert, versendet und meldet Trackingnummern zurueck.
5. Ein Nutzer beantragt Rueckerstattung/Rueckgabe; Kundenservice prueft und loest Zahlungserstattung aus.
6. Operatoren sehen Konversion, Warenkorbwert, Wiederkauf, Bestand und Kampagnenerfolg.

## 6. Funktionale Anforderungen

### 6.1 Funktionsueberblick

[Fassen Sie die Kernfaehigkeiten des Shop-Systems zusammen]

Beschreibung: Diese Anforderung umfasst sieben Faehigkeitsgruppen: Produkte, Warenkorb, Bestellung und Zahlung, Aktionen, Mitglieder und Kunden, After-Sales und Analysen.

### 6.2 Funktionsdetails

#### 6.2.1 Produkt- und SKU-Verwaltung

- Beschreibung: Pflegt Kategorien, Marken, SPU/SKU, Bilder, Spezifikationen, Preise, Bestand und Listingstatus.
- Ausloeser: Ein Operator erstellt oder aktualisiert ein Produkt.
- Fachliche Regeln / Logik:
-   Unterstuetzt Kategoriehierarchie, Marke, Attribute und SKU-Kombinationen
-   Unterstuetzt Entwurf, Vorschau, Listing/Delisting, Sortierung und Empfehlungstags
-   Unterstuetzt Preis, Bestand, Kauflimit und Verkaufsregion
- Eingaben: Produktdaten, SKU, Preis, Bestand, Bilder, Tags
- Ausgaben: Produktdetail, SKU-Liste, Listingstatus
- Ausnahmen: SKU-Konflikt, zu wenig Bestand, Preisfehler, Produkt in Bestellung referenziert

#### 6.2.2 Warenkorb und Checkout

- Beschreibung: Unterstuetzt Warenkorb, Artikelauswahl, Mengenanpassung, Rabattberechnung und Bestellung.
- Ausloeser: Ein Nutzer legt Artikel in den Warenkorb oder geht zum Checkout.
- Fachliche Regeln / Logik:
-   Unterstuetzt Menge, Auswahlstatus und Hinweise fuer ungueltige Artikel
-   Unterstuetzt Gutscheine, Mengenrabatte, Mitgliederpreise, Punkteabzug und Versandkosten
-   Unterstuetzt Adresse, Rechnung, Bemerkung und Lieferart
- Eingaben: Nutzer, SKU, Menge, Rabatt, Adresse, Lieferart
- Ausgaben: Warenkorb, Checkout-Beleg, Zahlbetrag
- Ausnahmen: Zu wenig Bestand, Preisaenderung, Rabatt nicht nutzbar, Adresse nicht lieferbar

#### 6.2.3 Bestellung und Zahlung

- Beschreibung: Verwaltet Erstellung, Zahlung, Storno, Timeout-Schliessung, Versand und Empfangsbestaetigung.
- Ausloeser: Nutzer sendet Bestellung ab oder Zahlungsrueckruf kommt an.
- Fachliche Regeln / Logik:
-   Unterstuetzt Bestellstatus, Zahlungsdatensatz, Rueckerstattung und Log
-   Unterstuetzt mehrere Zahlungsarten, Rueckrufpruefung und Timeout-Schliessung
-   Unterstuetzt geteilte Bestellungen, Teillieferung und Bemerkungen
- Eingaben: Bestellung, Zahlung, Nutzer, Produkt, Betrag, Status
- Ausgaben: Bestelldetail, Zahlungsergebnis, Versandaufgabe
- Ausnahmen: Doppelzahlung, Zahlungsfehler, Timeout, Betragsabweichung

#### 6.2.4 Aktionen und Mitgliederbetrieb

- Beschreibung: Konfiguriert Gutscheine, Mengenrabatte, Flash Sales, Mitgliederpreise, Empfehlungsplaetze und Kampagnenseiten.
- Ausloeser: Operator erstellt Kampagne oder Nutzer nimmt teil.
- Fachliche Regeln / Logik:
-   Unterstuetzt Kampagnenzeit, Produktumfang, Nutzerumfang und Stapelregeln
-   Unterstuetzt Gutscheinabruf, Einloesung, Ablauf und Schwellenwert
-   Unterstuetzt Kampagnenerfolg und Zielgruppen-Tags
- Eingaben: Kampagne, Gutschein, Mitgliederlevel, Zielgruppe, Produktumfang
- Ausgaben: Rabattergebnis, Kampagnenseite, Marketingbericht
- Ausnahmen: Kampagnenkonflikt, falsche Stapelung, Bestandsreservierung

#### 6.2.5 After-Sales und Service

- Beschreibung: Bearbeitet Rueckerstattung, Rueckgabe, Umtausch, Beschwerden und Bestellfehler.
- Ausloeser: Nutzer stellt After-Sales-Antrag oder Service erstellt Ticket.
- Fachliche Regeln / Logik:
-   Unterstuetzt Grund, Nachweis, Pruefung, Ruecksendung und Rueckerstattung
-   Unterstuetzt Servicenotizen, Verhandlungsdaten und Timeout-Erinnerungen
-   Unterstuetzt Statusfluss und Verantwortungszuordnung
- Eingaben: After-Sales-Fall, Bestellung, Zahlung, Nachweis, Serviceprotokoll
- Ausgaben: Pruefergebnis, Rueckerstattung, Fortschritt
- Ausnahmen: Frist abgelaufen, Artikel nicht rueckgabefaehig, Rueckerstattung fehlgeschlagen, Sendung verloren

#### 6.2.6 Commerce-Analysen

- Beschreibung: Stellt Dashboards fuer Umsatz, Konversion, Bestand, Kunden und Kampagnen bereit.
- Ausloeser: Operator oder Manager sieht Daten.
- Fachliche Regeln / Logik:
-   Unterstuetzt Umsatz, Warenkorbwert, Konversion und Wiederkauf
-   Unterstuetzt Produktsales, Bestandsumschlag, Kampagnen-ROI und Kanal
-   Unterstuetzt Export und Kennzahlendefinitionen
- Eingaben: Bestellungen, Zahlungen, Produkte, Nutzerverhalten, Kampagnen
- Ausgaben: Operations-Dashboard, Produktbericht, Kundenanalyse
- Ausnahmen: Datenverzug, fehlende Berechtigung, Kennzahl geaendert

## 7. Seiten und Prozesse

| Seite / Einstieg | Einstieg | Schluesselinhalte | Hauptaktionen | Ablauf |
| --- | --- | --- | --- | --- |
| Shop-Startseite | Kundeneinstieg | Suche, Banner, Kategorien, Empfehlungen, Kampagnen | Suchen, browsen, Produkt oeffnen, anmelden | Nutzer gelangt ueber Kategorie, Suche oder Kampagne zu Produkten. |
| Produktdetail | Produktliste / Suche | Bilder, Preis, Spezifikation, Bestand, Bewertungen, Empfehlungen | Spezifikation waehlen, Warenkorb, Sofortkauf, Merken | Nutzer bestaetigt Produktinformationen und kauft oder merkt vor. |
| Warenkorb und Checkout | Warenkorb-Einstieg | Artikel, Rabatte, Adresse, Lieferung, Rechnung, Betrag | Menge aendern, Rabatt waehlen, Bestellung senden | System prueft Bestand und Preis und erstellt unbezahlte Bestellung. |
| Bestellcenter | Mitgliederbereich | Bestellliste, Status, Tracking, Zahlung, After-Sales | Zahlen, stornieren, Empfang bestaetigen, After-Sales beantragen | Nutzer verfolgt Bestellung und bearbeitet Zahlung oder After-Sales. |
| Shop-Backend | Admin-Einstieg | Produkte, Kampagnen, Bestellungen, After-Sales, Kunden, Berichte | Produkt listen, Kampagne konfigurieren, Ausnahme behandeln, Bericht exportieren | Operatoren pflegen Shop-Betrieb und messen Ergebnisse. |

## 8. Fachliche Regeln und Daten

### 8.1 Fachliche Regeln / Logik

- Bestellung muss Preis-, Rabatt- und Bestandssnapshot sperren.
- Nur bezahlte Bestellungen duerfen in Versandbereit wechseln; Timeout-Bestellungen werden geschlossen und Bestand freigegeben.
- Aktionen muessen Produktumfang, Nutzerumfang, Zeit und Stapelregeln pruefen.
- Rueckerstattung darf den bezahlten Betrag nicht ueberschreiten und muss Kanaltransaktionen behalten.
- Preis-, Bestands-, Bestell- und After-Sales-Aenderungen muessen protokolliert werden.

### 8.2 Wichtige Datenobjekte

- Produkt/SPU: ID, Name, Kategorie, Marke, Status, Hauptbild
- SKU: Spezifikation, Preis, Bestand, Kauflimit, Verkaufsregion
- Warenkorb: Nutzer, SKU, Menge, Auswahlstatus, Ungueltigkeitsstatus
- Bestellung: Bestellnummer, Nutzer, Positionen, Betrag, Status, Lieferadresse
- Zahlung: Zahlungsnummer, Kanal, Betrag, Status, Rueckruftransaktion
- After-Sales-Fall: Bestellung, Grund, Nachweis, Pruefstatus, Rueckerstattungsstatus

## 9. Nichtfunktionale Anforderungen

- Performance: Haeufige Startseiten- und Produktdetailabfragen innerhalb von 3 Sekunden.
- Konsistenz: Bestellung, Zahlung, Bestand und Rueckerstattung brauchen Nachverfolgbarkeit und finale Konsistenz.
- Sicherheit: Zahlungsrueckrufe, Nutzeradressen und Bestellbetraege brauchen Signatur- und Berechtigungspruefung.
- Benutzbarkeit: Bestellung, Zahlung und Rueckerstattung brauchen Wiederholung und klare Hinweise.
- Audit: Preis-, Bestands-, Bestell- und After-Sales-Aenderungen muessen Bearbeiter und Zeit erfassen.

## 10. Integrationen und Abhaengigkeiten

- Payment Gateway
- Logistik-Tracking-Service
- Bestands-/Lagersystem
- SMS- oder Nachrichtendienst
- Rechnungs-/Steuerservice
- Unternehmens-DWH / BI

## 11. Risiken und offene Fragen

### 11.1 Risiken

- Komplexe Rabattstapelung kann Preisfehler verursachen.
- Inkonsistenz zwischen Zahlung und Bestand beeinflusst Fulfillment und Service.
- Peak-Kampagnen koennen Bestandssperre und Bestellperformance belasten.
- Unklare After-Sales-Policy kann Servicekonflikte verursachen.

### 11.2 Offene Fragen

- Sollen Mehrlagerbestand und geteilte Lieferung unterstuetzt werden?
- Duerfen Gutscheine, Mengenrabatte und Mitgliederpreise gestapelt werden?
- Wie werden Bestell-Timeout und Bestandsfreigabe konfiguriert?
- Brauchen Rueckerstattungen Originalweg und manuelle Pruefung?
- Sind Rechnung, Punkte, Mitgliederlevel und Bewertungen erforderlich?

## 12. Meilensteine und Abnahme

| Meilenstein | Zieldatum | Abnahmekriterien |
| --- | --- | --- |
| Anforderungsbestaetigung | T+1 Woche | Transaktionsablauf, Aktionen, Bestand und After-Sales bestaetigen |
| Prototyp-Review | T+3 Wochen | Startseite, Detail, Checkout, Bestellung und Backend-Prototypen abschliessen |
| Entwicklung und Integration | T+8 Wochen | Zahlung, Bestand, Logistik und Benachrichtigung integrieren |
| Pilotstart | T+10 Wochen | Ausgewaehlte Produkte und Nutzer im Gray Launch starten |
| Produktivstart | T+12 Wochen | Gesamtrelease, Betriebskonfiguration und Abnahme abschliessen |
