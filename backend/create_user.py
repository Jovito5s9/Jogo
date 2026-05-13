from backend.auth import signup

response = signup(
    "novoemail@email.com",
    "12345678"
)

print(response)