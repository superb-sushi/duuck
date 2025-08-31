# Project Duuck

## Overview
Project Duuck turns short-form video challenges into community-backed competitions. Users browse trending challenges, chip in to prize pools, and submit their own videos. The community votes to determine winners, with automatic payouts to the top three entries after each challenge—turning engagement into real rewards. Followers can track favorite challenges, watch real-time leaderboards, and discover rising creators. Under the hood, an ML fraud-detection model flags suspicious activity—like abnormal voting spikes or high-value transfer patterns—to protect contributors and creators. The result is a safe, dynamic way to gamify content creation, connect communities, and reward talent—built for rapid, fair, and fun participation.


## Problem Statement

TikTok enables creators worldwide to earn revenue through short videos and live streams, with higher-quality content typically generating greater rewards. However, designing a fair and effective reward mechanism is complex due to challenges such as fairness, regulatory compliance, and fraud prevention. These issues can result in misaligned incentives, under-compensated creators, and reduced ecosystem engagement.

This project aims to design a new value-sharing solution that establishes a transparent and legitimate flow of value from consumers to creators. Key factors addressed include:

- Profit-sharing mechanisms
- AML (Anti-Money Laundering) compliance
- Anti-fraud and system gaming prevention
## Features
### Bounty

1. Users can create and participate in bounties related to content creation.
   - Bounties created will go through a check to ensure it is not harmful and avoids repetitive bounties
    - Users can follow bounties and be notified of new submissions.
2. Bounty management includes tracking progress, rewarding participants, and displaying active/completed bounties.
	- Measures are in place to ensure that users cannot game the system.
	- Users who started the bounties or have contributed the prize pool are not able to create submissions.
	- Users who submitted their videos are not able to further contribute to the bounties.
3. Users will be able to vote for the content they enjoyed the most to decide the winners.
	- Users who have submitted videos to the bounties will not be able to vote.
	- Votes are limited per user.
4. Transparent profit-sharing mechanisms ensure fair distribution of rewards among creators based on content quality and engagement.
	- Viewers will get to view which creators won the bounty.
5. UI components for bounty cards, modals, and progress bars provide an interactive experience for users. (TBD)

### Anti Fraud Model

1. Integrated machine learning model for fraud detection, leveraging user and transaction data to identify suspicious activities.
2. Automated checks for system gaming, fake engagement, and other fraudulent behaviors.
3. AML (Anti-Money Laundering) compliance features to monitor and prevent illicit value transfers.
4. Backend endpoints for real-time fraud assessment and reporting, supporting a secure and compliant ecosystem.

## What's next for Project Duuck
- Add real-time notifications for new submissions and prize pool updates.
- Enhance fraud detection with more sophisticated machine learning models.
- Expand analytics to show trending challenges and top creators.
- Optimize mobile experience for wider accessibility.

## Development Tools

- **Frontend:** Lynx, TypeScript, CSS 
- **Backend:** Python, SQLite, scikit-learn (for ML), FastAPI
- **General:** VS Code, npm, pip

## APIs

- Custom internal APIs for moderation, bounty management, and fraud detection.
- Potential integration with external livestream APIs (e.g., TikTok).

## Assets

- PNG and JPG images for UI icons and backgrounds (`src/assets/`)
- Custom CSS for component styling

## Libraries

- **Frontend:** Lynx, TypeScript, CSS
- **Backend:** Python, scikit-learn, SQLAlchemy (or similar), FastAPI


## Getting Started

### Prerequisites

- Node.js and npm
- Python 3.12+
- VS Code (recommended)

### Installation

#### Frontend

```bash
cd src
npm install
npm run dev
```

#### Backend

```bash
cd backend
pip install -r requirements.txt
python app/main.py
```

### Testing

