# Full Stack Annotation App

## Overview

This is a full-stack annotation platform designed for collaborative document annotation, user authentication, and data management. It consists of a backend (FastAPI, Supabase, PostgreSQL), a frontend (Next.js, React, Tailwind CSS), and optional Streamlit tools for enhanced validation and analytics.

---

## Features

- User registration, authentication (JWT, Supabase)
- Document upload and annotation
- Tagset management (CSV import, editing)
- Project and user management
- RESTful API endpoints
- Frontend dashboard for annotation workflow
- Streamlit-based validation and analytics

---

## Project Structure

```
backend/      # FastAPI backend, database, authentication
frontend/     # Next.js React frontend, UI components

```

---

## Getting Started

### Prerequisites

- Python 3.10+
- Node.js 18+
- PostgreSQL database
- Supabase account (for auth/storage)

### Backend Setup

1. Install dependencies:
   ```sh
   cd backend
   pip install -r requirements.txt
   ```
2. Configure environment variables (Supabase, DB connection)
3. Run the server:
   ```sh
   uvicorn main:app --reload
   ```

### Frontend Setup

1. Install dependencies:
   ```sh
   cd frontend
   npm install
   ```
2. Start the development server:
   ```sh
   npm run dev
   ```

### Streamlit Tools

1. Install dependencies:
   ```sh
   cd streamlit
   pip install -r requirements.txt
   ```
2. Run Streamlit app:
   ```sh
   streamlit run app.py
   ```

---

## Configuration

- See `backend/README.md` and `frontend/README.md` for detailed setup and environment variables.
- Database schema migrations: `backend/update_tagsets_schema.sql`
- Supabase setup: `backend/setup_supabase.py`

---

## Testing

- Backend: Run Python test files in `backend/`
- Frontend: Use `npm test` or integration scripts
- End-to-end: Manual and automated tests available

---

## Documentation

- See Markdown files in the root and `docs/` for feature guides and troubleshooting.
- Key docs:
  - `AUTHENTICATION_FIX.md`, `DOCUMENT_UPLOAD_SOLUTION.md`, `TAGSET_CSV_SETUP.md`

---

## License

MIT License

---

## Contact

For issues or contributions, open a GitHub issue or contact the maintainer.
