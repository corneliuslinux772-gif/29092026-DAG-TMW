import json

from src.ingestion.source_quarantine import quarantine_source


def test_quarantine_moves_file(
    tmp_path,
    monkeypatch,
):

    source = tmp_path / "database.db"
    source.write_bytes(b"corrupted database")

    quarantine_dir = tmp_path / "quarantine"

    monkeypatch.setattr(
        "src.ingestion.source_quarantine.QUARANTINE_DIR",
        quarantine_dir,
    )

    validation_result = {
        "valid": False,
        "errors": [
            "SQLite integrity check failed"
        ],
    }

    result = quarantine_source(
        validation_result,
        source,
    )

    quarantined_file = (
        result / "database.db"
    )

    report_file = (
        result / "validation_report.json"
    )

    assert not source.exists()
    assert quarantined_file.exists()
    assert report_file.exists()

    report = json.loads(
        report_file.read_text(
            encoding="utf-8"
        )
    )

    assert report["valid"] is False
    assert (
        "SQLite integrity check failed"
        in report["errors"]
    )