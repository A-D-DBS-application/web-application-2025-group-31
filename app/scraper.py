import requests
from bs4 import BeautifulSoup
import json
import re

# -----------------------------
# JSON-LD extraction
# -----------------------------
def extract_json_ld(soup):
    """Zoekt JSON-LD structured data (schema.org) voor bedrijven."""
    result_blocks = []
    json_ld_tags = soup.find_all("script", type="application/ld+json")

    for tag in json_ld_tags:
        try:
            data = json.loads(tag.string)

            # lijst van JSON-LD blokken
            if isinstance(data, list):
                for block in data:
                    if isinstance(block, dict):
                        result_blocks.append(block)

            # enkel blok
            elif isinstance(data, dict):
                result_blocks.append(data)

        except:
            continue

    return result_blocks


# -------------------------------------------
# Office Locations
# -------------------------------------------
def extract_office_locations(json_blocks, text):
    locations = set()

    # JSON-LD
    for block in json_blocks:
        # schema.org/Organization → hasPart of location
        if "location" in block:
            loc = block.get("location")
            if isinstance(loc, list):
                for l in loc:
                    if isinstance(l, dict):
                        city = l.get("address", {}).get("addressLocality")
                        if city:
                            locations.add(city)
            elif isinstance(loc, dict):
                city = loc.get("address", {}).get("addressLocality")
                if city:
                    locations.add(city)

        # Multiple addresses
        if "address" in block:
            addr = block["address"]
            if isinstance(addr, list):
                for a in addr:
                    if isinstance(a, dict):
                        city = a.get("addressLocality")
                        if city:
                            locations.add(city)

    # Regex fallback
    fallback = re.findall(r"(office|located in|based in)\s+([A-Za-z ,]+)", text, re.IGNORECASE)
    for match in fallback:
        city = match[1].strip()
        if len(city) < 40:
            locations.add(city)

    return ", ".join(sorted(locations)) if locations else None


# -------------------------------------------
# Funding History
# -------------------------------------------
def extract_funding_history(text):
    patterns = [
        r"(Series [A-J][^.,;]*)",
        r"(Seed funding[^.,;]*)",
        r"(Pre-seed[^.,;]*)",
        r"(raised\s+[€$]?\s?\d+[.,]?\d*\s*(M|K|million|billion)[^.,;]*)",
        r"(investment round[^.,;]*)",
    ]

    results = []

    for p in patterns:
        matches = re.findall(p, text, re.IGNORECASE)
        for m in matches:
            results.append(m[0] if isinstance(m, tuple) else m)

    return "; ".join(results) if results else None


# -------------------------------------------
# Traction Signals (awards, users, partners)
# -------------------------------------------
def extract_traction_signals(text):
    signals = []

    rules = {
        "customers": r"\b(\d{3,} customers)\b",
        "users": r"\b(\d{3,} users)\b",
        "clients": r"\b(\d{3,} clients)\b",
        "growth": r"(growth rate[^.,;]*)",
        "partners": r"(partner(ed)? with [A-Za-z0-9 ]+)",
        "awards": r"(award[^.,;]*)",
        "milestones": r"(reached [^.,;]*)",
    }

    for label, pattern in rules.items():
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            signals.append(match.group(1))

    return "; ".join(signals) if signals else None


# -----------------------------
# Fallback extractors (HQ, team, total funding)
# -----------------------------
def extract_headquarters(text):
    patterns = [
        r"Headquarters[:\s]+([A-Za-z ,]+)",
        r"Hoofdkantoor[:\s]+([A-Za-z ,]+)",
        r"Based in ([A-Za-z ,]+)",
        r"Located in ([A-Za-z ,]+)",
    ]
    for p in patterns:
        match = re.search(p, text, re.IGNORECASE)
        if match:
            return match.group(1).strip()
    return None


def extract_team_size(text):
    match = re.search(r"(\d{2,5})\s+(employees|team|staff)", text, re.IGNORECASE)
    if match:
        return int(match.group(1))
    return None


def extract_funding(text):
    match = re.search(
        r"([€$]?\s?\d+[.,]?\d*\s?(M|K|million|billion)?)\s+(funding|series)",
        text,
        re.IGNORECASE,
    )
    if match:
        return match.group(1).strip()
    return None


# -----------------------------
# MAIN SCRAPER
# -----------------------------
def scrape_website(url):
    """Premium scraper die alle baseline-informatie ophaalt."""
    try:
        response = requests.get(url, headers={"User-Agent": "RivalBot/2.0"}, timeout=10)

        if response.status_code != 200:
            return {"error": f"Kon pagina niet ophalen (status {response.status_code})"}

        soup = BeautifulSoup(response.text, "html.parser")
        text = soup.get_text(" ", strip=True)

        title = soup.title.string.strip() if soup.title else "Geen titel gevonden"

        meta_desc = soup.find("meta", attrs={"name": "description"})
        meta_desc = meta_desc["content"].strip() if meta_desc else None

        headings = [h.get_text(strip=True) for h in soup.find_all("h1")]

        json_blocks = extract_json_ld(soup)

        # ---- Headquarters ----
        headquarters = None
        for block in json_blocks:
            if isinstance(block.get("address"), dict):
                city = block["address"].get("addressLocality")
                if city:
                    headquarters = city
        if not headquarters:
            headquarters = extract_headquarters(text)

        # ---- Team Size ----
        team_size = None
        for block in json_blocks:
            if block.get("numberOfEmployees"):
                team_size = block.get("numberOfEmployees")
        if not team_size:
            team_size = extract_team_size(text)

        # ---- Total Funding ----
        funding_total = None
        for block in json_blocks:
            if block.get("funding"):
                funding_total = block.get("funding")
        if not funding_total:
            funding_total = extract_funding(text)

        # ---- Office Locations ----
        office_locations = extract_office_locations(json_blocks, text)

        # ---- Funding History ----
        funding_history = extract_funding_history(text)

        # ---- Traction Signals ----
        traction_signals = extract_traction_signals(text)

        return {
            "url": url,
            "title": title,
            "description": meta_desc or "Geen meta description",
            "headings": headings,
            "headquarters": headquarters,
            "team_size": team_size,
            "funding": funding_total,
            "office_locations": office_locations,
            "funding_history": funding_history,
            "traction_signals": traction_signals,
        }

    except Exception as e:
        return {"error": str(e)}
