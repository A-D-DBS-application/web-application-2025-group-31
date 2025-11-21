import requests
from bs4 import BeautifulSoup
import json
import re


# -----------------------------
# JSON-LD extraction
# -----------------------------
def extract_json_ld(soup):
    """Zoekt JSON-LD structured data (Company schema.org) op."""
    result = {}
    json_ld_tags = soup.find_all("script", type="application/ld+json")

    for tag in json_ld_tags:
        try:
            data = json.loads(tag.string)
            if isinstance(data, list):
                for block in data:
                    if isinstance(block, dict) and block.get("@type"):
                        result.update(block)
            elif isinstance(data, dict) and data.get("@type"):
                result.update(data)
        except:
            continue

    return result


# -----------------------------
# Fallback extractors (regex op page text)
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
    """Premium scraper voor alleen Company-kolommen."""
    try:
        response = requests.get(url, headers={"User-Agent": "RivalBot/2.0"}, timeout=10)

        if response.status_code != 200:
            return {"error": f"Kon pagina niet ophalen (status {response.status_code})"}

        soup = BeautifulSoup(response.text, "html.parser")
        text = soup.get_text(" ", strip=True)

        # --- Basic ---
        title = soup.title.string.strip() if soup.title else "Geen titel gevonden"

        meta_desc = soup.find("meta", attrs={"name": "description"})
        meta_desc = meta_desc["content"].strip() if meta_desc else None

        headings = [h.get_text(strip=True) for h in soup.find_all("h1")]

        # --- JSON-LD ---
        json_ld = extract_json_ld(soup)

        # Headquarters
        headquarters = None
        if isinstance(json_ld.get("address"), dict):
            addr = json_ld["address"]
            headquarters = addr.get("addressLocality") or addr.get("addressRegion")

        if not headquarters:
            headquarters = extract_headquarters(text)

        # Team size
        team_size = json_ld.get("numberOfEmployees")
        if not team_size:
            team_size = extract_team_size(text)

        # Funding
        funding = json_ld.get("funding")
        if not funding:
            funding = extract_funding(text)

        # Return only Company fields
        return {
            "url": url,
            "title": title,
            "description": meta_desc or "Geen meta description",
            "headings": headings,
            "headquarters": headquarters,
            "team_size": team_size,
            "funding": funding,
        }

    except Exception as e:
        return {"error": str(e)}

