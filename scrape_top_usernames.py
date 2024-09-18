# scrape_top_usernames.py
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
def scrape_top_users_concurrently(num_users, max_workers):
    users = set()  # Use a set to avoid duplicates
    page_number = 1

    # Continue scraping until we have enough users
    while len(users) < num_users:
        pages_to_scrape = list(range(page_number, page_number + max_workers))

        with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = {executor.submit(scrape_single_page, page): page for page in pages_to_scrape}

            for future in concurrent.futures.as_completed(futures):
                try:
                    page_users = future.result()
                    if page_users:
                        users.update(page_users)  # Add users, using set to avoid duplicates

                    # If we have enough users, stop collecting more
                    if len(users) >= num_users:
                        users = set(list(users)[:num_users])  # Ensure we don't have more than num_users
                        break
                except Exception as exc:
                    print(f"Error processing page: {exc}")

        page_number += max_workers

    return list(users)  # Return exactly the number of users you need


# print(len(scrape_top_users_concurrently(num_users=100, max_workers=1)))

