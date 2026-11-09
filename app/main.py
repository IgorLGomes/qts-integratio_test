from fastapi import FastAPI, HTTPException, Response, status
from fastapi.responses import HTMLResponse
from app.schemas import AppointmentCreate, AppointmentResponse
from app.services import ExternalServiceError, insurance_gateway, repository

app = FastAPI(
    title="MedSync - Sistema de Agendamento Médico",
    description=(
        "SUT da Atividade Avaliativa AT2 (QTS) com FastAPI, Pydantic, "
        "validação externa de convênio médico e interface web acessível (WCAG 2.1 AA)."
    ),
    version="1.0.0",
)

INDEX_HTML = """<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>MedSync - Agendamento de Consultas Médicas</title>
    <style>
        :root {
            --bg-page: #f8fafc;
            --bg-card: #ffffff;
            --text-primary: #0f172a;
            --text-secondary: #334155;
            --border-color: #94a3b8;
            --primary-btn: #1e3a8a;
            --primary-btn-hover: #172554;
            --secondary-btn: #334155;
            --focus-ring: #1d4ed8;
            --success-bg: #dcfce7;
            --success-text: #14532d;
            --error-bg: #fee2e2;
            --error-text: #7f1d1d;
        }

        * {
            box-sizing: border-box;
        }

        body {
            font-family: system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
            background-color: var(--bg-page);
            color: var(--text-primary);
            margin: 0;
            padding: 0;
            line-height: 1.5;
        }

        header {
            background-color: #0f172a;
            color: #ffffff;
            padding: 1.5rem 2rem;
            border-bottom: 4px solid #1d4ed8;
        }

        header h1 {
            margin: 0;
            font-size: 1.75rem;
        }

        header p {
            margin: 0.4rem 0 0;
            color: #e2e8f0;
            font-size: 1rem;
        }

        main {
            max-width: 1080px;
            margin: 2rem auto;
            padding: 0 1.5rem;
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 2rem;
        }

        @media (max-width: 820px) {
            main {
                grid-template-columns: 1fr;
            }
        }

        section {
            background: var(--bg-card);
            border: 1px solid #cbd5e1;
            border-radius: 8px;
            padding: 1.5rem;
            box-shadow: 0 1px 3px rgba(15, 23, 42, 0.08);
        }

        h2 {
            margin-top: 0;
            font-size: 1.35rem;
            color: var(--text-primary);
            border-bottom: 2px solid #e2e8f0;
            padding-bottom: 0.5rem;
        }

        .form-group {
            margin-bottom: 1rem;
        }

        label {
            display: block;
            font-weight: 600;
            margin-bottom: 0.35rem;
            color: var(--text-primary);
        }

        input, select {
            width: 100%;
            padding: 0.65rem 0.75rem;
            font-size: 1rem;
            color: var(--text-primary);
            background-color: #ffffff;
            border: 2px solid #475569;
            border-radius: 6px;
        }

        input:focus-visible,
        select:focus-visible,
        button:focus-visible {
            outline: 3px solid var(--focus-ring);
            outline-offset: 2px;
        }

        .actions {
            display: flex;
            gap: 0.75rem;
            margin-top: 1.25rem;
        }

        button {
            cursor: pointer;
            font-size: 1rem;
            font-weight: 600;
            padding: 0.7rem 1.2rem;
            border-radius: 6px;
            border: none;
        }

        .btn-primary {
            background-color: var(--primary-btn);
            color: #ffffff;
        }

        .btn-primary:hover {
            background-color: var(--primary-btn-hover);
        }

        .btn-secondary {
            background-color: #e2e8f0;
            color: #0f172a;
            border: 2px solid #475569;
        }

        #feedback-banner {
            margin-top: 1rem;
            padding: 0.85rem 1rem;
            border-radius: 6px;
            font-weight: 600;
            display: none;
        }

        #feedback-banner.success {
            display: block;
            background-color: var(--success-bg);
            color: var(--success-text);
            border: 2px solid #15803d;
        }

        #feedback-banner.error {
            display: block;
            background-color: var(--error-bg);
            color: var(--error-text);
            border: 2px solid #b91c1c;
        }

        table {
            width: 100%;
            border-collapse: collapse;
            margin-top: 0.75rem;
        }

        th, td {
            text-align: left;
            padding: 0.65rem 0.5rem;
            border-bottom: 1px solid #cbd5e1;
            font-size: 0.92rem;
        }

        th {
            background-color: #f1f5f9;
            color: var(--text-primary);
            font-weight: 700;
        }

        .badge {
            display: inline-block;
            padding: 0.2rem 0.55rem;
            border-radius: 4px;
            font-weight: 700;
            font-size: 0.8rem;
            background-color: var(--success-bg);
            color: var(--success-text);
        }

        footer {
            max-width: 1080px;
            margin: 2rem auto;
            padding: 1rem 1.5rem;
            color: var(--text-secondary);
            font-size: 0.9rem;
            border-top: 1px solid #cbd5e1;
            text-align: center;
        }
    </style>
</head>
<body>
    <header role="banner">
        <h1>MedSync — Triagem e Agendamento Médico</h1>
        <p>Sistema de Agendamento com Validação de Convênio e Conformidade WCAG 2.1 AA</p>
    </header>

    <main role="main">
        <section aria-labelledby="form-heading">
            <h2 id="form-heading">Novo Agendamento</h2>
            <form id="appointment-form" novalidate>
                <div class="form-group">
                    <label for="patient-name">Nome Completo do Paciente</label>
                    <input
                        id="patient-name"
                        name="patient_name"
                        type="text"
                        required
                        autocomplete="name"
                        placeholder="Ex.: Maria Aparecida Silva"
                    />
                </div>

                <div class="form-group">
                    <label for="cpf">CPF (somente números)</label>
                    <input
                        id="cpf"
                        name="cpf"
                        type="text"
                        inputmode="numeric"
                        maxlength="14"
                        required
                        placeholder="Ex.: 12345678901"
                    />
                </div>

                <div class="form-group">
                    <label for="email">E-mail do Paciente</label>
                    <input
                        id="email"
                        name="email"
                        type="email"
                        required
                        autocomplete="email"
                        placeholder="Ex.: maria.silva@exemplo.com.br"
                    />
                </div>

                <div class="form-group">
                    <label for="specialty">Especialidade Médica</label>
                    <select id="specialty" name="specialty" required>
                        <option value="Cardiologia">Cardiologia</option>
                        <option value="Dermatologia">Dermatologia</option>
                        <option value="Ortopedia">Ortopedia</option>
                        <option value="Clínica Geral">Clínica Geral</option>
                        <option value="Pediatria">Pediatria</option>
                    </select>
                </div>

                <div class="form-group">
                    <label for="appointment-date">Data da Consulta</label>
                    <input
                        id="appointment-date"
                        name="appointment_date"
                        type="text"
                        required
                        value="2026-12-15"
                        placeholder="Ex.: 2026-12-15"
                    />
                </div>

                <div class="form-group">
                    <label for="insurance-card">Número da Carteirinha do Convênio</label>
                    <input
                        id="insurance-card"
                        name="insurance_card"
                        type="text"
                        required
                        placeholder="Ex.: CONV-998877"
                    />
                </div>

                <div class="actions">
                    <button type="submit" class="btn-primary">Confirmar Agendamento</button>
                    <button type="reset" id="reset-btn" class="btn-secondary">Limpar Formulário</button>
                </div>
            </form>

            <div id="feedback-banner" role="status" aria-live="polite"></div>
        </section>

        <section aria-labelledby="list-heading">
            <h2 id="list-heading">Consultas Agendadas</h2>
            <p id="empty-state">Nenhum agendamento registrado até o momento.</p>
            <table id="appointments-table" aria-label="Tabela de Consultas Agendadas">
                <thead>
                    <tr>
                        <th scope="col">Paciente</th>
                        <th scope="col">Especialidade</th>
                        <th scope="col">Data</th>
                        <th scope="col">Protocolo</th>
                        <th scope="col">Status</th>
                    </tr>
                </thead>
                <tbody id="appointments-body"></tbody>
            </table>
        </section>
    </main>

    <footer role="contentinfo">
        <p>MedSync v1.0.0 — Qualidade e Teste de Software (QTS) — ISO/IEC 25010 &amp; WCAG 2.1 AA</p>
    </footer>

    <script>
        const form = document.getElementById("appointment-form");
        const banner = document.getElementById("feedback-banner");
        const tableBody = document.getElementById("appointments-body");
        const emptyState = document.getElementById("empty-state");

        function showFeedback(message, type) {
            banner.textContent = message;
            banner.className = type;
        }

        async function loadAppointments() {
            try {
                const res = await fetch("/api/appointments");
                if (!res.ok) return;
                const items = await res.json();
                tableBody.innerHTML = "";
                if (items.length === 0) {
                    emptyState.style.display = "block";
                    return;
                }
                emptyState.style.display = "none";
                for (const item of items) {
                    const tr = document.createElement("tr");
                    tr.innerHTML = `
                        <td>${item.patient_name}</td>
                        <td>${item.specialty}</td>
                        <td>${item.appointment_date}</td>
                        <td>${item.authorization_protocol}</td>
                        <td><span class="badge">${item.status}</span></td>
                    `;
                    tableBody.appendChild(tr);
                }
            } catch (err) {
                console.error("Erro ao carregar agendamentos:", err);
            }
        }

        form.addEventListener("submit", async (event) => {
            event.preventDefault();
            const payload = {
                patient_name: document.getElementById("patient-name").value,
                cpf: document.getElementById("cpf").value,
                email: document.getElementById("email").value,
                specialty: document.getElementById("specialty").value,
                appointment_date: document.getElementById("appointment-date").value,
                insurance_card: document.getElementById("insurance-card").value,
            };

            try {
                const response = await fetch("/api/appointments", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify(payload),
                });

                const data = await response.json();
                if (response.status === 201) {
                    form.reset();
                    document.getElementById("appointment-date").value = "2026-12-15";
                    showFeedback(
                        `Agendamento confirmado para ${data.patient_name}! Protocolo: ${data.authorization_protocol}`,
                        "success"
                    );
                    await loadAppointments();
                } else {
                    const detail = typeof data.detail === "string"
                        ? data.detail
                        : "Dados inválidos no formulário. Verifique os campos preenchidos.";
                    showFeedback(`Erro no agendamento: ${detail}`, "error");
                }
            } catch (error) {
                showFeedback("Erro de comunicação com o servidor.", "error");
            }
        });

        document.getElementById("reset-btn").addEventListener("click", () => {
            banner.className = "";
            banner.textContent = "";
        });

        loadAppointments();
    </script>
</body>
</html>
"""


