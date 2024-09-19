# scrape_user_ratings.py
import os
import time
import aiohttp
import asyncio
import pandas as pd
from bs4 import BeautifulSoup

from scrape_top_usernames import scrape_top_users_concurrently

# Function to scrape a single page of a user's watched movies asynchronously
async def scrape_watched_movies_from_page(session, username, page_number):
    url = f'https://letterboxd.com/{username}/films/page/{page_number}/'
    try:
        async with session.get(url, timeout=5) as response:
            response.raise_for_status()
            html = await response.text()
    except Exception as e:
        print(f"Failed to retrieve watched movies for user {username} on page {page_number}: {e}")
        return []

    # Parse the HTML content
    soup = BeautifulSoup(html, 'html.parser')
    poster_containers = soup.find_all('li', class_='poster-container')

    if not poster_containers:
        return []  # No more movies found

    watched_movies = []
    for poster in poster_containers:
        film_slug_tag = poster.find('div', {'data-film-slug': True})
        film_slug = film_slug_tag['data-film-slug'] if film_slug_tag else None

        # Check if the movie is watched, rated, or hearted
        if film_slug:
            watched_movies.append(film_slug)

    print(f"Finished scraping page {page_number} for user {username}")
    return watched_movies

# Function to scrape all pages of a user's watched movies asynchronously
async def scrape_all_watched_movies(session, username, semaphore, max_pages=10):
    print(f"Started scraping all watched movies for user {username}")

    # Create a list of tasks to scrape each page concurrently
    tasks = []
    for page_number in range(1, max_pages + 1):
        task = scrape_watched_movies_from_page(session, username, page_number)
        tasks.append(task)

    # Run the tasks concurrently with semaphore limits
    async with semaphore:
        pages_watched_movies = await asyncio.gather(*tasks)

    # Flatten the list of watched movies from all pages
    all_watched_movies = [movie for page_movies in pages_watched_movies if page_movies for movie in page_movies]

    if not all_watched_movies:
        print(f"Finished all pages for user {username} (no watched movies found).")
    else:
        print(f"Finished scraping all watched movies for user {username}.")

    return all_watched_movies


# Function to scrape a single page of a user's movie ratings asynchronously
async def scrape_user_ratings_from_page(session, username, page_number):
    url = f'https://letterboxd.com/{username}/films/page/{page_number}/'
    try:
        async with session.get(url, timeout=5) as response:
            response.raise_for_status()
            html = await response.text()
    except Exception as e:
        print(f"Failed to retrieve ratings for user {username} on page {page_number}: {e}")
        return []

    # Parse the HTML content
    soup = BeautifulSoup(html, 'html.parser')
    poster_containers = soup.find_all('li', class_='poster-container')

    if not poster_containers:
        return []  # No more ratings found

    user_ratings = []
    for poster in poster_containers:
        film_slug_tag = poster.find('div', {'data-film-slug': True})
        film_slug = film_slug_tag['data-film-slug'] if film_slug_tag else None

        rating_tag = poster.find('span', class_='rating')
        rating = rating_tag.text.strip() if rating_tag else "No rating"
        hearted = poster.find('span', class_='like')  # Check if the movie is hearted
        print("is hearted:", hearted)
        if film_slug:
            if rating != "No rating":
                # Movie has a rating, include it
                user_ratings.append({
                    'username': username,
                    'movie_slug': film_slug,
                    'rating': convert_rating_to_numeric(rating)
                })
            elif hearted:
                # Movie is hearted but not rated, assign placeholder rating
                user_ratings.append({
                    'username': username,
                    'movie_slug': film_slug,
                    'rating': 4.0  # Placeholder rating for hearted movies
                })
    # print(f"Finished scraping page {page_number} for user {username}")
    return user_ratings

# Helper function to convert the Letterboxd rating stars to numeric value
def convert_rating_to_numeric(rating_str):
    star_mapping = {
        "★": 1, "★★": 2, "★★★": 3, "★★★★": 4, "★★★★★": 5,
        "½": 0.5, "★½": 1.5, "★★½": 2.5, "★★★½": 3.5, "★★★★½": 4.5
    }
    return star_mapping.get(rating_str, 0)

