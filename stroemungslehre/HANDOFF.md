# Übergabe: Lernskript Strömungslehre

Stand: 15.10.2026 (aktualisiert). Dieses Dokument fasst den bisherigen Chat zusammen, damit die Arbeit in Claude Code weitergehen kann.

## Ziel

Aus dem Vorlesungsskript „Grundlagen der Strömungslehre“ (Prof. Dr.-Ing. G. Thieleke, HS Ravensburg-Weingarten, WS 2021, 70 Seiten plus Aufgabenblatt) ein kompaktes Lernskript für die Prüfung erstellen:

- Zusammenfassung pro Kapitel: Kernaussage, prüfungsrelevante Formeln, Merksätze.
- Grafiken aus dem Original nachgezeichnet (nicht kopiert).
- Lösungswege der Übungsaufgaben 1, 2, 7, 8, 9, 13.
- Spickzettel und typische Prüfungsfehler am Ende.

## Wünsche des Nutzers

- Sprache: Deutsch.
- Formeln müssen **richtig mathematisch gesetzt** sein, nicht als LaTeX-Quelltext.
- Grafiken sollen fachlich korrekt und nah am Original sein.
- Der Nutzer liest und annotiert das Ergebnis als PDF auf dem iPad (Notiz-App). Darum gibt es rechts einen breiten Rand für handschriftliche Notizen.

## Verlauf und Entscheidungen

