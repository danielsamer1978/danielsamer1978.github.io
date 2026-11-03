# danielsamer.de – neue Webseite

Statische Webseite ohne Baukasten, ohne Abo, ohne Cookies.

## Aufbau

- `content/site.json` – **alle Inhalte**: Projekte, weitere Arbeiten, Fotos, Info-Text, Kontaktdaten
- `build.py` – erzeugt aus `site.json` alle HTML-Seiten in `docs/`
- `docs/` – die fertige Webseite (wird von GitHub Pages ausgeliefert)
  - `assets/` – Design (`style.css`), Skript (`site.js`), Schrift Poppins (lokal)
  - `img/full`, `img/thumb` – Bilder in groß und klein, `img/video` – Video-Vorschaubilder
  - `ber/`, `photographie/` … – Weiterleitungen von alten Squarespace-Adressen
- `_import/` – Original-Downloads von Squarespace (Sicherung, wird nicht veröffentlicht)

## Seite neu erzeugen

```bash
python3 build.py
```

## Lokal ansehen

```bash
python3 -m http.server 8080 --directory docs
```

Dann http://localhost:8080 öffnen.

## Veröffentlichen

Änderungen werden mit `git add -A && git commit -m "…" && git push` hochgeladen;
GitHub Pages ist nach etwa einer Minute aktualisiert.
