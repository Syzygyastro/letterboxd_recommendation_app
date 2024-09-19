import asyncio
import os
import aiohttp
from dotenv import load_dotenv
from flask import Flask, request, jsonify
from flask_cors import CORS
import pandas as pd
from surprise import Dataset, Reader, SVD
from tmdbv3api import TMDb, Movie
import re
# Import the scraping function from scrape_user_ratings.py
from scrape_top_user_ratings import scrape_all_watched_movies, scrape_user_ratings

# Only load environment variables from .env file if not in production
if os.environ.get('FLASK_ENV') != 'production':
    load_dotenv()
    
# Access the TMDB_API_KEY environment variable
tmdb_api_key = os.getenv('TMDB_API_KEY')
tmdb = TMDb()
tmdb.api_key = tmdb_api_key  # Replace with your TMDb API key
movie = Movie()

# Load the existing ratings dataset (1000 users)
df_ratings = pd.read_csv('letterboxd_user_ratings.csv')

app = Flask(__name__) 
CORS(app)

# Function to fetch poster URL from TMDb
def get_movie_poster(movie_slug):
    # print(f"TMDb API Key: {tmdb_api_key}")  # Add this to your app temporarily
    movie_slug = re.sub(r'-\d{4}$', '', movie_slug)
    # print(movie_slug)
    search_result = movie.search(movie_slug.replace('-', ' '))
    # print(search_result)
    if search_result and len(search_result) > 0:
        poster_path = search_result[0].poster_path
        return f"https://image.tmdb.org/t/p/w500{poster_path}" if poster_path else None
    return None



# Function to train an SVD model using the combined dataset
def train_combined_model(user_ratings_df):
    # Combine the user's ratings with the existing 1000 users' ratings
    combined_df = pd.concat([df_ratings, user_ratings_df])

    # Create a Surprise dataset from the combined ratings
    reader = Reader(rating_scale=(1, 5))
    data = Dataset.load_from_df(combined_df[['username', 'movie_slug', 'rating']], reader)

    # Build the full trainset and train the SVD model
    trainset = data.build_full_trainset()
    svd_model = SVD()
    svd_model.fit(trainset)
    return svd_model

# Function to generate recommendations using the trained model
def get_recommendations_for_user(user_ratings_df, watched_movies, model, n=5):
    # Get all movie slugs from the combined dataset (i.e., top 1000 users' data)
    all_movie_ids = df_ratings['movie_slug'].unique()
    # Get the list of movies the user has watched
    watched_movie_set = set(watched_movies)
    # Get the list of movies the user has already rated
    rated_movies = user_ratings_df['movie_slug'].unique()

    # Filter out movies the user has already watched
    movies_to_predict = [movie for movie in all_movie_ids if movie not in watched_movie_set]

    # Predict ratings for all unseen movies
    predictions = [model.predict(user_ratings_df.iloc[0]['username'], movie_id) for movie_id in movies_to_predict]

    # Sort the predicted ratings in descending order
    recommendations = sorted(predictions, key=lambda x: x.est, reverse=True)

    # Return the top N recommendations
    return recommendations[:n]

@app.route('/recommend', methods=['POST'])
async def recommend():
    print("Request received!")
    data = request.get_json()
    username = data.get('username')

    # Scrape all the user's ratings (using the imported function)
    user_ratings = await scrape_user_ratings(username)
    user_ratings_df = pd.DataFrame(user_ratings)

    if user_ratings_df is None or user_ratings_df.empty:
        return jsonify({"error": "Could not scrape user data or user has no ratings."}), 404

    # Scrape all the user's watched movies (rated, hearted, or just watched)
    semaphore = asyncio.Semaphore(5)
    async with aiohttp.ClientSession() as session:
        watched_movies = await scrape_all_watched_movies(session, username, semaphore, max_pages=10)
    if not watched_movies:
        return jsonify({"error": "Could not scrape watched movies or user has no watched movies."}), 404
    
    await asyncio.sleep(0.250)
    
    # Train the SVD model using the user's ratings and the existing 1000 users' ratings
    svd_model = train_combined_model(user_ratings_df)

    # Generate movie recommendations using the trained model
    recommendations = get_recommendations_for_user(user_ratings_df, watched_movies, svd_model)

    # Format the recommendations for the client
    recommendations_formatted = [{
        "slug": rec.iid,
        "poster_url": get_movie_poster(rec.iid),  # Use TMDb to get the poster URL
        "rating": rec.est
    } for rec in recommendations]

    return jsonify({"recommendations": recommendations_formatted})

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
