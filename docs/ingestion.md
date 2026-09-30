# Ingestion

## Objetivo

Responsável por receber a fonte SQLite, validar sua estrutura e integridade,
promover fontes válidas para `source/` e enviar fontes inválidas para
`quarantine/` antes da carga no PostgreSQL RAW.

---

## Fluxo

```text
Kaggle
  ↓
data/incoming/
  ↓
source_validator
  ↓
┌───────────────┐
│               │
PASS            FAIL
│               │
↓               ↓
source/       quarantine/
│             ├── database.db
│             └── validation_report.json
↓
PostgreSQL RAW
````

---

## Diretórios

```text
data/
├── incoming/
├── source/
└── quarantine/
```

### `incoming/`

Área transitória para arquivos recém-recebidos.

Nenhum arquivo dessa área deve ser carregado diretamente no RAW.

### `source/`

Contém somente arquivos que passaram pela validação de fonte.

### `quarantine/`

Contém arquivos rejeitados durante a validação, juntamente com o relatório
do motivo da rejeição.

---

## Componentes

### `source_validator.py`

Responsável exclusivamente por validar:

* existência do arquivo;
* arquivo não vazio;
* formato SQLite;
* integridade SQLite;
* tabelas esperadas;
* schema esperado.

Não realiza limpeza ou transformação dos dados.

---

### `source_promotion.py`

Responsável por promover uma fonte validada:

```text
incoming/database.db
        ↓
source/database.db
```

---

### `source_quarantine.py`

Responsável por retirar uma fonte inválida do fluxo:

```text
incoming/database.db
        ↓
quarantine/<timestamp>/
```

Também gera:

```text
validation_report.json
```

com os erros encontrados.

---

### `ingest_source.py`

Orquestra:

```text
validate
   ↓
PASS → promotion

FAIL → quarantine
```

---

### `load_raw.py`

Executa a carga da fonte validada para PostgreSQL.

Características da camada RAW:

* preserva os dados originais;
* não aplica regras de negócio;
* não elimina registros;
* não corrige valores;
* não cria relacionamentos de negócio;
* mantém a estrutura próxima da fonte original.

---

### `run_ingestion.py`

Orquestra o fluxo completo:

```text
ingest_source
      ↓
source
      ↓
load_raw
```

O `load_raw` somente é executado após o sucesso do `ingest_source`.

---

## Contrato de execução

```text
Source inválida
    ↓
quarantine
    ↓
pipeline interrompida
```

```text
Source válida
    ↓
source
    ↓
RAW
    ↓
pipeline continua
```

---

## Testes

A ingestão possui testes unitários para:

* validação de arquivo inexistente;
* arquivo vazio;
* arquivo SQLite inválido;
* integridade SQLite;
* promoção;
* quarentena;
* orquestração da ingestão;
* bloqueio da carga RAW quando a validação falha.

Execução:

```bash
uv run pytest tests/ingestion -v
```

---

## Resultado atual

Fluxo de ingestão implementado e validado.

Última execução real:

```text
Source validation: PASS
Source promotion: SUCCESS
RAW ingestion: SUCCESS
```

Tabelas carregadas:

| Tabela                     | Registros |
| -------------------------- | --------: |
| cursos                     |        32 |
| cursos_episodios           |       375 |
| cursos_episodios_completos |    43.276 |
| habilidades                |        25 |
| habilidades_cargos         |       275 |
| habilidades_usuarios       |    58.647 |
| recompensas_usuarios       |       675 |
| usuarios_tmw               |     2.506 |

````

### Depois

```bash
git status
git add docs/ingestion.md src/ingestion tests/ingestion
git commit -m "feat: implement source ingestion and quarantine flow"
````

**Info técnica:** esse documento não é redundante com `data_contract.md`. O `data_contract.md` define **o que esperamos da fonte**; o `ingestion.md` define **como a fonte entra no pipeline**. São responsabilidades diferentes.
