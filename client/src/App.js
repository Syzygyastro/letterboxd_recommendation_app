import React, { useState } from 'react';
import axios from 'axios';
import './App.css'; // Import the CSS file for styling

// Determine base URL based on environment
const BASE_URL = process.env.NODE_ENV === 'production' 
  ? 'https://letterboxd-reccomendation-app-93739ce42474.herokuapp.com'  // Heroku URL for production
  : 'http://localhost:5000';  // Localhost for development

function App() {
  const [username, setUsername] = useState('');
  const [recommendations, setRecommendations] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);  // Start the loading state
    setError('');  // Clear previous errors
    try {
      const response = await axios.post(`${BASE_URL}/recommend`, { username });
      setRecommendations(response.data.recommendations);
    } catch (error) {
      console.error('Error fetching recommendations', error);
      setError('Could not fetch recommendations. Please check the username.');
    } finally {
      setLoading(false);  // End the loading state
    }
  };

  return (
    <div className="app-container">
      <h1 className="title">Letterboxd Movie Recommendations</h1>
      <form onSubmit={handleSubmit} className="form">
        <label htmlFor="username">Enter your Letterboxd Username: </label>
        <input
          type="text"
          id="username"
          value={username}
          onChange={(e) => setUsername(e.target.value)}
          required
          className="input"
        />
        <button type="submit" className="button">Get Recommendations</button>
      </form>

      {loading && <p className="loading">Loading recommendations...</p>}
      {error && <p className="error">{error}</p>}

      <h2 className="subtitle">Movie Recommendations</h2>
      <ul className="recommendation-list">
        {recommendations.length > 0 ? (
          recommendations.map((movie, index) => (
            <li key={index} className="recommendation-item">
              <a href={`https://letterboxd.com/film/${movie.slug}/`} target="_blank" rel="noopener noreferrer" className="movie-link">
                <img src={movie.poster_url} alt={movie.slug} className="movie-poster" />
              </a>
              <div className="movie-details">
                <a href={`https://letterboxd.com/film/${movie.slug}/`} target="_blank" rel="noopener noreferrer" className="movie-title">
                  {movie.slug.replaceAll('-', ' ')}
                </a>
                <p className="movie-rating">Predicted Rating: {movie.rating.toFixed(1)}</p>
              </div>
            </li>
          ))
        ) : (
          <p className="no-recommendations">No recommendations yet.</p>
        )}
      </ul>
    </div>
  );
}

export default App;
