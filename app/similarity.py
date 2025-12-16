# Definieer de gewichten voor de verschillende attributen
gewichten = {
    "target_segment": 0.40,
    "key_features": 0.30,
    "product_description": 0.20,
    "pricing": 0.10,
}

def woorden(text):
    """
    Splits tekst in woorden, verwijder leestekens en zet om naar kleine letters.
    """
    if not text:
        return set()    
    return set(woord.strip().lower() for woord in text.split() if woord.strip())

def text_similarity(a, b):
    """
    Bereken de Jaccard-similariteit tussen twee woorden:
    0.0 voor geen overlap, 1.0 voor identieke woorden.
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
    """
    score = 0.0
    totaal_gewicht = 0.0

    # Target Segment
    gewicht = gewichten["target_segment"]
    sim = text_similarity(company_a.target_segment, company_b.target_segment)
    score += sim * gewicht
    totaal_gewicht += gewicht

    # Key Features
    gewicht = gewichten["key_features"]
    sim = list_similarity(company_a.key_features, company_b.key_features)
    score += sim * gewicht
    totaal_gewicht += gewicht

    # Product Description
    gewicht = gewichten["product_description"]
    sim = text_similarity(company_a.product_description, company_b.product_description)
    score += sim * gewicht
    totaal_gewicht += gewicht

    # Pricing
    gewicht = gewichten["pricing"]
    sim = text_similarity(company_a.pricing, company_b.pricing)
    score += sim * gewicht
    totaal_gewicht += gewicht

    if totaal_gewicht == 0:
        return 0.0

    # Normaliseer naar percentage
    return (score / totaal_gewicht) * 100.0

def top_similar_companies(target_company, all_companies, top_n=5):
    """
    Vind de top N meest vergelijkbare bedrijven voor een gegeven bedrijf.
    Retourneer een lijst van (bedrijf, score) tuples, gesorteerd op score.
    """
    scores = []
    for company in all_companies:
        if company.company_id == target_company.company_id:
            continue  # Sla hetzelfde bedrijf over
        score = round(similarity_score(target_company, company), 2)
        scores.append((company, score))
    
    # Sorteer op score (hoog naar laag) en neem de top N
    scores.sort(key=lambda x: x[1], reverse=True)
    return scores[:top_n]
    

