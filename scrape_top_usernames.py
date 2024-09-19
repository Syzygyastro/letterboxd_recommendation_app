import time
import aiohttp
import asyncio
from bs4 import BeautifulSoup

# Function to scrape a single page of top users asynchronously
async def scrape_single_page(session, page_number):
    base_url = f"https://letterboxd.com/members/popular/page/{page_number}/"
    try:
        async with session.get(base_url, timeout=5) as response:
            response.raise_for_status()
            html = await response.text()
    except Exception as e:
        print(f"Failed to retrieve page {page_number}: {e}")
        return []

    # Parse the HTML content
    soup = BeautifulSoup(html, 'html.parser')

    # Extract user profile links
    user_tags = soup.find_all('a', class_='name')
    usernames = [tag['href'].strip('/').split('/')[-1] for tag in user_tags]

    return usernames

# Function to scrape multiple pages concurrently using asyncio
async def scrape_top_users_concurrently(num_users, max_workers):
    users = set()  # Use a set to ensure unique users
    page_number = 1

    async with aiohttp.ClientSession() as session:
        while len(users) < num_users:
            # Create a list of tasks for scraping multiple pages concurrently
            tasks = [scrape_single_page(session, page_number + i) for i in range(max_workers)]
            results = await asyncio.gather(*tasks)

            # Flatten the results and add to the set
            for result in results:
                if result:
                    users.update(result)
                if len(users) >= num_users:
                    break

            page_number += max_workers

    return list(users)[:num_users] 

# # Test function to scrape users and performance with changing workers
# async def main():
#     # num_users = 10
#     # max_workers = 5
#     # top_users = await scrape_top_users_concurrently(num_users=num_users, max_workers=max_workers)
#     # print(f"Found {len(top_users)} top users")
    
#     # Test with different number of workers
#     for workers in [100,500]:
#         num_users = 1000
#         start_time = time.time()
#         top_users = await scrape_top_users_concurrently(num_users=num_users, max_workers=workers)
#         elapsed_time = time.time() - start_time
#         print(f"Found {len(top_users)} top users with {workers} workers in {elapsed_time:.2f} seconds")
#     await asyncio.sleep(0.250)  

# # Running the async scraping task
# if __name__ == "__main__":
#     asyncio.run(main())
