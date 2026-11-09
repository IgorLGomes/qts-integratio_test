import pytest
from fastapi.testclient import TestClient
from pytest_mock import MockerFixture
from app.schemas import InsuranceAuthResult
from app.services import ExternalServiceError
from tests.factories import AppointmentFactory


@pytest.mark.integration
def test_health_check_returns_200(client: TestClient) -> None:
    # Arrange
    endpoint = "/health"

    # Act
    response = client.get(endpoint)

    # Assert
    assert response.status_code == 200
    assert response.json() == {"status": "healthy", "service": "MedSync API"}


@pytest.mark.integration
def test_create_appointment_success_with_mocked_gateway(
    client: TestClient, mocker: MockerFixture
) -> None:
    # Arrange
    payload = AppointmentFactory.build_payload(specialty="Cardiologia")
    mock_verify = mocker.patch(
        "app.main.insurance_gateway.verify_coverage",
        return_value=InsuranceAuthResult(
            authorized=True,
            protocol="AUTH-MOCK-9001",
            reason=None,
        ),
    )

    # Act
    response = client.post("/api/appointments", json=payload)

    # Assert
    assert response.status_code == 201
    data = response.json()
    assert data["id"] == 1
    assert data["patient_name"] == payload["patient_name"]
    assert data["cpf"] == payload["cpf"]
    assert data["specialty"] == "Cardiologia"
    assert data["status"] == "CONFIRMADO"
    assert data["authorization_protocol"] == "AUTH-MOCK-9001"
    mock_verify.assert_called_once_with(
        cpf=payload["cpf"],
        insurance_card=payload["insurance_card"],
    )


@pytest.mark.integration
def test_create_appointment_denied_by_external_gateway(
    client: TestClient, mocker: MockerFixture
) -> None:
    # Arrange
    payload = AppointmentFactory.build_payload()
    mock_verify = mocker.patch(
        "app.main.insurance_gateway.verify_coverage",
        return_value=InsuranceAuthResult(
            authorized=False,
            protocol=None,
            reason="Plano em período de carência contratual.",
        ),
    )

    # Act
    response = client.post("/api/appointments", json=payload)

    # Assert
    assert response.status_code == 403
    assert response.json()["detail"] == "Plano em período de carência contratual."
    mock_verify.assert_called_once()


@pytest.mark.integration
def test_create_appointment_external_gateway_unavailable_returns_503(
    client: TestClient, mocker: MockerFixture
) -> None:
    # Arrange
    payload = AppointmentFactory.build_payload()
    mocker.patch(
        "app.main.insurance_gateway.verify_coverage",
        side_effect=ExternalServiceError(
            "Timeout ao conectar com o gateway externo de convênio."
        ),
    )

    # Act
    response = client.post("/api/appointments", json=payload)

    # Assert
    assert response.status_code == 503
    assert "Timeout ao conectar" in response.json()["detail"]


@pytest.mark.integration
def test_create_appointment_invalid_cpf_returns_422(client: TestClient) -> None:
    # Arrange
    invalid_payload = AppointmentFactory.build_payload(cpf="12345")

    # Act
    response = client.post("/api/appointments", json=invalid_payload)

    # Assert
    assert response.status_code == 422
    errors = response.json()["detail"]
    assert any("CPF" in err["msg"] for err in errors)


@pytest.mark.integration
def test_list_and_delete_appointments_flow(
    client: TestClient, mocker: MockerFixture
) -> None:
    # Arrange
    mocker.patch(
        "app.main.insurance_gateway.verify_coverage",
        return_value=InsuranceAuthResult(
            authorized=True,
            protocol="AUTH-BATCH-100",
        ),
    )
    batch_payloads = AppointmentFactory.build_batch(2)
    for item in batch_payloads:
        client.post("/api/appointments", json=item)

    # Act
    list_response = client.get("/api/appointments")
    delete_response = client.delete("/api/appointments/1")
    after_delete_list = client.get("/api/appointments")

    # Assert
    assert list_response.status_code == 200
    assert len(list_response.json()) == 2
    assert delete_response.status_code == 204
    assert len(after_delete_list.json()) == 1
    assert after_delete_list.json()[0]["id"] == 2

