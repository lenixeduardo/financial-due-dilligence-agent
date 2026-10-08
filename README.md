# FinSight — Financial Due Diligence Agent

Ferramenta de pesquisa e análise financeira individual, setorial e multissetorial, construída com **React + TypeScript**, **FastAPI + Python** e **SQLite**. Não é SaaS.

**Princípio:** a IA interpreta; o código calcula; as fontes comprovam.

## Funcionalidades desenvolvidas

- Dossiê individual: importação PDF/TXT/CSV e DFP ZIP, busca FTS5, citações de evidências e indicadores determinísticos iniciais.
- Análise setorial/multissetorial: validação de compatibilidade dos indicadores, fórmulas e períodos. Dados inseridos manualmente continuam classificados como não verificados.
- CVM: parser DFP/ITR ZIP, seleção por código CVM e ano; cálculo DFP inicial de margens e liquidez. Versões contábeis conflitantes são recusadas, não mescladas.
- Persistência SQLite local, vetores opcionais, revisão humana com trilha de auditoria e versões preservadas.
- Autenticação individual opt-in por sessões SQLite e papéis (reader, analyst, reviewer, admin). Em produção, a chave de workspace de desenvolvimento é rejeitada.
- Contêineres para servidor único, proxy HTTPS Caddy, persistência SQLite, rotina de backups e testes automatizados.

**Não homologado para produção.** O código funciona para exploração local, mas a publicação com usuários e dados reais depende dos controles de [aceite operacional](docs/PRODUCTION_RELEASE_CHECKLIST.md).

## Desenvolvimento local

```bash
python -m venv .venv
# Ative o ambiente antes da instalação.
pip install -r backend/requirements.txt
export FINSIGHT_SQLITE_PATH=data/finsight.sqlite3
export FINSIGHT_WORKSPACE_ID=local
export FINSIGHT_WORKSPACE_API_KEY=dev-use-uma-chave-aleatoria
PYTHONPATH=backend python -c "from app.db import initialize_database;initialize_database()"
uvicorn app.main:app --app-dir backend --host 127.0.0.1 --port 8000
```

Em outro terminal:

```bash
cd frontend
npm install
npm run dev
```

PowerShell: configurar variáveis com `$env:NOME='valor'`. Nunca registrar senhas reais em comandos de shell.

## Autenticação e implantação

Para habilitar usuários, defina `FINSIGHT_AUTH_MODE=users`, provisione a conta inicial via CLI e compile o frontend com `VITE_FINSIGHT_AUTH_MODE=users`. Veja [Identidade](docs/IDENTITY_DEPLOYMENT.md).

Para VPS Linux com armazenamento persistente, veja [Docker/HTTPS](deploy/README.md), [backup e restauração](docs/OPERATIONS.md) e [checklist de lançamento](docs/PRODUCTION_RELEASE_CHECKLIST.md). Não hospedar o SQLite em disco efêmero do Vercel/serverless.

## Critérios ainda pendentes para produção

Homologação real de CVM/DFP/ITR, regras de reapresentação, fórmulas por setor, processamento seguro de fontes externas, avaliação dos modelos locais, testes de segurança e carga, monitoramento, política LGPD, cópias off-host cifradas, testes de restauração e aceitação em domínio HTTPS real.

Nenhuma informação calculada sem revisão é parecer de auditoria ou recomendação de investimento.

## Licença

Não há licença pública de redistribuição declarada.
