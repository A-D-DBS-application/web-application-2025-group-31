# 🚀 Rival MVP — Competitive Intelligence Dashboard

**Partner:** StarApps  
**Projectgroep:** UGent – Business Informatics  
**Deadline:** 19 december 2025  

Rival is een webapplicatie die ondernemers en analisten helpt om **bedrijven en concurrenten te analyseren** op basis van publiek beschikbare data.  
De MVP werd ontwikkeld als proof of concept binnen het vak *Application Development* aan de Universiteit Gent.

---

## Overzicht

**Doel:**  
Rival automatiseert bedrijfsanalyse door informatie over websites, bedrijven en concurrenten te verzamelen.  
Gebruikers kunnen:
- een bedrijfs-URL invoeren om automatisch een baseline rapport te genereren;
- bedrijven beheren via een dashboard;
- websites scrapen voor basisinformatie;
- meldingen en watchlists bekijken;
- data beheren die rechtstreeks wordt opgeslagen in **Supabase** (PostgreSQL).

---

## Belangrijkste Functionaliteiten

| Functie | Beschrijving |
|----------|---------------|
| 🔐 **Login / Register** | Gebruikers kunnen zich registreren en inloggen. |
| 🏠 **Dashboard** | Hoofdscherm met scraper, alerts en watchlist. |
| 🏢 **Bedrijvenbeheer** | Lijst van bedrijven uit Supabase, met mogelijkheid om nieuwe toe te voegen. |
| 🌐 **Web Scraper** | Analyseert websites en toont titel, meta description en H1-koppen. |
| 🧾 **Supabase-integratie** | Alle bedrijfsgegevens worden rechtstreeks opgeslagen in de cloud. |
| ⚙️ **Modelstructuur** | Volledige SQLAlchemy-modellen voor Company, Report, Metric, AuditLog, enz. |

---

## 🧱 Projectstructuur

