from backend.supabase_client import supabase


def submit_score(
    user_id: str,
    game_mode: str,
    score: int
):
    response = supabase.table("scores").insert({
        "user_id": user_id,
        "game_mode": game_mode,
        "score": score
    }).execute()

    return response


def get_top_scores(limit: int = 10):
    response = (
        supabase.table("scores")
        .select("*")
        .order("score", desc=True)
        .limit(limit)
        .execute()
    )

    return response