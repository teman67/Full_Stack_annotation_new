# Backend - Annotation LLM API

FastAPI backend for the Annotation LLM application with Supabase integration.

## 🏗️ Project Structure

```
backend/
├── app/                    # Main application package
│   ├── api/               # API route handlers
│   │   ├── auth.py        # Authentication endpoints
│   │   ├── projects.py    # Project management
│   │   ├── documents.py   # Document handling  
│   │   ├── annotations.py # Annotation CRUD
│   │   └── admin.py       # Admin operations
│   ├── core/              # Core functionality
│   │   ├── config.py      # Configuration settings
│   │   ├── database.py    # Database connection
│   │   └── security.py    # Security utilities
│   ├── models/            # SQLAlchemy database models
│   ├── schemas/           # Pydantic request/response models
│   ├── services/          # Business logic services
│   │   ├── supabase_auth.py # Authentication service
│   │   ├── supabase_db.py   # Database service
│   │   └── llm_service.py   # LLM processing service
│   └── dependencies.py    # FastAPI dependencies
├── docs/                  # Documentation
│   ├── MANUAL_SETUP.md    # Manual database setup guide
│   └── SUPABASE_SETUP.md  # Supabase configuration guide
├── scripts/               # Setup and utility scripts
│   ├── setup_supabase.py     # Database setup (PostgreSQL)
│   ├── setup_supabase_alt.py # Database setup (Supabase client)
│   ├── setup.bat             # Windows setup
│   └── setup.sh              # Unix/Linux setup
├── tests/                 # Test files
│   ├── test_comprehensive_db.py # Full database test
│   ├── test_db_connection.py    # Connection test
│   └── test_supabase_client.py  # Supabase client test
├── alembic/               # Database migrations
├── main.py                # FastAPI application entry point
├── requirements.txt       # Python dependencies
├── .env                   # Environment variables (local)
├── .env.example          # Environment template
├── Dockerfile            # Container configuration
└── alembic.ini           # Alembic configuration
```

## 🚀 Quick Start

### 1. Environment Setup
```bash
# Copy environment template
cp .env.example .env

# Edit .env with your Supabase credentials
# SUPABASE_URL=your_supabase_url
# SUPABASE_ANON_KEY=your_anon_key
# DATABASE_URL=your_postgres_url
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Database Setup
```bash
# Option 1: Automatic setup
python scripts/setup_supabase.py

# Option 2: If connection issues
python scripts/setup_supabase_alt.py

# Option 3: Manual setup
# Follow docs/MANUAL_SETUP.md
```

### 4. Start Server
```bash
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### 5. Access API
- **API Docs**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

## 🧪 Testing

Run tests to verify setup:
```bash
# Comprehensive database test
python tests/test_comprehensive_db.py

# Basic connection test  
python tests/test_db_connection.py

# Supabase client test
python tests/test_supabase_client.py
```

## 📚 API Documentation

Once running, visit http://localhost:8000/docs for interactive API documentation.

### Main Endpoints
- **Authentication**: `/auth/*` - User registration, login, logout
- **Projects**: `/projects/*` - Project management 
- **Documents**: `/documents/*` - Document upload and processing
- **Annotations**: `/annotations/*` - Text annotation CRUD
- **Admin**: `/admin/*` - User and system administration

## 🔧 Configuration

### Environment Variables
- `SUPABASE_URL`: Supabase project URL
- `SUPABASE_ANON_KEY`: Supabase anonymous key
- `SUPABASE_SERVICE_ROLE_KEY`: Supabase service role key
- `DATABASE_URL`: PostgreSQL connection string
- `SECRET_KEY`: JWT signing key
- `OPENAI_API_KEY`: OpenAI API key (optional)
- `ANTHROPIC_API_KEY`: Anthropic API key (optional)
- `GROQ_API_KEY`: Groq API key (optional)

### Database
- **Provider**: Supabase (PostgreSQL)
- **ORM**: SQLAlchemy 2.0 with async support
- **Migrations**: Alembic

### Authentication
- **Provider**: Supabase Auth
- **Method**: JWT tokens
- **Features**: Registration, login, logout, role-based access

## 🐳 Docker Support

```bash
# Build image
docker build -t annotation-llm-backend .

# Run container  
docker run -p 8000:8000 --env-file .env annotation-llm-backend
```

## 📖 Documentation

- **Setup Guide**: `docs/MANUAL_SETUP.md`
- **Supabase Config**: `docs/SUPABASE_SETUP.md`
- **API Docs**: http://localhost:8000/docs (when running)

## 🆘 Troubleshooting

### Common Issues

1. **Database Connection Failed**
   - Check DATABASE_URL in .env
   - Verify Supabase credentials
   - Run `python tests/test_db_connection.py`

2. **Import Errors**
   - Ensure you're in the backend directory
   - Check Python path and dependencies

3. **Server Won't Start**
   - Check port 8000 is available
   - Verify all environment variables are set
   - Check logs for specific errors

### Getting Help

1. Check the test files in `tests/` directory
2. Review documentation in `docs/` directory  
3. Check the issue tracker for known problems
