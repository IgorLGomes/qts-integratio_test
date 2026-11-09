import pytest
from axe_playwright_python.sync_playwright import Axe
from playwright.sync_api import Page, expect
from tests.factories import AppointmentFactory
from tests.pages.appointment_page import AppointmentPage


@pytest.mark.e2e
def test_e2e_create_appointment_flow_with_pom(
    page: Page, live_server_url: str
) -> None:
    # Arrange
    appointment_page = AppointmentPage(page, live_server_url)
    payload = AppointmentFactory.build_payload(
        specialty="Ortopedia",
        appointment_date="2026-12-20",
    )

    # Act
    appointment_page.navigate()
    appointment_page.fill_appointment_form(payload)
    appointment_page.submit_form()

    # Assert
    appointment_page.expect_success_message(payload["patient_name"])
    expect(appointment_page.appointments_table).to_contain_text("Ortopedia")
    expect(appointment_page.appointments_table).to_contain_text("CONFIRMADO")


@pytest.mark.e2e
def test_e2e_denied_insurance_shows_error_banner(
    page: Page, live_server_url: str
) -> None:
    # Arrange
    appointment_page = AppointmentPage(page, live_server_url)
    payload = AppointmentFactory.build_payload(insurance_card="NEG-000111")

    # Act
    appointment_page.navigate()
    appointment_page.fill_appointment_form(payload)
    appointment_page.submit_form()

    # Assert
    appointment_page.expect_error_message("carência ou bloqueio cadastral")


@pytest.mark.accessibility
def test_accessibility_wcag_21_aa_audit_with_axe(
    page: Page, live_server_url: str
) -> None:
    # Arrange
    appointment_page = AppointmentPage(page, live_server_url)
    appointment_page.navigate()
    axe = Axe()

    # Act
    results = axe.run(
        page,
        options={
            "runOnly": {
                "type": "tag",
                "values": ["wcag2a", "wcag2aa", "wcag21a", "wcag21aa"],
            }
        },
    )

    # Assert
    assert results.violations_count == 0, (
        f"Foram encontradas violações WCAG 2.1 AA:\n{results.generate_report()}"
    )


@pytest.mark.accessibility
def test_accessibility_keyboard_navigation_tab_order(
    page: Page, live_server_url: str
) -> None:
    # Arrange
    appointment_page = AppointmentPage(page, live_server_url)
    appointment_page.navigate()

    # Act & Assert: verifica a sequência lógica de foco via tecla Tab
    page.keyboard.press("Tab")
    expect(appointment_page.name_input).to_be_focused()

    page.keyboard.press("Tab")
    expect(appointment_page.cpf_input).to_be_focused()

    page.keyboard.press("Tab")
    expect(appointment_page.email_input).to_be_focused()

    page.keyboard.press("Tab")
    expect(appointment_page.specialty_select).to_be_focused()

    page.keyboard.press("Tab")
    expect(appointment_page.date_input).to_be_focused()

    page.keyboard.press("Tab")
    expect(appointment_page.insurance_input).to_be_focused()

    page.keyboard.press("Tab")
    expect(appointment_page.submit_button).to_be_focused()

    page.keyboard.press("Tab")
    expect(appointment_page.reset_button).to_be_focused()

