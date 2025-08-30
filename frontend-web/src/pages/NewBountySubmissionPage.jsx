import React, { useState } from 'react';
import axios from 'axios';

const NewBountySubmissionPage = () => {
  const [title, setTitle] = useState('');
  const [description, setDescription] = useState('');
  const [initialDonation, setInitialDonation] = useState(0);
  const [similarBounties, setSimilarBounties] = useState([]);
  const [error, setError] = useState(null);

  const handleSubmit = async (e) => {
    e.preventDefault();

    if (initialDonation < 10) {
      alert('Minimum donation is $10.');
      return;
    }

    try {
      const response = await axios.post('/bounty/create', {
        title,
        description,
        creator_id: 1, // Replace with actual user ID
        initial_donation: initialDonation,
      });
      alert(response.data.message);
    } catch (err) {
      setError('Failed to create bounty.');
    }
  };

  const fetchSimilarBounties = async () => {
    try {
      const response = await axios.get('/bounty/similar', {
        params: { title, tags: ['example-tag'] }, // Replace with actual tags if available
      });
      setSimilarBounties(response.data);
    } catch (err) {
      setError('Failed to fetch similar bounties.');
    }
  };

  return (
    <div>
      <h1>Create New Bounty</h1>
      {error && <p>{error}</p>}
      <form onSubmit={handleSubmit}>
        <label>
          Title:
          <input
            type="text"
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            onBlur={fetchSimilarBounties}
          />
        </label>
        <br />
        <label>
          Description:
          <textarea
            value={description}
            onChange={(e) => setDescription(e.target.value)}
          />
        </label>
        <br />
        <label>
          Initial Donation:
          <input
            type="number"
            value={initialDonation}
            onChange={(e) => setInitialDonation(Number(e.target.value))}
          />
        </label>
        <br />
        <button type="submit">Submit</button>
      </form>

      <h2>Similar Bounties</h2>
      <ul>
        {similarBounties.map((bounty) => (
          <li key={bounty.id}>
            <h3>{bounty.title}</h3>
            <p>{bounty.description}</p>
          </li>
        ))}
      </ul>
    </div>
  );
};

export default NewBountySubmissionPage;
