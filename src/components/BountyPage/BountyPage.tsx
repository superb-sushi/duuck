import { useEffect, useState } from "react";
import BountyCard from "./BountyCard.js";
import BountyModal from "./BountyModal.js";
import "./styles/BountyPage.css";
import BountyCardOver from "./BountyCardOver.js";

interface Video {
  id: string;
  title: string;
  creator: string;
  views: string;
  thumbnail: string;
  duration: string;
  votes: number;
  likes: number;
}

interface Bounty {
  id: string;
  title: string;
  contributions: number;
  deadline: string;
  videos: Video[];
  following: boolean;
}

const mockIdeas: Bounty[] = [
  {
    id: "1",
    title: "24 Hours in Zero Gravity Challenge",
    contributions: 32500,
    deadline: "2025-09-01",
    following: true,
    videos: [
      {
        id: "1",
        title: "Testing Zero G Water Drops",
        creator: "spaceguy",
        views: "2.1M",
        thumbnail: "",
        duration: "0:45",
        votes: 1200,
        likes: 10029,
      },
      {
        id: "2",
        title: "Floating Pizza Challenge",
        creator: "foodieflix",
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
    title: "Living Like It's 1823 for 30 Days",
    contributions: 18750,
    deadline: "2025-09-20",
    following: true,
    videos: [
      {
        id: "3",
        title: "Making Candles from Scratch",
        creator: "historymaker",
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
    title: "I Bought Every Item in a Gas Station",
    contributions: 22500,
    deadline: "2025-08-10",
    following: false,
    videos: [
      {
        id: "4",
        title: "Gas Station Haul Part 1",
        creator: "buyitall",
        views: "3.2M",
        thumbnail: "",
        duration: "8:45",
        votes: 1500,
        likes: 2932,
      },
      {
        id: "5",
        title: "Weird Gas Station Finds",
        creator: "buyitall",
        views: "2.7M",
        thumbnail: "",
        duration: "6:23",
        votes: 1300,
        likes: 293802,
      },
      {
        id: "6",
        title: "Eating Only Gas Station Food",
        creator: "hungryhank",
        views: "1.4M",
        thumbnail: "",
        duration: "12:01",
        votes: 800,
        likes: 3511,
      },
      {
        id: "10",
        title: "Yosemite Gas Station Mukbang",
        creator: "adventuretime101",
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
    title: "Building the World's Largest Domino Chain",
    contributions: 45300,
    deadline: "2025-10-01",
    following: true,
    videos: [
      {
        id: "7",
        title: "Domino Setup Day 1",
        creator: "dominokid",
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
    title: "Teaching My Grandma to Become a Gamer",
    contributions: 8900,
    deadline: "2025-09-25",
    following: false,
    videos: [],
  },
  {
    id: "6",
    title: "Recreating Every Movie Genre in 1 Day",
    contributions: 19200,
    deadline: "2025-09-18",
    following: true,
    videos: [
      {
        id: "8",
        title: "Horror Scene Behind the Scenes",
        creator: "filmfanatic",
        views: "890K",
        thumbnail: "",
        duration: "4:17",
        votes: 300,
        likes: 2341,
      },
      {
        id: "9",
        title: "Action Sequence Fails",
        creator: "filmfanatic",
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
  const [ideas] = useState<Bounty[]>(mockIdeas);
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

  const isOver = (deadline: string) => {
    const daysLeft = Math.ceil(
      (new Date(deadline).getTime() - new Date().getTime()) / (1000 * 60 * 60 * 24)
    );
    return daysLeft < 0;
  }

  useEffect(() => {
    const getBounties = async () =>{ 
      const res = await fetch("https://openvision-oq79.onrender.com", {
          method: "GET",
          headers: { "Content-Type": "application/json" },
      });
      const data = await res.text(); // gives HTML
      console.log(data);
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
              {isOver(idea.deadline) 
              ? <BountyCardOver
                  title={idea.title}
                  pledged={idea.contributions}
                  deadline={idea.deadline}
                  videos={idea.videos}
                  modalClick={() => handleInvest(idea)}
                  following={idea.following}
                />
              : <BountyCard
                  title={idea.title}
                  pledged={idea.contributions}
                  deadline={idea.deadline}
                  videos={idea.videos}
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
          challengeTitle={selectedIdea.title}
          currentPledged={selectedIdea.contributions}
          deadline={selectedIdea.deadline}
          videos={selectedIdea.videos}
        />
      )}
    </view>
  );
};

export default BountyPage;