# Duuck API Testing Platform

## Overview

Duuck API Testing Platform is a full-stack web application designed to facilitate API testing, moderation, and fraud detection for bounty and livestream-based platforms. It provides a secure and interactive environment for managing user-generated content, financial incentives, and livestream events.

## Features

- **Backend (Python):**
  - API endpoints for idea moderation, bounty management, and fraud detection.
  - Machine learning model for fraud detection.
  - SQLite database integration.
  - Modular architecture for scalability.

- **Frontend (React + TypeScript):**
  - Interactive UI for bounty management and livestream features.
  - Components for user profiles, modals, progress bars, and more.
  - Asset-rich interface with custom icons and images.

- **Testing:**
  - Unit and integration tests for frontend components.
  - HTTP request testing for backend endpoints.

## Development Tools

- **Frontend:** React, TypeScript, Tailwind CSS, Vite, Vitest
- **Backend:** Python, SQLite, scikit-learn (for ML), FastAPI/Flask (inferred)
- **General:** VS Code, npm, pip

## APIs

- Custom internal APIs for moderation, bounty management, and fraud detection.
- Potential integration with external livestream APIs (e.g., TikTok).

## Assets

- PNG and JPG images for UI icons and backgrounds (`src/assets/`)
- Custom CSS for component styling

## Libraries

- **Frontend:** React, TypeScript, Tailwind CSS, Vitest, Vite
- **Backend:** Python, scikit-learn, SQLAlchemy (or similar), FastAPI/Flask

## Problem Statement

This project addresses the need for a secure, scalable, and interactive platform for API testing and moderation, with features for fraud detection, bounty management, and livestream/video integration.

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

