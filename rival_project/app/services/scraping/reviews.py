from bs4 import BeautifulSoup
import requests

def scrape_reviews(url):
    response = requests.get(url)
    if response.status_code != 200:
        return None

    soup = BeautifulSoup(response.text, 'html.parser')
    reviews = []

    for review in soup.find_all('div', class_='review'):
        title = review.find('h3', class_='review-title').text.strip()
        content = review.find('p', class_='review-content').text.strip()
        rating = review.find('span', class_='review-rating').text.strip()
        
        reviews.append({
            'title': title,
            'content': content,
            'rating': rating
        })

    return reviews

def save_reviews_to_db(reviews):
    # Placeholder for database saving logic
    pass

def get_reviews(url):
    reviews = scrape_reviews(url)
    if reviews:
        save_reviews_to_db(reviews)
    return reviews