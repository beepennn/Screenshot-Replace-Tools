#!/usr/bin/env python3
"""Screenshot Replace Tool

Turn screenshots into actionable reminders, notes, and tasks.
"""

from __future__ import annotations

import argparse
import json
import re
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional


TASK_KEYWORDS = {
    "todo",
    "to-do",
    "buy",
    "call",
    "email",
    "submit",
    "finish",
    "pay",
    "schedule",
    "book",
    "fix",
}

REMINDER_KEYWORDS = {
    "remind",
    "remember",
    "deadline",
    "meeting",
    "appointment",
    "tomorrow",
    "today",
    "tonight",
    "monday",
    "tuesday",
    "wednesday",
    "thursday",
    "friday",
    "saturday",
    "sunday",
}


@dataclass
class CaptureItem:
    source: str
    kind: str
    title: str
    body: str
    reminder_at: Optional[str]
    created_at: str


class ScreenshotReplacer:
    def __init__(self, store_path: Path):
        self.store_path = store_path

    def ingest(self, screenshot: Path, fallback_text: str = "") -> CaptureItem:
        extracted = self._extract_text(screenshot) or fallback_text.strip() or screenshot.stem.replace("_", " ")
        cleaned = self._clean_text(extracted)

        kind = self._classify(cleaned)
        title = self._title(cleaned)
        reminder_at = self._extract_time_hint(cleaned)

        item = CaptureItem(
            source=str(screenshot),
            kind=kind,
            title=title,
            body=cleaned,
            reminder_at=reminder_at,
            created_at=datetime.utcnow().isoformat(timespec="seconds") + "Z",
        )
        self._save(item)
        return item

    def list_items(self) -> list[CaptureItem]:
        if not self.store_path.exists():
            return []
        raw = json.loads(self.store_path.read_text())
        return [CaptureItem(**entry) for entry in raw]

    def _save(self, item: CaptureItem) -> None:
        current = []
        if self.store_path.exists():
            current = json.loads(self.store_path.read_text())
        current.append(asdict(item))
        self.store_path.write_text(json.dumps(current, indent=2))

    @staticmethod
    def _extract_text(screenshot: Path) -> str:
        try:
            import pytesseract  # type: ignore
            from PIL import Image  # type: ignore

            return pytesseract.image_to_string(Image.open(screenshot)).strip()
        except Exception:
            return ""

    @staticmethod
    def _clean_text(text: str) -> str:
        compact = re.sub(r"\s+", " ", text).strip()
        return compact or "Untitled capture"

    @staticmethod
    def _classify(text: str) -> str:
        lowered = text.lower()
        tokens = set(re.findall(r"[a-zA-Z\-]+", lowered))

        if tokens & TASK_KEYWORDS:
            return "task"
        if tokens & REMINDER_KEYWORDS:
            return "reminder"
        return "note"

    @staticmethod
    def _title(text: str, max_words: int = 8) -> str:
        words = text.split()
        summary = " ".join(words[:max_words])
        return summary if len(words) <= max_words else summary + "…"

    @staticmethod
    def _extract_time_hint(text: str) -> Optional[str]:
        lowered = text.lower()
        now = datetime.utcnow()

        if "tomorrow" in lowered:
            return (now + timedelta(days=1)).replace(hour=9, minute=0, second=0, microsecond=0).isoformat() + "Z"
        if "today" in lowered or "tonight" in lowered:
            return now.replace(hour=18, minute=0, second=0, microsecond=0).isoformat() + "Z"

        weekdays = {
            "monday": 0,
            "tuesday": 1,
            "wednesday": 2,
            "thursday": 3,
            "friday": 4,
            "saturday": 5,
            "sunday": 6,
        }
        for name, day_index in weekdays.items():
            if name in lowered:
                days_ahead = (day_index - now.weekday()) % 7
                days_ahead = 7 if days_ahead == 0 else days_ahead
                target = (now + timedelta(days=days_ahead)).replace(hour=9, minute=0, second=0, microsecond=0)
                return target.isoformat() + "Z"
        return None


def _print_human_item(item: CaptureItem) -> None:
    print("Saved capture")
    print(f"- type: {item.kind}")
    print(f"- title: {item.title}")
    print(f"- reminder: {item.reminder_at or 'none'}")
    print(f"- source: {item.source}")


def _print_human_list(items: list[CaptureItem], store: Path) -> None:
    if not items:
        print(f"No captured items yet in {store}.")
        print("Tip: run ingest with --text, then run list again.")
        return

    print(f"Captured items in {store}:")
    for idx, item in enumerate(items, start=1):
        reminder = item.reminder_at or "none"
        print(f"{idx}. [{item.kind}] {item.title} (reminder: {reminder})")
        print(f"   source: {item.source}")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Replace screenshot hoarding with action items.",
        epilog=(
            "Examples:\n"
            "  python screenshot_replace_tool.py ingest shot.png --text 'Pay rent tomorrow'\n"
            "  python screenshot_replace_tool.py list\n"
            "  python screenshot_replace_tool.py list --json"
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("command", choices=["ingest", "list"], help="Action to perform.")
    parser.add_argument("screenshot", nargs="?", help="Screenshot path for ingest command.")
    parser.add_argument("--text", default="", help="Fallback text when OCR is unavailable.")
    parser.add_argument("--store", default="captures.json", help="JSON store path.")
    parser.add_argument("--json", action="store_true", help="Print raw JSON output.")
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    replacer = ScreenshotReplacer(Path(args.store))

    if args.command == "ingest":
        if not args.screenshot:
            parser.error("ingest requires a screenshot path")
        item = replacer.ingest(Path(args.screenshot), args.text)

        if args.json:
            print(json.dumps(asdict(item), indent=2))
        else:
            _print_human_item(item)
            print(f"\nStored in: {replacer.store_path}")
            print("Run: python screenshot_replace_tool.py list")
        return 0

    if args.command == "list":
        items = replacer.list_items()
        if args.json:
            print(json.dumps([asdict(item) for item in items], indent=2))
        else:
            _print_human_list(items, replacer.store_path)
        print(json.dumps(asdict(item), indent=2))
        return 0

    if args.command == "list":
        items = [asdict(item) for item in replacer.list_items()]
        print(json.dumps(items, indent=2))
        return 0

    parser.error("Unknown command")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
