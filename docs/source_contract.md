# Data Contract — TeoMeWhy Education Platform

## 1. Fonte

| Campo | Valor |
|---|---|
| Origem | Kaggle — TeoMeWhy Education Platform |
| Formato | SQLite |
| Arquivo | `database.db` |
| Encoding | UTF-8 |
| Engine | SQLite 3 |
| Tabelas | 8 |

O arquivo SQLite representa a fonte bruta utilizada pelo pipeline.

A camada RAW deve preservar os dados da fonte sem aplicar regras de negócio,
limpeza ou transformação.

---

## 2. Tabelas

| Tabela | Registros | Chave identificada |
|---|---:|---|
| `cursos` | 32 | `descSlugCurso` |
| `cursos_episodios` | 375 | `descSlugCurso`, `nrEp` |
| `cursos_episodios_completos` | 43276 | `idCursoEpisodioCompleto` |
| `habilidades` | 25 | `idHabilidade` |
| `habilidades_cargos` | 275 | `descNomeCargo`, `descNivelCargo`, `descNomeHabilidade` |
| `habilidades_usuarios` | 58647 | `idHabilidadeusuario` |
| `recompensas_usuarios` | 675 | `idUsuario`, `idRecompensa` |
| `usuarios_tmw` | 2506 | `idUsuario` |

---

## 3. Regras de nulidade

As tabelas possuem os seguintes campos com valores NULL:

| Tabela | Campo | NULLs |
|---|---|---:|
| `habilidades_usuarios` | `descNivelHabilidade` | 1887 |

Os demais campos não apresentaram valores NULL no profiling atual.

A existência de NULL na fonte não deve provocar descarte automático do registro
durante a ingestão RAW.

---

## 4. Integridade das chaves

As seguintes chaves compostas apresentaram unicidade:

- `cursos_episodios`
  - `(descSlugCurso, nrEp)`

- `habilidades_cargos`
  - `(descNomeCargo, descNivelCargo, descNomeHabilidade)`

- `habilidades_usuarios`
  - `(idUsuario, descNomeHabilidade)`

- `recompensas_usuarios`
  - `(idUsuario, idRecompensa)`

As seguintes chaves simples apresentaram unicidade:

- `cursos.descSlugCurso`
- `cursos_episodios_completos.idCursoEpisodioCompleto`
- `habilidades.idHabilidade`
- `habilidades.descNomeHabilidade`
- `habilidades_cargos.idHabilidadeCargo`
- `habilidades_usuarios.idHabilidadeusuario`
- `usuarios_tmw.idUsuario`
- `usuarios_tmw.idTMWCliente`

---

## 5. Relacionamentos

### Relacionamentos com cobertura completa

| Origem | Destino | Cobertura |
|---|---|---:|
| `cursos_episodios.descSlugCurso` | `cursos.descSlugCurso` | 100% |
| `cursos_episodios_completos.descSlugCurso` | `cursos.descSlugCurso` | 100% |
| `habilidades_cargos.descNomeHabilidade` | `habilidades.descNomeHabilidade` | 100% |
| `habilidades_usuarios.descNomeHabilidade` | `habilidades.descNomeHabilidade` | 100% |

### Relacionamentos com registros sem correspondência

| Origem | Destino | Registros órfãos | Percentual |
|---|---|---:|---:|
| `cursos_episodios_completos.idUsuario` | `usuarios_tmw.idUsuario` | 15625 | 36.11% |
| `habilidades_usuarios.idUsuario` | `usuarios_tmw.idUsuario` | 31970 | 54.51% |
| `recompensas_usuarios.idUsuario` | `usuarios_tmw.idUsuario` | 3 | 0.44% |

Essas relações não devem ser tratadas como referências obrigatórias no RAW.

Os registros órfãos devem ser preservados.

---

## 6. Regras para a camada RAW

A ingestão RAW deve:

1. Carregar todos os registros presentes na fonte.
2. Preservar os valores originais.
3. Não remover registros por NULL.
4. Não remover registros órfãos.
5. Não aplicar regras de negócio.
6. Não alterar identificadores.
7. Preservar as colunas da fonte.
8. Registrar metadados da execução da ingestão.
9. Permitir rastreabilidade entre o registro RAW e a origem.

A camada RAW representa o estado observado da fonte no momento da ingestão.

---

## 7. Regras de qualidade

As validações de qualidade devem ocorrer após a ingestão RAW.

As regras mínimas identificadas durante o profiling são:

- chaves identificadas devem permanecer únicas;
- colunas que não apresentaram NULL na fonte devem ser monitoradas;
- `descNivelHabilidade` pode conter NULL;
- relacionamentos com cobertura de 100% devem permanecer válidos;
- relacionamentos com órfãos conhecidos não devem falhar a ingestão RAW.

---

## 8. Evolução do contrato

Este contrato representa o estado observado da fonte durante o profiling.

Alterações futuras na estrutura, cardinalidade, nulidade ou relacionamentos
devem ser identificadas pelo pipeline e avaliadas antes de alterar as regras
de qualidade.

O contrato não define regras de negócio da camada analítica.