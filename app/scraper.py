import json
import requests
from bs4 import BeautifulSoup
from openai import OpenAI
import os

# Load API key safely
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


# ==========================================================
# 1. FETCH RAW HTML TEXT
# ==========================================================
def fetch_page_text(url, max_chars=15000):
    try:
        r = requests.get(url, headers={"User-Agent": "RivalBot/1.0"}, timeout=10)
        if r.status_code != 200:
            return {"error": f"HTTP {r.status_code}", "title": None, "text": ""}

        soup = BeautifulSoup(r.text, "html.parser")

        title = soup.title.string.strip() if soup.title and soup.title.string else None
        text = soup.get_text(separator=" ", strip=True)[:max_chars]

        return {"error": None, "title": title, "text": text}

    except Exception as e:
        return {"error": str(e), "title": None, "text": ""}


# ==========================================================
# 2. AI-GENERATED CLEAN DESCRIPTION
# ==========================================================
def generate_ai_description(text: str) -> str:
    if not text or len(text.strip()) < 50:
        return "Geen nuttige omschrijving beschikbaar."

    system_msg = (
        "You summarize website content. Ignore menus, navigation, footers, "
        "cookie banners, language selectors, and UI text. Write a clean, "
        "human-friendly description in 2–3 sentences focusing on what the company does."
    )

    user_msg = f"""
Vat deze website samen in 2–3 zinnen.
Negeer navigatie, footers, menus, cookie banners en taalopties.

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


# ==========================================================
# Helper voor default AI-resultaat
# ==========================================================
def _empty_ai_result(ai_summary: str = ""):
    return {
        "ai_summary": ai_summary,
        "value_proposition": "",
        "product_description": "",
        "target_segment": "",
        "pricing": "",
        "key_features": [],
        "competitors": [],
        "headquarters": "",
        "office_locations": "",
        "team_size": None,
        "funding": "",
        "funding_history": "",
        "traction_signals": "",
    }


# ==========================================================
# 3. AI BUSINESS FUNDAMENTALS EXTRACTION
# ==========================================================
def ask_ai_for_company_info(url, title, text):
    prompt = f"""
You extract business fundamentals from messy website text.

Keep all previous behavior, but EXPAND your logic as follows:

===========================================================
PRICING (enhanced rules)
===========================================================
If explicit prices exist (e.g., "€29/mo", "pricing plans", "tiers"):
  → Extract exact pricing text.

If pricing is NOT explicitly mentioned:
  → Infer pricing TIER based on sector, wording, and target customers.
  → Choose ONE of: "Low-end", "Mid-market", "Premium", "Enterprise", "Freemium", "Unknown".
  → Never return an empty string. Return "Unknown" if no inference is possible.

===========================================================
REVIEWS (enhanced rules)
===========================================================
Search for mentions of:
  - "reviews", "testimonials", "ratings", "customer stories"
  - e.g. "4.8 based on 120 reviews"

If NO review count is explicitly present:
  → Infer one of:
      "Geen reviews gevonden"
      "Enkele reviews verwacht"
      "Veel reviews verwacht"
      "Unknown"

Return a short human-friendly phrase, e.g.:
  "212 verified reviews (4.6★)"
  "Geen reviews gevonden"

===========================================================
FUNDING (enhanced rules)
===========================================================
If funding is explicitly stated (e.g., “€5M seed”, “Series A”):
  → Extract exactly.

If NOT stated:
  → Infer funding profile based on company type:
        • Consultancy, agency, law/accounting firms → "Privately held, no external funding"
        • SaaS startups → "Likely early-stage (<€5M)"
        • Large known brands → "Likely well-funded or corporate-backed"
        • Non-profits or institutions → "Publicly funded or donor-based"
  → Never return an empty string.

===========================================================
TEAM SIZE / HIRING
===========================================================
Use word patterns:
- "team of 120", "over 50 experts", "200+ employees"
- If ambiguous, infer:
    Boutique agency → 5–30
    Growing B2B SaaS → 10–80
    Large brand → 100+

Return an INTEGER where possible.

===========================================================
RETURN STRICT JSON ONLY WITH EXACTLY THESE FIELDS
===========================================================

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

CONTENT SOURCE:
URL: {url}
TITLE: {title}

CONTENT:
{text}
"""

    try:
        response = client.chat.completions.create(
            model="gpt-4.1-mini",
            temperature=0,
            messages=[
                {"role": "system", "content": "Return JSON only."},
                {"role": "user", "content": prompt},
            ],
        )

        raw = response.choices[0].message.content.strip()

        # Probeer direct JSON te parsen
        try:
            return json.loads(raw)
        except Exception:
            # strip ```json ``` blokken
            cleaned = raw.replace("```json", "").replace("```", "").strip()
            try:
                return json.loads(cleaned)
            except Exception:
                # Fallback: stop ruwe output in ai_summary
                return _empty_ai_result(ai_summary=raw)

    except Exception as e:
        # Bij eender welke API-fout: altijd een geldige dict
        return _empty_ai_result(ai_summary=f"AI error: {e}")


# ==========================================================
# 4. COMPETITOR ENGINE (Force 5–10 real competitors)
# ==========================================================
def generate_competitors(value_prop, target_segment, summary):
    prompt = f"""
You are an expert competitive intelligence analyst.

Based on the company's value proposition, target segment, and summary,
predict the MOST LIKELY direct competitors.

VALUE PROPOSITION:
{value_prop}

TARGET SEGMENT:
{target_segment}

SUMMARY:
{summary}

Return STRICT JSON ONLY:

{{
  "competitors": []
}}

Rules:
- Provide 5–10 concrete companies.
- Must be real, well-known, or industry-specific.
- Include direct + indirect competitors.
- If no data, infer from industry.
"""

    try:
        response = client.chat.completions.create(
            model="gpt-4.1-mini",
            temperature=0.4,
            messages=[
                {"role": "system", "content": "Return JSON only."},
                {"role": "user", "content": prompt},
            ],
        )

        raw = response.choices[0].message.content.strip()

        try:
            return json.loads(raw).get("competitors", [])
        except Exception:
            cleaned = raw.replace("```json", "").replace("```", "").strip()
            try:
                return json.loads(cleaned).get("competitors", [])
            except Exception:
                return []

    except Exception:
        return []


# ==========================================================
# 5. MAIN SCRAPER PIPELINE
# ==========================================================
def scrape_website(url):
    base = fetch_page_text(url)
    if base["error"]:
        return {"error": base["error"]}

    title = base["title"] or "Geen titel"
    text = base["text"] or ""

    description = generate_ai_description(text)

    # Zorg dat we ALTIJD een dict hebben
    ai = ask_ai_for_company_info(url, title, text) or {}
    if not isinstance(ai, dict):
        ai = _empty_ai_result(ai_summary=str(ai))

    # Competitor fallback
    competitors_extra = generate_competitors(
        ai.get("value_proposition", ""),
        ai.get("target_segment", ""),
        ai.get("ai_summary", "")
    )

    competitors_final = ai.get("competitors") or competitors_extra

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
        "competitors": competitors_final,

        "headquarters": ai.get("headquarters"),
        "office_locations": ai.get("office_locations"),
        "team_size": ai.get("team_size"),
        "funding": ai.get("funding"),
        "funding_history": ai.get("funding_history"),
        "traction_signals": ai.get("traction_signals"),
    }


# ==========================================================
# 6. SELF-TEST
# ==========================================================
if __name__ == "__main__":
    test_url = "https://www.unisport.com"
    print("Scraping test URL:", test_url)
    result = scrape_website(test_url)
    print(json.dumps(result, indent=2, ensure_ascii=False))







