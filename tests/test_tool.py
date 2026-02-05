from pathlib import Path

from screenshot_replace_tool import ScreenshotReplacer


def test_ingest_classifies_task_and_sets_tomorrow(tmp_path: Path):
    store = tmp_path / "captures.json"
    fake_shot = tmp_path / "pay_bill.png"
    fake_shot.write_bytes(b"fake image")

    replacer = ScreenshotReplacer(store)
    item = replacer.ingest(fake_shot, "Pay electricity bill tomorrow")

    assert item.kind == "task"
    assert item.reminder_at is not None
    assert store.exists()


def test_ingest_uses_filename_when_no_text(tmp_path: Path):
    store = tmp_path / "captures.json"
    fake_shot = tmp_path / "brainstorm_ideas.png"
    fake_shot.write_bytes(b"fake image")

    replacer = ScreenshotReplacer(store)
    item = replacer.ingest(fake_shot)

    assert item.body == "brainstorm ideas"
    assert item.kind == "note"


def test_list_items(tmp_path: Path):
    store = tmp_path / "captures.json"
    fake_shot = tmp_path / "meeting.png"
    fake_shot.write_bytes(b"fake image")

    replacer = ScreenshotReplacer(store)
    replacer.ingest(fake_shot, "Team meeting monday")

    items = replacer.list_items()
    assert len(items) == 1
    assert items[0].kind == "reminder"
