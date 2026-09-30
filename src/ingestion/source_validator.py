from pathlib import Path
import sqlite3

from src.profiling.source_profile import (
    EXPECTED_TABLES,
    get_columns,
    get_tables,
)

from src.ingestion.config import (
    EXPECTED_SCHEMA,
    SOURCE_DB,
    INCOMING_DB
)


def validate_source(source_db: Path = SOURCE_DB) -> dict:
    errors = []

    if not source_db.exists():
        return {
            "valid": False,
            "errors": [f"Source not found: {source_db}"],
        }

    if source_db.stat().st_size == 0:
        return {
            "valid": False,
            "errors": ["Source file is empty"],
        }

    try:
        conn = sqlite3.connect(source_db)

        with conn:
            integrity = conn.execute(
                "PRAGMA integrity_check;"
            ).fetchone()[0]
    
            if integrity != "ok":
                errors.append(
                    f"SQLite integrity check failed: {integrity}"
                )
    
            actual_tables = get_tables(conn)
    
            if actual_tables != EXPECTED_TABLES:
                errors.append(
                    f"Unexpected tables. "
                    f"Expected={EXPECTED_TABLES}, "
                    f"Actual={actual_tables}"
                )
    
            for table, expected_columns in EXPECTED_SCHEMA.items():
                if table not in actual_tables:
                    continue
    
                actual_columns = {
                    column["name"]: column["type"]
                    for column in get_columns(conn, table)
                }
    
                if actual_columns != expected_columns:
                    errors.append(
                        f"Schema mismatch in '{table}'. "
                        f"Expected={expected_columns}, "
                        f"Actual={actual_columns}"
                    )
    
    except sqlite3.DatabaseError as exc:
        return {
            "valid": False,
            "errors": [f"Invalid SQLite database: {exc}"],
        }

    

    return {
        "valid": not errors,
        "errors": errors,
    }


if __name__ == "__main__":
    result = validate_source(INCOMING_DB)

    if result["valid"]:
        print("SOURCE VALIDATION: PASS")
        raise SystemExit(0)

    print("SOURCE VALIDATION: FAIL")

    for error in result["errors"]:
        print(f"- {error}")

    raise SystemExit(1)