# similarity.py

# Definieer de gewichten voor de verschillende attributen
gewichten = {
    "target_segment": 0.40,
    "key_features": 0.30,
    "product_description": 0.20,
    "pricing": 0.10,
}

def woorden(text):
    """
    Splits tekst in woorden en zet om naar kleine letters.
    (Eenvoudig gehouden: split op spaties + lowercase)
    """
    if not text:
        return set()
    return set(woord.strip().lower() for woord in text.split() if woord.strip())

def text_similarity(a, b):
    """
    Bereken de Jaccard-similariteit tussen twee teksten op woordniveau:
    0.0 voor geen overlap, 1.0 voor identiek.
    """
    A = woorden(a)
    B = woorden(b)
    if not A and not B:
        return 1.0  # Beide leeg → identiek
    if not A or not B:
        return 0.0  # Eén is leeg → geen overlap
    return len(A & B) / len(A | B)

def list_similarity(a, b):
    """
    Bereken de Jaccard-similariteit tussen twee lijsten.
    """
    A = set(a or [])
    B = set(b or [])
    if not A and not B:
        return 1.0  # Beide leeg → identiek
    if not A or not B:
        return 0.0  # Eén is leeg → geen overlap
    return len(A & B) / len(A | B)

def similarity_score(company_a, company_b):
    """
    Bereken de gewogen similariteitsscore tussen twee bedrijven.
    -> retourneer een percentagescore tussen 0 en 100

    Fix: velden die ontbreken (leeg/None) worden NIET meegerekend in totaal_gewicht,
    zodat je geen 'straf' krijgt door missing data.
    """
    score = 0.0
    totaal_gewicht = 0.0

    # Target Segment
    gewicht = gewichten["target_segment"]
    if company_a.target_segment and company_b.target_segment:
        sim = text_similarity(company_a.target_segment, company_b.target_segment)
        score += sim * gewicht
        totaal_gewicht += gewicht

    # Key Features
    gewicht = gewichten["key_features"]
    if company_a.key_features is not None and company_b.key_features is not None:
        sim = list_similarity(company_a.key_features, company_b.key_features)
        score += sim * gewicht
        totaal_gewicht += gewicht

    # Product Description
    gewicht = gewichten["product_description"]
    if company_a.product_description and company_b.product_description:
        sim = text_similarity(company_a.product_description, company_b.product_description)
        score += sim * gewicht
        totaal_gewicht += gewicht

    # Pricing
    gewicht = gewichten["pricing"]
    if company_a.pricing and company_b.pricing:
        sim = text_similarity(company_a.pricing, company_b.pricing)
        score += sim * gewicht
        totaal_gewicht += gewicht

    if totaal_gewicht == 0:
        return 0.0

    return (score / totaal_gewicht) * 100.0


# -----------------------------
# Sector filtering (nieuw)
# -----------------------------

def _get_sector(company):
    """
    Haal sector/industry veld op (pas desnoods namen aan jouw model aan).
    """
    # meest waarschijnlijke veldnamen:
    for attr in ("sector", "industry", "category"):
        val = getattr(company, attr, None)
        if val:
            return str(val).strip().lower()
    return None

def filter_by_sector(target_company, all_companies):
    """
    Behoud alleen bedrijven met dezelfde sector als target.
    Als target geen sector heeft, return alle bedrijven (geen filter).
    """
    target_sector = _get_sector(target_company)
    if not target_sector:
        return list(all_companies)

    filtered = []
    for c in all_companies:
        if c.company_id == target_company.company_id:
            continue
        if _get_sector(c) == target_sector:
            filtered.append(c)

    return filtered


def top_similar_companies(target_company, all_companies, top_n=5):
    """
    Vind de top N meest vergelijkbare bedrijven voor een gegeven bedrijf.
    Retourneer een lijst van (bedrijf, score) tuples, gesorteerd op score.
    """
    scores = []
    for company in all_companies:
        if company.company_id == target_company.company_id:
            continue
        score = round(similarity_score(target_company, company), 2)
        scores.append((company, score))

    scores.sort(key=lambda x: x[1], reverse=True)
    return scores[:top_n]


def top_similar_companies_in_same_sector(target_company, all_companies, top_n=5):
    """
    Top N vergelijkbare bedrijven, maar ALLEEN binnen dezelfde sector.
    Dit voorkomt vreemde matches (bv. Burger King ↔ CeraVe).
    """
    candidates = filter_by_sector(target_company, all_companies)
    return top_similar_companies(target_company, candidates, top_n=top_n)


def top_similar_companies_ranked_only(target_company, all_companies, top_n=5):
    """
    Geeft alleen de top N bedrijven terug (op volgorde), zonder scores.
    """
    ranked = top_similar_companies(target_company, all_companies, top_n=top_n)
    return [company for company, _score in ranked]


