import { useState } from "@lynx-js/react";
import clockIcon from "../../assets/clock.png";
import "./styles/BountyCardOver.css";

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
  id: string,
}

const BountyCardOver = ({
  title,
  pledged,
  deadline,
  videos,
  className = "",
  following,
  modalClick,
  id
}: IdeaCardProps) => {

  return (
    <view className={`idea-card-over ${className}`} style="margin-bottom: 2rem">
      <view className="idea-card-content">
        {/* Title & Deadline */}
        <view className="idea-card-header">
          <view style="display: flex; gap: 0.5rem; align-items: center;">
            <view>
              <text className="idea-title">{title}</text>
            </view>
          </view>
          <view className={`deadline-badge urgent`}>
            <image src={clockIcon} style={'height: 0.75rem; width: 0.75rem'}/>
            <text className={`deadline-text urgent`}>Done</text>
          </view>
        </view>

        {/* Description */}
        {/* <text className="idea-description">{description}</text> */}

        {/* Meta Info */}
        <view className="idea-meta">
          <view className="meta-item">
            <text className="meta-text">Ended on {new Date(deadline).toLocaleDateString()}</text>
          </view>
          <view className="meta-item">
            <text className="meta-text">📹 {videos.length} video(s) created</text>
          </view>
        </view>

        <view>
          <view className="pledge-container">
            <text className="meta-text" style={'font-size: 1rem'}>Total Pledged</text>
            <text className="pledge-amt">
              ${pledged.toLocaleString()}
            </text>
          </view>
          <view class="bar">
            <view class="fill-over"></view>
          </view>
          <text className="meta-text">Community Funded Challenge</text>
        </view>

        {/*Button */}
        <view className="btn-container">
          <view className="neon-button-over" bindtap={modalClick}>
              <text className="btn-text">View the biggest winners!</text>
          </view>
        </view>
      </view>
    </view>
  );
};

export default BountyCardOver;