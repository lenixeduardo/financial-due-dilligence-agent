# FinSight — Financial Due Diligence Agent

Aplicação **sob medida**, em desenvolvimento, para análise individual, comparação setorial e análise multissetorial. Não é SaaS.

**Regra:** a IA interpreta; o código calcula; as fontes comprovam.

## Banco de dados: SQLite

Não precisa de Supabase ou PostgreSQL. O arquivo persistente local fica em `data/finsight.sqlite3` por padrão e não deve ser enviado ao GitHub.

```sh
python -m venv .venv
# Ative o ambiente virtual antes de instalar.
pip install -r backend/requirements.txt
export FINSIGHT_SQLITE_PATH=data/finsight.sqlite3
export FINSIGHT_WORKSPACE_ID=local
export FINSIGHT_WORKSPACE_API_KEY='configure-uma-chave-longa-aleatoria'
PYTHONPATH=backend python -c "from app.db import initialize_database; initialize_database()"
uvicorn app.main:app --app-dir backend --host 127.0.0.1 --port 8000
```

Para Windows PowerShell, configure as mesmas variáveis com `$env:NOME = 'valor'` e use `$env:PYTHONPATH = 'backend'`.

Frontend:

```sh
cd frontend
npm install
npm run dev
```

Testes:

```sh
PYTHONPATH=backend pytest -q backend/tests
```

Leia [SQLite](docs/SQLITE.md) para backup e limitações, e [Segurança](docs/SECURITY.md) antes de implantar.

## Status de implementação

- API FastAPI e núcleo financeiro determinístico.
- Evidências e busca FTS5 isoladas por workspace e empresa.
- Armazenamento local SQLite com WAL e chaves estrangeiras.
- Busca híbrida local com vetores 384-d armazenados como JSON; requer geração externa de embeddings.
- Protótipo React com três modos.
- Testes automáticos e CI.

**Pendências:** fontes reais CVM/B3, pipeline de embeddings, integração do LLM, identidade de usuários/RBAC, auditoria de segurança e relatórios auditáveis de ponta a ponta. Não publicar a API na internet como serviço de produção.

## Licença

Nenhuma licença de redistribuição declarada.
