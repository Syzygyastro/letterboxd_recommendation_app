import React, { useState } from 'react';
import axios from 'axios';
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
    <div style={{ fontFamily: 'Arial, sans-serif', padding: '20px' }}>
      <h1>Letterboxd Movie Recommendations</h1>
      <form onSubmit={handleSubmit} style={{ marginBottom: '20px' }}>
        <label htmlFor="username">Enter your Letterboxd Username: </label>
        <input
          type="text"
          id="username"
          value={username}
          onChange={(e) => setUsername(e.target.value)}
          required
          style={{ padding: '10px', marginRight: '10px', width: '250px' }}
        />
        <button type="submit" style={{ padding: '10px 20px', cursor: 'pointer' }}>Get Recommendations</button>
      </form>

      {loading && <p>Loading recommendations...</p>}
      {error && <p style={{ color: 'red' }}>{error}</p>}

      <h2>Movie Recommendations</h2>
      <ul style={{ listStyle: 'none', padding: 0 }}>
        {recommendations.length > 0 ? (
          recommendations.map((movie, index) => (
            <li key={index} style={{ display: 'flex', alignItems: 'center', marginBottom: '20px' }}>
              <a href={`https://letterboxd.com/film/${movie.slug}/`} target="_blank" rel="noopener noreferrer" style={{ marginRight: '20px' }}>
                <img src={movie.poster_url} alt={movie.slug} style={{ width: '100px', height: '150px', objectFit: 'cover' }} />
              </a>
              <div>
                <a href={`https://letterboxd.com/film/${movie.slug}/`} target="_blank" rel="noopener noreferrer" style={{ textDecoration: 'none', color: 'black', fontSize: '18px', fontWeight: 'bold' }}>
                  {movie.slug.replaceAll('-', ' ')}
                </a>
                <p style={{ margin: 0 }}>Predicted Rating: {movie.rating.toFixed(1)}</p>
              </div>
            </li>
          ))
        ) : (
          <p>No recommendations yet.</p>
        )}
      </ul>
    </div>
  );
}

export default App;
