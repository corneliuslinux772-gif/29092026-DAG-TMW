import pytest
from src.ingestion.run_ingestion import run_ingestion


def test_run_ingestion_does_not_load_after_failure(
    monkeypatch,
):
    load_called = False

    def fake_ingest_source():
        raise ValueError("Source validation failed")

    def fake_load_raw(_):
        nonlocal load_called
        load_called = True

    monkeypatch.setattr(
        "src.ingestion.run_ingestion.ingest_source",
        fake_ingest_source,
    )

    monkeypatch.setattr(
        "src.ingestion.run_ingestion.load_raw",
        fake_load_raw,
    )

    with pytest.raises(
        ValueError,
        match="Source validation failed",
    ):
        run_ingestion()

    assert load_called is False


def test_run_ingestion_loads_after_success(
    monkeypatch,
):
    calls = []

    def fake_ingest_source():
        calls.append("ingest")
        return "/source/database.db"

    def fake_load_raw(source):
        calls.append(("load_raw", source))

    monkeypatch.setattr(
        "src.ingestion.run_ingestion.ingest_source",
        fake_ingest_source,
    )

    monkeypatch.setattr(
        "src.ingestion.run_ingestion.load_raw",
        fake_load_raw,
    )

    run_ingestion()

    assert calls == [
        "ingest",
        ("load_raw", "/source/database.db"),
    ]