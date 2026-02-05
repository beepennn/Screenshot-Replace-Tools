# Screenshot Replace Tool

Turn screenshots into reminders, notes, or tasks.

## GitHub Pages version (new)
This repo now includes a static web app that runs fully in-browser on GitHub Pages:
- `index.html`
- `app.js`
- `style.css`

It uses `localStorage` to save items and `tesseract.js` (CDN) for OCR.

### Run locally
```bash
python -m http.server 8000
```
Then open: `http://localhost:8000`

### Deploy on GitHub Pages
1. Push this repo to GitHub.
2. In **Settings → Pages**.
3. Set source to **Deploy from a branch**.
4. Choose your branch (`main` or `work`) and folder `/ (root)`.
5. Save. GitHub will publish `index.html`.

## How to use in browser
1. Choose a screenshot file.
2. (Optional) Add fallback text if OCR misses.
3. Click **Ingest**.
4. See saved items in the **Saved items** list.
5. Click **Download JSON** to export your items.

## CLI version (existing)
You can still use the Python CLI:

```bash
python screenshot_replace_tool.py ingest ./anything.png --text "Pay rent tomorrow"
python screenshot_replace_tool.py list
python screenshot_replace_tool.py list --json
```
A tiny CLI that converts screenshots into structured **tasks**, **reminders**, or **notes** so your screenshot folder stops being a graveyard.

## Why
People screenshot things to remember them, then never look back. This tool turns each screenshot into an actionable item automatically.

## What is this for?
Think of this as a personal inbox for screenshots:
- Instead of saving an image and forgetting it, you ingest it.
- The tool extracts text (OCR if available), then creates a task/reminder/note.
- You can immediately **see output in your terminal** and save items in a JSON file.

## Features
- Attempts OCR via `pytesseract` + `Pillow` (if installed).
- Falls back to provided text (`--text`) or filename.
- Auto-classifies captures into `task`, `reminder`, or `note`.
- Detects simple time hints like `tomorrow`, `today`, and weekdays.
- Stores all items in a local JSON file.
- Human-friendly output by default, with optional `--json` output.

## Quick start (how to see output)

Run these exact commands from the project folder:

```bash
python screenshot_replace_tool.py ingest ./anything.png --text "Pay rent tomorrow"
python screenshot_replace_tool.py list
```

You should see terminal output like:

```text
Saved capture
- type: task
- title: Pay rent tomorrow
- reminder: 2026-01-11T09:00:00Z
- source: anything.png

Stored in: captures.json
Run: python screenshot_replace_tool.py list
```

Then `list` shows all saved items in a readable list.

## JSON output mode

```bash
python screenshot_replace_tool.py list --json
python screenshot_replace_tool.py ingest ./shot.png --text "Book dentist appointment Friday" --store my-items.json --json
```

## Output file location
By default, items are saved in:

- `./captures.json` (in your current working directory)

You can change it with `--store`.
