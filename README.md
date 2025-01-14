
# Letterboxd Recommendation App 🎥
https://syzygy-lttrbxd-movie-recc.netlify.app/  
  
The Letterboxd Recommendation App is a web application that provides personalized movie recommendations based on user ratings from Letterboxd. By leveraging collaborative filtering techniques, the app suggests films that align with a user's unique preferences.

## Features

- **Personalized Recommendations:** Delivers movie suggestions tailored to individual user tastes.
- **Collaborative Filtering:** Employs Singular Value Decomposition (SVD) to analyze user rating patterns and predict preferences.
- **Web Interface:** Offers an intuitive interface for users to input their Letterboxd username and receive recommendations.

## Technologies Used

- **Backend:** Python, Flask
- **Frontend:** HTML, CSS, JavaScript
- **Machine Learning:** Surprise library for building the recommendation model
- **Data Handling:** Pandas for data manipulation
- **Web Scraping:** Beautiful Soup and Requests for extracting user ratings from Letterboxd

## Setup Instructions

### 1. Clone the Repository
`git clone https://github.com/Syzygyastro/letterboxd_recommendation_app.git`

### 2. Navigate to the Project Directory
`cd letterboxd_recommendation_app`

### 3. Set Up a Virtual Environment
`python -m venv env`
`source env/bin/activate  # On Windows: env\Scripts\activate`

### 4. Install Dependencies
`pip install -r requirements.txt`

### 5. Train the Recommendation Model
 Ensure you have a dataset of user ratings in CSV format.
 The provided script `train_svd.py` can be used to train the model.
`python train_svd.py`

 This will generate a `svd_model.pkl` file containing the trained model.

### 6. Run the Application
`flask run`
### Access the app at `http://localhost:5000`

## Note
### Ensure your Letterboxd ratings are publicly accessible for the app to retrieve and analyze your data effectively.
