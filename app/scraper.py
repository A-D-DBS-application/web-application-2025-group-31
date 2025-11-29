import json
import requests
from bs4 import BeautifulSoup
from openai import OpenAI

client = OpenAI(api_key="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")


# ------------------------------------------
# HTML SCRAPER
# ------------------------------------------
def fetch_page_text(url, max_chars=8000):
    try:
        r = requests.get(url, headers={"User-Agent": "RivalBot/1.0"}, timeout=10)
        if r.status_code != 200:
            return {"error": f"HTTP {r.status_code}", "title": None, "text": ""}

        soup = BeautifulSoup(r.text, "html.parser")

        title = soup.title.string.strip() if soup.title and soup.title.string else None
        text = soup.get_text(separator=" ", strip=True)
        if text:
            text = text[:max_chars]

        return {"error": None, "title": title, "text": text}

    except Exception as e:
        return {"error": str(e), "title": None, "text": ""}


# ------------------------------------------
# AI BESCHRIJVING (mooie samenvatting)
# ------------------------------------------
def generate_ai_description(text: str) -> str:
    if not text or len(text.strip()) < 50:
        return "Geen nuttige omschrijving beschikbaar."

    system_msg = (
        "You summarize website content. "
        "Ignore menus, navigation, footers, cookie banners, language selectors, and UI text. "
        "Write a clean, human-friendly description in 2–3 sentences focusing on what the company does."
    )

    user_msg = f"""
Vat deze website samen in maximaal 2–3 zinnen.
Negeer navigatie, menu's, footers, taalkeuzes, cookie banners en irrelevante interface tekst.
Beschrijf enkel wat het bedrijf doet en voor wie.

CONTENT:
{text}
"""

    try:
        response = client.chat.completions.create(
            model="gpt-4.1-mini",
            temperature=0.3,
            messages=[
                {"role": "system", "content": system_msg},
                {"role": "user", "content": user_msg},
            ],
        )

        return response.choices[0].message.content.strip()

    except Exception as e:
        return f"AI-fout bij omschrijving: {e}"


# ------------------------------------------
# AI EXTRACTIE VAN BUSINESS INFO
# ------------------------------------------
def ask_ai_for_company_info(url, title, text):

    prompt = f"""
Extract structured business intelligence from this website text.

Return VALID JSON ONLY with exact keys:

{{
  "ai_summary": "",
  "value_proposition": "",
  "product_description": "",
  "target_segment": "",
  "pricing": "",
  "key_features": [],
  "competitors": [],
  "headquarters": "",
  "office_locations": "",
  "team_size": null,
  "funding": "",
  "funding_history": "",
  "traction_signals": ""
}}

URL: {url}
TITLE: {title}
CONTENT:
{text}
"""

    try:
        response = client.chat.completions.create(
            model="gpt-4.1-mini",
            messages=[
                {"role": "system", "content": "Return JSON only."},
                {"role": "user", "content": prompt},
            ],
            temperature=0,
        )

        raw = response.choices[0].message.content.strip()

        print("AI RAW OUTPUT:", raw)

        try:
            return json.loads(raw)
        except:
            return {"ai_summary": raw}

    except Exception as e:
        return {
            "ai_summary": f"AI error: {e}",
            "value_proposition": None,
            "product_description": None,
            "target_segment": None,
            "pricing": None,
            "key_features": [],
            "competitors": [],
            "headquarters": None,
            "office_locations": None,
            "team_size": None,
            "funding": None,
            "funding_history": None,
            "traction_signals": None,
        }


# ------------------------------------------
# MAIN SCRAPER FUNCTIE
# ------------------------------------------
def scrape_website(url):
    base = fetch_page_text(url)
    if base["error"]:
        return {"error": base["error"]}

    title = base["title"] or "Geen titel"
    text = base["text"] or ""

    # ✨ NIEUW — mooie AI-beschrijving
    description = generate_ai_description(text)

    ai = ask_ai_for_company_info(url, title, text)

    return {
        "url": url,
        "title": title,
        "description": description,

        "ai_summary": ai.get("ai_summary"),
        "value_proposition": ai.get("value_proposition"),
        "product_description": ai.get("product_description"),
        "target_segment": ai.get("target_segment"),
        "pricing": ai.get("pricing"),
        "key_features": ai.get("key_features"),
        "competitors": ai.get("competitors"),

        "headquarters": ai.get("headquarters"),
        "office_locations": ai.get("office_locations"),
        "team_size": ai.get("team_size"),
        "funding": ai.get("funding"),
        "funding_history": ai.get("funding_history"),
        "traction_signals": ai.get("traction_signals"),
    }


# ------------------------------------------
# SELF TEST
# ------------------------------------------
if __name__ == "__main__":
    test_url = "https://www.unisport.com"
    print("Scraping test URL:", test_url)

    result = scrape_website(test_url)
    print("\n--- RESULTAAT ---\n")
    print(json.dumps(result, indent=2, ensure_ascii=False))