@app.get("/", response_class=HTMLResponse, summary="Interface Web de Agendamento")
def read_index() -> HTMLResponse:
    """Retorna a página HTML principal acessível (WCAG 2.1 AA)."""
    return HTMLResponse(content=INDEX_HTML, status_code=status.HTTP_200_OK)


@app.get("/health", summary="Healthcheck do Serviço")
def health_check() -> dict[str, str]:
    """Verifica a disponibilidade operacional da API."""
    return {"status": "healthy", "service": "MedSync API"}


@app.post(
    "/api/appointments",
    response_model=AppointmentResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Criar novo agendamento médico",
)
def create_appointment(payload: AppointmentCreate) -> AppointmentResponse:
    """
    Valida os dados com Pydantic, consulta o serviço externo de convênio médico
    e registra o agendamento em caso de autorização positiva.
    """
    try:
        auth_result = insurance_gateway.verify_coverage(
            cpf=payload.cpf,
            insurance_card=payload.insurance_card,
        )
    except ExternalServiceError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(exc),
        ) from exc

    if not auth_result.authorized:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=auth_result.reason or "Cobertura negada pelo convênio médico.",
        )

    protocol = auth_result.protocol or "AUTH-DEFAULT"
    return repository.create(payload=payload, protocol=protocol)


@app.get(
    "/api/appointments",
    response_model=list[AppointmentResponse],
    status_code=status.HTTP_200_OK,
    summary="Listar agendamentos",
)
def list_appointments() -> list[AppointmentResponse]:
    """Retorna todos os agendamentos cadastrados."""
    return repository.list_all()


@app.get(
    "/api/appointments/{appointment_id}",
    response_model=AppointmentResponse,
    status_code=status.HTTP_200_OK,
    summary="Buscar agendamento por ID",
)
def get_appointment(appointment_id: int) -> AppointmentResponse:
    """Busca os detalhes de um agendamento específico pelo ID."""
    record = repository.get_by_id(appointment_id)
    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Agendamento não encontrado.",
        )
    return record


@app.delete(
    "/api/appointments/{appointment_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Cancelar agendamento",
)
def delete_appointment(appointment_id: int) -> Response:
    """Remove um agendamento existente pelo ID."""
    deleted = repository.delete(appointment_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Agendamento não encontrado para exclusão.",
        )
    return Response(status_code=status.HTTP_204_NO_CONTENT)

