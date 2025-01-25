import requests
from bs4 import BeautifulSoup
import json
import re
from concurrent.futures import ThreadPoolExecutor

# Mimic a browser by setting headers
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36',
    'Accept-Language': 'en-US,en;q=0.9'
}

def scrape_url(url):
    """Scrapes a single URL and returns the parsed book data."""
    try:
        res = requests.get(url, headers=headers)
        if res.status_code != 200:
            print(f"Failed to retrieve {url}, status code: {res.status_code}")
            return []

        soup = BeautifulSoup(res.text, 'html.parser')

        # Find all book rows
        books = soup.find_all('tr', {'itemtype': 'http://schema.org/Book'})
        listname = soup.find('h1', class_='gr-h1 gr-h1--serif').get_text(strip=True)
        book_list = []

        for book in books:
            rank = int(book.find('td', class_='number').get_text(strip=True))  # Rank
            title = book.find('a', class_='bookTitle').get_text(strip=True)  # Title
            author = book.find('a', class_='authorName').get_text(strip=True)  # Author

            # Handle ratings
            rating_text = book.find('span', class_='minirating').get_text(strip=True)  # Full minirating text
            rating = float(re.search(r'\d+\.\d+', rating_text).group())

            # Handle number of ratings
            num_ratings_text = book.find('span', class_='minirating').get_text(strip=True).split(' — ')[-1]  # Ratings text
            num_ratings = int(num_ratings_text.split(' ')[0].replace(',', ''))

            # Append data to the list
            book_list.append({
                "Rank": rank,
                "Title": title,
                "Author": author,
                "Rating": rating,
                "Number of Ratings": num_ratings,
                "list": listname,
            })

        return book_list

    except Exception as e:
        print(f"Error while scraping {url}: {e}")
        return []


urls = ['https://www.goodreads.com/list/show/1?ref=ls_pl_car_0', 'https://www.goodreads.com/list/show/264?ref=ls_pl_car_1', 'https://www.goodreads.com/list/show/43?ref=ls_pl_car_2', 'https://www.goodreads.com/list/show/1043?ref=ls_pl_car_3', 'https://www.goodreads.com/list/show/6?ref=ls_pl_car_4']
# Use ThreadPoolExecutor for parallel scraping
all_books = []
with ThreadPoolExecutor() as executor:
    results = executor.map(scrape_url, urls)
    for result in results:
        all_books.extend(result)

# Save to a file
with open(r'.\project10\books.json', 'w') as file:
    json.dump(all_books, file, indent=4)
