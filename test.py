import requests

CLIENT_ID = "49164"
CLIENT_SECRET = "Vh3zYLuWxYoRS7o2RmOvhEunh40Z8kWLfPw21tQm"

def fetch_star_rate(beatmapset_id: int, beatmap_id: int):
    """
    Fetch the official star rating of a beatmap from osu! API v2.

    Parameters:
    - beatmapset_id: The beatmap set ID
    - beatmap_id: The specific beatmap ID (difficulty) within the set

    Returns:
    - Star rating as a float
    """
    # 1️⃣ Get OAuth token
    token_res = requests.post(
        "https://osu.ppy.sh/oauth/token",
        json={
            "client_id": CLIENT_ID,
            "client_secret": CLIENT_SECRET,
            "grant_type": "client_credentials",
            "scope": "public"
        }
    )
    token = token_res.json()["access_token"]

    # 2️⃣ Fetch beatmap info
    headers = {"Authorization": f"Bearer {token}"}
    url = f"https://osu.ppy.sh/api/v2/beatmaps/{beatmap_id}"
    response = requests.get(url, headers=headers)
    data = response.json()

    # 3️⃣ Return the star rating
    return data["difficulty_rating"]

# -----------------------------
# Example usage
beatmapset_id = 2372473
beatmap_id = 5121289
print(fetch_star_rate(beatmapset_id, beatmap_id))