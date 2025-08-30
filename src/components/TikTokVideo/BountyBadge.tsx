import type { Dispatch, SetStateAction } from '@lynx-js/react';
import { useNavigate } from 'react-router';

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

const BountyBadge = ({video, toggleVideo}: {video: Video, toggleVideo: Dispatch<SetStateAction<boolean>>}) => {

  const nav = useNavigate();

  const handleGoBack = () => {
    toggleVideo(false);
    () => nav('/bounty');
  }

    return (
      <view className="live-header-container">
        {/* Live Badge */}
        <view className="live-badge">
          <view className="bounty-badge-content" bindtap={handleGoBack}>
            <text className="badge-text">CHALLENGE</text>
          </view>
        </view>
      </view>
    );
};

export default BountyBadge;