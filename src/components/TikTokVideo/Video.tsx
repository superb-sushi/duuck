import { useCallback, useEffect, useState } from '@lynx-js/react'

import { UserProfile } from './UserProfileVid.js'
import ActionButtons from './ActionButtonVid.js'
import LiveVideoContainerVid from './LiveVideoContainerVid.js'
import BountyBadge from './BountyBadge.js'

function Video(props: {
  onRender?: () => void
}) {

  useEffect(() => {
    console.info('Hello, ReactLynx')
  }, [])
  props.onRender?.()

  return (
    <view className="app-screen">
      <UserProfile />
      <ActionButtons />
      <LiveVideoContainerVid />
      <BountyBadge />
    </view>
  )
}

export default Video
