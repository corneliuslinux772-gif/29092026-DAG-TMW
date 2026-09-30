import sqlite3

from src.ingestion.source_validator import validate_source

def test_missing_source_is_invalid(tmp_path):

    source = tmp_path / "database.db"

    result = validate_source(source)

    assert result["valid"] is False
    assert "Source not found" in result["errors"][0]


def test_empty_source_is_invalid(tmp_path):

    source = tmp_path / "database.db"
    source.touch()

    result = validate_source(source)

    assert result["valid"] is False
    assert "Source file is empty" in result["errors"]


def test_invalid_sqlite_is_rejected(tmp_path):

    source = tmp_path / "database.db"
    source.write_bytes(b"not a sqlite database")

    result = validate_source(source)

    assert result["valid"] is False
    assert any(
        "Invalid SQLite database" in error
        for error in result["errors"]
    )


def test_sqlite_integrity_is_checked(tmp_path):

    source = tmp_path / "database.db"

    conn = sqlite3.connect(source)

    conn.execute(
        "CREATE TABLE cursos (id INTEGER)"
    )

    conn.commit()
    conn.close()

    result = validate_source(source)

    assert result["valid"] is False