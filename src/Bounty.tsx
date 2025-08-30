import { useEffect } from '@lynx-js/react'
import './App.css'
import BountyPage from './components/BountyPage/BountyPage.js'

export function Bounty(props: {
  onRender?: () => void
}) {

  useEffect(() => {
  }, [])
  props.onRender?.()

  return (
    <view className="app-screen">
      <BountyPage />
    </view>
  )
}
