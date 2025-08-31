import React, { useState, useEffect } from 'react';
import axios from 'axios';

const VideoSubmissionPage = () => {
  const [bounties, setBounties] = useState([]);
  const [title, setTitle] = useState('');
  const [bountyId, setBountyId] = useState(null);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchBounties = async () => {
      try {
        const response = await axios.get('/bounty');
        setBounties(Array.isArray(response.data) ? response.data : []);
      } catch (err) {
        setError('Failed to fetch bounties.');
      }
    };

    fetchBounties();
  }, []);

  const handleSubmit = async (e) => {
    e.preventDefault();

    try {
      const response = await axios.post('/video/submit', {
        title,
        bounty_id: bountyId,
        creator_id: 1, // Replace with actual creator ID
      });
      alert(response.data.message);
    } catch (err) {
      setError('Failed to submit video.');
    }
  };

  return (
    <div>
      <h1>Submit Video</h1>
      {error && <p>{error}</p>}
      <form onSubmit={handleSubmit}>
        <label>
          Title:
          <input
            type="text"
            value={title}
            onChange={(e) => setTitle(e.target.value)}
          />
        </label>
        <br />
        <label>
          Select Bounty:
          <select
            value={bountyId}
            onChange={(e) => setBountyId(Number(e.target.value))}
          >
            <option value="">Select a bounty</option>
            {bounties.map((bounty) => (
              <option key={bounty.id} value={bounty.id}>
                {bounty.title}
              </option>
            ))}
          </select>
        </label>
        <br />
        <button type="submit">Submit</button>
      </form>
    </div>
  );
};

export default VideoSubmissionPage;
