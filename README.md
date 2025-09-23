# Full Stack Annotation App

## Overview

This is a full-stack annotation platform designed for scientific text annotation, collaborative document management, and AI-powered analysis. It consists of a robust backend (FastAPI, Supabase, PostgreSQL), a modern frontend (Next.js, React, Tailwind CSS), and specialized Streamlit tools for enhanced validation and analytics with LLM integration.

The platform enables researchers and teams to efficiently annotate scientific documents, manage project workflows, and leverage AI for improved annotation quality.

---

<div align="center">
  <img src="./image/Screenshot 2025-09-23 143403.png" alt="AgentSem Poster" width="100%" style="max-width: 1200px; height: auto;">
  <br>
  <em>Overview of the annotation application using LLM</em>
  <br><br>
  <a href="./image/Screenshot 2025-09-23 143403.png" target="_blank">🔍 View Full Resolution</a>
</div>

## Features

### Authentication & User Management

- JWT and Supabase-based authentication system
- User registration with email verification
- Role-based access control (admin/user)
- Session management with secure token handling

### Document Management

- Secure document upload to Supabase storage
- Document versioning and history tracking
- Multiple file format support
- Organized document libraries by project

### Annotation Capabilities

- Collaborative real-time annotation
- Custom tagset definition and management
- CSV import/export for tagsets
- Entity recognition and annotation
- AI-assisted annotation recommendations

### Project Management

- Multi-project support with custom settings
- Team collaboration features
- Progress tracking and analytics
- Role-based project permissions

### Technical Features

- RESTful API architecture with FastAPI
- React-based responsive UI with Radix UI components
- Supabase integration for auth, storage, and database
- LLM integration (OpenAI, Anthropic, Groq) for enhanced capabilities
- Comprehensive error handling and troubleshooting

### Analytics & Validation

- Streamlit-based annotation validation
- Quality metrics and reporting
- Entity detection and correction tools
- Export to various formats (including CoNLL)

---

## Project Structure

```
backend/      # FastAPI backend with Supabase integration
├── app/      # Main application package
│   ├── api/  # API route handlers for auth, projects, documents
│   ├── core/ # Core functionality (config, database, security)
│   ├── models/ # Database models
│   └── services/ # Business logic services
├── alembic/  # Database migrations
├── tests/    # Backend test suite
└── scripts/  # Setup and utility scripts

frontend/     # Next.js React application
├── src/
│   ├── app/  # Next.js app router pages
│   ├── components/ # UI components organized by feature
│   │   ├── admin/ # Admin panel components
│   │   ├── auth/  # Authentication components
│   │   ├── ui/    # Shared UI components
│   │   └── layout/ # Layout components
│   ├── lib/  # Utility functions and shared logic
│   └── types/ # TypeScript type definitions

streamlit/    # Validation and analytics tools
├── app.py    # Main Streamlit application
└── helper.py # Helper functions for LLM integration

# Utility scripts
apply_combined_patches.py  # Apply all patches at once
fix_jwt_auth.py           # Fix JWT authentication issues
test_document_upload.py   # Test document upload functionality
```

---

## Getting Started

### Prerequisites

- Python 3.10+ with pip
- Node.js 18+ with npm
- PostgreSQL database
- Supabase account (for authentication, storage, and database)
- API keys for LLM services (optional for Streamlit tools)
  - OpenAI
  - Anthropic
  - Groq

### Environment Setup

1. Clone the repository
2. Create and configure `.env` files in backend and frontend directories

#### Backend .env Configuration

```
# Supabase Configuration
SUPABASE_URL=your_supabase_url
SUPABASE_ANON_KEY=your_supabase_anon_key
SUPABASE_SERVICE_KEY=your_supabase_service_key

# Database Connection
DATABASE_URL=postgresql://user:password@localhost:5432/database

# JWT Configuration
SECRET_KEY=your_secret_key  # Required for JWT authentication
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60

# Application Settings
APP_NAME="Scientific Text Annotator"
DEBUG=true
ALLOWED_ORIGINS=http://localhost:3000,https://yourdomain.com
```

#### Frontend .env.local Configuration

```
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_SUPABASE_URL=your_supabase_url
NEXT_PUBLIC_SUPABASE_ANON_KEY=your_supabase_anon_key
```

### Backend Setup

1. Install dependencies:

   ```sh
   cd backend
   pip install -r requirements.txt
   ```

2. Set up database and Supabase:

   ```sh
   # Option 1: Automated setup
   python scripts/setup_supabase.py

   # Option 2: If connection issues
   python scripts/setup_supabase_alt.py
   ```

3. Run database migrations:

   ```sh
   alembic upgrade head
   ```

4. Run the server:

   ```sh
   python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload --log-level debug
   ```

5. Access API documentation:
   - Swagger UI: http://localhost:8000/docs
   - ReDoc: http://localhost:8000/redoc

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

