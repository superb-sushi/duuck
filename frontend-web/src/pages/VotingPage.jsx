import React, { useEffect, useState } from 'react';
import axios from 'axios';

const VotingPage = () => {
  const [videos, setVideos] = useState([]);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchVideos = async () => {
      try {
        const response = await axios.get('/bounty/1/videos'); // Replace 1 with actual bounty ID
        setVideos(response.data.sort(() => Math.random() - 0.5)); // Randomize order
      } catch (err) {
        setError('Failed to fetch videos.');
      }
    };

    fetchVideos();
  }, []);

  const voteForVideo = async (videoId) => {
    try {
      await axios.post(`/bounty/1/vote`, { // Replace 1 with actual bounty ID
        video_id: videoId,
        user_handle: "user1", // Replace with actual user handle
      });
      alert('Vote cast successfully!');
    } catch (err) {
      alert('Failed to cast vote.');
    }
  };

  return (
    <div>
      <h1>Vote for Videos</h1>
      {error && <p>{error}</p>}
      <ul>
        {videos.map((video) => (
          <li key={video.id}>
            <h2>{video.title}</h2>
            <button onClick={() => voteForVideo(video.id)}>Vote</button>
          </li>
        ))}
      </ul>
    </div>
  );
};

export default VotingPage;
