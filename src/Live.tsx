import { useCallback, useEffect, useState } from '@lynx-js/react'
import './App.css'
import { LiveVideo } from './components/TikTokLive/LiveVideo.js'
import Video from './components/TikTokVideo/Video.js'

export function Live(props: {
  onRender?: () => void
}) {

  useEffect(() => {
  }, [])
  props.onRender?.()

  return (
    <view className="app-screen">
      <LiveVideo />
    </view>
  )
}
