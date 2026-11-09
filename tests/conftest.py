import socket
import threading
import time
from collections.abc import Generator
import pytest
import uvicorn
from fastapi.testclient import TestClient
from app.main import app
from app.services import repository


@pytest.fixture(autouse=True)
def clean_repository() -> Generator[None, None, None]:
    """
    Fixture com Setup e Teardown via yield para garantir isolamento total
    do estado em memória antes e depois de cada teste executado.
    """
    # Setup: limpa o repositório antes do teste iniciar
    repository.clear()
    yield
    # Teardown: limpa o repositório após o término do teste
    repository.clear()


@pytest.fixture
def client() -> Generator[TestClient, None, None]:
    """
    Fixture que instancia o TestClient do FastAPI com ciclo de vida gerenciado
    via yield (Setup e Teardown).
    """
    # Setup: inicializa o contexto do TestClient
    with TestClient(app) as test_client:
        yield test_client
    # Teardown: encerramento automático do contexto do cliente e limpeza


def _get_free_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind(("127.0.0.1", 0))
        return int(sock.getsockname()[1])


@pytest.fixture(scope="session")
def live_server_url() -> Generator[str, None, None]:
    """
    Fixture de sessão (com Setup e Teardown via yield) que inicia um servidor
    Uvicorn real em background para os testes E2E e de Acessibilidade com Playwright.
    """
    port = _get_free_port()
    config = uvicorn.Config(app, host="127.0.0.1", port=port, log_level="warning")
    server = uvicorn.Server(config)

    thread = threading.Thread(target=server.run, daemon=True)
    thread.start()

    # Aguarda o servidor estar pronto para conexões
    deadline = time.time() + 10.0
    while not server.started and time.time() < deadline:
        time.sleep(0.05)

    yield f"http://127.0.0.1:{port}"

    # Teardown: sinaliza parada limpa do servidor Uvicorn
    server.should_exit = True
    thread.join(timeout=5.0)