1. **Erster Versuch: Claude-Docs-Dokument** (claude.ai Artifact, Docs-Typ) mit 15 SVG-Skizzen. Problem: Docs rendert ` ```latex `-Blöcke nicht, im Export und in der Ansicht stand roher LaTeX-Code. Dieses Dokument ist **veraltet** und wird nicht mehr gepflegt.
2. **Zweiter Versuch, aktueller Stand: LaTeX-PDF** mit XeLaTeX und TikZ. Formeln sind korrekt gesetzt, alle Skizzen sind als TikZ neu gezeichnet und gegen das Original geprüft.
3. Fachliche Prüfung der Skizzen. Korrigiert wurden:
   - **Prandtl-Staurohr:** Die statische Bohrung saß nicht an der zugehörigen Leitung.
   - **Wanddruckmessung:** U-Rohr mit Sperrflüssigkeit und Manometer fehlten.

   Neu hinzugekommen: Prisma, turbulentes Geschwindigkeitssignal, Pumpe im h-s-Diagramm, U-Rohr-Schwingung, Ablösung, Tragflügel-Polare, Druckverlauf in der Lavaldüse.

## Dateien

| Datei | Inhalt |
| --- | --- |
| `stroemungslehre.tex` | LaTeX-Quelle, ca. 1400 Zeilen, ergibt 23 Seiten |
| `Stroemungslehre_Lernskript.pdf` | aktuelles Ergebnis (kompilierte Kopie von `stroemungslehre.pdf`) |
| `loesungen.tex` / `Stroemungslehre_Loesungen.pdf` | eigenes Lösungsheft, 9 Seiten: ausführliche Lösungswege der Aufgaben 1, 2, 7, 8, 9, 13 mit Skizzen und Ergebnisübersicht |
| `praeambel_loesungen.tex` | Präambel des Lösungshefts (Kopie der Lernskript-Präambel, andere Kopfzeile) |
| `skizzen/a*.tex` | TikZ-Skizzen zu den Aufgaben; werden in Lernskript und Lösungsheft per `\input` eingebunden |
| `HANDOFF.md` | dieses Dokument |
| Original-PDF | Scan des Vorlesungsskripts, 78 Seiten; Kapitelseite n liegt auf PDF-Seite n+3, die Seiten 32–35 sind im Scan vertauscht. Bitte selbst in den Ordner legen, es ist nicht Teil dieser Übergabe. |

## Bauen

```bash
xelatex -interaction=nonstopmode stroemungslehre.tex   # zweimal laufen lassen (Inhaltsverzeichnis)
xelatex -interaction=nonstopmode stroemungslehre.tex
grep -E "^!" stroemungslehre.log                       # Fehler
grep -c Overfull stroemungslehre.log                   # sollte 0 sein
pdftoppm -r 80 -png stroemungslehre.pdf png/p          # Seiten zur Sichtprüfung rendern
```

Voraussetzungen:

- **XeLaTeX** mit `fontspec`. Die Schrift ist Latin Modern als OTF; pdfLaTeX ergab Bitmap-Schriften, weil `cm-super` fehlt.
- **Deutsche Silbentrennung:** `\usepackage[ngerman]{babel}` braucht das Paket `texlive-lang-german`. Ohne dieses Paket werden lange deutsche Komposita nicht getrennt, und es entstehen Overfull-Boxen.
- Weitere Pakete: tikz (arrows.meta, calc, decorations.markings), tcolorbox [most], siunitx (locale=DE), booktabs, tabularx, enumitem, titlesec, fancyhdr, caption, hyperref, mathtools.

## Aufbau der .tex-Datei

- **Seitenlayout:** A4, `left=2cm, right=4.3cm` (Notizrand), `\emergencystretch=2em`.
- **Farben:** `acc` (blau, Hauptakzent), `acc2` (orange-rot), `acc3` (grün), `merk` (orange, Merke-Boxen), `wasser` (hellblau, Fluidfüllung).
- **Umgebungen und Befehle:**
  - `formel[title=…]`: blaue Box für Kernformeln.
  - `merke[Titel]`: orange Box.
  - `bild`: Minipage, damit Grafik und Bildunterschrift nicht über einen Seitenumbruch getrennt werden.
  - `\abb{…}`: Bildunterschrift (`\captionof{figure}`).
  - `\dd`: aufrechtes d für Differentiale.
- **TikZ-Stile:** `wand` (dicke Linie), `fluid`, `pf` (Kraft- und Geschwindigkeitspfeil), `mass` (Bemaßungspfeil), `lbl` (kleine Beschriftung).
- **Gliederung:** 1 Prüfungs-Fahrplan · 2 Eigenschaften von Fluiden · 3 Grundgleichungen · 4 Statik · 5 Bernoulli · 6 Impulssatz/Impulsmomentensatz · 7 Rohrhydraulik · 8 Gase (`\label{sec:gas}`) · 9 Übungsaufgaben · 10 Spickzettel (beginnt auf neuer Seite).
- **Konventionen:** Breite Gleichungen in mehrere `\[ \]`- oder `aligned`-Blöcke aufteilen, damit nichts über den Rand läuft. Bei Änderungen mit `pdftoppm` rendern und Beschriftungen auf Überlappung prüfen.

## Ergebnisse der Übungsaufgaben (nachgerechnet, g = 9,81 m/s²)

| Aufgabe | Ergebnis |
| --- | --- |
| 1a | T₁ ≈ 278,9 K, v₁ ≈ 262 m/s, ρ₁ ≈ 5,0 kg/m³ |
| 1b | ρ = ρ₀ ≈ 6,67 kg/m³ → v ≈ 245 m/s, Fehler ≈ −7 % |
| 1c | T₁ ≈ 289,1 K, ρ₁ ≈ 4,82 kg/m³, η ≈ 0,70 |
| 2 | v_oben / v_unten ≈ 1,05 (Δp oben ≈ 2206 Pa) |
| 7 | p₂ = 0,5 bar, p₃ = 1,5 bar, c_W = α/(1−α)² = 2,0 |
| 8 | F = πR²[(p₁−p₂) + ρv_max²/12], Q̇ = πR²(v_max/2)[(p₁−p₂) + ρv_max²/8] |
| 9 | h ≈ 0,82 m |
| 13 | Y* ≈ 256 J/kg, P ≈ 79 kW, Q̇ ≈ 75 kW, p_D ≈ 4,48 bar, p_S ≈ 1,91 bar (Überdruck) |

Hinweise:

- **Aufgabe 8:** Die Aufgabe nennt keine Geschwindigkeit, deshalb steht das Ergebnis in v_max.
- **Aufgabe 13:** Annahmen sind 4 Krümmer laut Skizze und dass L₁ von der Druckseite D zur Armatur führt.
- Die Ergebnisse sind nicht mit offiziellen Musterlösungen abgeglichen.
- **Aufgabe 7:** p₁ = 2 bar und v₁ = 10 m/s sind aus den Zwischenergebnissen rückgerechnet.
- **Aufgabe 9:** h₁ = 0,03 m, v₁ = 8 m/s, h₂ = 0,5 m sind aus den Zwischenergebnissen (v_r = 0,51 m/s, Summe 2,04) rückgerechnet, gegen das Blatt prüfen.
- **Aufgabe 13 d):** p_A, h, L₁, L₂ und λ einzeln stehen nicht in der Übergabe; die Werte 4,48 / 1,91 bar sind übernommen.

## Mögliche nächste Schritte

- Ergebnisse mit den Musterlösungen der Übung vergleichen.
- Noch fehlende Skizzen ergänzen: Behälter mit Fundamentkraft (6.2.1), radiales Turbinenlaufrad (6.3.1), Flügelgitter für die Zirkulation (6.4), rotierender Kanal (5.2.5), plötzliche Verengung und Drosselblende (7.2.2), Energie- und Drucklinienplan einer Pumpenanlage.
- ~~Skizzen zu den Übungsaufgaben neben die Lösungswege setzen~~ (erledigt für 1, 2, 7, 8, 9, 13).
- Aufgaben 3–6 und 10–12 lösen: dafür wird das Aufgabenblatt gebraucht.
- Optional: Karteikarten oder Prüfungsfragen zum Abfragen aus dem Spickzettel ableiten.
