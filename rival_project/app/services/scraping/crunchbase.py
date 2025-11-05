from bs4 import BeautifulSoup
import requests

class CrunchbaseScraper:
    BASE_URL = "https://www.crunchbase.com"

    def __init__(self):
        self.session = requests.Session()

    def get_company_data(self, company_name):
        search_url = f"{self.BASE_URL}/searches/companies.json?query={company_name}"
        response = self.session.get(search_url)
        if response.status_code == 200:
            data = response.json()
            if data['data']['items']:
                company_slug = data['data']['items'][0]['path']
                return self.scrape_company_details(company_slug)
        return None

    def scrape_company_details(self, company_slug):
        company_url = f"{self.BASE_URL}{company_slug}"
        response = self.session.get(company_url)
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            company_info = {
                'name': self.extract_name(soup),
                'description': self.extract_description(soup),
                'founded': self.extract_founded(soup),
                'location': self.extract_location(soup),
                'website': self.extract_website(soup),
            }
            return company_info
        return None

    def extract_name(self, soup):
        return soup.find('h1', class_='profile-name').get_text(strip=True)

    def extract_description(self, soup):
        return soup.find('div', class_='profile-description').get_text(strip=True)

    def extract_founded(self, soup):
        founded_info = soup.find('span', class_='founded-date')
        return founded_info.get_text(strip=True) if founded_info else None

    def extract_location(self, soup):
        location_info = soup.find('span', class_='location')
        return location_info.get_text(strip=True) if location_info else None

    def extract_website(self, soup):
        website_info = soup.find('a', class_='website-link')
        return website_info['href'] if website_info else None

# Example usage:
# scraper = CrunchbaseScraper()
# company_data = scraper.get_company_data("example company")
# print(company_data)