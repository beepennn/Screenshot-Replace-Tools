import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def run_cmd(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(ROOT / "screenshot_replace_tool.py"), *args],
        capture_output=True,
        text=True,
        check=True,
        cwd=ROOT,
    )


def test_human_ingest_and_list_output(tmp_path: Path):
    store = tmp_path / "capt.json"
    fake_shot = tmp_path / "call_bank.png"
    fake_shot.write_bytes(b"fake")

    ingest = run_cmd("ingest", str(fake_shot), "--text", "Call bank tomorrow", "--store", str(store))
    assert "Saved capture" in ingest.stdout
    assert "Stored in:" in ingest.stdout

    listed = run_cmd("list", "--store", str(store))
    assert "Captured items in" in listed.stdout
    assert "[task] Call bank tomorrow" in listed.stdout


def test_list_json_output(tmp_path: Path):
    store = tmp_path / "capt.json"
    fake_shot = tmp_path / "ideas.png"
    fake_shot.write_bytes(b"fake")

    run_cmd("ingest", str(fake_shot), "--text", "Project ideas", "--store", str(store))
    listed = run_cmd("list", "--store", str(store), "--json")
    assert listed.stdout.strip().startswith("[")
    assert '"kind": "note"' in listed.stdout
