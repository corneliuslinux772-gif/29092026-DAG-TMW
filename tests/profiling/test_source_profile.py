import pytest

from profiling.source_profile import (
    EXPECTED_TABLES,
    SOURCE_DB,
    get_connection,
    get_tables,
    profile_source,
)


@pytest.fixture
def connection():
    conn = get_connection()
    yield conn
    conn.close()


def test_source_database_exists():
    assert SOURCE_DB.exists()


def test_expected_tables_exist(connection):
    tables = get_tables(connection)

    assert EXPECTED_TABLES.issubset(tables)


def test_source_profile_contains_all_tables():
    profile = profile_source()

    assert set(profile["tables"]) == EXPECTED_TABLES


def test_source_has_no_unexpected_tables():
    profile = profile_source()

    assert set(profile["tables"]) == EXPECTED_TABLES


def test_primary_candidate_keys_are_unique():
    profile = profile_source()

    for table, metadata in profile["tables"].items():
        for key in metadata["composite_keys"]:
            assert key["is_unique"], (
                f"Composite key is not unique: "
                f"{table} {key['columns']}"
            )


def test_expected_relationships_are_profiled():
    profile = profile_source()

    assert len(profile["relationships"]) == 7


def test_expected_valid_relationships():
    profile = profile_source()

    expected_valid = {
        (
            "cursos_episodios",
            "descSlugCurso",
            "cursos",
            "descSlugCurso",
        ),
        (
            "cursos_episodios_completos",
            "descSlugCurso",
            "cursos",
            "descSlugCurso",
        ),
        (
            "habilidades_cargos",
            "descNomeHabilidade",
            "habilidades",
            "descNomeHabilidade",
        ),
        (
            "habilidades_usuarios",
            "descNomeHabilidade",
            "habilidades",
            "descNomeHabilidade",
        ),
    }

    for relationship in profile["relationships"]:
        key = (
            relationship["child_table"],
            relationship["child_column"],
            relationship["parent_table"],
            relationship["parent_column"],
        )

        if key in expected_valid:
            assert relationship["is_valid"], (
                f"Expected valid relationship failed: {key}"
            )
