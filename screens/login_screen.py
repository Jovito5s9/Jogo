from kivy.uix.popup import Popup
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput

from utils.customizedButton import CustomizedButton
from utils.resourcesPath import resource_path
from screens.shared import configuracoes
from backend.auth import restore_session, signup as backend_signup, login as backend_login, get_current_user

import json


class MenuLogin(Popup):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.size_hint = (0.4, 0.5)
        self.title = ""
        self.background = ""
        self.background_color = (0, 0, 0, 0)
        self.separator_height = 0

        self.linguagem = configuracoes().get("linguagem", "pt")
        with open(resource_path(f"content/ui/{self.linguagem}.json"), "r", encoding="utf-8") as f:
            self.ui_texts = json.load(f)

        self.layout = BoxLayout(
            orientation="vertical",
            padding=(30, 30, 30, 30),
            spacing=20,
            size_hint = (0.45,0.8)
        )

        self.button_login = CustomizedButton(
            text=self.ui_texts.get("login", "Login"),
            font_size=45,
            bold=True,
            color=(0.1, 0.1, 0.1, 1),
        )
        self.button_login.bind(on_release=self.login)

        self.button_signup = CustomizedButton(
            text=self.ui_texts.get("signup", "Signup"),
            font_size=40,
            bold=True,
            color=(0.1, 0.1, 0.1, 1),
        )
        self.button_signup.bind(on_release=self.signup)

        self.button_quit = CustomizedButton(
            text=self.ui_texts.get("return", "Return"),
            font_size=40,
            bold=True,
            color=(0.1, 0.1, 0.1, 1),
        )
        self.button_quit.bind(on_release=self.dismiss)

        self.layout.add_widget(self.button_login)
        self.layout.add_widget(self.button_signup)
        self.layout.add_widget(self.button_quit)

        self.add_widget(self.layout)

    def _message_popup(self, title, message):
        content = BoxLayout(orientation="vertical", padding=20, spacing=20)

        lbl = Label(
            text=message,
            halign="center",
            valign="middle"
        )
        lbl.bind(size=lbl.setter("text_size"))

        btn = CustomizedButton(
            text=self.ui_texts.get("ok", "OK"),
            font_size=32,
            bold=True,
            color=(0.1, 0.1, 0.1, 1),
        )

        popup = Popup(
            title=title,
            content=content,
            size_hint=(0.5, 0.35),
            auto_dismiss=False
        )

        btn.bind(on_release=popup.dismiss)

        content.add_widget(lbl)
        content.add_widget(btn)

        popup.open()

    def login(self, *args):
        restored = restore_session()

        if not restored:
            self._message_popup(
                self.ui_texts.get("login_error_title", "Login"),
                self.ui_texts.get("login_no_saved_session", "Nenhuma sessão salva foi encontrada.")
            )
            return

        user = get_current_user()

        if user:
            self._message_popup(
                self.ui_texts.get("login_success_title", "Login"),
                self.ui_texts.get("login_success_message", "Sessão recuperada com sucesso.")
            )
            self.dismiss()
        else:
            self._message_popup(
                self.ui_texts.get("login_error_title", "Login"),
                self.ui_texts.get("login_no_saved_session", "Sessão salva, mas não foi possível validar o usuário.")
            )


    def signup(self, *args):
        content = BoxLayout(orientation="vertical", padding=20, spacing=15)

        title_lbl = Label(
            text=self.ui_texts.get("signup_title", "Create account"),
            size_hint_y=None,
            height=40
        )

        email_input = TextInput(
            hint_text=self.ui_texts.get("email", "Email"),
            multiline=False,
            size_hint_y=None,
            height=45
        )

        password_input = TextInput(
            hint_text=self.ui_texts.get("password", "Password"),
            password=True,
            multiline=False,
            size_hint_y=None,
            height=45
        )

        confirm_password_input = TextInput(
            hint_text=self.ui_texts.get("confirm_password", "Confirm password"),
            password=True,
            multiline=False,
            size_hint_y=None,
            height=45
        )

        buttons = BoxLayout(size_hint_y=None, height=50, spacing=10)

        btn_cancel = CustomizedButton(
            text=self.ui_texts.get("cancel", "Cancel"),
            font_size=28,
            bold=True,
            color=(0.1, 0.1, 0.1, 1),
        )

        btn_create = CustomizedButton(
            text=self.ui_texts.get("create_account", "Create"),
            font_size=28,
            bold=True,
            color=(0.1, 0.1, 0.1, 1),
        )

        popup = Popup(
            title=self.ui_texts.get("signup", "Signup"),
            content=content,
            size_hint=(0.7, 0.6),
            auto_dismiss=False
        )

        def do_create(*_):
            email = email_input.text.strip()
            password = password_input.text.strip()
            confirm_password = confirm_password_input.text.strip()

            if not email or not password:
                self._message_popup(
                    self.ui_texts.get("signup_error_title", "Signup"),
                    self.ui_texts.get("signup_missing_fields", "Preencha email e senha.")
                )
                return

            if password != confirm_password:
                self._message_popup(
                    self.ui_texts.get("signup_error_title", "Signup"),
                    self.ui_texts.get("signup_password_mismatch", "As senhas não coincidem.")
                )
                return

            try:
                backend_signup(email, password)

                backend_login(email, password)

                self._message_popup(
                    self.ui_texts.get("signup_success_title", "Signup"),
                    self.ui_texts.get("signup_success_message", "Conta criada e sessão salva.")
                )
                popup.dismiss()
                self.dismiss()

            except Exception as e:
                self._message_popup(
                    self.ui_texts.get("signup_error_title", "Signup"),
                    f"{self.ui_texts.get('signup_failed', 'Falha ao criar conta.')}\n{e}"
                )

        btn_cancel.bind(on_release=popup.dismiss)
        btn_create.bind(on_release=do_create)

        buttons.add_widget(btn_cancel)
        buttons.add_widget(btn_create)

        content.add_widget(title_lbl)
        content.add_widget(email_input)
        content.add_widget(password_input)
        content.add_widget(confirm_password_input)
        content.add_widget(buttons)

        popup.open()