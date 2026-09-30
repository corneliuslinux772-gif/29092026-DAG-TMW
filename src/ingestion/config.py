from pathlib import Path
import os

PROJECT_ROOT = Path(__file__).resolve().parents[2]

INCOMING_DB = PROJECT_ROOT / "data" / "incoming" / "database.db"

SOURCE_DB = PROJECT_ROOT / "data" / "source" / "database.db"

QUARANTINE_DIR = PROJECT_ROOT / "data" / "quarantine"


EXPECTED_SCHEMA = {
    "cursos": {
        "descSlugCurso": "TEXT",
        "descCurso": "TEXT",
        "descDescricao": "TEXT",
        "nrAno": "BIGINT",
    },
    "cursos_episodios": {
        "descSlugCurso": "TEXT",
        "nrEp": "BIGINT",
        "descEpisodio": "TEXT",
        "descYoutubeID": "TEXT",
    },
    "cursos_episodios_completos": {
        "idCursoEpisodioCompleto": "BIGINT",
        "idUsuario": "TEXT",
        "descSlugCurso": "TEXT",
        "descSlugCursoEpisodio": "TEXT",
        "dtCriacao": "DATETIME",
    },
    "habilidades": {
        "idHabilidade": "BIGINT",
        "descNomeHabilidade": "TEXT",
        "descDescricaoHabilidade": "TEXT",
    },
    "habilidades_cargos": {
        "idHabilidadeCargo": "BIGINT",
        "descNomeCargo": "TEXT",
        "descNivelCargo": "TEXT",
        "descNomeHabilidade": "TEXT",
        "descNivelHabilidade": "TEXT",
    },
    "habilidades_usuarios": {
        "idHabilidadeusuario": "BIGINT",
        "idUsuario": "TEXT",
        "descNomeHabilidade": "TEXT",
        "descNivelHabilidade": "TEXT",
        "dtCriacao": "DATETIME",
    },
    "recompensas_usuarios": {
        "idUsuario": "TEXT",
        "idRecompensa": "TEXT",
        "dtRecompensa": "DATETIME",
    },
    "usuarios_tmw": {
        "idUsuario": "TEXT",
        "idTMWCliente": "TEXT",
    },
}


TABLES = [
    "cursos",
    "cursos_episodios",
    "cursos_episodios_completos",
    "habilidades",
    "habilidades_cargos",
    "habilidades_usuarios",
    "recompensas_usuarios",
    "usuarios_tmw",
]


POSTGRES_CONFIG = {
    "host": os.getenv("POSTGRES_HOST", "localhost"),
    "port": os.getenv("POSTGRES_PORT", "5432"),
    "dbname": os.getenv("POSTGRES_DB", "teomewhy"),
    "user": os.getenv("POSTGRES_USER", "teomewhy"),
    "password": os.getenv("POSTGRES_PASSWORD", "teomewhy"),
}