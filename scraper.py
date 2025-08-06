
import requests
from bs4 import BeautifulSoup
import json
import time
import random
from fake_useragent import UserAgent

class WebScraper:
    def __init__(self):
        self.session = requests.Session()
        self.ua = UserAgent()

    def _get_headers(self):
        return {
            'User-Agent': self.ua.random,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        }

    def fetch_page(self, url):
        try:
            headers = self._get_headers()
            response = self.session.get(url, headers=headers, timeout=10)
            response.raise_for_status()  # Raise an HTTPError for bad responses (4xx or 5xx)
            return response.text
        except requests.exceptions.RequestException as e:
            print(f"Error fetching {url}: {e}")
            return None

    def parse_html(self, html_content):
        if html_content:
            return BeautifulSoup(html_content, 'lxml')
        return None

    def scrape(self, url):
        print(f"Scraping: {url}")
        html = self.fetch_page(url)
        if html:
            soup = self.parse_html(html)
            if soup:
                # Example: Extract all paragraph texts
                paragraphs = [p.get_text() for p in soup.find_all('p')]
                return {"url": url, "paragraphs": paragraphs}
        return None

if __name__ == "__main__":
    scraper = WebScraper()
    # Example usage: Replace with a URL you want to scrape
    example_url = "https://www.google.com"
    data = scraper.scrape(example_url)
    if data:
        print("Scraped data:")
        print(json.dumps(data, indent=2))
    else:
        print("Failed to scrape data.")


