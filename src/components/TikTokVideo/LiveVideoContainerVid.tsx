import liveStreamerImage from '../../assets/livestream.jpg';

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

const LiveVideoContainerVid = ({video}: {video: Video}) => {
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

export default LiveVideoContainerVid;