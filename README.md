# Screenshot Replace Tool

A tiny CLI that converts screenshots into structured **tasks**, **reminders**, or **notes** so your screenshot folder stops being a graveyard.

## Why
People screenshot things to remember them, then never look back. This tool turns each screenshot into an actionable item automatically.

## Features
- Attempts OCR via `pytesseract` + `Pillow` (if installed).
- Falls back to provided text (`--text`) or filename.
- Auto-classifies captures into `task`, `reminder`, or `note`.
- Detects simple time hints like `tomorrow`, `today`, and weekdays.
- Stores all items in a local JSON file.

## Usage

```bash
python screenshot_replace_tool.py ingest ./screens/pay_rent.png --text "Pay rent tomorrow"
python screenshot_replace_tool.py list
```

Use a custom storage file:

```bash
python screenshot_replace_tool.py ingest ./shot.png --text "Book dentist appointment Friday" --store my-items.json
```

## Output example

```json
{
  "source": "./screens/pay_rent.png",
  "kind": "task",
  "title": "Pay rent tomorrow",
  "body": "Pay rent tomorrow",
  "reminder_at": "2026-01-11T09:00:00Z",
  "created_at": "2026-01-10T15:27:11Z"
}
```
