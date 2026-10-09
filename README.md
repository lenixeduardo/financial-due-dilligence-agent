# FinSight
### Financial Due Diligence Intelligence

**Investigação financeira baseada em evidências, métodos reproduzíveis e revisão humana.**

O FinSight é uma plataforma de análise de demonstrações financeiras desenvolvida com **Python, FastAPI, React, TypeScript e SQLite**. Reúne processamento de documentos, indicadores calculados por regras explícitas, comparação entre empresas e histórico de revisão em um ambiente local.

> **A IA interpreta. O código calcula. As fontes comprovam.**

**Estado:** desenvolvimento avançado / instalação local disponível para Windows 10/11. **Ainda não homologado para produção com dados reais.**

## O que o FinSight faz

| Área | Capacidades disponíveis |
| --- | --- |
| **Dossiê individual** | Importação de PDF, TXT, CSV e conjuntos DFP em ZIP; recuperação de trechos com referência à fonte |
| **Indicadores CVM** | Cálculos determinísticos iniciais de margem operacional, margem líquida e liquidez corrente |
| **Comparações** | Validação de indicadores, períodos e metodologias em análises setoriais e multissetoriais |
| **Rastreabilidade** | Hash SHA-256 do conjunto de origem, identificação de contas contábeis e versão da fórmula |
| **Revisão humana** | Aprovação/rejeição manual com justificativa e histórico de eventos |
| **Segurança local** | Contas individuais, sessões temporárias e permissões `reader`, `analyst`, `reviewer`, `admin` |
| **Persistência** | SQLite, pesquisa FTS5, verificação de integridade e backups locais |

Dados financeiros importados e indicadores não passam a ser “verificados” apenas porque foram processados. O sistema conserva o status de revisão pendente e rejeita combinações incompatíveis de demonstrações e versões.

## Arquitetura

```text
                    FIN SIGHT · LOCAL
┌───────────────────────────────────────────┐
│ React + TypeScript                        │
│ Dossiês · Comparações · Revisões · Login  │
└──────────────────────┬────────────────────┘
                       │ /api
┌──────────────────────▼────────────────────┐
│ Python + FastAPI                          │
│ Autenticação · Ingestão · Indicadores      │
│ Evidências · Comparação · Revisões        │
└──────────────────────┬────────────────────┘
                       │
┌──────────────────────▼────────────────────┐
│ SQLite local                              │
│ Workspaces · Documentos · FTS5            │
│ Indicadores · Sessões · Trilha de revisão │
└───────────────────────────────────────────┘
```

**Stack:** React 19, TypeScript, Vite, Lucide, Python 3.12, FastAPI, Pydantic, SQLite, pypdf, pytest e GitHub Actions. Existem adaptadores opcionais para embeddings locais e Ollama, mas o fluxo de IA não deve ser considerado homologado de ponta a ponta.

## Instalação no Windows 10/11

A instalação local **não exige Docker Desktop, Supabase, VPS ou PostgreSQL**. É destinada inicialmente ao próprio computador, no endereço `127.0.0.1`, sem publicação para outras máquinas.

### 1. Pré-requisitos

- **Git**, **Python 3.12** e **Node.js 22 LTS**.
- Windows PowerShell 5.1 ou superior.
- Conexão à internet para instalar as dependências na primeira execução.

Confira os comandos:

```powershell
git --version
py -3.12 --version
node --version
npm --version
```

Se aparecer `No runtime installed that matches 3.12`, instale o Python 3.12:

```powershell
py install 3.12
py -3.12 --version
```

