# duuck

## How to Start the Application

### Backend

#### Backend Initial Setup (Run Once)

```bash
cd backend
python -m venv .venv && .venv\\Scripts\\activate
pip install -r requirements.txt
```

#### Start the Backend Server

```bash
cd backend
.venv\Scripts\activate
uvicorn app.main:app --reload
```

### Frontend (React web fallback; Lynx code skeleton below)

#### Frontend Initial Setup (Run Once)

```bash
cd frontend-web
npm i
```

#### Start the Frontend Server

```bash
cd frontend-web
npm run dev
```