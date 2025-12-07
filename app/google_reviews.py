import requests
import os

GOOGLE_KEY = os.getenv("GOOGLE_API_KEY")

def get_google_reviews(business_name: str):
    """
    Haalt rating + aantal reviews op via Google Places API.
    Retourneert (review_count, label).
    """

    if not GOOGLE_KEY:
        return 0, "Geen Google API key"

    # 1) Zoek bedrijf → krijg place_id
    search_url = (
        "https://maps.googleapis.com/maps/api/place/textsearch/json"
        f"?query={business_name}&key={GOOGLE_KEY}"
    )
    resp = requests.get(search_url).json()

    results = resp.get("results", [])
    if not results:
        return 0, "Geen reviews gevonden"

    place_id = results[0].get("place_id")
    if not place_id:
        return 0, "Geen reviews gevonden"

    # 2) Haal reviews + rating op
    details_url = (
        "https://maps.googleapis.com/maps/api/place/details/json"
        f"?place_id={place_id}&fields=rating,user_ratings_total&key={GOOGLE_KEY}"
    )
    details = requests.get(details_url).json().get("result", {})

    count = details.get("user_ratings_total", 0)
    rating = details.get("rating")

    if count == 0:
        return 0, "Geen reviews gevonden"

    return count, f"{count} Google-reviews ({rating}★)"
