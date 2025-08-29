import { useCallback, useEffect, useState } from '@lynx-js/react'

import { UserProfile } from './UserProfile.js'
import ActionButtons from './ActionButtons.js'
import LiveVideoContainer from './LiveVideoContainer.js'
import LiveHeader from './LiveHeader.js'

export function LiveVideo(props: {
  onRender?: () => void
}) {

  useEffect(() => {
    console.info('Hello, ReactLynx')
  }, [])
  props.onRender?.()

  return (
    <view className="app-screen">
      <LiveHeader />
      <UserProfile />
      <ActionButtons />
      <LiveVideoContainer />
    </view>
  )
}
