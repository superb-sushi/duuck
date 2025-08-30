import { useCallback, useEffect, useState } from '@lynx-js/react'
import './App.css'
import { LiveVideo } from './components/TikTokLive/LiveVideo.js'
import Video from './components/TikTokVideo/Video.js'
import { useNavigate } from 'react-router';

export function App(props: {
  onRender?: () => void
}) {

  useEffect(() => {
  }, [])
  props.onRender?.()

  const nav = useNavigate();

  return (
    <view className="app-screen centralise">
      <view className="underline">
        <text style="color: white" bindtap={() => nav('/vid')}>Navigate to Video Screen</text>
      </view>
      <view className="underline">
        <text style="color: white" bindtap={() => nav('/bounty')}>Navigate to Bounty Screen</text>
      </view>
      <view className="underline">
        <text style="color: white" bindtap={() => nav('/live')}>Navigate to Live Video Screen</text>
      </view>
    </view>
  )
}
