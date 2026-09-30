from pathlib import Path

import pytest

from src.ingestion.ingest_source import ingest_source


def test_ingest_source_promotes_valid_file(
    tmp_path,
    monkeypatch,
):
    incoming = tmp_path / "incoming" / "database.db"
    source = tmp_path / "source" / "database.db"

    incoming.parent.mkdir()
    incoming.write_bytes(b"valid database")

    monkeypatch.setattr(
        "src.ingestion.ingest_source.validate_source",
        lambda _: {
            "valid": True,
            "errors": [],
        },
    )

    monkeypatch.setattr(
        "src.ingestion.ingest_source.promote_source",
        lambda source_db: source,
    )

    result = ingest_source(incoming)

    assert result == source


def test_ingest_source_quarantines_invalid_file(
    tmp_path,
    monkeypatch,
):
    incoming = tmp_path / "incoming" / "database.db"

    incoming.parent.mkdir()
    incoming.write_bytes(b"invalid database")

    quarantine_called = {}

    def fake_quarantine(
        validation_result,
        source_db,
    ):
        quarantine_called["source"] = source_db
        quarantine_called["result"] = validation_result

        return tmp_path / "quarantine"

    monkeypatch.setattr(
        "src.ingestion.ingest_source.validate_source",
        lambda _: {
            "valid": False,
            "errors": ["Invalid SQLite database"],
        },
    )

    monkeypatch.setattr(
        "src.ingestion.ingest_source.quarantine_source",
        fake_quarantine,
    )

    with pytest.raises(ValueError, match="validation failed"):
        ingest_source(incoming)

    assert quarantine_called["source"] == incoming

    assert quarantine_called["result"]["valid"] is False