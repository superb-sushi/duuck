import { useCallback, useEffect, useState } from '@lynx-js/react'
import './App.css'
import { LiveVideo } from './components/TikTokLive/LiveVideo.js'
import Video from './components/TikTokVideo/Video.js'
import { useNavigate } from 'react-router';

export function Vid(props: {
  onRender?: () => void
}) {

  useEffect(() => {
  }, [])
  props.onRender?.()

  const nav = useNavigate();

  return (
    <view className="app-screen">
      <Video />
    </view>
  )
}
