from pathlib import Path

from src.profiling.source_profile import SOURCE_DB


def promote_source(
    source_db: Path,
    target_db: Path = SOURCE_DB,
) -> Path:

    target_db.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    source_db.replace(target_db)

    return target_db