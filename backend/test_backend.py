from supabase import create_client
from supabase_auth.errors import AuthApiError

# -------------------------------------------------
# SUPABASE CONFIG
# -------------------------------------------------

url = "https://vobcctcufpyeotwqaddu.supabase.co"

key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InZvYmNjdGN1ZnB5ZW90d3FhZGR1Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3Nzg1Nzc0MjQsImV4cCI6MjA5NDE1MzQyNH0.Xe83ubXKlK4EUd8W8ikiivA362UdOxKnZFiYCeJkpZ8"

supabase = create_client(url, key)

# -------------------------------------------------
# USER DATA
# -------------------------------------------------

EMAIL = "luan.a.vieira@gmail.com"
PASSWORD = "12345678"

# -------------------------------------------------
# LOGIN OR CREATE ACCOUNT
# -------------------------------------------------

try:
    print("\nTentando login...")

    auth_response = supabase.auth.sign_in_with_password({
        "email": EMAIL,
        "password": PASSWORD
    })

    print("\nLogin realizado com sucesso!")

except AuthApiError as error:

    print("\nLogin falhou.")

    error_message = str(error)

    # -------------------------------------------------
    # USER DOES NOT EXIST
    # -------------------------------------------------

    if (
        "Invalid login credentials" in error_message
        or
        "Email not confirmed" in error_message
        or
        "User not found" in error_message
    ):

        print("\nUsuário não existe.")
        print("Criando conta...")

        signup_response = supabase.auth.sign_up({
            "email": EMAIL,
            "password": PASSWORD
        })

        print("\nConta criada!")

        print("\nRealizando login...")

        auth_response = supabase.auth.sign_in_with_password({
            "email": EMAIL,
            "password": PASSWORD
        })

        print("\nLogin realizado!")

    else:
        raise error

# -------------------------------------------------
# USER INFO
# -------------------------------------------------

print("\nAUTH RESPONSE:")
print(auth_response)

user_id = auth_response.user.id

print("\nUSER ID:")
print(user_id)

# -------------------------------------------------
# INSERT SCORE
# -------------------------------------------------

score_response = supabase.table("scores").insert({
    "user_id": user_id,
    "game_mode": "survival",
    "score": 1500
}).execute()

print("\nSCORE INSERT:")
print(score_response)

# -------------------------------------------------
# GET LEADERBOARD
# -------------------------------------------------

leaderboard = (
    supabase.table("scores")
    .select("*")
    .order("score", desc=True)
    .limit(10)
    .execute()
)

print("\nLEADERBOARD:")
print(leaderboard)

# -------------------------------------------------
# SAVE PROGRESS
# -------------------------------------------------

save_response = (
    supabase.table("progress")
    .upsert({
        "user_id": user_id,
        "level": 5,
        "xp": 2300,
        "coins": 500
    })
    .execute()
)

print("\nSAVE RESPONSE:")
print(save_response)

# -------------------------------------------------
# LOAD PROGRESS
# -------------------------------------------------

progress_response = (
    supabase.table("progress")
    .select("*")
    .eq("user_id", user_id)
    .single()
    .execute()
)

print("\nPROGRESS:")
print(progress_response)