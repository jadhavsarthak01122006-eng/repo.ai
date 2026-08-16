# CivicPulse - Closed-Loop Civic Operating System

## 🏙️ Vision
CivicPulse transforms unstructured citizen complaints into prioritized, trackable, and verifiable work orders, bridging the trust gap between citizens and municipalities.

## 🚀 Quick Start

### Prerequisites
- Docker & Docker Compose
- OR: Python 3.11+, Node.js 20+

### Option 1: Docker (Recommended)
```bash
docker-compose up -d
```

This starts:
- PostgreSQL with PostGIS (port 5432)
- Redis (port 6379)
- FastAPI Backend (port 8000)
- Next.js Frontend (port 3000)

### Option 2: Manual Setup

#### Backend
```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

#### Frontend
```bash
cd frontend
npm install
npm run dev
```

## 📁 Project Structure

```
civicpulse/
├── backend/                 # FastAPI backend
│   ├── app/
│   │   ├── api/            # API routes
│   │   ├── core/           # Config, security, database
│   │   ├── models/         # SQLAlchemy models
│   │   ├── schemas/        # Pydantic schemas
│   │   └── services/       # Business logic, AI service
│   └── requirements.txt
├── frontend/               # Next.js PWA frontend
│   ├── src/
│   │   ├── components/     # Reusable components
│   │   ├── pages/          # Next.js pages
│   │   ├── hooks/          # Custom hooks, Zustand stores
│   │   └── utils/          # API client, utilities
│   └── package.json
└── docker-compose.yml
```

## 🔑 Key Features

### Closed-Loop Lifecycle
1. **Citizen** → Reports issue via PWA with photo + GPS
2. **AI** → Categorizes, estimates severity, detects duplicates
3. **Officer** → Reviews AI suggestions, assigns tasks
4. **Field Worker** → Navigates to site, uploads before/after photos
5. **Verification** → Citizen notified, loop closed

### Smart Features
- 🤖 **AI Triage**: Multimodal LLM categorization with confidence scores
- 📍 **Duplicate Detection**: Spatial + text similarity prevents spam
- 🎯 **Priority Scoring**: Severity + location criticality + age
- ✅ **Evidence-Based Closure**: Before/after photos required
- 🔐 **RBAC**: Role-based access control (Citizen, Officer, Field Worker, Admin)

## 🛠️ Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | Next.js 14, TypeScript, Tailwind CSS, Zustand |
| Backend | FastAPI, Python 3.11 |
| Database | PostgreSQL + PostGIS + pgvector |
| Maps | MapLibre GL JS + OpenStreetMap |
| Cache | Redis |
| AI | Multimodal LLM APIs (fallback rules engine) |
| Auth | JWT with OAuth2 |

## 📡 API Endpoints

### Authentication
- `POST /api/auth/register` - Register new user
- `POST /api/auth/login` - Login (email + password)
- `GET /api/auth/me` - Get current user

### Issue Reports
- `POST /api/reports` - Create new report (Citizens)
- `GET /api/reports` - List reports with pagination
- `GET /api/reports/{id}` - Get specific report
- `PUT /api/reports/{id}` - Update report (Officers/Workers)
- `POST /api/reports/{primary}/merge/{duplicate}` - Merge duplicates (Officers)

### Dashboard
- `GET /api/dashboard/stats` - Get statistics (Officers/Admins)
- `GET /api/reports/ai/triage/{id}` - Get AI triage suggestion

## 👥 User Roles

| Role | Permissions |
|------|-------------|
| **Citizen** | Create reports, view own reports |
| **Officer** | Assign issues, merge duplicates, view dashboard |
| **Field Worker** | Update status, upload resolution photos |
| **Admin** | Full access |

## 🎯 Demo Flow (Golden Path)

1. Citizen spots pothole → snaps photo (30 secs)
2. AI flags as "High Severity - Roads Dept" + warns of duplicate
3. Officer clicks "Assign"
4. Worker app shows route → uploads fixed photo
5. Citizen gets push notification: "Resolved"
6. Dashboard updates city health score in real-time

## ⚠️ MVP Constraints (What We DON'T Build)

- ❌ Blockchain (zero value for civic routing)
- ❌ Native iOS/Android apps (PWA is sufficient)
- ❌ Custom CV models (use Multimodal LLMs)
- ❌ Heavy gamification (encourages spam)
- ❌ Microservices (modular monolith for speed)

## 🔧 Environment Variables

### Backend (.env)
```
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/civicpulse
SECRET_KEY=your-secret-key-change-in-production
REDIS_URL=redis://localhost:6379
AI_API_KEY=optional-for-multimodal-llm
```

### Frontend (.env.local)
```
NEXT_PUBLIC_API_URL=http://localhost:8000/api
```

## 📝 License
MIT License - Build better cities together!

---

**Mentor's Directive**: Build the lifecycle first, polish second. A working end-to-end loop beats a beautiful app that submits forms into a void.
