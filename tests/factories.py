import random
from datetime import date, timedelta
from typing import Any
from faker import Faker

fake = Faker("pt_BR")

SPECIALTIES = [
    "Cardiologia",
    "Dermatologia",
    "Ortopedia",
    "Clínica Geral",
    "Pediatria",
]


class AppointmentFactory:
    """
    Padrão Factory para geração de massa de dados sintéticos realistas
    utilizando Faker configurado para a localidade brasileira ('pt_BR').
    """

    @staticmethod
    def build_payload(**overrides: Any) -> dict[str, Any]:
        """Gera um dicionário válido de payload para criação de agendamento."""
        raw_cpf = "".join(ch for ch in fake.cpf() if ch.isdigit())
        future_days = random.randint(1, 90)
        appointment_date = (date.today() + timedelta(days=future_days)).isoformat()

        payload: dict[str, Any] = {
            "patient_name": fake.name(),
            "cpf": raw_cpf,
            "email": fake.unique.email(),
            "specialty": random.choice(SPECIALTIES),
            "appointment_date": appointment_date,
            "insurance_card": f"CONV-{fake.random_number(digits=6, fix_len=True)}",
        }
        payload.update(overrides)
        return payload

    @classmethod
    def build_batch(cls, count: int, **overrides: Any) -> list[dict[str, Any]]:
        """Gera uma lista de payloads sintéticos para testes em lote."""
        return [cls.build_payload(**overrides) for _ in range(count)]

