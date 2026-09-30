# ETL TeoMeWhy

Pipeline de dados da plataforma TeoMeWhy.

## Arquitetura

                         ┌─────────────┐
                         │    START    │
                         └──────┬──────┘
                                │
                                ▼
                    ┌──────────────────────┐
                    │ Download Kaggle      │
                    │ / atualizar dataset  │
                    └──────────┬───────────┘
                               │
                               ▼
                    ┌──────────────────────┐
                    │ Validate Files       │
                    │ existência / schema  │
                    │ formato / integridade│
                    └──────────┬───────────┘
                               │
                         ┌─────▼─────┐
                         │   PASS?   │
                         └──┬─────┬──┘
                            │     │
                           YES    NO
                            │     │
                            │     ▼
                            │  QUARANTINE
                            │     / FAIL
                            │
                            ▼
                  ┌─────────────────────┐
                  │ PostgreSQL          │
                  │        RAW          │
                  │                     │
                  │ CSV → tabelas RAW   │
                  └──────────┬──────────┘
                             │
                             ▼
                  ┌─────────────────────┐
                  │ Great Expectations  │
                  │                     │
                  │ qualidade RAW       │
                  └──────────┬──────────┘
                             │
                       ┌─────▼─────┐
                       │   PASS?   │
                       └──┬─────┬──┘
                          │     │
                         YES    NO
                          │     │
                          │     ▼
                          │ QUARANTINE
                          │    / FAIL
                          │
                          ▼
                  ┌─────────────────────┐
                  │ dbt staging         │
                  │                     │
                  │ limpeza / tipos /   │
                  │ padronização        │
                  └──────────┬──────────┘
                             │
                             ▼
                  ┌─────────────────────┐
                  │ dbt tests           │
                  │                     │
                  │ PK / FK / schema / │
                  │ regras de negócio  │
                  └──────────┬──────────┘
                             │
                       ┌─────▼─────┐
                       │   PASS?   │
                       └──┬─────┬──┘
                          │     │
                         YES    NO
                          │     │
                          │     ▼
                          │    FAIL
                          │
                          ▼
                  ┌─────────────────────┐
                  │ dbt analytics       │
                  │                     │
                  │ marts / dimensões / │
                  │ fatos / métricas    │
                  └──────────┬──────────┘
                             │
                             ▼
                  ┌─────────────────────┐
                  │ Final validation    │
                  │                     │
                  │ dados analíticos    │
                  └──────────┬──────────┘
                             │
                             ▼
                        ┌──────────┐
                        │   END    │
                        └──────────┘


## Stack

- Python
- PostgreSQL
- Docker
- dbt
- Great Expectations
- Airflow

## Fases do DAG

                  FASE 1 — SOURCE DISCOVERY
                        ↓
                  database.db
                        ↓
                  profiling exploratório
                        ↓
                  FASE 2 — SOURCE VALIDATION  ← estamos aqui
                        ↓
                  código versionado
                        ↓
                  commit
                        ↓
                  FASE 3 — INGESTION
                        ↓
                  PostgreSQL RAW

