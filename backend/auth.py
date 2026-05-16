from __future__ import annotations

from typing import Optional, Any

from supabase_auth.errors import AuthApiError

from backend.supabase_client import supabase
from backend.session_manager import SessionManager


session_manager = SessionManager()


def signup(email: str, password: str) -> Any:
    response = supabase.auth.sign_up({
        "email": email,
        "password": password
    })
    return response


def login(email: str, password: str) -> Any:
    response = supabase.auth.sign_in_with_password({
        "email": email,
        "password": password
    })

    session_manager.save_from_auth_response(response, email=email)
    return response


def logout(clear_saved_session: bool = True) -> None:
    try:
        supabase.auth.sign_out()
    finally:
        if clear_saved_session:
            session_manager.clear_session()


def restore_session() -> bool:
    return session_manager.restore_session(supabase)


def is_logged_in() -> bool:
    return session_manager.is_logged_in()


def get_saved_session() -> dict:
    return session_manager.get_session()


def get_current_user() -> Optional[Any]:
    try:
        response = supabase.auth.get_user()
        return response.user
    except Exception:
        return None


def get_current_session() -> Optional[Any]:
    try:
        response = supabase.auth.get_session()
        return response.session
    except Exception:
        return None


if __name__ == "__main__":
    print("Sessão salva localmente?", is_logged_in())

    restored = restore_session()
    print("Sessão restaurada?", restored)

    user = get_current_user()
    print("Usuário atual:", user)