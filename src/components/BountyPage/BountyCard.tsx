import { useState } from "@lynx-js/react";
import clockIcon from "../../assets/clock.png";
import "./styles/BountyCard.css";
import heartIcon from '../../assets/heart.png';

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

interface IdeaCardProps {
  title: string;
  pledged: number;
  deadline: string;
  videos: Video[];
  className?: string;
  modalClick?: () => void;
  following: boolean;
  id: string;
}

const BountyCard = ({
  title,
  pledged,
  deadline,
  videos,
  className = "",
  following,
  modalClick,
  id,
}: IdeaCardProps) => {
  const daysLeft = Math.ceil(
    (new Date(deadline).getTime() - new Date().getTime()) /
      (1000 * 60 * 60 * 24)
  );
  const isUrgent = daysLeft <= 3;

  const [liked, setLiked] = useState(following);

  const handleLike = () => {
    setLiked(!liked);
    following = !following;
  };

  return (
    <view className={`idea-card ${className}`} style="margin-bottom: 2rem">
      <view className="idea-card-content">
        {/* Title & Deadline */}
        <view className="idea-card-header">
          <view style="display: flex; gap: 0.5rem; align-items: center;">
            <view>
              <text className="idea-title">{title}</text>
            </view>
            {/* Like Button */}
            <view style={'height: 25px; width: 25px;'} bindtap={handleLike} className={`btn-circle like-btn ${liked ? 'liked' : ''}`}>
              <image src={heartIcon} className="action-icon"/>
            </view>
          </view>
          <view className={`deadline-badge ${isUrgent ? "urgent" : "normal"}`}>
            <image src={clockIcon} style={'height: 0.75rem; width: 0.75rem'}/>
            <text className={`deadline-text ${isUrgent ? "urgent" : "normal"}`}>{daysLeft}d left</text>
          </view>
        </view>

        {/* Description */}
        {/* <text className="idea-description">{description}</text> */}

        {/* Meta Info */}
        <view className="idea-meta">
          <view className="meta-item">
            <text className="meta-text">Ends {new Date(deadline).toLocaleDateString()}</text>
          </view>
          <view className="meta-item">
            <text className="meta-text">📹 {videos.length} video(s) created</text>
          </view>
        </view>

        {/*Community Funded Statement*/}
        <view>
          <view className="pledge-container">
            <text className="meta-text" style={'font-size: 1rem'}>Total Pledged</text>
            <text className="pledge-amt">
              ${pledged.toLocaleString()}
            </text>
          </view>
          <view class="bar">
            <view class="fill"></view>
          </view>
          <text className="meta-text">Community Funded Challenge</text>
        </view>

        {/*Button */}
        <view className="btn-container">
          <view className="neon-button" bindtap={modalClick}>
              <text className="btn-text">💰 Back This Challenge</text>
          </view>
        </view>
      </view>
    </view>
  );
};

export default BountyCard;