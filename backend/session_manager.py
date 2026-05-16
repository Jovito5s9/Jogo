# backend/session_manager.py

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Optional


class SessionManager:

    def __init__(self, session_file: Optional[str | Path] = None) -> None:
        base_dir = Path(__file__).resolve().parents[1]
        self.session_file = Path(session_file) if session_file else base_dir / "saved" / "session.json"
        self.session_file.parent.mkdir(parents=True, exist_ok=True)
        self._ensure_file_exists()


    def _ensure_file_exists(self) -> None:
        if not self.session_file.exists():
            self._write_json({})

    def _read_json(self) -> dict[str, Any]:
        self._ensure_file_exists()

        try:
            with self.session_file.open("r", encoding="utf-8") as f:
                data = json.load(f)

            if isinstance(data, dict):
                return data

            return {}
        except (json.JSONDecodeError, OSError):
            return {}

    def _write_json(self, data: dict[str, Any]) -> None:
        self.session_file.parent.mkdir(parents=True, exist_ok=True)

        with self.session_file.open("w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)


    def get_session(self) -> dict[str, Any]:
        return self._read_json()

    def has_session(self) -> bool:
        session = self._read_json()
        return bool(session.get("access_token") and session.get("refresh_token") and session.get("user_id"))

    def save_session(
        self,
        email: str,
        user_id: str,
        access_token: str,
        refresh_token: str,
        expires_at: Optional[int] = None,
        remember_login: bool = True,
        extra_data: Optional[dict[str, Any]] = None,
    ) -> dict[str, Any]:
        data = {
            "email": email,
            "user_id": user_id,
            "access_token": access_token,
            "refresh_token": refresh_token,
            "expires_at": expires_at,
            "remember_login": remember_login,
        }

        if extra_data:
            data.update(extra_data)

        self._write_json(data)
        return data

    def update_session(self, **kwargs: Any) -> dict[str, Any]:
        data = self._read_json()
        data.update(kwargs)
        self._write_json(data)
        return data

    def clear_session(self) -> None:
        self._write_json({})

    def remove_session_file(self) -> None:
        if self.session_file.exists():
            self.session_file.unlink()
        self._ensure_file_exists()


    def get_email(self) -> Optional[str]:
        return self._read_json().get("email")

    def get_user_id(self) -> Optional[str]:
        return self._read_json().get("user_id")

    def get_access_token(self) -> Optional[str]:
        return self._read_json().get("access_token")

    def get_refresh_token(self) -> Optional[str]:
        return self._read_json().get("refresh_token")

    def get_expires_at(self) -> Optional[int]:
        return self._read_json().get("expires_at")

    def set_remember_login(self, value: bool) -> dict[str, Any]:
        return self.update_session(remember_login=bool(value))


    def save_from_auth_response(self, auth_response: Any, email: Optional[str] = None) -> dict[str, Any]:
        user = getattr(auth_response, "user", None)
        session = getattr(auth_response, "session", None)

        if user is None or session is None:
            raise ValueError("auth_response inválida: esperado user e session.")

        resolved_email = email or getattr(user, "email", None)

        return self.save_session(
            email=resolved_email or "",
            user_id=getattr(user, "id", ""),
            access_token=getattr(session, "access_token", ""),
            refresh_token=getattr(session, "refresh_token", ""),
            expires_at=getattr(session, "expires_at", None),
            remember_login=True,
        )

    def restore_session(self, supabase_client: Any) -> bool:
        session = self._read_json()

        access_token = session.get("access_token")
        refresh_token = session.get("refresh_token")

        if not access_token or not refresh_token:
            print("restore_session: faltando access_token ou refresh_token")
            return False

        try:
            auth = supabase_client.auth

            if hasattr(auth, "set_session"):
                auth.set_session(access_token, refresh_token)
            elif hasattr(auth, "refresh_session"):
                auth.refresh_session(refresh_token)
            else:
                print("restore_session: cliente Supabase sem set_session/refresh_session")
                return False

            # valida de verdade com o servidor
            try:
                user_response = auth.get_user()
                print("restore_session: usuário validado:", user_response.user.id)
                return True
            except Exception as e:
                print("restore_session: sessão carregada, mas get_user falhou:", e)
                return False

        except Exception as e:
            print("restore_session: erro ao restaurar sessão:", e)
            return False

    def is_logged_in(self) -> bool:
        return self.has_session()


if __name__ == "__main__":
    manager = SessionManager()
    print("Arquivo:", manager.session_file)
    print("Existe sessão?", manager.has_session())
    print("Conteúdo atual:", manager.get_session())