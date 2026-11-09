# Relatório de Transparência e Governança de Uso de IA (`AI_USAGE.md`)

## 1. Identificação da Ferramenta Utilizada
- **Ferramenta / Assistente:** Antigravity (Google DeepMind Coding Agent)
- **Arquivos de Governança e Contexto Aplicados:** `PRD.md`, `AGENTS.md` e `.cursorrules`
- **Escopo da Atividade:** AT2 — Testes de Integração, E2E com Playwright, Acessibilidade (Axe-core) e Carga (Locust)

---

## 2. Como a IA foi Utilizada no Desenvolvimento
A Inteligência Artificial foi utilizada como par de programação (*pair programming*) sob governança estrita definida nos arquivos `PRD.md`, `AGENTS.md` e `.cursorrules`, atuando nas seguintes frentes:

1. **Estruturação do SUT (FastAPI + Pydantic + UI HTML):**
   - Apoio na criação dos schemas Pydantic (`app/schemas.py`) com validadores de CPF, nome e carteirinha de convênio.
   - Construção da página HTML semântica em `app/main.py` seguindo os critérios de contraste e marcação exigidos pela norma **WCAG 2.1 Nível AA**.
2. **Elaboração da Suíte de Testes de Integração (`tests/test_integration.py`):**
   - Implementação da `AppointmentFactory` com `Faker("pt_BR")` em `tests/factories.py`.
   - Estruturação das fixtures com ciclo de setup/teardown via `yield` em `tests/conftest.py`.
   - Criação dos testes com `mocker.patch` isolando o `InsuranceGateway.verify_coverage` em cenários de sucesso (`201`), negativa de cobertura (`403`) e indisponibilidade externa (`503`).
3. **Testes E2E, Page Object Model e Acessibilidade (`tests/test_e2e_accessibility.py`):**
   - Modelagem da classe `AppointmentPage` (`tests/pages/appointment_page.py`) com seletores semânticos (`get_by_role`, `get_by_label`, `get_by_text`).
   - Integração do `axe-playwright-python` para auditoria automatizada WCAG 2.1 AA e script de verificação de foco por teclado (`Tab` + `to_be_focused()`).
4. **Script de Teste de Carga (`locustfile.py`):**
   - Configuração da classe `MedSyncUser(HttpUser)` com tarefas ponderadas (`@task`) e geração dinâmica de payloads com `Faker("pt_BR")`.

---

## 3. Processo de Auditoria Humana e Validação Técnica
Todo código sugerido ou gerado com auxílio da IA passou por auditoria e verificação prática antes da consolidação no repositório:

1. **Auditoria de Isolamento de Testes:**
   - Foi verificado que a fixture `clean_repository` (em `tests/conftest.py`) executa `repository.clear()` antes e após o `yield`, impedindo que dados criados em um teste afetem testes subsequentes.
2. **Auditoria dos Mocks (`pytest-mock`):**
   - Foi validado que `mocker.patch("app.main.insurance_gateway.verify_coverage", ...)` intercepta de fato a chamada ao gateway externo e que `assert_called_once_with(...)` confirma os parâmetros exatos enviados pela rota FastAPI.
3. **Auditoria de Acessibilidade Real no Navegador (Axe-core + Teclado):**
   - A página HTML foi auditada diretamente no Chromium via Playwright + `axe-playwright-python` filtrando pelas tags `["wcag2a", "wcag2aa", "wcag21a", "wcag21aa"]`, comprovando `violations_count == 0`.
   - A ordem de tabulação foi testada passo a passo pressionando `Tab` desde o primeiro campo até o último botão do formulário.
4. **Auditoria de Carga e Desempenho (Locust):**
   - Os testes de carga foram executados contra a instância real do servidor Uvicorn/FastAPI, coletando métricas verídicas de RPS, latência p95 e taxa de erro documentadas no `README.md`.

