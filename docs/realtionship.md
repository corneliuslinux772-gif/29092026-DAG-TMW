# Relacionamentos e populações de usuários

## usuarios_tmw

A tabela `usuarios_tmw` possui 691 usuários distintos.

Ela não representa a população completa de usuários encontrada nas tabelas
`cursos_episodios_completos` e `habilidades_usuarios`.

## Cobertura

| Relacionamento | Total | Encontrados | Cobertura |
|---|---:|---:|---:|
| cursos_episodios_completos -> usuarios_tmw | 1119 | 328 | 29.31% |
| habilidades_usuarios -> usuarios_tmw | 1439 | 387 | 26.89% |
| cursos_episodios_completos -> habilidades_usuarios | 1119 | 512 | 45.76% |
| habilidades_usuarios -> cursos_episodios_completos | 1439 | 512 | 35.58% |

## Conclusão

`usuarios_tmw` deve ser tratado como uma população parcial em relação às
tabelas de atividade e habilidades.

As relações:

- `cursos_episodios_completos.idUsuario -> usuarios_tmw.idUsuario`
- `habilidades_usuarios.idUsuario -> usuarios_tmw.idUsuario`

não devem ser consideradas chaves estrangeiras obrigatórias no modelo RAW.

Os registros sem correspondência não serão removidos durante a ingestão RAW.

A ausência de correspondência deve ser preservada para investigação e para
permitir que as camadas posteriores (`staging` e `analytics`) definam regras
de negócio explicitamente.

As tabelas de atividade e habilidades também possuem populações parcialmente
sobrepostas, indicando que não representam necessariamente o mesmo universo
de usuários.