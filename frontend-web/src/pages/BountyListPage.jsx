import React, { useEffect, useState } from 'react';
import api from '../api';

const BountyListPage = () => {
  const [bounties, setBounties] = useState([]);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchBounties = async () => {
      try {
        const response = await api.get('/bounty');
        console.log('Fetched bounties:', response.data); // Debugging log
        setBounties(Array.isArray(response.data) ? response.data : []);
      } catch (err) {
        setError('Failed to fetch bounties.');
      }
    };

    fetchBounties();
  }, []);

  const followBounty = async (bountyId) => {
    try {
      await api.post(`/bounty/${bountyId}/follow`, { user_id: 1 }); // Replace with actual user ID
      alert('Bounty followed successfully!');
    } catch (err) {
      alert('Failed to follow bounty.');
    }
  };

  return (
    <div>
      <h1>Top Bounties</h1>
      {error && <p>{error}</p>}
      <ul>
        {bounties.length > 0 ? (
          bounties.map((bounty) => (
            <li key={bounty.id}>
              <h2>{bounty.title}</h2>
              <p>{bounty.description}</p>
              <p>Total Donations: ${bounty.total_donations}</p>
              <button onClick={() => followBounty(bounty.id)}>Follow</button>
            </li>
          ))
        ) : (
          <p>No bounties available.</p>
        )}
      </ul>
    </div>
  );
};

export default BountyListPage;
