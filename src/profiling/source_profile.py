from pathlib import Path
import sqlite3


PROJECT_ROOT = Path(__file__).resolve().parents[2]
SOURCE_DB = PROJECT_ROOT / "data" / "source" / "database.db"


EXPECTED_TABLES = {
    "cursos",
    "cursos_episodios",
    "cursos_episodios_completos",
    "habilidades",
    "habilidades_cargos",
    "habilidades_usuarios",
    "recompensas_usuarios",
    "usuarios_tmw",
}


COMPOSITE_KEY_CANDIDATES = {
    "cursos_episodios": [
        ("descSlugCurso", "nrEp"),
    ],
    "habilidades_cargos": [
        ("descNomeCargo", "descNivelCargo", "descNomeHabilidade"),
    ],
    "habilidades_usuarios": [
        ("idUsuario", "descNomeHabilidade"),
    ],
    "recompensas_usuarios": [
        ("idUsuario", "idRecompensa"),
    ],
}


RELATIONSHIP_CANDIDATES = [
    ("cursos_episodios", "descSlugCurso", "cursos", "descSlugCurso"),
    ("cursos_episodios_completos", "descSlugCurso", "cursos", "descSlugCurso"),
    ("cursos_episodios_completos", "idUsuario", "usuarios_tmw", "idUsuario"),
    ("habilidades_cargos", "descNomeHabilidade", "habilidades", "descNomeHabilidade"),
    ("habilidades_usuarios", "idUsuario", "usuarios_tmw", "idUsuario"),
    ("habilidades_usuarios", "descNomeHabilidade", "habilidades", "descNomeHabilidade"),
    ("recompensas_usuarios", "idUsuario", "usuarios_tmw", "idUsuario"),
]


# ====================================================================== 
# CONNECTION
# ======================================================================

def get_connection() -> sqlite3.Connection:
    return sqlite3.connect(SOURCE_DB)


def get_tables(conn: sqlite3.Connection) -> set[str]:
    rows = conn.execute(
        """
        SELECT name
        FROM sqlite_master
        WHERE type = 'table'
        ORDER BY name;
        """
    ).fetchall()

    return {row[0] for row in rows}


# ====================================================================== 
# ROWS AND COLUMNS (COUNT)
# ======================================================================

def get_row_count(
    conn: sqlite3.Connection,
    table_name: str,
) -> int:
    row = conn.execute(
        f'SELECT COUNT(*) FROM "{table_name}";'
    ).fetchone()

    return row[0]


def get_columns(
    conn: sqlite3.Connection,
    table_name: str,
) -> list[dict]:
    rows = conn.execute(
        f'PRAGMA table_info("{table_name}");'
    ).fetchall()

    return [
        {
            "name": row[1],
            "type": row[2],
            "not_null": bool(row[3]),
            "primary_key": bool(row[5]),
        }
        for row in rows
    ]


# ====================================================================== 
# NULLS, UNIQUES
# ======================================================================

def get_null_counts(
    conn: sqlite3.Connection,
    table_name: str,
    columns: list[dict],
) -> dict[str, int]:

    null_counts = {}

    for column in columns:
        column_name = column["name"]

        row = conn.execute(
            f"""
            SELECT COUNT(*)
            FROM "{table_name}"
            WHERE "{column_name}" IS NULL;
            """
        ).fetchone()

        null_counts[column_name] = row[0]

    return null_counts


def get_unique_profile(
    conn: sqlite3.Connection,
    table_name: str,
    columns: list[dict],
) -> dict[str, dict]:

    profile = {}

    for column in columns:
        column_name = column["name"]

        row = conn.execute(
            f"""
            SELECT
                COUNT(*) AS total,
                COUNT(DISTINCT "{column_name}") AS distinct_count
            FROM "{table_name}";
            """
        ).fetchone()

        profile[column_name] = {
            "total": row[0],
            "distinct": row[1],
            "is_unique": row[0] == row[1],
        }

    return profile


# ====================================================================== 
# FOREIGN KEYS
# ======================================================================

def get_composite_key_profile(
    conn: sqlite3.Connection,
    table_name: str,
    key_columns: tuple[str, ...],
) -> dict:

    columns_sql = ", ".join(
        f'"{column}"'
        for column in key_columns
    )

    row = conn.execute(
        f"""
        SELECT
            COUNT(*) AS total,
            COUNT(*) - (
                SELECT COUNT(*)
                FROM (
                    SELECT {columns_sql}
                    FROM "{table_name}"
                    GROUP BY {columns_sql}
                )
            ) AS duplicate_count
        FROM "{table_name}";
        """
    ).fetchone()

    return {
        "columns": key_columns,
        "total": row[0],
        "duplicate_count": row[1],
        "is_unique": row[1] == 0,
    }


# ====================================================================== 
# REFERENTIAL INTEGRITY
# ======================================================================

