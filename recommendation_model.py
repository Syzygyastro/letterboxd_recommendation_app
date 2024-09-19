import pandas as pd
from surprise import Dataset, Reader
from surprise import SVD
from surprise.model_selection import train_test_split

# Example dataset: Replace this with actual data from your project (e.g., Letterboxd scraped data)
ratings_dict = {
    'user_id': [1, 1, 1, 2, 2, 2, 3, 3, 3],
    'item_id': [101, 102, 103, 101, 102, 104, 101, 103, 104],
    'rating': [5, 3, 4, 4, 2, 5, 5, 3, 4]
}

# Load the data into a DataFrame
df = pd.DataFrame(ratings_dict)

# Convert the DataFrame into a Surprise Dataset
reader = Reader(rating_scale=(1, 5))
data = Dataset.load_from_df(df[['user_id', 'item_id', 'rating']], reader)

# Train the SVD model
def train_svd_model():
    # Split the data into train and test sets
    trainset, testset = train_test_split(data, test_size=0.25)
    
    # Create and train the SVD model
    model = SVD()
    model.fit(trainset)
    
    # Return the trained model
    return model

# Function to get movie recommendations for a given user
def get_recommendations(user_id, n=5):
    # Train the model (or load a pre-trained model if applicable)
    model = train_svd_model()

    # List of all unique movies in the dataset
    all_movie_ids = df['item_id'].unique()

    # Get the movies that the user has already rated
    rated_movies = df[df['user_id'] == user_id]['item_id'].unique()

    # Predict ratings for all movies the user hasn't rated yet
    movies_to_predict = [movie for movie in all_movie_ids if movie not in rated_movies]

    # Predict ratings and recommend the top N movies
    predictions = [model.predict(user_id, movie_id) for movie_id in movies_to_predict]
    recommendations = sorted(predictions, key=lambda x: x.est, reverse=True)

    # Return the top N movie recommendations
    return [{"movie_id": rec.iid, "predicted_rating": rec.est} for rec in recommendations[:n]]
