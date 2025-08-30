import { useCallback, useEffect, useState, type Dispatch, type SetStateAction } from '@lynx-js/react'

import { UserProfile } from './UserProfileVid.js'
import ActionButtons from './ActionButtonVid.js'
import LiveVideoContainerVid from './LiveVideoContainerVid.js'
import BountyBadge from './BountyBadge.js'

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

function Video({video, toggleVideo}: {video: Video, toggleVideo: Dispatch<SetStateAction<boolean>>}) {

  return (
    <view className="app-screen">
      <UserProfile video={video}/>
      <ActionButtons video={video}/>
      <LiveVideoContainerVid video={video}/>
      <BountyBadge video={video} toggleVideo={toggleVideo} />
    </view>
  )
}

export default Video
