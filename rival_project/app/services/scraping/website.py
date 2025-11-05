from bs4 import BeautifulSoup
import requests

class WebsiteScraper:
    def __init__(self, url):
        self.url = url

    def fetch_content(self):
        try:
            response = requests.get(self.url)
            response.raise_for_status()  # Raise an error for bad responses
            return response.text
        except requests.RequestException as e:
            print(f"Error fetching {self.url}: {e}")
            return None

    def parse_content(self, html_content):
        soup = BeautifulSoup(html_content, 'html.parser')
        # Example: Extracting the title of the webpage
        title = soup.title.string if soup.title else 'No title found'
        return title

    def scrape(self):
        html_content = self.fetch_content()
        if html_content:
            return self.parse_content(html_content)
        return None

# Example usage:
# scraper = WebsiteScraper('https://example.com')
# print(scraper.scrape())