3. Access the frontend:

   - Development: http://localhost:3000

4. Build for production:
   ```sh
   npm run build
   npm start
   ```

### Streamlit Tools

1. Install dependencies:

   ```sh
   cd streamlit
   pip install -r requirements.txt
   ```

2. Download required language models:

   ```sh
   python -m spacy download en_core_web_sm
   ```

3. Run Streamlit app:

   ```sh
   streamlit run app.py
   ```

4. Access the Streamlit dashboard:
   - http://localhost:8501

---

## Configuration

### Backend Configuration Details

- **Database Setup**:

  - Detailed instructions in `backend/README.md` and `backend/MANUAL_SETUP.md`
  - SQL schema updates in `backend/update_tagsets_schema.sql`
  - Supabase setup scripts in `backend/setup_supabase.py` and `backend/setup_supabase_alt.py`

- **API Configuration**:

  - FastAPI settings in `backend/app/core/config.py`
  - CORS settings for cross-origin requests
  - Rate limiting configuration

- **Authentication**:
  - JWT configuration in `backend/app/core/security.py`
  - Supabase auth integration in `backend/app/dependencies_supabase.py`
  - Admin role configuration

### Frontend Configuration Details

- **API Integration**:

  - Axios configuration for backend communication
  - Authentication state management with React hooks
  - Error handling and retry mechanisms

- **UI Customization**:

  - Theme settings in `tailwind.config.ts`
  - Component customization with shadcn/ui
  - Responsive layout configuration

- **Performance Optimization**:
  - Next.js build optimization
  - Image and asset optimization
  - API request caching strategy

### Streamlit Tools Configuration

- **LLM Integration**:

  - API key configuration for OpenAI, Anthropic, and Groq
  - Model selection and parameters
  - Token usage monitoring

- **Annotation Processing**:
  - Entity validation parameters
  - Batch processing settings
  - Export format configuration

---

## Testing

### Backend Testing

- **Unit Tests**:

  ```sh
  cd backend
  pytest tests/
  ```

- **API Testing**:

  - Authentication: `python test_jwt_auth.py`
  - Document Upload: `python test_document_upload.py`
  - Database Connection: `python test_db_connection.py`

- **Manual Tests**:
  - Use Swagger UI at `/docs` to test API endpoints
  - JWT validation with `auth_troubleshooter.py`
  - Document upload with `document_upload_troubleshooter.py`

### Frontend Testing

- **Component Testing**:

  ```sh
  cd frontend
  npm run test
  ```

- **Integration Testing**:

  - Use `test_integration.py` for API integration tests
  - Browser testing for UI components

- **E2E Testing**:
  - Manual end-to-end workflow testing
  - Cross-browser compatibility

---

## Troubleshooting

### Common Issues and Solutions

#### Authentication Issues

- See `AUTHENTICATION_FIX.md` and `JWT_AUTH_FIX.md` for JWT authentication fixes
- Use `auth_troubleshooter.py` to debug authentication problems
- Check Supabase policies for proper setup

#### Document Upload Issues

- See `DOCUMENT_UPLOAD_SOLUTION.md` for complete troubleshooting
- Verify storage bucket configuration
- Check permissions and CORS settings

#### Database Connection Issues

- Review connection string in `.env` file
- Use `test_db_connection.py` to verify connectivity
- Check PostgreSQL server status

#### Frontend Build Issues

- Clear Next.js cache: `npm run dev -- --turbopack`
- Update dependencies: `npm update`
- Check TypeScript errors: `npx tsc --noEmit`

---

## Documentation

### Key Documents

- **Setup Guides**:

  - `backend/SUPABASE_SETUP.md`: Complete Supabase configuration
  - `TAGSET_CSV_SETUP.md`: CSV import/export setup
  - `backend/MANUAL_SETUP.md`: Manual database configuration

- **Feature Documentation**:

  - `DOCUMENT_UPLOAD_COMPLETE_SOLUTION.md`: Document upload workflow
  - `AUTHENTICATION_FIX_REVISED.md`: Authentication system details
  - `docs/TAGSET_EDIT_FEATURE.md`: Tagset editing features

- **Roadmap and Status**:
  - `frontend/PHASE_2_PROGRESS.md`: Frontend development status
  - `streamlit/PHASE_1_STATUS.md`: Streamlit tools status
  - `streamlit/MIGRATION_TODO.md`: Migration plans

### API Documentation

- OpenAPI documentation available at `/docs` when running the backend
- Endpoint descriptions and request/response schemas
- Authentication requirements for each endpoint

---

## License

MIT License

Copyright (c) 2025

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files.

---

## Contact & Support

- **Issues & Contributions**: Open a GitHub issue on the repository
- **Feature Requests**: Use the issues tracker with "enhancement" label
- **Technical Support**: Contact the maintainer through GitHub
- **Security Issues**: Report privately to the repository owner
