from pathlib import Path

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
