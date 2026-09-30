from src.ingestion.ingest_source import ingest_source
from src.ingestion.load_raw import load_raw


def run_ingestion():
    source_path = ingest_source()

    print(
        f"Source ready: {source_path}"
    )

    load_raw(source_path)

    print("INGESTION PIPELINE: SUCCESS")


if __name__ == "__main__":
    run_ingestion()