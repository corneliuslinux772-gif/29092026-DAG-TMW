from src.profiling.source_profile import (
    get_connection,
    get_orphan_values,
)


RELATIONSHIPS = [
    (
        "cursos_episodios_completos",
        "idUsuario",
        "usuarios_tmw",
        "idUsuario",
    ),
    (
        "habilidades_usuarios",
        "idUsuario",
        "usuarios_tmw",
        "idUsuario",
    ),
]


def investigate_relationship(
    conn,
    child_table,
    child_column,
    parent_table,
    parent_column,
):
    print("=" * 70)
    print(
        f"{child_table}.{child_column}"
        f" -> "
        f"{parent_table}.{parent_column}"
    )
    print("=" * 70)

    orphan_values = get_orphan_values(
        conn,
        child_table,
        child_column,
        parent_table,
        parent_column,
        limit=20,
    )

    for item in orphan_values:
        value = item["value"]
        occurrences = item["occurrences"]

        print(f"\nID: {value}")
        print(f"Ocorrências: {occurrences}")

        rows = conn.execute(
            f"""
            SELECT *
            FROM "{child_table}"
            WHERE "{child_column}" = ?
            LIMIT 5;
            """,
            (value,),
        ).fetchall()

        columns = [
            column[1]
            for column in conn.execute(
                f'PRAGMA table_info("{child_table}");'
            ).fetchall()
        ]

        for row in rows:
            print(dict(zip(columns, row)))

def compare_user_populations(conn):
    print("\n" + "=" * 70)
    print("COMPARAÇÃO DAS POPULAÇÕES DE USUÁRIOS")
    print("=" * 70)

    queries = {
        "usuarios_tmw": """
            SELECT COUNT(DISTINCT idUsuario)
            FROM usuarios_tmw;
        """,
        "cursos_episodios_completos": """
            SELECT COUNT(DISTINCT idUsuario)
            FROM cursos_episodios_completos;
        """,
        "habilidades_usuarios": """
            SELECT COUNT(DISTINCT idUsuario)
            FROM habilidades_usuarios;
        """,
    }

    for name, query in queries.items():
        count = conn.execute(query).fetchone()[0]
        print(f"{name}: {count}")

    print("\nInterseções:")

    queries = {
        "episodios ∩ usuarios_tmw": """
            SELECT COUNT(DISTINCT c.idUsuario)
            FROM cursos_episodios_completos c
            INNER JOIN usuarios_tmw u
                ON c.idUsuario = u.idUsuario;
        """,
        "habilidades ∩ usuarios_tmw": """
            SELECT COUNT(DISTINCT h.idUsuario)
            FROM habilidades_usuarios h
            INNER JOIN usuarios_tmw u
                ON h.idUsuario = u.idUsuario;
        """,
        "episodios ∩ habilidades": """
            SELECT COUNT(DISTINCT c.idUsuario)
            FROM cursos_episodios_completos c
            INNER JOIN habilidades_usuarios h
                ON c.idUsuario = h.idUsuario;
        """,
    }

    for name, query in queries.items():
        count = conn.execute(query).fetchone()[0]
        print(f"{name}: {count}")


def compare_user_coverage(conn):
    print("\n" + "=" * 70)
    print("COBERTURA DAS POPULAÇÕES")
    print("=" * 70)

    queries = {
        "episodios -> usuarios_tmw": """
            SELECT
                COUNT(DISTINCT c.idUsuario),
                COUNT(DISTINCT CASE
                    WHEN u.idUsuario IS NOT NULL THEN c.idUsuario
                END)
            FROM cursos_episodios_completos c
            LEFT JOIN usuarios_tmw u
                ON c.idUsuario = u.idUsuario;
        """,

        "habilidades -> usuarios_tmw": """
            SELECT
                COUNT(DISTINCT h.idUsuario),
                COUNT(DISTINCT CASE
                    WHEN u.idUsuario IS NOT NULL THEN h.idUsuario
                END)
            FROM habilidades_usuarios h
            LEFT JOIN usuarios_tmw u
                ON h.idUsuario = u.idUsuario;
        """,

        "episodios -> habilidades": """
            SELECT
                COUNT(DISTINCT c.idUsuario),
                COUNT(DISTINCT CASE
                    WHEN h.idUsuario IS NOT NULL THEN c.idUsuario
                END)
            FROM cursos_episodios_completos c
            LEFT JOIN (
                SELECT DISTINCT idUsuario
                FROM habilidades_usuarios
            ) h
                ON c.idUsuario = h.idUsuario;
        """,

        "habilidades -> episodios": """
            SELECT
                COUNT(DISTINCT h.idUsuario),
                COUNT(DISTINCT CASE
                    WHEN c.idUsuario IS NOT NULL THEN h.idUsuario
                END)
            FROM habilidades_usuarios h
            LEFT JOIN (
                SELECT DISTINCT idUsuario
                FROM cursos_episodios_completos
            ) c
                ON h.idUsuario = c.idUsuario;
        """,
    }

    for name, query in queries.items():
        total, matched = conn.execute(query).fetchone()

        coverage = (
            matched / total * 100
            if total
            else 0
        )

        print(f"{name}")
        print(f"  total: {total}")
        print(f"  encontrados: {matched}")
        print(f"  cobertura: {coverage:.2f}%")


def main():
    conn = get_connection()

    try:
        for relationship in RELATIONSHIPS:
            investigate_relationship(conn, *relationship)

        compare_user_populations(conn)
        compare_user_coverage(conn)

    finally:
        conn.close()


if __name__ == "__main__":
    main()