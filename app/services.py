import os
import httpx
from app.schemas import AppointmentCreate, AppointmentResponse, InsuranceAuthResult


class ExternalServiceError(Exception):
    """Exceção lançada quando o serviço externo de convênio está indisponível."""


class InsuranceGateway:
    """
    Cliente de integração com serviço externo de validação de convênio médico.
    Em produção consulta uma API externa via HTTP; nos testes de integração é isolado via Mock (mocker.patch).
    """

    BASE_URL = os.getenv("INSURANCE_API_URL", "https://api.convenio-externo.medsync.local")

    def verify_coverage(self, cpf: str, insurance_card: str) -> InsuranceAuthResult:
        """
        Verifica se o paciente possui cobertura ativa no convênio médico externo.
        Caso a variável INSURANCE_LIVE_HTTP esteja ativa, realiza chamada HTTP real via httpx.
        Por padrão, em execução local (E2E / Carga), executa validação determinística rápida.
        """
        if os.getenv("INSURANCE_LIVE_HTTP") == "1":
            try:
                response = httpx.post(
                    f"{self.BASE_URL}/v1/authorizations",
                    json={"cpf": cpf, "insurance_card": insurance_card},
                    timeout=3.0,
                )
                response.raise_for_status()
                data = response.json()
                return InsuranceAuthResult(**data)
            except httpx.HTTPError as exc:
                raise ExternalServiceError(
                    "Falha de comunicação com o gateway externo de convênio."
                ) from exc

        # Comportamento determinístico para execução local (UI E2E e Locust):
        if insurance_card.startswith("NEG"):
            return InsuranceAuthResult(
                authorized=False,
                protocol=None,
                reason="Carteirinha com carência ou bloqueio cadastral no convênio.",
            )

        return InsuranceAuthResult(
            authorized=True,
            protocol=f"AUTH-{cpf[:4]}-{insurance_card[-4:]}",
            reason=None,
        )


class AppointmentRepository:
    """Repositório em memória para armazenamento de agendamentos médicos."""

    def __init__(self) -> None:
        self._items: dict[int, AppointmentResponse] = {}
        self._counter: int = 0

    def create(
        self, payload: AppointmentCreate, protocol: str
    ) -> AppointmentResponse:
        self._counter += 1
        record = AppointmentResponse(
            id=self._counter,
            patient_name=payload.patient_name,
            cpf=payload.cpf,
            email=payload.email,
            specialty=payload.specialty,
            appointment_date=payload.appointment_date,
            insurance_card=payload.insurance_card,
            status="CONFIRMADO",
            authorization_protocol=protocol,
        )
        self._items[record.id] = record
        return record

    def list_all(self) -> list[AppointmentResponse]:
        return list(self._items.values())

    def get_by_id(self, appointment_id: int) -> AppointmentResponse | None:
        return self._items.get(appointment_id)

    def delete(self, appointment_id: int) -> bool:
        if appointment_id in self._items:
            del self._items[appointment_id]
            return True
        return False

    def clear(self) -> None:
        self._items.clear()
        self._counter = 0


repository = AppointmentRepository()
insurance_gateway = InsuranceGateway()

