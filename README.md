# duuck

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

First, install the dependencies:

```bash
npm install
```

Then, run the development server:

```bash
npm run dev
```

Scan the QRCode in the terminal with your LynxExplorer App to see the result.
Click on `Navigate to Bounty Screen` to interact with the relevant portion of the App.
