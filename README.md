# MedSync — Sistema de Triagem e Agendamento Médico (AT2 - QTS)

Aplicação web desenvolvida em **Python 3.12+**, **FastAPI** e **Pydantic v2** para a **Atividade Avaliativa AT2** da disciplina de **Qualidade e Teste de Software (QTS)**, contemplando os níveis intermediário e superior da Pirâmide de Testes e os requisitos não funcionais da **ISO/IEC 25010**:

- **Testes de Integração (`@pytest.mark.integration`):** `TestClient`, padrão **AAA**, `@pytest.fixture` com setup e teardown via `yield`, isolamento de serviço externo com **Mocks (`pytest-mock` / `mocker.patch`)** e massa sintética com **`Faker("pt_BR")`** no padrão **Factory**.
- **Testes End-to-End (`@pytest.mark.e2e`):** **Playwright (`pytest-playwright`)**, padrão **Page Object Model (POM)** e seletores semânticos (`get_by_role`, `get_by_label`, `get_by_text`).
- **Auditoria de Acessibilidade (`@pytest.mark.accessibility`):** Conformidade **WCAG 2.1 Nível AA** automatizada com **Axe-core (`axe-playwright-python`)** e validação de navegação sequencial por teclado (`Tab` + `expect(...).to_be_focused()`).
- **Testes de Carga e Performance:** Simulação de múltiplos usuários concorrentes com **Locust (`locustfile.py`)**.

---

## 1. Estrutura do Repositório

```text
qts-integration_test/
├── app/
│   ├── __init__.py
│   ├── main.py                  # Aplicação FastAPI (Rotas REST + Interface HTML WCAG 2.1 AA)
│   ├── schemas.py               # Contratos e validações com Pydantic v2
│   └── services.py              # Repositório em memória e cliente externo (InsuranceGateway)
├── tests/
│   ├── pages/
│   │   ├── __init__.py
│   │   └── appointment_page.py  # Page Object Model (POM) com seletores semânticos
│   ├── __init__.py
│   ├── conftest.py              # Fixtures com setup e teardown via yield + servidor live E2E
│   ├── factories.py             # Padrão Factory com Faker("pt_BR")
│   ├── test_integration.py      # Testes de integração (TestClient, Mocks, Fixtures e Faker)
│   └── test_e2e_accessibility.py# Testes E2E (Playwright/POM) e Acessibilidade (Axe-core/Tab)
├── .cursorrules                 # Regras de contexto para IA (Cursor)
├── AGENTS.md                    # Governança e diretrizes arquiteturais para Agentes de IA
├── AI_USAGE.md                  # Relatório detalhado de transparência e auditoria de IA
├── PRD.md                       # Especificação do produto, rotas, UI e requisitos ISO/IEC 25010
├── locustfile.py                # Script de teste de carga com Locust (HttpUser e @task)
├── pyproject.toml               # Gerenciamento de dependências e marcadores pytest via uv
└── README.md                    # Documentação geral, métricas de carga e instruções
```

---

## 2. Pré-requisitos e Execução via `uv`

### 2.1. Instalar dependências e navegador do Playwright
```bash
uv sync
uv run playwright install chromium
```

### 2.2. Executar a Aplicação Web (SUT)
```bash
uv run uvicorn app.main:app --reload
```
Acesse no navegador: `http://127.0.0.1:8000` (Documentação interativa OpenAPI em `http://127.0.0.1:8000/docs`).

### 2.3. Executar a Suíte Completa de Testes (Integração + E2E + Acessibilidade)
> A fixture `live_server_url` em `tests/conftest.py` sobe automaticamente o servidor FastAPI em background durante a execução dos testes E2E e de Acessibilidade.

```bash
uv run pytest -v
```

Para executar por categoria (markers):
```bash
uv run pytest -m integration -v
uv run pytest -m e2e -v
uv run pytest -m accessibility -v
```

### 2.4. Executar os Testes de Carga com Locust
> O arquivo `locustfile.py` verifica automaticamente se o servidor FastAPI está rodando na porta `8000` e, caso não esteja, inicia uma instância em background automaticamente.

**Modo Interface Web do Locust (`http://localhost:8089`):**
```bash
uv run locust
```

**Modo Terminal (Headless — 30 usuários concorrentes por 10 segundos):**
```bash
uv run locust --headless -u 30 -r 10 -t 10s --only-summary
```

---

## 3. Métricas Obtidas no Teste de Carga (Locust)

Cenário avaliado: **30 usuários simultâneos** (`-u 30`), taxa de entrada de **10 usuários/s** (`-r 10`) durante **10 segundos** (`-t 10s`), exercitando os fluxos `GET /`, `GET /api/appointments`, `POST /api/appointments` (com massa sintética `Faker("pt_BR")`) e `GET /health`.

| Tipo | Endpoint / Fluxo | Total Reqs | Falhas (%) | Tempo Médio (ms) | Mediana p50 (ms) | **Percentil p95 (ms)** | **RPS (`req/s`)** |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| `GET` | `GET / (Interface Web)` | 170 | `0 (0.00%)` | 4 ms | 2 ms | **14 ms** | `17.04` |
| `GET` | `GET /api/appointments` | 207 | `0 (0.00%)` | 4 ms | 3 ms | **5 ms** | `20.75` |
| `POST` | `POST /api/appointments` | 119 | `0 (0.00%)` | 6 ms | 3 ms | **17 ms** | `11.93` |
| `GET` | `GET /health` | 56 | `0 (0.00%)` | 7 ms | 2 ms | **16 ms** | `5.61` |
| **Total** | **Agregado Geral** | **552** | **`0 (0.00%)`** | **5 ms** | **2 ms** | **14 ms** | **`55.32 req/s`** |

### Análise frente à ISO/IEC 25010 (Eficiência de Desempenho)
- **Capacidade / Throughput (RPS):** A aplicação sustentou **55,32 requisições por segundo** em ambiente local sem degradação.
- **Comportamento Temporal (p95):** O percentil 95 global ficou em **14 ms** (bem abaixo do limite de 200 ms especificado no `PRD.md`).
- **Confiabilidade sob Carga (Taxa de Falhas):** **0,00% de falhas** em 552 requisições concorrentes.

---

## 4. Relatório Resumido de Transparência de IA

> O relatório completo encontra-se no arquivo [`AI_USAGE.md`](./AI_USAGE.md).

- **Ferramenta Utilizada:** Antigravity (Google DeepMind Coding Agent).
- **Governança Aplicada:** Regras de contexto definidas em [`PRD.md`](./PRD.md), [`AGENTS.md`](./AGENTS.md) e [`.cursorrules`](./.cursorrules).
- **Escopo de Uso:** Auxílio na estruturação do SUT em FastAPI/Pydantic, geração da `AppointmentFactory` com `Faker("pt_BR")`, modelagem do Page Object (`AppointmentPage`) e configuração da suíte Playwright + Axe-core + Locust.
- **Auditoria Realizada:** Revisão humana e validação empírica do isolamento de estado (`yield` nas fixtures), confirmação das asserções de chamadas nos mocks (`assert_called_once_with`), verificação de `0` violações WCAG 2.1 AA no relatório do Axe-core e coleta real das métricas do Locust no terminal.
