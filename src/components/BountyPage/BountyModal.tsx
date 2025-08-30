import { useState } from "react";
import CloseIcon from "../../assets/close.png";
import "./styles/BountyModal.css";
import VideoPage from "../TikTokVideo/Video.js"
import { useEffect } from "@lynx-js/react";

interface User {
  handle: string,
  wallet: number,
  total_donations: number,
  time_spent_on_app: number,
  account_age_days: number,
  total_interactions: number
}

interface Video {
  id: string;
  title: string;
  creator_handle: string;
  views: string;
  thumbnail: string;
  duration: string;
  votes: number;
  likes: number;
}

interface InvestmentModalProps {
  isOpen: boolean;
  onClose: () => void;
  challengeTitle: string;
  currentPledged: number;
  deadline: string;
  videos: Video[];
  id: string;
}

const BountyModal = ({
  isOpen,
  onClose,
  challengeTitle,
  currentPledged,
  deadline,
  videos,
  id
}: InvestmentModalProps) => {
  const [activeTab, setActiveTab] = useState<"contribute" | "join" | "videos">("contribute");
  const [investmentAmount, setInvestmentAmount] = useState<number>(0);

  const [currPool, setCurrPool] = useState<number>(currentPledged)

  const [isVideoOn, setIsVideoOn] = useState<boolean>(false);
  const [focusedVideo, setFocusedVideo] = useState<Video>();

  const[modalIsOpen, setModalIsOpen] = useState<boolean>(isOpen);

  const [creator, setCreator] = useState<User>();

  const handleGoVideo = (v: Video) => {
    setIsVideoOn(true);
    setFocusedVideo(v);
    setModalIsOpen(false);
  }

  useEffect(() => {
    const getCreator = async () =>{ 
      const res = await fetch("https://buuck.onrender.com/user/getdefault", {
          method: "GET",
          headers: { "Content-Type": "application/json" },
      });
      const data = await res.json();
      setCreator(data);
    }
    getCreator();
  }, [])

  if (!isOpen) return null;

  const daysLeft = Math.ceil(
    (new Date(deadline).getTime() - new Date().getTime()) / (1000 * 60 * 60 * 24)
  );

  const isOver = daysLeft < 0;

  const [warning, setWarning] = useState<string>("");
  const [joinMsg, setJoinMsg] = useState<string>("");
  const [joined, setJoined] = useState<boolean>(false);
  const [invested, setInvested] = useState<boolean>(false);

  const handleInvest = () => {
    if (!investmentAmount || parseFloat(investmentAmount.toString()) <= 0 || investmentAmount > creator!.wallet) {
      setWarning("⚠️ Please enter a valid investment amount.");
      return;
    }
    setCreator(prev => ({...prev!, wallet: prev!.wallet - investmentAmount}));
    setWarning(`🚀 Investment Successful! You've invested $${investmentAmount}!`);
    setInvested(true);
    setCurrPool(currPool + investmentAmount);
    const updatePrizePool = async () =>{ 
      const res = await fetch(`https://buuck.onrender.com/bounty/${id}/contribute?viewer_handle=${creator!.handle}&amount=${investmentAmount}`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
      });
    }
    updatePrizePool();
    setInvestmentAmount(0);
  };

  const handleJoinChallenge = () => {
    setJoinMsg(`🎬 Welcome! @${creator!.handle} joined "${challengeTitle}"`);
    setJoined(true);
  };

  return (
    <>
    {focusedVideo && <VideoPage video={focusedVideo} toggleVideo={setIsVideoOn} />}
    <view className={modalIsOpen ? "modal-overlay" : "hidden"}>
      <view className="modal-content">
        <view style={'width: 100%; display: flex; justify-content: flex-end;'}>
          <image src={CloseIcon} className="modal-exit-icon" bindtap={() => onClose()}/>
        </view>
        {/* Header */}
        <view className="modal-header">
          <text className="modal-header-h2">{challengeTitle}</text>
          {/* <text className="modal-header-p">{challengeDescription}</text> */}

          <view className="challenge-stats">
            <view>
              <text className="challenge-stats-text">💰 ${currPool.toFixed(2)} raised!</text>
            </view>
            <view>
              📅 <text className={daysLeft <= 3 ? "urgent" : "not-urgent"}>{daysLeft < 0 ? "challenge over!": daysLeft + "d left!"}</text>
            </view>
          </view>
        </view>

        {/* Tabs */}
        {isOver 
        ? <>
          <view>
            <text className="invest-header" style={'margin-top: 0.75rem'}>Top 3 Winners</text>
          </view>

          <view className="tab-panel">
            <text style={'color: white; font-weight: bold; margin-bottom: 0.75rem;'}>{videos.length} videos created</text>
            {videos.length === 0 ? (
              <view className="empty-videos">No videos were submitted for this challenge.</view>
            ) : (
              <scroll-view scroll-orientation="vertical" className="video-list">
                {videos.sort((a, b) => a.votes - b.votes).filter((v, id) => id < 3).map((video, id) => (
                  <view key={video.id} className={id == 0 ? "video-card-1" : id == 1 ? "video-card-2" : "video-card-3"} bindtap={() => handleGoVideo(video)}>
                    <view className="video-thumbnail">
                      <text className="vid-play-btn">▶</text>
                    </view>
                    <view style='display: flex; flex-direction: column; gap: 0.2rem; justify-content: center; flex-grow: 1; margin-left: 10px;'>
                      <text style={'color: white; font-weight: 900'}>{video.title}</text>
                      <text style={'color: white'}>@{video.creator_handle} • {video.views} views • {video.votes} votes</text>
                    </view>
                    <text className="video-info">{video.duration}</text>
                  </view>
                ))}
              </scroll-view>
            )}
          </view>
        </>
        : <>
        <view className="tabs">
          <text
            className={`tabs-button ${activeTab === "contribute" ? "active" : ""}`}
            bindtap={() => setActiveTab("contribute")}
          >
            💰 Contribute
          </text>
          <text
            className={`tabs-button ${activeTab === "join" ? "active" : ""}`}
            bindtap={() => setActiveTab("join")}
          >
            🎬 Join
          </text>
          <text
            className={`tabs-button ${activeTab === "videos" ? "active" : ""}`}
            bindtap={() => setActiveTab("videos")}
          >
            📹 Videos
          </text>
        </view>

        {/* Tab Content */}
        {activeTab === "contribute" && (
          <view className="tab-panel">
            <view style={'display: flex; justify-content: space-between'}>
              <text className="invest-header">Contribute Amount</text>
              {creator && <text style="color: #a1a1a1;">You have ${creator!.wallet.toFixed(2)}!</text>}
            </view>
            <view className="input-wrapper">
              <text style={'color: white'}>$ </text>
              <view className="modal-input-box">
                <text style={'color: white; font-size: 2rem; font-weight: bold; text-align: center; width: 100%'}>
                  {investmentAmount.toFixed(2)}
                </text>
              </view>
            </view>

            <text style={invested ? 'color: green;': 'color: red;'}>{warning}</text>

            <view className="quick-amounts">
              {[-0.10, -1, -10, 0.10, 1, 10].map((amt) => (
                <text style={`color: white; ${amt < 0 ? 'color: red;' : 'color: white;'}`} className="quick-amt-button" key={amt} bindtap={() => investmentAmount + amt < 0 ? 0 : setInvestmentAmount(investmentAmount + amt)}>
                  ${amt}
                </text>
              ))}
            </view>

            <view style={'width: 100%; display: flex; justify-content: center; margin-top: 20px;'}>
              <view className="neon-button-modal" bindtap={handleInvest}>
                <text style={'color: white; font-weight: 900;'}>Contribute Now</text>
              </view>
            </view>
          </view>
        )}

        {activeTab === "join" && (
          <view className="tab-panel">
            <text style={'color: white; font-weight: bold;'}>Creator Username</text>
            <view className="input-wrapper">
              <text style="color: #d1d1d1">@  </text>
              <view className="modal-input-box">
                <text style="color: #a1a1a1;">{creator!.handle}</text>
              </view>
            </view>
            <text className="helper-text">
              Join this challenge and create epic content! Your videos will be tagged.
            </text>

            <view style={'width: 100%; display: flex; justify-content: center; margin-top: 20px;'}>
              <view className={joined ? "opacity: 25%; neon-button " : "neon-button "} bindtap={handleJoinChallenge}>
                <text style={'color: white; font-weight: 900;'}>Join Now</text>
              </view>
            </view>
            <text style={joined ? 'color: green; margin-top: 0.75rem': 'color: red; margin-top: 0.75rem'}>{joinMsg}</text>
          </view>
          
        )}

        {activeTab === "videos" && (
          <view className="tab-panel">
            <text style={'color: white; font-weight: bold; margin-bottom: 0.75rem;'}>{videos.length} videos created</text>
            {videos.length === 0 ? (
              <view className="empty-videos">No videos yet. Be the first to create!</view>
            ) : (
              <scroll-view scroll-orientation="vertical" className="video-list">
                {videos.map((video) => (
                  <view key={video.id} className="video-card" bindtap={() => handleGoVideo(video)}>
                    <view className="video-thumbnail">
                      <text className="vid-play-btn">▶</text>
                    </view>
                    <view style='display: flex; flex-direction: column; gap: 0.2rem; justify-content: center; flex-grow: 1; margin-left: 10px;'>
                      <text style={'color: white; font-weight: 900'}>{video.title}</text>
                      <text style={'color: white'}>@{video.creator_handle} • {video.views} views • {video.votes} votes</text>
                    </view>
                    <text className="video-info">{video.duration}</text>
                  </view>
                ))}
              </scroll-view>
            )}
          </view>
        )}
        </>}
      </view>
    </view>
    </>
  );
};

export default BountyModal;