# FinSight — Financial Due Diligence Agent

Ferramenta sob medida de análise financeira, em desenvolvimento. **Não é SaaS**.

## Escopo
- Análise individual: desempenho, riscos, fluxo de caixa e evidências.
- Comparação setorial: indicadores equivalentes com benchmarks.
- Análise multissetorial: proíbe comparações diretas de métricas incompatíveis.

## Princípio
**A IA interpreta; o código calcula; as fontes comprovam.** O modelo não calcula nem fabrica indicadores.

## Status
Fundação inicial do backend. Não há RAG em produção, conectores CVM/B3, interface ou relatórios verificados. Exemplos são fictícios.

## Executar
```sh
python -m venv .venv
pip install -r backend/requirements.txt
uvicorn app.main:app --app-dir backend --reload
pytest backend/tests
```

API de desenvolvimento em `http://127.0.0.1:8000/docs`. Nenhum endpoint aceita documentos confidenciais nesta fase.

## Segurança
Sem URLs arbitrárias, uploads ou acesso à internet pelo backend inicial. Evite inserir informações pessoais ou sigilosas. Veja `docs/SECURITY.md`.

## Licença
Nenhuma licença de redistribuição declarada.
