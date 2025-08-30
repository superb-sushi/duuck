import { useState } from 'react';
import voteIcon from '../../assets/vote.png';
import shareIcon from '../../assets/share.png';
import commentIcon from '../../assets/comment.png';
import heartIcon from '../../assets/heart.png';

const ActionButtonsVid = () => {
  const [liked, setLiked] = useState(false);
  const [likeCount, setLikeCount] = useState(847);

  const handleLike = () => {
    setLiked(!liked);
    setLikeCount(prev => liked ? prev - 1 : prev + 1);
  };
  
  const handleVote = () => {
    setIsVoted(!isVoted)
  }

  const [isVoted, setIsVoted] = useState<boolean>(false);

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

      {/* Vote Button */}
      {isVoted ? <view className="btn-group">
        <view className="btn-circle vote-btn" bindtap={handleVote}>
          <image src={voteIcon} style="height: 100%; width: 100%;"/>
        </view>
        <text className="btn-label">Vote</text>
      </view>
      : <view className="btn-group">
          <view className="btn-circle translucent-btn" bindtap={handleVote}>
            <image src={voteIcon} style="height: 100%; width: 100%;"/>
          </view>
          <text className="btn-label">Vote</text>
        </view>}
    </view>
    </>
  );
};

export default ActionButtonsVid;