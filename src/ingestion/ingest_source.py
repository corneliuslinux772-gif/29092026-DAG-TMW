from pathlib import Path

from src.ingestion.source_promotion import promote_source
from src.ingestion.source_quarantine import quarantine_source
from src.ingestion.source_validator import (
    INCOMING_DB,
    validate_source,
)


def ingest_source(
    source_db: Path = INCOMING_DB,
) -> Path:

    validation_result = validate_source(
        source_db
    )

    if validation_result["valid"]:
        return promote_source(source_db)

    quarantine_source(
        validation_result,
        source_db,
    )

    raise ValueError(
        "Source validation failed. "
        "File moved to quarantine."
    )


if __name__ == "__main__":
    result = ingest_source()

    print(
        f"Source ingestion successful: {result}"
    )