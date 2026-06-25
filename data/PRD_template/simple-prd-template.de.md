# PRD-Vorlage (Einfache Version)

> Geeignet für: einfache Anforderungen, interne Abstimmung, schnelle Projektinitiierung  
> Hinweis: Diese Vorlage enthält **keine Performance-Anforderungen** und **keine Abnahmekriterien**

## 1. Dokumentinformationen

- Projektname:
- Anforderungsname:

## 2. Hintergrund

### 2.1 Hintergrundbeschreibung

Beschreiben Sie kurz, warum diese Anforderung notwendig ist und welches Problem oder welche Chance aktuell besteht.

### 2.2 Ziel

Beschreiben Sie klar, was mit dieser Anforderung erreicht werden soll.

Beispiele:

- Die Effizienz eines Prozesses verbessern
- Eine fehlende Basisfunktion ergänzen
- Die Benutzererfahrung optimieren

## 3. Umfang

### 3.1 Im Umfang enthalten

Beschreiben Sie, was in dieser Anforderung enthalten ist.

Beispiele:

- Neue XX-Funktion hinzufügen
- XX-Seite anpassen
- XX-Prozess optimieren

### 3.2 Nicht im Umfang enthalten

Beschreiben Sie, was ausdrücklich nicht enthalten ist, um Missverständnisse zu vermeiden.

Beispiele:

- Keine Anpassung des Admin-Backends
- Keine Datenmigration
- Keine Anpassung für mobile Endgeräte

## 4. Benutzer und Nutzungsszenarien

### 4.1 Zielbenutzer

Beschreiben Sie, wer diese Funktion verwenden wird.

Beispiele:

- Normale Plattformnutzer
- Mitarbeitende im Betrieb
- Interne Administratoren

### 4.2 Zentrale Nutzungsszenarien

Beschreiben Sie, in welchen Situationen diese Funktion verwendet wird.

Beispiele:

1. Wenn ein Nutzer XX benötigt, kann er die Aufgabe über XX erledigen
2. Wenn das Operationsteam XX bearbeiten muss, kann es dies auf der XX-Seite tun

## 5. Funktionale Anforderungen

### 5.1 Funktionsübersicht

Beschreiben Sie in einem kurzen Absatz die Gesamtlogik der Funktion.

### 5.2 Funktionsdetails

#### Funktion 1: Funktionsname

- Beschreibung:
- Auslöser:
- Verarbeitungslogik:
- Eingaben:
- Ergebnisse:
- Ausnahmefälle:

#### Funktion 2: Funktionsname

- Beschreibung:
- Auslöser:
- Verarbeitungslogik:
- Eingaben:
- Ergebnisse:
- Ausnahmefälle:

> Bei Bedarf können weitere Funktionen im gleichen Format ergänzt werden

## 6. Geschäftsregeln

Beschreiben Sie Regeln, Einschränkungen, Bedingungen und Statusübergänge der Funktion.

Beispiele:

- Nutzer dürfen XX nur im Status XX ausführen
- Wenn Feld A leer ist, ist eine Übermittlung nicht erlaubt
- Wenn ein Nutzer eine Aktion wiederholt, wird XX angezeigt

## 7. Seiten- / Interaktionsbeschreibung

Wenn die Anforderung Seiten oder Bedienabläufe betrifft, beschreiben Sie diese hier.

### 7.1 Seitenbeschreibung

- Seitenname:
- Einstiegspunkt:
- Seitenelemente:
- Schaltflächenaktionen:

### 7.1.1 Diagramm-Anforderungen (falls ein oder mehrere Diagramme benötigt werden)

- Diagrammname:
- Diagrammtyp: Linie / Balken / Kreis / Tabellendiagramm / Sonstiges
- Datenquelle:
- Schlüsselfelder:
- Feldlogik:
- Dimensionen / Kennzahlen / Achsenbeschreibung:
- Such- oder Filterbedingungen:
- Detaildatenanzeige:
- Beziehungen zwischen mehreren Diagrammen:
- Diagramminteraktionen: Verknüpfung / Drill-down / Tab-Wechsel / Tooltip / Klickfilter usw.

