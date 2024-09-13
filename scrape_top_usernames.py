import time
import requests
from bs4 import BeautifulSoup
import concurrent.futures

# Function to scrape a single page of top users
def scrape_single_page(page_number):
    base_url = f"https://letterboxd.com/members/popular/page/{page_number}/"
    try:
        response = requests.get(base_url, timeout=5)  # Set timeout to avoid hanging
        response.raise_for_status()
    except (requests.RequestException, requests.Timeout) as e:
        print(f"Failed to retrieve page {page_number}: {e}")
        return []

    # Parse the HTML content
    soup = BeautifulSoup(response.content, 'html.parser')

    # Extract user profile links
    user_tags = soup.find_all('a', class_='name')
    usernames = [tag['href'].strip('/').split('/')[-1] for tag in user_tags]

    return usernames

# Function to scrape multiple pages concurrently, skipping failed pages
def scrape_top_users_concurrently(num_users=100, max_workers=10):
    users = []
    page_number = 1

    # Continue scraping until we have enough users
    while len(users) < num_users:
        # Create a batch of page numbers to scrape concurrently
        pages_to_scrape = list(range(page_number, page_number + max_workers))

        # Use ThreadPoolExecutor to scrape multiple pages concurrently
        with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = {executor.submit(scrape_single_page, page): page for page in pages_to_scrape}

            for future in concurrent.futures.as_completed(futures):
                try:
                    page_users = future.result()
                    if page_users:
                        users.extend(page_users)
                    # Stop early if we reach the desired number of users
                    if len(users) >= num_users:
                        break
                except Exception as exc:
                    print(f"Error processing page: {exc}")

        # Update page_number for the next batch of pages
        page_number += max_workers

    return users

# start_time = time.time()
# top_users = scrape_top_users_concurrently(1000)
# end_time = time.time()
# print(f"Concurrent Execution Time: {end_time - start_time:.2f} seconds")

# start_time = time.time()
# top_users = scrape_top_users_concurrently(100, max_workers=1)
# end_time = time.time()

# print(f"Single Thread Execution Time: {end_time - start_time:.2f} seconds")
