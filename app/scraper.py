import json
import requests
from bs4 import BeautifulSoup
from openai import OpenAI

import os
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# ------------------------------------------
# RELEVANTE SUBPAGINA’S VINDEN
# ------------------------------------------
def discover_relevant_links(url, soup):
    KEYWORDS = [
        "about", "company", "over", "team", "jobs", "careers",
        "contact", "locations", "investors", "press", "news"
    ]

    links = set()

    for a in soup.find_all("a", href=True):
        href = a["href"].lower()

        if any(k in href for k in KEYWORDS):
            if href.startswith("http"):
                links.add(href)
            else:
                base = url.rstrip("/")
                href = href.lstrip("/")
                links.add(base + "/" + href)

    return list(links)


# ------------------------------------------
# HTML SCRAPER (MET SUBPAGE DETECTIE)
# ------------------------------------------
def fetch_page_text(url, max_chars=8000):
    try:
        r = requests.get(url, headers={"User-Agent": "RivalBot/1.0"}, timeout=10)
        if r.status_code != 200:
            return {"error": f"HTTP {r.status_code}", "title": None, "text": "", "subpages": []}

        soup = BeautifulSoup(r.text, "html.parser")

        title = soup.title.string.strip() if soup.title and soup.title.string else None
        text = soup.get_text(separator=" ", strip=True)
        if text:
            text = text[:max_chars]

        # ⭐ BELANGRIJK: subpages ontdekken
        subpages = discover_relevant_links(url, soup)

        return {"error": None, "title": title, "text": text, "subpages": subpages}

    except Exception as e:
        return {"error": str(e), "title": None, "text": "", "subpages": []}


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
# AI EXTRACTIE VAN BUSINESS INFO (verbeterde prompt)
# ------------------------------------------
def ask_ai_for_company_info(url, title, text):

    prompt = f"""
You are an expert in extracting business fundamentals from messy website text.

Your task:
Scan the ENTIRE provided content and extract *any* business intelligence signals.

Be extremely proactive:
Even small hints like “we operate in 6 countries”, “team of 120”, “HQ in Amsterdam”, 
“€5M Series A”, “Offices in Copenhagen / Stockholm / Oslo” MUST be captured.

If something is uncertain, guess the MOST LIKELY answer but keep it short.

Return STRICT VALID JSON ONLY with EXACTLY these fields:

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

Rules:
- Look for HQ using any address, city, country mentions, “HQ”, “headquartered in”, etc.
- Look for team size using patterns like “team of 150”, “120 colleagues”, etc.
- Look for funding using amounts like “€18M”, “Series A”, “Seed round”.
- Look for office locations using ANY city list, region description, etc.
- Look for traction signals: new features, partnerships, growth claims, hiring spikes.
- Infer competitors from industry if not explicitly listed.
- If something is NOT found, return "" or null.

CONTENT SOURCE:
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
# MAIN SCRAPER FUNCTIE (MET MULTI-PAGE SCRAPING)
# ------------------------------------------
def scrape_website(url):
    base = fetch_page_text(url)
    if base["error"]:
        return {"error": base["error"]}

    title = base["title"] or "Geen titel"
    text = base["text"] or ""

    # ⭐ Combineer homepage + subpages voor betere AI
    full_text = text

    for link in base["subpages"][:5]:   # max 5 extra pagina’s
        try:
            r = requests.get(link, headers={"User-Agent": "RivalBot/1.0"}, timeout=10)
            if r.status_code == 200:
                soup = BeautifulSoup(r.text, "html.parser")
                extra = soup.get_text(separator=" ", strip=True)
                if extra:
                    full_text += "\n" + extra[:5000]
        except:
            pass

    combined_text = full_text[:15000]

    # Mooie omschrijving op basis van combined_text
    description = generate_ai_description(combined_text)

    # AI business intelligence feed with extended context
    ai = ask_ai_for_company_info(url, title, combined_text)

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