# Function to scrape all pages of a user's ratings asynchronously
async def scrape_user_ratings(session, username, semaphore, max_pages=10):
    print(f"Started scraping ratings for user {username}")

    # Create a list of tasks to scrape each page concurrently
    tasks = []
    for page_number in range(1, max_pages + 1):
        task = scrape_user_ratings_from_page(session, username, page_number)
        tasks.append(task)

    # Run the tasks concurrently with semaphore limits
    async with semaphore:
        pages_ratings = await asyncio.gather(*tasks)

    # Flatten the list of ratings from all pages
    all_ratings = [rating for page_ratings in pages_ratings if page_ratings for rating in page_ratings]

    if not all_ratings:
        print(f"Finished all pages for user {username} (no ratings found).")
    else:
        print(f"Finished scraping all ratings for user {username}.")

    return all_ratings

# Function to scrape ratings for multiple users asynchronously with max_workers (semaphore)
async def scrape_ratings_for_users_concurrently(usernames, max_workers=10):
    all_ratings = []
    semaphore = asyncio.Semaphore(max_workers)  # Limit concurrency

    async with aiohttp.ClientSession() as session:
        tasks = [scrape_user_ratings(session, username, semaphore) for username in usernames]
        results = await asyncio.gather(*tasks)

        for user_ratings in results:
            if user_ratings:
                print(f"Finished scraping ratings for user {user_ratings[0]['username']}")
                all_ratings.extend(user_ratings)

    return pd.DataFrame(all_ratings)

# Function to save ratings to CSV
def save_ratings_to_csv(df_all_ratings, filename='letterboxd_user_ratings.csv'):
    i = 1
    while os.path.exists(filename):
        filename = f'letterboxd_user_ratings_{i}.csv'
        i += 1
    df_all_ratings.to_csv(filename, index=False)
    print(f"Scraped ratings saved to '{filename}'")

# Test function to scrape top users and their ratings, then save to CSV
# async def main():
    # Step 1: Scrape top users
    # print("Scraping top users...")
    # top_users = await scrape_top_users_concurrently(num_users=100, max_workers=10)
    # print(f"Found {len(top_users)} top users.")

    # # Step 2: Scrape ratings for those top users
    # print("Scraping ratings for top users...")
    # df_all_ratings = await scrape_ratings_for_users_concurrently(top_users, max_workers=5)
    # print(f"Scraped a total of {len(df_all_ratings)}")
    
    # Step 3: Save ratings to CSV using the reusable function
    # save_ratings_to_csv(df_all_ratings)
    
    #Time comparison between 1 worker and 5 workers
    # start_time = time.time()
    # df_all_ratings = await scrape_ratings_for_users_concurrently(top_users, max_workers=4)
    # elapsed_time = time.time() - start_time
    # print(f"Scraped a total of {len(df_all_ratings)} ratings using worker in {elapsed_time:.2f} seconds")
    
    # start_time = time.time()
    # df_all_ratings = await scrape_ratings_for_users_concurrently(["1q79"], max_workers=10)
    # elapsed_time = time.time() - start_time
    # print(f"Scraped a total of {df_all_ratings} ratings using 10 workers in {elapsed_time:.2f} seconds")

    # semaphore = asyncio.Semaphore(5)
    # async with aiohttp.ClientSession() as session:
    #     watched_movies = await scrape_all_watched_movies(session, "1q79", semaphore, max_pages=10)
    # print(watched_movies)
    # start_time = time.time()
    # df_all_ratings = await scrape_ratings_for_users_concurrently(top_users, max_workers=50)
    # elapsed_time = time.time() - start_time
    # print(f"Scraped a total of {len(df_all_ratings)} ratings using 50 workers in {elapsed_time:.2f} seconds")
       
#     await asyncio.sleep(0.250)

# # Running the async scraping task
# if __name__ == "__main__":
#     asyncio.run(main())

