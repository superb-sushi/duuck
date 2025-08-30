import React from "react";
import "./styles/ProgressBar.css";

interface ProgressBarProps {
  current: number;
  goal: number;
  className?: string;
}

const ProgressBar = ({ current, goal, className }: ProgressBarProps) => {
  const progress = Math.min((current / goal) * 100, 100);

  return (
    <view className={`progress-container ${className || ""}`}>
      <view className="progress-header">
        <text className="progress-label">Total Pledged</text>
        <text className="progress-value">
          ${current.toLocaleString()} / ${goal.toLocaleString()}
        </text>
      </view>
      <view className="progress-bar">
        <view
          className="progress-fill"
          style={{ width: `${progress}%` }}
        />
      </view>
      <view className="progress-footer">
        Community funded challenge
      </view>
    </view>
  );
};

export default ProgressBar;