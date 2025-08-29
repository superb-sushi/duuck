import { useNavigate } from 'react-router';

const BountyBadge = () => {

  const nav = useNavigate();

    return (
      <view className="live-header-container">
        {/* Live Badge */}
        <view className="live-badge">
          <view className="bounty-badge-content" bindtap={() => nav('/')}>
            <text className="badge-text">CHALLENGE</text>
          </view>
        </view>
      </view>
    );
};

export default BountyBadge;