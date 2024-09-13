# scrape_user_ratings.py
import requests
from bs4 import BeautifulSoup
import pandas as pd
import concurrent.futures

# Function to scrape a single page of a user's movie ratings
def scrape_user_ratings_from_page(username, page_number):
    url = f'https://letterboxd.com/{username}/films/ratings/page/{page_number}/'
    try:
        response = requests.get(url, timeout=5)
        response.raise_for_status()
    except (requests.RequestException, requests.Timeout) as e:
        print(f"Failed to retrieve ratings for user {username} on page {page_number}: {e}")
        return []

    # Parse the HTML content
    soup = BeautifulSoup(response.content, 'html.parser')
    poster_containers = soup.find_all('li', class_='poster-container')

    if not poster_containers:
        return []  # No more ratings found

    user_ratings = []
    for poster in poster_containers:
        film_slug_tag = poster.find('div', {'data-film-slug': True})
        film_slug = film_slug_tag['data-film-slug'] if film_slug_tag else None

        rating_tag = poster.find('span', class_='rating')
        rating = rating_tag.text.strip() if rating_tag else "No rating"

        if film_slug and rating != "No rating":
            user_ratings.append({
                'username': username,
                'movie_slug': film_slug,
                'rating': convert_rating_to_numeric(rating)
            })

    return user_ratings

# Helper function to convert the Letterboxd rating stars to numeric value
def convert_rating_to_numeric(rating_str):
    star_mapping = {
        "★": 1, "★★": 2, "★★★": 3, "★★★★": 4, "★★★★★": 5,
        "½": 0.5, "★½": 1.5, "★★½": 2.5, "★★★½": 3.5, "★★★★½": 4.5
    }
    return star_mapping.get(rating_str, 0)

# Function to scrape all pages of a user's ratings
def scrape_user_ratings(username):
    all_ratings = []
    page_number = 1

    while True:
        page_ratings = scrape_user_ratings_from_page(username, page_number)
        if not page_ratings:
            break  # No more ratings on the next page, exit loop
        all_ratings.extend(page_ratings)
        page_number += 1  # Move to the next page

    return all_ratings

# Function to scrape ratings for multiple users concurrently
def scrape_ratings_for_users_concurrently(usernames, max_workers=10):
    all_ratings = []

    # Use ThreadPoolExecutor to scrape ratings for multiple users concurrently
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {executor.submit(scrape_user_ratings, username): username for username in usernames}

        for future in concurrent.futures.as_completed(futures):
            try:
                user_ratings = future.result()
                if user_ratings:
                    all_ratings.extend(user_ratings)
            except Exception as exc:
                print(f"Error processing user: {exc}")

    return pd.DataFrame(all_ratings)

def save_ratings_to_csv(df_all_ratings, filename='letterboxd_user_ratings.csv'):
    df_all_ratings.to_csv(filename, index=False)
    print(f"Scraped ratings saved to '{filename}'")

# Test
usernames = ['deathproof', 'jay', 'kurstboy']  # Replace with actual scraped usernames
df_all_ratings = scrape_ratings_for_users_concurrently(usernames, max_workers=10)
save_ratings_to_csv(df_all_ratings)
