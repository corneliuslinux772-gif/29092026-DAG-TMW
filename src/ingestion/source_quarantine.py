from pathlib import Path

import json
from datetime import datetime, timezone

from src.ingestion.config import (
    QUARANTINE_DIR,
    SOURCE_DB
)

def quarantine_source(
    validation_result: dict,
    source_db: Path = SOURCE_DB,
) -> Path:

    timestamp = datetime.now(timezone.utc).strftime(
        "%Y%m%dT%H%M%SZ"
    )

    quarantine_path = QUARANTINE_DIR / timestamp
    quarantine_path.mkdir(
        parents=True,
        exist_ok=True,
    )

    if source_db.exists():
        source_db.replace(
            quarantine_path / source_db.name
        )

    report = {
        "source": str(source_db),
        "quarantined_at": timestamp,
        "valid": validation_result["valid"],
        "errors": validation_result["errors"],
    }

    with open(
        quarantine_path / "validation_report.json",
        "w",
        encoding="utf-8",
    ) as file:
        json.dump(
            report,
            file,
            indent=2,
            ensure_ascii=False,
        )

    return quarantine_path