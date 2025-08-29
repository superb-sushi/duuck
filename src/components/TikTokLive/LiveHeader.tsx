import CloseIcon from '../../assets/close.png';
import { useNavigate } from 'react-router';

const LiveHeader = () => {

  const nav = useNavigate();

    return (
      <view className="live-header-container">
        {/* Live Badge */}
        <view className="live-badge">
          <view className="badge-content">
            <view className="pulse-dot" />
            <text className="badge-text">LIVE</text>
          </view>
        </view>
        
        {/* Viewer Count */}
        <view className="viewer-count">
          <view className="viewer-box">
            <text className="viewer-text">12.3K viewers</text>
          </view>
        </view>
        
        {/* Exit Button */}
        <view className="exit-btn" >
          <view className="exit-circle" bindtap={() => nav('/')}>
            <image src={CloseIcon} className="exit-icon" />
          </view>
        </view>
      </view>
    );
};

export default LiveHeader;