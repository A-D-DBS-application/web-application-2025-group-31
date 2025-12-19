# Rival MVP — Competitive Intelligence Dashboard

**Partner:** StarApps  
**Projectgroep:** UGent – Business Informatics  
**Deadline:** 19 december 2025  

**Live application (Render):**  
https://web-application-2025-group-31-11.onrender.com

---

## Over het project

Rival is een webapplicatie die ondernemers en analisten helpt om **bedrijven en concurrenten te analyseren** op basis van publiek beschikbare data.  
De MVP werd ontwikkeld als proof of concept binnen de vakken *Algoritmen & datastructuren* en *Databasesystemen* aan de Universiteit Gent.

---

## Overzicht

**Doel**  
Rival automatiseert bedrijfsanalyse door informatie over websites, bedrijven en concurrenten te verzamelen.

Gebruikers kunnen:
- een bedrijfs-URL invoeren om automatisch een baseline rapport te genereren;
- bedrijven beheren via een dashboard;
- websites scrapen voor basisinformatie;
- meldingen en watchlists bekijken;
- data beheren die rechtstreeks wordt opgeslagen in **Supabase** (PostgreSQL).

---

## Belangrijkste functionaliteiten

| Functie | Beschrijving |
|--------|--------------|
| 🔐 **Login / Register** | Gebruikers kunnen zich registreren en inloggen. |
| 🏠 **Dashboard** | Hoofdscherm met scraper, alerts en watchlist. |
| 🏢 **Bedrijvenbeheer** | Lijst van bedrijven uit Supabase, met mogelijkheid om nieuwe toe te voegen. |
| 🌐 **Web Scraper** | Analyseert websites en toont titel, meta description en H1-koppen. |
| 🧾 **Supabase-integratie** | Alle bedrijfsgegevens worden rechtstreeks opgeslagen in de cloud. |
| ⚙️ **Modelstructuur** | Volledige SQLAlchemy-modellen voor Company, Report, Metric, AuditLog, enz. |

---


## Lokale Installatie
Volg deze stappen om een lokale kopie van Rival op je computer te draaien voor ontwikkeling of testen.

1. Vereisten
Zorg ervoor dat je de volgende software hebt geïnstalleerd:

Python 3.10 of hoger.

Git om de repository te clonen.

2. Installatie
Clone de repository en ga naar de projectmap:

Bash

git clone https://github.com/jouw-gebruikersnaam/rival-project.git
cd rival-project
3. Virtuele Omgeving
Het wordt aangeraden om een virtuele omgeving te gebruiken om je dependencies gescheiden te houden:

Bash

# Omgeving aanmaken
python -m venv venv

# Activeren (Windows)
venv\Scripts\activate

# Activeren (Mac/Linux)
source venv/bin/activate
4. Dependencies Installeren
Installeer alle benodigde pakketten, waaronder Flask, SQLAlchemy en de scraper-tools:

Bash

pip install -r requirements.txt
5. Configuratie (Omgevingsvariabelen)
Rival maakt gebruik van Supabase (PostgreSQL) en AI-modellen. Maak een bestand aan genaamd .env in de hoofdmap en voeg daar de volgende gegevens aan toe (vervang de placeholders door je eigen keys):

Codefragment

OPENAI_API_KEY=jouw_openai_key
GOOGLE_API_KEY=jouw_google_key
DATABASE_URL=postgresql://gebruiker:wachtwoord@host:poort/postgres
SECRET_KEY=een_geheime_sleutel_voor_sessies
⚠️ Let op: Deel je .env bestand nooit met anderen en zet het niet op GitHub!

6. De App Starten
Start de Flask development server met het volgende commando:

Bash

flask run
Zodra de server draait, kun je de app bekijken in je browser op http://127.0.0.1:5000.



## Feedback sessions

Audio recordings of the feedback sessions with our project partner:

