import liveStreamerImage from '../../assets/livestream.jpg';

const LiveVideoContainer = () => {
  return (
    <view className="live-container">
      {/* Background Video/Image */}
      <view className="background">
        <image 
          src={liveStreamerImage} 
          className="background-image"
        />
        <view className="background-overlay" />
      </view>
    </view>
  );
};

export default LiveVideoContainer;