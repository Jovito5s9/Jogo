EMAIL = "luan.a.vieira@gmail.com"
PASSWORD = "12345678"
from backend.auth import login, logout, restore_session, get_current_user

restore_session()

resp = login(EMAIL, PASSWORD)
print(resp.user.id)