- **Feedback session 1:**  
  https://drive.google.com/file/d/1HSkTbfF5iNlQhHZGLmBCUQD71RoKzIZs/view?usp=sharing

- **Feedback session 2:**  
    Wegens technische problemen verliep de communicatie deze sprint via een Loom-video. De feedback werd per e-mail ontvangen.

    Thanks voor de loom video - geeft me een duidelijk idee waar jullie vandaag staan. 
    Zou handig zijn om er toch zelf even te kunnen doorlopen, waar staan jullie intussen met het live krijgen via Render? 
    Verder kleinere vragen: 
    Je geeft 3 opties om te exporteren: wat kan ik verwachten in een "VC memo"?
    Hebben jullie een voorbeeld van een newsletter? Hoe is die gestructureerd?

- **Feedback session 3:**  
  https://drive.google.com/file/d/1bfRbiPLT7Ammqkg0QMOAOPu0MHC_rU8_/view?usp=sharing

---


## User stories

🔴 Must-Haves
Baseline Generation
  As an entrepreneur
  I want to paste a company URL (my own or a competitor)
  So that Rival auto-generates a baseline report instead of me spending hours on research

Company Fundamentals
As an entrepreneur
  I want the baseline report to show HQ, office locations, team size, funding history, and traction signals
  So that I instantly understand the company’s fundamentals

Competitor Detection
  As an entrepreneur
  I want Rival to auto-detect and list direct competitors with a similar value proposition and target segment
  So that I can quickly map the competitive landscape

Strategic Signal Highlighting
  As a product strategist
  I want Rival to highlight signals like new features, changed pricing, or new product lines
  So that I can anticipate strategic moves

Market Entry Flagging
  As an entrepreneur
  I want Rival to flag market entry (competitor enters my geography or targets a new segment)
  So that I can adjust my go-to-market before it’s too late

Real-time Dashboard
  As a strategy lead
  I want a real-time dashboard aggregating competitor metrics (pricing, features, reviews, hiring trends)
  So that I can brief leadership with structured facts instead of scattered data

Metric Configuration
  As a product manager
  I want to configure which competitors and metrics to track
  So that I only see what matters for my roadmap

Due Diligence Profiles
  As a VC analyst
  I want quick one-click company profiles with structured data
  So that I can prepare due diligence packs faster

Weekly Digest
  As a user
  I want to opt-in to a weekly digest mail with the latest detected changes
  So that Rival acts as my watchdog without me logging in daily

Audit Logs
  As a compliance/IT admin
  I want exportable audit logs of data sources
  So that I know Rival’s signals come from verifiable, compliant sources

🟡 Should-Haves
Side-by-Side Comparison
  As a strategy team
  I want to compare 2–3 companies side by side
  So that I can quickly benchmark options

Historical Trends
  As a strategy team
  I want to see historical trend graphs
  So that I can detect medium-term patterns

Custom Digest
  As a strategy lead
  I want to customize my weekly digest (competitors, frequency, signals)
  So that the updates are relevant

Export to PDF/Slides
  As a VC associate
  I want a polished PDF/slide export of the baseline report
  So that I can drop findings into an investment memo

Saved Watchlist
  As a team
  I want Rival to maintain a saved watchlist and refresh data weekly
  So that I have a living portfolio of monitored targets

🔵 Could-Haves
Similarity Engine
  As a user
  I want Rival to suggest “similar companies” to ones I track
  So that I can discover adjacent competitors

API Enrichment
  As a data analyst
  I want an API feed of all tracked events
  So that I can enrich our BI tools

Push Alerts
  As a founder
  I want push alerts when a competitor makes a major move
  So that I can react tactically in near real time

Campaign Monitoring
  As a marketing lead
  I want to monitor competitor campaigns/promotions
  So that I can adjust my messaging

AI Insights
  As a product strategist
  I want AI-generated summaries of competitor movements
  So that I can consume insights faster
