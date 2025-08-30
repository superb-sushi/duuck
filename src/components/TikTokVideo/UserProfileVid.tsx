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

export const UserProfile = ({video}: {video: Video}) => {
  return (
    <view className="user-profile">
      {/* User Avatar */}
      <view className="avatar-wrapper">
        <view className="avatar-border">
          <view className="avatar">
            <text className="avatar-text">A</text>
          </view>
        </view>
        <view className="status-badge"></view>
      </view>
      
      {/* User Info */}
      <view className="user-info">
        <text className="username">{video.creator}</text>
        <text className="user-bio">Its makan time! 🎉</text>
      </view>
      
      {/* Follow Button */}
      <view className="follow-btn">
        <text className="follow-text">Follow</text>
      </view>
    </view>
  );
};