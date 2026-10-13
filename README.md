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

**Aufbau:**

1. **Aus Menü auswählen** „Wohin geht's?“ → `🎓 Zur DHBW` / `🏠 Heimweg` / `📍 Vom aktuellen Standort`
2. **🎓 Zur DHBW**
   - DB Navigator → **Haltestellen suchen** → `Laupheim West`
   - **Objekt aus Liste abrufen** → *Erstes Objekt* → **Variable konfigurieren** `Start`
   - DB Navigator → **Haltestellen suchen** → `Hochschule Friedrichshafen`
   - **Objekt aus Liste abrufen** → *Erstes Objekt* → **Variable konfigurieren** `Ziel`
3. **🏠 Heimweg**: wie oben, nur Start und Ziel vertauscht
4. **📍 Vom aktuellen Standort**
   - DB Navigator → **Haltestellen in der Nähe**
   - **Objekt aus Liste abrufen** → *Erstes Objekt* → **Variable konfigurieren** `Start`
     (also die nächste Haltestelle bei dir)
   - verschachteltes **Aus Menü auswählen** „Wohin?“ → `🏠 Nach Hause` / `🎓 Zur DHBW`,
     darin jeweils **Haltestellen suchen** → **Erstes Objekt** → **Variable konfigurieren** `Ziel`
5. Nach **Menü „Ende“**: DB Navigator → **Reiseauskunft**
   - Bei *Start* (bzw. *Von*) die Variable `Start` einsetzen, bei *Ziel* (bzw. *Nach*) die Variable `Ziel`
   - Unter dem Pfeil `>` in der Aktion gibt es evtl. noch Optionen wie Zeit oder
     „App öffnen“ – so einstellen, dass die App mit der Suche aufgeht.

**Hinweis:** Wie die Felder in „Reiseauskunft“ genau heißen, steht unter dem ⓘ neben
der Aktion. Falls du dort Text direkt eintippen kannst, kannst du dir die Schritte
„Haltestellen suchen“ und „Erstes Objekt“ sparen und einfach
`Laupheim West` / `Hochschule Friedrichshafen` reinschreiben.

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
