import atexit
import random
import socket
import subprocess
import sys
import time
from datetime import date, timedelta
from typing import Any
from faker import Faker
from locust import HttpUser, between, events, task

fake = Faker("pt_BR")
SPECIALTIES = [
    "Cardiologia",
    "Dermatologia",
    "Ortopedia",
    "Clínica Geral",
    "Pediatria",
]

_server_proc: subprocess.Popen[Any] | None = None


def _is_port_open(host: str, port: int) -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.settimeout(0.5)
        return sock.connect_ex((host, port)) == 0


@events.init.add_listener
def _ensure_sut_running(environment: Any, **kwargs: Any) -> None:
    """
    Garante que o servidor FastAPI (SUT) esteja ativo na porta 8000
    caso o usuário execute 'uv run locust' sem iniciar o Uvicorn separadamente.
    """
    global _server_proc
    if not _is_port_open("127.0.0.1", 8000):
        _server_proc = subprocess.Popen(
            [
                sys.executable,
                "-m",
                "uvicorn",
                "app.main:app",
                "--host",
                "127.0.0.1",
                "--port",
                "8000",
                "--log-level",
                "error",
            ],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        atexit.register(lambda: _server_proc.terminate() if _server_proc else None)
        deadline = time.time() + 10.0
        while not _is_port_open("127.0.0.1", 8000) and time.time() < deadline:
            time.sleep(0.1)


class MedSyncUser(HttpUser):
    """
    Usuário virtual do Locust simulando múltiplos acessos concorrentes
    aos fluxos de interface web e endpoints REST da API MedSync.
    """

    wait_time = between(0.2, 0.8)
    host = "http://127.0.0.1:8000"

    @task(3)
    def view_home_page(self) -> None:
        """Simula o carregamento da página principal HTML."""
        self.client.get("/", name="GET / (Interface Web)")

    @task(4)
    def list_appointments(self) -> None:
        """Simula a listagem de consultas médicas agendadas."""
        self.client.get("/api/appointments", name="GET /api/appointments")

    @task(2)
    def create_appointment(self) -> None:
        """Simula o envio de um novo agendamento com dados sintéticos Faker pt_BR."""
        raw_cpf = "".join(ch for ch in fake.cpf() if ch.isdigit())
        payload = {
            "patient_name": fake.name(),
            "cpf": raw_cpf,
            "email": fake.email(),
            "specialty": random.choice(SPECIALTIES),
            "appointment_date": (
                date.today() + timedelta(days=random.randint(1, 60))
            ).isoformat(),
            "insurance_card": f"CONV-{fake.random_number(digits=6, fix_len=True)}",
        }
        self.client.post(
            "/api/appointments",
            json=payload,
            name="POST /api/appointments",
        )

    @task(1)
    def health_check(self) -> None:
        """Simula a verificação de disponibilidade (healthcheck)."""
        self.client.get("/health", name="GET /health")
