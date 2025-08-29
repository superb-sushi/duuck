import { useState } from 'react';
import giftIcon from '../../assets/gift.png';
import shareIcon from '../../assets/share.png';
import commentIcon from '../../assets/comment.png';
import heartIcon from '../../assets/heart.png';
import trophyIcon from '../../assets/trophy.png';
import LiveOptions from './LiveOptions.js';

const ActionButtons = () => {
  const [liked, setLiked] = useState(false);
  const [likeCount, setLikeCount] = useState(847);

  const handleLike = () => {
    setLiked(!liked);
    setLikeCount(prev => liked ? prev - 1 : prev + 1);
  };

  const [optionDisplayed, setOptionDisplayed] = useState<boolean>(false);

  const handleToggleOptions = () => {
    setOptionDisplayed(!optionDisplayed);
  }

  const [giftsDisplayed, setGiftsDisplayed] = useState<boolean>(false);

  const handleToggleGifts = () => {
    setGiftsDisplayed(!giftsDisplayed);
  }

  return (
    <>
    <view className="action-buttons">
      {/* Like Button */}
      <view className="btn-group">
        <view 
          bindtap={handleLike}
          className={`btn-circle like-btn ${liked ? 'liked' : ''}`}
        >
          <image src={heartIcon} className="action-icon"/>
        </view>
        <text className="btn-label">{likeCount}</text>
      </view>

      {/* Comment Button */}
      <view className="btn-group">
        <view className="btn-circle translucent-btn">
          <image src={commentIcon} className="action-icon"/>
        </view>
        <text className="btn-label">234</text>
      </view>

      {/* Share Button */}
      <view className="btn-group">
        <view className="btn-circle translucent-btn">
          <image src={shareIcon} className="action-icon"/>
        </view>
        <text className="btn-label">Share</text>
      </view>

      {/* Gift Button */}
      <view className="btn-group">
        <view className="btn-circle gift-btn">
          <image src={giftIcon} className="action-icon"/>
        </view>
        <text className="btn-label">Gift</text>
      </view>

      {/* Challenges Button */}
      <view className="btn-group">
        <view className="btn-circle trophy-btn" bindtap={handleToggleOptions}>
          <image src={trophyIcon} className="action-icon"/>
        </view>
        <text className="btn-label">Challenges</text>
      </view>
    </view>
    <LiveOptions displayed={optionDisplayed}/>
    </>
  );
};

export default ActionButtons;