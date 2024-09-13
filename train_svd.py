import pandas as pd
from surprise import Dataset, Reader, SVD, accuracy
from surprise.model_selection import train_test_split
import pickle

# Load the scraped ratings data
df_ratings = pd.read_csv('letterboxd_user_ratings.csv')

# Prepare the data for Surprise
reader = Reader(rating_scale=(1, 5))
data = Dataset.load_from_df(df_ratings[['username', 'movie_slug', 'rating']], reader)

# Split into train and test sets
trainset, testset = train_test_split(data, test_size=0.2)

# Train the SVD model
svd_model = SVD()
svd_model.fit(trainset)

# Evaluate the model
predictions = svd_model.test(testset)
accuracy.rmse(predictions)

# Save the trained model (optional)
with open('svd_model.pkl', 'wb') as model_file:
    pickle.dump(svd_model, model_file)

# Function to generate top N recommendations for a user
def get_recommendations_for_user(user_id, model, n=5):
    all_movie_ids = df_ratings['movie_slug'].unique()
    rated_movies = df_ratings[df_ratings['username'] == user_id]['movie_slug'].unique()
    movies_to_predict = [movie for movie in all_movie_ids if movie not in rated_movies]
    predictions = [model.predict(user_id, movie_id) for movie_id in movies_to_predict]
    recommendations = sorted(predictions, key=lambda x: x.est, reverse=True)
    return recommendations[:n]

# Example: Get top 5 recommendations for a user
user_id = 'deathproof'  # Replace with actual user ID from your data
recommendations = get_recommendations_for_user(user_id, svd_model)

# Display the recommended movies
for rec in recommendations:
    print(f"Movie: {rec.iid}, Predicted Rating: {rec.est}")
