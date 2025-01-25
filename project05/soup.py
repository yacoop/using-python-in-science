import requests
from bs4 import BeautifulSoup
import json
import re
import argparse

parser = argparse.ArgumentParser(description="Site scraping")
parser.add_argument(
    "--file",
    "-f",
    type=str,
    default='books.json',
    help="Name of the save file",
)
args = parser.parse_args()
name = args.file

# URL of the Goodreads list
url = "https://www.goodreads.com/list/show/1.Best_Books_Ever?ref=ls_pl_car_0"

# Mimic a browser by setting headers
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36',
    'Accept-Language': 'en-US,en;q=0.9'
}

res = requests.get(url, headers=headers)

# Check if the request was successful
if res.status_code == 200:
    soup = BeautifulSoup(res.text, 'html.parser')

    # Find all book rows
    books = soup.find_all('tr', {'itemtype': 'http://schema.org/Book'})

    book_list = []

    for book in books:
        rank = float(book.find('td', class_='number').get_text(strip=True))  # Rank
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
            "Number of Ratings": num_ratings
        })

    # Print the scraped data in JSON format
    print(json.dumps(book_list, ensure_ascii=False, indent=4))

    # Optionally, save to a file
    with open(f'project05/{name}', 'w') as file:
        json.dump(book_list, file, indent=4)
else:
    print(f"Failed to retrieve the website, status code: {res.status_code}")
