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
    - Users can contribute in bounties.
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

1. Collect and identified key metadata from user viewing and donating to the bounty/ content (time watched before donating, interactions with content components)
2. Integrated machine learning model for fraud detection, leveraging user and macro donation data to predict potential money laundering intentions
3. Automated checks for suspicious donation amounts and user application usage habits (how often the app is used vs how long the app was downloaded)
4. Applied contextual understanding of model purpose to minimise inconvenience to regular viewers, hence opting for a lower recall but higher precision model in finding non fraudulent users. 

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


## Getting Started

### Prerequisites

- Node.js and npm
- Python 3.12+
- VS Code (recommended)

### Installation

## How to Start the Application

### Backend

#### Backend Initial Setup (Run Once)

```bash
cd backend
python -m venv .venv && .venv\Scripts\activate
pip install -r requirements.txt
```

#### Start the Backend Server

```bash
cd backend
.venv\Scripts\activate
uvicorn app.main:app --reload
```

## Rspeedy project (frontend)

This is a ReactLynx project bootstrapped with `create-rspeedy`.

## Getting Started
First, [clone this github repository](https://docs.github.com/en/repositories/creating-and-managing-repositories/cloning-a-repository) into your local device. Navigate to the root folder.

Then, install the dependencies:

```bash
npm install
```

Then, run the development server:

```bash
npm run dev
```

Scan the QRCode in the terminal with your LynxExplorer App (preferably Android) to see the result.
Click on `Navigate to Bounty Screen` to interact with the relevant portion of the App.

