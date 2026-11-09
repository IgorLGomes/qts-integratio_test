# AGENTS.md — Regras de Contexto e Governança para Agentes de IA

## 1. Contexto do Projeto
Este repositório implementa o sistema **MedSync** para a **Atividade Avaliativa AT2** da disciplina de **Qualidade e Teste de Software (QTS)**, contemplando testes de integração, E2E com Playwright, auditoria de acessibilidade com Axe-core e testes de carga com Locust.

## 2. Stack Tecnológica Obrigatória
- **Linguagem:** Python 3.12+
- **Gerenciador de Pacotes e Ambiente:** `uv` (`pyproject.toml`)
- **Backend / SUT:** FastAPI + Pydantic v2 + Uvicorn
- **Testes de Integração:** `pytest`, `fastapi.testclient.TestClient`, `pytest-mock` (`mocker.patch`), `Faker("pt_BR")`
- **Testes E2E e Acessibilidade:** `playwright`, `pytest-playwright`, `axe-playwright-python`
- **Testes de Carga:** `locust` (`HttpUser`, `@task`)

## 3. Diretrizes Arquiteturais e de Qualidade
1. **Padrão AAA (Arrange, Act, Assert):** Todo teste automatizado deve separar claramente as três etapas com comentários `# Arrange`, `# Act` e `# Assert`.
2. **Isolamento de Estado com Fixtures (`yield`):** Nenhuma mutação de estado em memória pode vazar entre testes. Utilize sempre `@pytest.fixture` com setup antes do `yield` e teardown após o `yield`.
3. **Isolamento de Dependências Externas:** Chamadas ao serviço externo (`InsuranceGateway.verify_coverage`) nos testes de integração devem ser isoladas com `mocker.patch`, exercitando obrigatoriamente cenários de sucesso (`201`) e falha (`403` e `503`).
4. **Massa de Dados Sintética:** Proibido usar dados estáticos repetitivos nos testes quando aplicável; utilize `AppointmentFactory` com `Faker("pt_BR")`.
5. **Page Object Model (POM) e Seletores Semânticos:** Nos testes E2E com Playwright, proibido acoplar seletores CSS frágeis nos scripts de teste. Centralize os seletores em `tests/pages/appointment_page.py` usando `get_by_role`, `get_by_label` e `get_by_text`.
6. **Conformidade WCAG 2.1 AA:** Toda alteração de HTML/CSS em `app/main.py` deve manter contraste mínimo de 4.5:1, rótulos explícitos `<label for="...">`, regiões semânticas (`header`, `main`, `footer`) e zero violações no `Axe().run()`.