Caso o comando `py install` não seja aceito, instale o Python 3.12 pelo [site oficial](https://www.python.org/downloads/windows/) e execute a verificação novamente.

### 2. Baixar o projeto

**Atenção:** execute os próximos comandos dentro da pasta do **FinSight**, não de outros projetos (como PORTUS).

```powershell
cd $HOME\Desktop
git clone https://github.com/lenixeduardo/financial-due-dilligence-agent.git
cd financial-due-dilligence-agent
```

Se já tiver clonado, entre na pasta e atualize o código:

```powershell
cd $HOME\Desktop\financial-due-dilligence-agent
git pull origin main
```

Confirme que o instalador existe:

```powershell
Test-Path .\deploy\windows\Install-FinSight.ps1
```

O retorno deve ser `True`.

### 3. Instalar

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\deploy\windows\Install-FinSight.ps1
```

O script cria o ambiente Python, instala dependências, compila o React, prepara o banco SQLite e solicita a criação da conta administrativa. Também configura a inicialização do FinSight após o login do usuário no Windows.

### 4. Iniciar e acessar

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\deploy\windows\Start-FinSight.ps1
```

No navegador, abra **http://127.0.0.1:8765** e entre com a conta criada durante a instalação. Mantenha a janela do servidor aberta enquanto estiver utilizando o FinSight.

### Dados persistentes

| Recurso | Local no Windows |
| --- | --- |
| Banco SQLite | `%LOCALAPPDATA%\FinSight\data\finsight.sqlite3` |
| Backups | `%LOCALAPPDATA%\FinSight\backups` |
| Inicialização automática | Atalho `FinSight.lnk` na pasta de inicialização do usuário |

Backups locais são gerados aproximadamente a cada seis horas enquanto o servidor está em execução, com retenção das últimas 14 cópias. **Cópias no mesmo disco não substituem backups externos criptografados.**

Leia o [guia completo de instalação para Windows](deploy/windows/README.md).

## Desenvolvimento

Para o ambiente Linux/macOS ou execução separada da API e do frontend:

```bash
python -m venv .venv
# Ative a .venv e instale as dependências
pip install -r backend/requirements.txt
export FINSIGHT_SQLITE_PATH=data/finsight.sqlite3
export FINSIGHT_WORKSPACE_ID=local
export FINSIGHT_WORKSPACE_API_KEY=chave-local-aleatoria
uvicorn app.main:app --app-dir backend --host 127.0.0.1 --port 8000
```

Em outro terminal:

```bash
cd frontend
npm ci
npm run dev
```

O modo com chaves compartilhadas é **apenas para desenvolvimento**. Para contas individuais, utilize `FINSIGHT_AUTH_MODE=users` e consulte [Identidade e permissões](docs/IDENTITY_DEPLOYMENT.md).

## Validações

O repositório inclui testes de backend e SQLite, compilação TypeScript/Vite, construção dos containers e verificações específicas em Windows executadas pelo GitHub Actions.

```powershell
$env:PYTHONPATH = "backend"
python -m pytest -q backend/tests
```

Os resultados do CI não substituem o teste de instalação na máquina final.

## Limites e próximos marcos

As seguintes entregas **ainda bloqueiam a declaração de prontidão total para produção**:

- Homologação de demonstrativos e reapresentações reais da CVM, com revisão das regras por setor.
- Validação de ponta a ponta da instalação Windows: primeiro login, importação DFP, revisão e reinicialização.
- Avaliação dos componentes opcionais de IA e recuperação de evidências em casos financeiros reais.
- Avaliação de segurança, dependências, privacidade/LGPD e uso operacional.
- Teste de restauração, backup fora da máquina, monitoramento e plano de recuperação.
- Liberação de acesso em rede somente após estabelecer HTTPS, controles de acesso e infraestrutura apropriada.

Veja o [checklist de aceite para produção](docs/PRODUCTION_RELEASE_CHECKLIST.md). Até a homologação, opere apenas localmente e trate os resultados como material preliminar de pesquisa, não como auditoria ou aconselhamento de investimentos.

## Documentação

- [Instalação local no Windows](deploy/windows/README.md)
- [Identidade e permissões](docs/IDENTITY_DEPLOYMENT.md)
- [Coleta de dados da CVM](docs/CVM_COLLECTION.md)
- [Indicadores financeiros](docs/CVM_INDICATORS.md)
- [Revisão humana](docs/INDICATOR_REVIEW.md)
- [Operações e recuperação](docs/OPERATIONS.md)
- [Checklist de produção](docs/PRODUCTION_RELEASE_CHECKLIST.md)

## Licença

Este repositório não declara atualmente uma licença pública de redistribuição.

---

**FinSight** — evidência antes da conclusão.
