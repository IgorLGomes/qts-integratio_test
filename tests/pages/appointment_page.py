from typing import Any
from playwright.sync_api import Locator, Page, expect


class AppointmentPage:
    """
    Page Object Model (POM) para a interface web de Agendamento Médico (MedSync).
    Utiliza exclusivamente seletores semânticos recomendados pelo Playwright:
    get_by_role, get_by_label e get_by_text.
    """

    def __init__(self, page: Page, base_url: str) -> None:
        self.page = page
        self.base_url = base_url

    @property
    def heading_main(self) -> Locator:
        return self.page.get_by_role(
            "heading", name="MedSync — Triagem e Agendamento Médico"
        )

    @property
    def name_input(self) -> Locator:
        return self.page.get_by_label("Nome Completo do Paciente")

    @property
    def cpf_input(self) -> Locator:
        return self.page.get_by_label("CPF (somente números)")

    @property
    def email_input(self) -> Locator:
        return self.page.get_by_label("E-mail do Paciente")

    @property
    def specialty_select(self) -> Locator:
        return self.page.get_by_label("Especialidade Médica")

    @property
    def date_input(self) -> Locator:
        return self.page.get_by_label("Data da Consulta")

    @property
    def insurance_input(self) -> Locator:
        return self.page.get_by_label("Número da Carteirinha do Convênio")

    @property
    def submit_button(self) -> Locator:
        return self.page.get_by_role("button", name="Confirmar Agendamento")

    @property
    def reset_button(self) -> Locator:
        return self.page.get_by_role("button", name="Limpar Formulário")

    @property
    def status_banner(self) -> Locator:
        return self.page.get_by_role("status")

    @property
    def appointments_table(self) -> Locator:
        return self.page.get_by_role("table", name="Tabela de Consultas Agendadas")

    def navigate(self) -> None:
        """Navega até a página inicial do sistema."""
        self.page.goto(self.base_url)
        expect(self.heading_main).to_be_visible()

    def fill_appointment_form(self, data: dict[str, Any]) -> None:
        """Preenche todos os campos do formulário utilizando seletores semânticos."""
        self.name_input.fill(data["patient_name"])
        self.cpf_input.fill(data["cpf"])
        self.email_input.fill(data["email"])
        self.specialty_select.select_option(data["specialty"])
        self.date_input.fill(data["appointment_date"])
        self.insurance_input.fill(data["insurance_card"])

    def submit_form(self) -> None:
        """Aciona o botão de submissão do agendamento."""
        self.submit_button.click()

    def expect_success_message(self, patient_name: str) -> None:
        """Verifica se a mensagem de confirmação é exibida para o paciente."""
        expect(
            self.page.get_by_text(f"Agendamento confirmado para {patient_name}!")
        ).to_be_visible()
        expect(self.appointments_table).to_contain_text(patient_name)

    def expect_error_message(self, partial_text: str) -> None:
        """Verifica se uma mensagem de erro é exibida no banner de feedback."""
        expect(self.status_banner).to_contain_text(partial_text)

