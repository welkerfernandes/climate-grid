# Climate Grid

[![CI](https://github.com/welkerfernandes/climate-grid/actions/workflows/ci.yml/badge.svg)](https://github.com/welkerfernandes/climate-grid/actions)

![Dashboard preview](docs/dashboard.png)

Equipes de campo precisam traduzir previsões em critérios operacionais explícitos, sem perder a origem dos dados.

Plataforma executável com dashboard responsivo, API autenticada e integração real com **Open-Meteo**.



## Funcionalidades

Previsão de sete dias por coordenada; limites configuráveis de calor, chuva e vento; estados normal/watch/high/unknown; histórico por workspace; gráfico de temperatura e tabela com unidades; proveniência por consulta.

## Executar

Python 3.12 ou 3.13. Na pasta do projeto:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m uvicorn app.main:app --host 127.0.0.1 --port 8201
```

Linux/macOS: `source .venv/bin/activate`.
Abra http://localhost:8201 e execute a análise.
O modo inicial da interface é **demonstração sintética**. Para consultar a fonte,
selecione **Consultar API pública**. Falhas do provedor são exibidas, sem substituição silenciosa por exemplos.
O contrato OpenAPI está em http://localhost:8201/docs.

Chaves locais: `local-alpha` e `local-beta`. A identidade do workspace é derivada da chave,
nunca de um header arbitrário de tenant. Configure `API_KEYS` antes de exposição externa.

## API

| Método | Rota | Função |
| --- | --- | --- |
| POST | `/api/analyze` | Consultar fonte, analisar e persistir snapshot |
| GET | `/api/history` | Últimos 30 snapshots do workspace |
| DELETE | `/api/history/{id}` | Excluir snapshot próprio |
| GET | `/health` | Liveness do processo |

Operações de negócio exigem `X-API-Key`. Exemplos completos estão na interface e no contrato `/docs`.

```bash
python -m pytest -q
docker build -t climate-grid .
docker run --rm -p 8201:8201 climate-grid
```

O banco no container é efêmero sem volume. Os testes usam banco temporário e transporte HTTP simulado,
sem depender da disponibilidade externa. O workflow testa Python 3.12 e 3.13.

## Arquitetura

```mermaid
flowchart LR
    HTTP --> WeatherAdapter
    WeatherAdapter --> OpenMeteo
    WeatherAdapter --> SchemaValidation
    SchemaValidation --> RiskRules
    RiskRules --> TenantSnapshots
```

O adaptador HTTP tem hosts permitidos, timeout explícito, cache TTL de cinco minutos,
capacidade limitada a 128 entradas e até duas tentativas para timeout/erro de rede ou erro 5xx inicial.
Não segue redirecionamentos nem repete 429. Não entrega cache expirado como se fosse atual.
O cache contém somente respostas públicas e é local ao processo; snapshots são isolados por workspace.

Leia [arquitetura](docs/architecture.md), [metodologia](docs/methodology.md),
[fontes](docs/data-sources.md), [operação](docs/runbook.md) e [segurança](SECURITY.md).

## Limites conhecidos

Dados em UTC, não no fuso local da unidade. Limites são heurísticas de demonstração e não constituem avaliação de segurança, alertas oficiais ou recomendação agronômica. O serviço não faz notificações nem monitora unidades automaticamente.

## Evolução

Separar unidades em entidade persistente, agendar coletas com deduplicação, adicionar alertas aprovados por operador e avaliar limites com histórico real de incidentes.

## Implementação em Go

Motor nativo integrado ao fluxo de análise, com testes próprios. Veja [execução e protocolo](docs/polyglot.md).

## Dashboard React + TypeScript

`web/` contém o frontend tipado, com estado de consulta, histórico e gráficos SVG. Execute `npm ci` e `npm run build` dentro de `web/`; a API servirá o build em `/`. Para desenvolvimento use `npm run dev` com a API ativa. Sem build, a API mantém uma console HTML funcional de apoio.

A imagem Docker compila o frontend e o motor nativo e j? ativa o componente Go/Java/Rust correspondente. O modo Python continua dispon?vel na execu??o local sem NATIVE_ENGINE.

## Verificação em navegador

O job `browser` da CI executa fluxos em Chromium, verifica a versão de 390 px e publica capturas como artifact `dashboard-screenshots`. Execute `npm install` em `ui/`, `npx playwright install chromium` e `node ui/smoke.cjs` na raiz com a API em localhost:8000 para repetir.

Consulte o [registro de validação](docs/validation.md) e a [captura mobile](docs/mobile.png).
