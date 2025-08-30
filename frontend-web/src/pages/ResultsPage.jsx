import React, { useEffect, useState } from 'react';
import axios from 'axios';

const ResultsPage = () => {
  const [results, setResults] = useState([]);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchResults = async () => {
      try {
        const response = await axios.get('/bounty/1/winners'); // Replace 1 with actual bounty ID
        setResults(response.data.winners);
      } catch (err) {
        setError('Failed to fetch results.');
      }
    };

    fetchResults();
  }, []);

  return (
    <div>
      <h1>Results</h1>
      {error && <p>{error}</p>}
      <ul>
        {results.map((result, index) => (
          <li key={result.video_id}>
            <h2>#{index + 1}: Video ID {result.video_id}</h2>
            <p>Vote Count: {result.vote_count}</p>
          </li>
        ))}
      </ul>
    </div>
  );
};

export default ResultsPage;
