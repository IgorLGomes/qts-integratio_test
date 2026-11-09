from datetime import date
from typing import Literal
from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator


SpecialtyType = Literal[
    "Cardiologia",
    "Dermatologia",
    "Ortopedia",
    "Clínica Geral",
    "Pediatria",
]


class AppointmentCreate(BaseModel):
    """Schema Pydantic de entrada para criação de agendamento médico."""

    patient_name: str = Field(
        ...,
        min_length=3,
        max_length=100,
        description="Nome completo do paciente",
    )
    cpf: str = Field(
        ...,
        description="CPF do paciente (11 dígitos numéricos ou formato XXX.XXX.XXX-XX)",
    )
    email: EmailStr = Field(
        ...,
        description="E-mail de contato do paciente",
    )
    specialty: SpecialtyType = Field(
        ...,
        description="Especialidade médica desejada",
    )
    appointment_date: date = Field(
        ...,
        description="Data do agendamento (YYYY-MM-DD)",
    )
    insurance_card: str = Field(
        ...,
        min_length=5,
        max_length=20,
        description="Número da carteirinha do convênio médico",
    )

    @field_validator("patient_name")
    @classmethod
    def validate_patient_name(cls, value: str) -> str:
        cleaned = " ".join(value.strip().split())
        if len(cleaned) < 3:
            raise ValueError("O nome do paciente deve ter pelo menos 3 caracteres válidos.")
        return cleaned

    @field_validator("cpf")
    @classmethod
    def validate_cpf(cls, value: str) -> str:
        digits = "".join(ch for ch in value if ch.isdigit())
        if len(digits) != 11:
            raise ValueError("O CPF deve conter exatamente 11 dígitos numéricos.")
        return digits

    @field_validator("insurance_card")
    @classmethod
    def validate_insurance_card(cls, value: str) -> str:
        cleaned = value.strip().upper()
        if len(cleaned) < 5:
            raise ValueError("O número da carteirinha deve ter pelo menos 5 caracteres.")
        return cleaned


class InsuranceAuthResult(BaseModel):
    """Resultado retornado pelo Gateway Externo de Convênio Médico."""

    authorized: bool
    protocol: str | None = None
    reason: str | None = None


class AppointmentResponse(BaseModel):
    """Schema Pydantic de saída para agendamento confirmado."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    patient_name: str
    cpf: str
    email: EmailStr
    specialty: SpecialtyType
    appointment_date: date
    insurance_card: str
    status: str
    authorization_protocol: str

