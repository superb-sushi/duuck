import { useEffect, useState } from "react";
import BountyCard from "./BountyCard.js";
import BountyModal from "./BountyModal.js";
import "./styles/BountyPage.css";
import BountyCardOver from "./BountyCardOver.js";

interface Video {
  id: string;
  title: string;
  creator_handle: string;
  views: string;
  thumbnail: string; //ignore this
  duration: string;
  votes: number;
  likes: number;
}

interface Bounty {
  id: string; //
  description: string; //
  prize_pool: number; //
  judging_end: string; //
  current_videos: Video[];
  following: boolean;
}

const mockIdeas: Bounty[] = [
  {
    id: "1",
    description: "24 Hours in Zero Gravity Challenge",
    prize_pool: 32500,
    judging_end: "2025-09-01",
    following: true,
    current_videos: [
      {
        id: "1",
        title: "Testing Zero G Water Drops",
        creator_handle: "spaceguy",
        views: "2.1M",
        thumbnail: "",
        duration: "0:45",
        votes: 1200,
        likes: 10029,
      },
      {
        id: "2",
        title: "Floating Pizza Challenge",
        creator_handle: "foodieflix",
        views: "1.8M",
        thumbnail: "",
        duration: "1:12",
        votes: 980,
        likes: 129,
      },
    ],
  },
  {
    id: "2",
    description: "Living Like It's 1823 for 30 Days",
    prize_pool: 18750,
    judging_end: "2025-09-20",
    following: true,
    current_videos: [
      {
        id: "3",
        title: "Making Candles from Scratch",
        creator_handle: "historymaker",
        views: "950K",
        thumbnail: "",
        duration: "2:34",
        votes: 450,
        likes: 928,
      },
    ],
  },
  {
    id: "3",
    description: "I Bought Every Item in a Gas Station",
    prize_pool: 22500,
    judging_end: "2025-08-10",
    following: false,
    current_videos: [
      {
        id: "4",
        title: "Gas Station Haul Part 1",
        creator_handle: "buyitall",
        views: "3.2M",
        thumbnail: "",
        duration: "8:45",
        votes: 1500,
        likes: 2932,
      },
      {
        id: "5",
        title: "Weird Gas Station Finds",
        creator_handle: "buyitall",
        views: "2.7M",
        thumbnail: "",
        duration: "6:23",
        votes: 1300,
        likes: 293802,
      },
      {
        id: "6",
        title: "Eating Only Gas Station Food",
        creator_handle: "hungryhank",
        views: "1.4M",
        thumbnail: "",
        duration: "12:01",
        votes: 800,
        likes: 3511,
      },
      {
        id: "10",
        title: "Yosemite Gas Station Mukbang",
        creator_handle: "adventuretime101",
        views: "11.1M",
        thumbnail: "",
        duration: "28:39",
        votes: 10000,
        likes: 2000012,
      },
    ],
  },
  {
    id: "4",
    description: "Building the World's Largest Domino Chain",
    prize_pool: 45300,
    judging_end: "2025-10-01",
    following: true,
    current_videos: [
      {
        id: "7",
        title: "Domino Setup Day 1",
        creator_handle: "dominokid",
        views: "1.2M",
        thumbnail: "",
        duration: "15:30",
        votes: 600,
        likes: 294,
      },
    ],
  },
  {
    id: "5",
    description: "Teaching My Grandma to Become a Gamer",
    prize_pool: 8900,
    judging_end: "2025-09-25",
    following: false,
    current_videos: [],
  },
  {
    id: "6",
    description: "Recreating Every Movie Genre in 1 Day",
    prize_pool: 19200,
    judging_end: "2025-09-18",
    following: true,
    current_videos: [
      {
        id: "8",
        title: "Horror Scene Behind the Scenes",
        creator_handle: "filmfanatic",
        views: "890K",
        thumbnail: "",
        duration: "4:17",
        votes: 300,
        likes: 2341,
      },
      {
        id: "9",
        title: "Action Sequence Fails",
        creator_handle: "filmfanatic",
        views: "1.1M",
        thumbnail: "",
        duration: "3:42",
        votes: 400,
        likes: 8372,
      },
    ],
  },
];

const BountyPage = () => {
  const [ideas, setIdeas] = useState<Bounty[]>(mockIdeas);
  const [selectedIdea, setSelectedIdea] = useState<Bounty | null>(null);
  const [isModalOpen, setIsModalOpen] = useState(false);

  const handleInvest = (idea: Bounty) => {
    setSelectedIdea(idea);
    setIsModalOpen(true);
  };

  const closeModal = () => {
    setIsModalOpen(false);
    setSelectedIdea(null);
  };

  const isOver = (judging_end: string) => {
    const daysLeft = Math.ceil(
      (new Date(judging_end).getTime() - new Date().getTime()) / (1000 * 60 * 60 * 24)
    );
    return daysLeft < 0;
  }

  useEffect(() => {
    const getBounties = async () =>{ 
      const res = await fetch("https://buuck.onrender.com/bounty", {
          method: "GET",
          headers: { "Content-Type": "application/json" },
      });
      const data = await res.json();
      setIdeas(data);
    }
    getBounties();
  }, [])

  return (
    <view className="video-ideas-page">
      <view className="content">
        {/* Header */}
        <view className="header">
          <text className="gradient-text header-h1" style={{ textShadow: "0px 0px 3px #fe2c55"}}>🔥 Trending</text>
          <text className="header-h2" style={{ textShadow: "0px 0px 3px white"}}>Video Creation Challenges</text>
          <text className="header-p">Back epic challenges and watch creators bring wild ideas to life</text>
        </view>

        {/* Ideas Grid */}
        <scroll-view scroll-orientation="vertical" className="ideas-grid">
          {ideas.map((idea, index) => (
            <view
              key={idea.id}
              className="idea-wrapper"
              style={{
                animationDelay: `${index * 100}ms`,
              }}
            >
              {isOver(idea.judging_end) 
              ? <BountyCardOver
                  id={idea.id}
                  title={idea.description}
                  pledged={idea.prize_pool}
                  deadline={idea.judging_end}
                  videos={idea.current_videos}
                  modalClick={() => handleInvest(idea)}
                  following={idea.following}
                />
              : <BountyCard
                  id={idea.id}
                  title={idea.description}
                  pledged={idea.prize_pool}
                  deadline={idea.judging_end}
                  videos={idea.current_videos}
                  modalClick={() => handleInvest(idea)}
                  following={idea.following}
                />}
            </view>
          ))}
        </scroll-view>

        {/* Footer */}
        <view className="footer">
          <text style={'color: #a1a1a1'}>🎬 More epic challenges coming soon...</text>
        </view>
      </view>

      {/* Modal */}
      {selectedIdea && (
        <BountyModal
          isOpen={isModalOpen}
          onClose={closeModal}
          challengeTitle={selectedIdea.description}
          currentPledged={selectedIdea.prize_pool}
          deadline={selectedIdea.judging_end}
          videos={selectedIdea.current_videos}
          id={selectedIdea.id}
        />
      )}
    </view>
  );
};

export default BountyPage;