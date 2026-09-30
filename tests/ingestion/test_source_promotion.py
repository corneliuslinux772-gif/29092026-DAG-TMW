from pathlib import Path

from src.ingestion.source_promotion import promote_source


def test_promote_source_moves_file(tmp_path):

    source = tmp_path / "incoming" / "database.db"
    target = tmp_path / "source" / "database.db"

    source.parent.mkdir()

    source.write_bytes(b"test database")

    result = promote_source(
        source,
        target,
    )

    assert result == target
    assert target.exists()
    assert not source.exists()
    assert target.read_bytes() == b"test database"