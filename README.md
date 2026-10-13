# Kurzbefehl „Bahn: Heim / DHBW“

Ein iPhone-Kurzbefehl, der fragt, wohin du fährst, und dann die DB-Navigator-App
mit der fertig eingetragenen Verbindung öffnet.

| Auswahl im Menü | Start | Ziel |
|---|---|---|
| 🎓 Zur DHBW | Laupheim West | Hochschule Friedrichshafen |
| 🏠 Heimweg | Hochschule Friedrichshafen | Laupheim West |
| 📍 Vom aktuellen Standort → Heim | aktueller Standort | Laupheim West |
| 📍 Vom aktuellen Standort → DHBW | aktueller Standort | Hochschule Friedrichshafen |

---

## ⭐ Empfohlen: mit den eingebauten DB-Navigator-Aktionen

Der DB Navigator bringt eigene Kurzbefehl-Aktionen mit (in der Aktionssuche
„DB Navigator“ eingeben). Damit braucht es keinen Link und keine URL-Codierung.

**Aufbau:** Bei „Reiseauskunft“ lassen sich *Von* und *Nach* nicht mit Variablen
füllen, sondern nur direkt auswählen. Deshalb kommt in **jede** Menü-Option eine
eigene Reiseauskunft-Aktion mit fest gewählten Haltestellen. Variablen braucht es nicht.

1. **Aus Menü auswählen** „Wohin geht's?“ → `🎓 Zur DHBW` / `🏠 Heimweg` / `📍 Vom aktuellen Standort`
2. Unter **🎓 Zur DHBW**: **Reiseauskunft** → *Von* antippen → `Laupheim West` suchen und
   auswählen, *Nach* → `Hochschule Friedrichshafen` auswählen
3. Unter **🏠 Heimweg**: **Reiseauskunft** → *Von* `Hochschule Friedrichshafen`,
   *Nach* `Laupheim West`
4. Unter **📍 Vom aktuellen Standort**: verschachteltes **Aus Menü auswählen** „Wohin?“
   → `🏠 Nach Hause` / `🎓 Zur DHBW`, darin jeweils eine **Reiseauskunft**:
   - *Von*: in der Auswahl nach einem Eintrag wie **„Aktueller Standort“** schauen
   - *Nach*: `Laupheim West` bzw. `Hochschule Friedrichshafen`
   - Gibt es „Aktueller Standort“ bei *Von* nicht, nimm für diese Option die
     URL-Variante unten (dort wird der Standort per „Aktuellen Ort abrufen“ eingesetzt).
5. Nach **Menü „Ende“** kommt nichts mehr. Alte Aktionen wie „Text“,
   „Variable konfigurieren“, „URL“ und „URLs öffnen“ löschen.

Die URL-Variante unten ist die Alternative, falls die Aktion nicht passt.

---

## Alternative: per Link (URL)

### Einrichtung (ca. 5 Minuten)

Öffne die App **Kurzbefehle** → **+** (neuer Kurzbefehl) → Name: `Bahn`.
Füge dann die Aktionen in dieser Reihenfolge hinzu (über die Suchleiste unten).

### 1. Hauptmenü

**Aktion: „Aus Menü auswählen“**
- Eingabeaufforderung: `Wohin geht's?`
- Drei Optionen anlegen:
  1. `🎓 Zur DHBW`
  2. `🏠 Heimweg`
  3. `📍 Vom aktuellen Standort`

### 2. Option „🎓 Zur DHBW“

Unter diese Option ziehen:
1. **Text** → `Laupheim West`
2. **Variable konfigurieren** → Name `Start`
3. **Text** → `Hochschule Friedrichshafen`
4. **Variable konfigurieren** → Name `Ziel`

### 3. Option „🏠 Heimweg“

1. **Text** → `Hochschule Friedrichshafen`
2. **Variable konfigurieren** → `Start`
3. **Text** → `Laupheim West`
4. **Variable konfigurieren** → `Ziel`

### 4. Option „📍 Vom aktuellen Standort“

1. **Aktuellen Standort abrufen**
2. **Text** → tippe ins Textfeld und füge die Variable *Aktueller Standort* ein,
   tippe sie an und wähle **Straße**; dahinter `, ` und nochmals
   *Aktueller Standort* → **Stadt**. Ergebnis z. B. `Hauptstraße 5, Ulm`.
3. **Variable konfigurieren** → `Start`
4. **Aus Menü auswählen** (verschachtelt), Eingabeaufforderung `Wohin?`, Optionen:
   - `🏠 Nach Hause` → **Text** `Laupheim West` → **Variable konfigurieren** `Ziel`
   - `🎓 Zur DHBW` → **Text** `Hochschule Friedrichshafen` → **Variable konfigurieren** `Ziel`

### 5. Nach „Menü beenden“ (ganz unten, für alle Optionen gemeinsam)

1. **URL-codieren** → Eingabe: Variable `Start` → *Codieren*
2. **Variable konfigurieren** → `StartURL`
3. **URL-codieren** → Eingabe: Variable `Ziel` → *Codieren*
4. **Variable konfigurieren** → `ZielURL`
5. **URL** →
   ```
   dbnavigator://query.exe/dn?S=[StartURL]&Z=[ZielURL]&timesel=depart&start=1
   ```
   (`[StartURL]` und `[ZielURL]` jeweils als Variable einfügen, nicht abtippen)
6. **URLs öffnen**

Fertig. Tipp: Über *Teilen → Zum Home-Bildschirm* bekommst du ein App-Symbol,
oder sag „Hey Siri, Bahn“.

---

## Falls die DB-App die Verbindung nicht vorausfüllt

Das `dbnavigator://`-Schema ist von der Bahn nicht offiziell dokumentiert und
kann sich mit App-Updates ändern. Wenn sich nur die App öffnet, aber Start/Ziel
leer bleiben, ersetze in Schritt 5.5 die URL durch die bahn.de-Suche:

```
https://www.bahn.de/buchung/fahrplan/suche#sts=true&so=[StartURL]&zo=[ZielURL]
```

Die öffnet die Verbindungssuche mit eingetragenem Start und Ziel (in Safari bzw.
in der DB-App, falls iOS den Link an die App weiterreicht).

## Haltestellennamen anpassen

Gib in der DB-App einmal von Hand `Hochschule Friedrichshafen` ein und schau,
wie die Haltestelle dort genau heißt (z. B. `Hochschule, Friedrichshafen` oder
`Friedrichshafen Fallenbrunnen`). Trag genau diesen Namen in die Text-Aktionen
ein, dann findet die App die Haltestelle eindeutig. Gleiches gilt für
`Laupheim West`.
