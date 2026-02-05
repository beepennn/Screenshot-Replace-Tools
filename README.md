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