### 7.1.2 Mehrdiagramm-Layout-Referenz (falls mehrere Diagramme benötigt werden)

Wenn eine Seite ein oder mehrere Diagramme enthält, kann das Layout anhand von Datenhierarchie, Vergleichsbedarf und verfügbarem Platz gewählt werden:

1. **Uniform Grid / Einheitliches Raster**: Alle Diagrammcontainer haben die gleiche Größe und sind sauber wie ein Schachbrett angeordnet; geeignet für Monitoring-Dashboards, gleichrangige Datenkarten und Statusübersichten.
2. **Primary-Detail / Hero Layout**: Ein Hauptdiagramm belegt oben oder links 50%-70% der Fläche, unterstützende Diagramme stehen daneben oder darunter; geeignet für Analyse-Seiten, z. B. großer Trendchart plus Kompositionscharts und Detailtabelle.
3. **Nested / Drill-down Layout**: Ein Diagramm enthält, verlinkt oder aktualisiert ein anderes Diagramm; geeignet für explorative Analysen und Drill-down-Szenarien.
4. **Tabbed Layout**: Mehrere homogene Diagramme teilen sich einen Container und werden über Tabs umgeschaltet; geeignet für Tag/Woche/Monat-Ansichten mit begrenztem Platz.
5. **Masonry / Waterfall Layout**: Elemente haben eine einheitliche Breite, aber unterschiedliche Höhen und füllen Lücken nacheinander; geeignet für Mixed-Media-Berichte, mobile H5-Seiten und Feeds, in Dashboards jedoch vorsichtig verwenden.

### 7.1.3 Prozessseiten-Beschreibung (falls ein Geschäftsprozess betroffen ist)

- Prozessname:
- Auslöser des Prozesses:
- Beteiligte Rollen:
- Prozessknoten:
- Aktionen je Knoten und Statusänderungen:
- Ausnahme- / Rückgabe- / Abbruchpfade:
- Hinweise zum Flussdiagramm:
- Zugehörige Seiten: Startseite / Aufgabenliste / Prozessdetails und Historie / Konfiguration / Berechtigungsverwaltung
- Berechtigungsregeln:

### 7.2 Interaktionsablauf

Der Ablauf kann in Textform beschrieben und bei Bedarf durch ein Flussdiagramm ergänzt werden.

Beispiele:

1. Der Nutzer öffnet die XX-Seite
2. Der Nutzer klickt auf die XX-Schaltfläche
3. Das System zeigt XX-Inhalte an
4. Nach dem Absenden sieht der Nutzer das XX-Ergebnis

## 8. Texte / Beschriftungen

Listen Sie Seitentexte, Button-Beschriftungen, Fehlermeldungen und ähnliche Inhalte auf.

Beispiele:

- Button-Text: Jetzt absenden
- Leerzustand: Keine Daten vorhanden
- Fehlermeldung: Senden fehlgeschlagen. Bitte versuchen Sie es später erneut.

## 9. Daten und Abhängigkeiten

Beschreiben Sie, ob diese Anforderung von anderen Systemen, APIs, Konfigurationen oder Datenquellen abhängt.

Beispiele:

- Abhängig vom User Center zur Rückgabe von Benutzerdaten
- Abhängig von der Konfigurationsplattform zur Auslieferung von Schaltern
- Abhängig von der XX-API zur Bereitstellung von Abfrageergebnissen

## 10. Risiken und Hinweise

Listen Sie bekannte Risiken, Einschränkungen oder Punkte auf, die vorab geklärt werden müssen.

Beispiele:

- Relevante APIs sind noch nicht fertig; der Integrationszeitplan muss bestätigt werden
- Bestehende Nutzer benötigen eventuell Zeit zur Umstellung auf den neuen Ablauf
- Einige Felddefinitionen warten noch auf die finale fachliche Bestätigung
