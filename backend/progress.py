from backend.auth import login

from backend.scores import (
    submit_score,
    get_top_scores
)

from backend.progress import (
    save_progress,
    load_progress
)

EMAIL = "SEU_EMAIL@gmail.com"
PASSWORD = "12345678"

# -------------------------------------------------
# LOGIN
# -------------------------------------------------

auth_response = login(
    EMAIL,
    PASSWORD
)

print("\nLOGIN:")
print(auth_response)

user_id = auth_response.user.id

# -------------------------------------------------
# SCORE
# -------------------------------------------------

score_response = submit_score(
    user_id=user_id,
    game_mode="survival",
    score=1500
)

print("\nSCORE INSERT:")
print(score_response)

# -------------------------------------------------
# LEADERBOARD
# -------------------------------------------------

leaderboard = get_top_scores()

print("\nLEADERBOARD:")
print(leaderboard)

# -------------------------------------------------
# SAVE PROGRESS
# -------------------------------------------------

save = save_progress(
    user_id=user_id,
    level=5,
    xp=2300,
    coins=500
)

print("\nSAVE:")
print(save)

# -------------------------------------------------
# LOAD PROGRESS
# -------------------------------------------------

progress = load_progress(user_id)

print("\nPROGRESS:")
print(progress)