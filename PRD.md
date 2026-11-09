# PRD — Product Requirements Document
## MedSync: Sistema de Triagem e Agendamento de Consultas Médicas

**Versão:** 1.0.0  
**Disciplina:** Qualidade e Teste de Software (QTS) — Atividade Avaliativa AT2  
**Normas de Referência:** ISO/IEC 25010 (Qualidade de Produto de Software) e W3C WCAG 2.1 Nível AA  

---

## 1. Visão Geral do Produto e Domínio
O **MedSync** é uma aplicação web desenvolvida em **Python 3.12+**, **FastAPI** e **Pydantic** destinada ao agendamento de consultas médicas ambulatoriais com validação automática de elegibilidade junto a um **Gateway Externo de Convênio Médico** (`InsuranceGateway`).

O sistema resolve o problema de agendamentos inconsistentes ao validar dados cadastrais rigorosos (CPF, e-mail, especialidade, data e número da carteirinha) antes de consultar a cobertura do paciente no serviço externo e emitir o protocolo de autorização.

---

## 2. Especificação das Rotas da API (SUT)

| Método | Rota | Status Esperado | Descrição e Regras de Negócio |
| :--- | :--- | :--- | :--- |
| `GET` | `/` | `200 OK` | Renderiza a interface web HTML5 semântica e acessível (WCAG 2.1 AA) contendo o formulário de agendamento e a tabela de consultas. |
| `GET` | `/health` | `200 OK` | Endpoint de *healthcheck* retornando `{"status": "healthy", "service": "MedSync API"}`. |
| `POST` | `/api/appointments` | `201 Created` / `403` / `422` / `503` | Valida o payload via Pydantic (`AppointmentCreate`), consulta o serviço externo `InsuranceGateway.verify_coverage(cpf, insurance_card)` e registra o agendamento com protocolo de autorização. |
| `GET` | `/api/appointments` | `200 OK` | Lista todos os agendamentos confirmados no repositório (`list[AppointmentResponse]`). |
| `GET` | `/api/appointments/{id}` | `200 OK` / `404 Not Found` | Retorna os detalhes de um agendamento específico pelo seu identificador único. |
| `DELETE` | `/api/appointments/{id}` | `204 No Content` / `404 Not Found` | Cancela e remove um agendamento existente pelo seu identificador único. |

### 2.1 Contrato de Dados (Pydantic — `AppointmentCreate`)
- `patient_name` (`str`): Nome completo do paciente (3 a 100 caracteres, sem espaços supérfluos).
- `cpf` (`str`): CPF contendo exatamente 11 dígitos numéricos após higienização.
- `email` (`EmailStr`): Endereço de e-mail válido do paciente.
- `specialty` (`Literal`): Especialidade médica permitida (`Cardiologia`, `Dermatologia`, `Ortopedia`, `Clínica Geral`, `Pediatria`).
- `appointment_date` (`date`): Data da consulta no formato ISO `YYYY-MM-DD`.
- `insurance_card` (`str`): Código da carteirinha do convênio (5 a 20 caracteres, normalizado em maiúsculas).

---

## 3. Especificação da Interface Web (UI)
A interface web (`GET /`) foi projetada em página única responsiva com duas seções semânticas principais dentro de `<main role="main">`:

1. **Seção "Novo Agendamento" (`<section aria-labelledby="form-heading">`)**:
   - Campos de formulário com `<label for="...">` explicitamente vinculados aos respectivos elementos `<input>` e `<select>`:
     - **Nome Completo do Paciente** (`#patient-name`)
     - **CPF (somente números)** (`#cpf`)
     - **E-mail do Paciente** (`#email`)
     - **Especialidade Médica** (`#specialty`)
     - **Data da Consulta** (`#appointment-date`)
     - **Número da Carteirinha do Convênio** (`#insurance-card`)
   - Botões de ação com papéis semânticos claros:
     - `Confirmar Agendamento` (`type="submit"`)
     - `Limpar Formulário` (`type="reset"`)
   - Região dinâmica de feedback (`role="status"` e `aria-live="polite"`) que anuncia confirmações (`201`) ou mensagens de erro (`403`/`422`/`503`) para tecnologias assistivas.

2. **Seção "Consultas Agendadas" (`<section aria-labelledby="list-heading">`)**:
   - Tabela semântica (`<table aria-label="Tabela de Consultas Agendadas">`) com cabeçalhos `<th scope="col">` exibindo Paciente, Especialidade, Data, Protocolo e Status (`CONFIRMADO`).

---

## 4. Requisitos Não Funcionais Avaliados (ISO/IEC 25010)

| Característica ISO/IEC 25010 | Subcaracterística | Requisito e Critério de Aceitação Mensurável | Técnica / Ferramenta de Verificação |
| :--- | :--- | :--- | :--- |
| **Adequação Funcional** | Completude e Correção Funcional | Todas as rotas REST devem validar contratos Pydantic e retornar códigos HTTP exatos (`200`, `201`, `204`, `403`, `404`, `422`, `503`). | Testes de Integração (`pytest`, `TestClient`, padrão AAA, `Faker("pt_BR")`). |
| **Compatibilidade / Confiabilidade** | Interoperabilidade e Tolerância a Falhas | A indisponibilidade ou recusa do serviço externo (`InsuranceGateway`) deve ser tratada graciosamente sem *crash* da aplicação (`403 Forbidden` ou `503 Service Unavailable`). | Isolamento com Mocks (`pytest-mock` / `mocker.patch`) cobrindo sucesso e falha. |
| **Usabilidade** | Acessibilidade (WCAG 2.1 Nível AA) | A interface web deve apresentar **0 violações** nas regras `wcag2a`, `wcag2aa`, `wcag21a` e `wcag21aa`, contraste mínimo > 4.5:1 e navegação completa via teclado (`Tab`). | Playwright + Page Object Model (POM) + `axe-playwright-python` + asserções `to_be_focused()`. |
| **Eficiência de Desempenho** | Comportamento Temporal e Capacidade | Suportar múltiplos usuários simultâneos com taxa de falhas `< 1%` e tempo de resposta no percentil 95 (`p95`) `< 200 ms` em execução local. | Teste de Carga automatizado com **Locust** (`locustfile.py`). |