def get_referential_profile(
    conn: sqlite3.Connection,
    child_table: str,
    child_column: str,
    parent_table: str,
    parent_column: str,
) -> dict:

    row = conn.execute(
        f"""
        SELECT
            COUNT(*) AS child_rows,
            COUNT(DISTINCT child."{child_column}") AS child_distinct,
            COUNT(parent."{parent_column}") AS matched_rows,
            COUNT(DISTINCT parent."{parent_column}") AS matched_distinct
        FROM "{child_table}" AS child
        LEFT JOIN "{parent_table}" AS parent
            ON child."{child_column}" = parent."{parent_column}";
        """
    ).fetchone()

    orphan_row = conn.execute(
        f"""
        SELECT COUNT(*)
        FROM "{child_table}" AS child
        LEFT JOIN "{parent_table}" AS parent
            ON child."{child_column}" = parent."{parent_column}"
        WHERE parent."{parent_column}" IS NULL;
        """
    ).fetchone()

    orphan_distinct = conn.execute(
        f"""
        SELECT COUNT(DISTINCT child."{child_column}")
        FROM "{child_table}" AS child
        LEFT JOIN "{parent_table}" AS parent
            ON child."{child_column}" = parent."{parent_column}"
        WHERE parent."{parent_column}" IS NULL;
        """
    ).fetchone()

    orphan_percentage = (
        (orphan_row[0] / row[0]) * 100
        if row[0] > 0
        else 0
    )

    return {
        "child_table": child_table,
        "child_column": child_column,
        "parent_table": parent_table,
        "parent_column": parent_column,
        "child_rows": row[0],
        "child_distinct": row[1],
        "matched_rows": row[2],
        "matched_distinct": row[3],
        "orphan_rows": orphan_row[0],
        "orphan_percentage": orphan_percentage,
        "orphan_distinct": orphan_distinct[0],
        "is_valid": orphan_row[0] == 0,
    }


# ====================================================================== 
# oRPHAN VALUES
# ======================================================================

def get_orphan_values(
    conn: sqlite3.Connection,
    child_table: str,
    child_column: str,
    parent_table: str,
    parent_column: str,
    limit: int = 20,
) -> list[dict]:

    rows = conn.execute(
        f"""
        SELECT
            child."{child_column}" AS value,
            COUNT(*) AS occurrences
        FROM "{child_table}" AS child
        LEFT JOIN "{parent_table}" AS parent
            ON child."{child_column}" = parent."{parent_column}"
        WHERE parent."{parent_column}" IS NULL
        GROUP BY child."{child_column}"
        ORDER BY occurrences DESC
        LIMIT ?;
        """,
        (limit,),
    ).fetchall()

    return [
        {
            "value": row[0],
            "occurrences": row[1],
        }
        for row in rows
    ]


# ====================================================================== 
# MAIN FUNCTIONS (PROFILE AND PRINT RESULTS)
# ======================================================================

def profile_source() -> dict:
    if not SOURCE_DB.exists():
        raise FileNotFoundError(
            f"Source database not found: {SOURCE_DB}"
        )

    with get_connection() as conn:
        tables = get_tables(conn)

        profile = {
            "source": str(SOURCE_DB),
            "tables": {},
        }

        for table in sorted(tables):
            columns = get_columns(conn, table)

            profile["tables"][table] = {
                "row_count": get_row_count(conn, table),
                "columns": columns,
                "null_counts": get_null_counts(
                    conn,
                    table,
                    columns,
                ),
                "unique_profile": get_unique_profile(
                    conn,
                    table,
                    columns,
                ),
                "composite_keys": [],
            }

            for key in COMPOSITE_KEY_CANDIDATES.get(table, []):
                profile["tables"][table]["composite_keys"].append(
                    get_composite_key_profile(
                        conn,
                        table,
                        key,
                    )
                )

        # CHORE: SHOWING RELATIONSHIPS
        profile["relationships"] = []

        for relationship in RELATIONSHIP_CANDIDATES:
            profile["relationships"].append(
                get_referential_profile(
                    conn,
                    *relationship,
                )
            )

        # CHORE: SHOWING ORPHAN VALUES
        profile["orphan_values"] = {}

        for relationship in RELATIONSHIP_CANDIDATES:
            child_table, child_column, parent_table, parent_column = relationship

            key = (
                f"{child_table}.{child_column}"
                f"->{parent_table}.{parent_column}"
            )

            profile["orphan_values"][key] = get_orphan_values(
                conn,
                child_table,
                child_column,
                parent_table,
                parent_column,
            )

        return profile
    

def print_profile(profile: dict) -> None:
    print("=" * 70)
    print("SOURCE PROFILING")
    print("=" * 70)

    print(f"\nSource: {profile['source']}")

    print("\nTables:")

    for table, metadata in profile["tables"].items():
        print(f"\n[{table}]")
        print(f"Rows: {metadata['row_count']}")

        for column in metadata["columns"]:
            name = column["name"]
            column_type = column["type"]
            null_count = metadata["null_counts"][name]

            unique = metadata["unique_profile"][name]

            print(
                f"  - {name}: "
                f"{column_type} | "
                f"NULLs: {null_count} | "
                f"Distinct: {unique['distinct']} | "
                f"Unique: {unique['is_unique']}"
            )

        for key in metadata["composite_keys"]:
            columns = ", ".join(key["columns"])

            print(
                f"  - Composite key ({columns}): "
                f"Duplicates: {key['duplicate_count']} | "
                f"Unique: {key['is_unique']}"
            )


    print()
    print("=" * 70)
    print("\nRelationships:")

    for relationship in profile["relationships"]:
        print(
            f"\n  {relationship['child_table']}."
            f"{relationship['child_column']}"
            f" -> "
            f"{relationship['parent_table']}."
            f"{relationship['parent_column']}"
        )

        print(
            f"    Child rows: {relationship['child_rows']} | "
            f"Child distinct: {relationship['child_distinct']}"
        )

        print(
            f"    Orphan rows: {relationship['orphan_rows']} | "
            f"Orphan distinct: {relationship['orphan_distinct']} | "
            f"Orphan %: {relationship['orphan_percentage']:.2f}%"
        )

        print(
            f"    Valid: {relationship['is_valid']}"
        )

    print()
    print("=" * 70)
    print("\nOrphan values:")

    for relationship, values in profile["orphan_values"].items():

        if not values:
            continue

        print(f"\n  {relationship}")

        for item in values[:5]:
            print(
                f"    - {item['value']}: "
                f"{item['occurrences']} rows"
            )

        print("    Maximum view to 5 lines.")


if __name__ == "__main__":
    profile = profile_source()
    print_profile(profile)