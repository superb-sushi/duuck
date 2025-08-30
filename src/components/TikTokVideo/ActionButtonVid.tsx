import { useState } from 'react';
import voteIcon from '../../assets/vote.png';
import shareIcon from '../../assets/share.png';
import commentIcon from '../../assets/comment.png';
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

const ActionButtonsVid = ({video}: {video: Video}) => {

  const [liked, setLiked] = useState(false);
  const [likeCount, setLikeCount] = useState(video.likes);

  const handleLike = () => {
    if (!liked) {
      handleLikes(likeCount + 1);
    } else {
      handleLikes(likeCount - 1);
    }
    setLiked(!liked);
    setLikeCount(prev => liked ? prev - 1 : prev + 1);
  };

  const [isVoted, setIsVoted] = useState<boolean>(false);
  const [voteCount, setVoteCount] = useState(video.votes);
  
  const handleVote = () => {
    if (!isVoted) {
      handleVotes(voteCount + 1);
    } else {
      handleVotes(voteCount - 1);
    }
    setIsVoted(!isVoted)
    setVoteCount(prev => isVoted ? prev - 1 : prev + 1);
  }

  const handleLikes = (likecount: number) => {
    const updateLikes = async () =>{ 
        const res = await fetch(`https://buuck.onrender.com/video/${video.id}?likes=${likecount}`, {
            method: "PUT",
            headers: { "Content-Type": "application/json" },
        });
      }
      updateLikes();
  }

  const handleVotes = (votecount: number) => {
    const updateLikes = async () =>{ 
        const res = await fetch(`https://buuck.onrender.com/video/${video.id}?votes=${votecount}`, {
            method: "PUT",
            headers: { "Content-Type": "application/json" },
        });
      }
      updateLikes();
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