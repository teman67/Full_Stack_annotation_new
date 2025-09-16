# 🚀 Full-Stack Migration To-Do List

## Scientific Text Annotator - Streamlit to Modern Web App

### 📋 Project Overview

**Goal**: Migrate current Streamlit-based Scientific Text Annotator to a modern, scalable, multi-user full-stack application

---

## 🎯 Phase 1: Backend Foundation & API Development (Weeks 1-3)

### Week 1: Project Setup & Core Infrastructure

#### 🔧 Development Environment Setup

- [x] **Create new repository structure**

  - [x] Create `backend/` directory for FastAPI application
  - [x] Create `frontend/` directory for Next.js application
  - [x] Create `shared/` directory for common types and utilities
  - [x] Set up `.gitignore` files for both frontend and backend
  - [x] Create `docker-compose.yml` for local development

- [x] **Backend Project Initialization**

  - [x] Initialize FastAPI project with proper structure
  - [x] Set up virtual environment and requirements.txt
  - [x] Install core dependencies (FastAPI, SQLAlchemy, Alembic, etc.)
  - [x] Configure environment variables and settings management
  - [x] Set up logging and error handling

- [x] **Database Setup**
  - [x] Create Supabase account and project
  - [x] Set up PostgreSQL database connection with RLS policies
  - [x] Install and configure Alembic for migrations
  - [x] Design initial database schema
  - [x] Create base models and relationships
  - [ ] Set up initial admin account seeding
  - [ ] Configure Supabase OAuth providers (Google, GitHub, LinkedIn)
  - [ ] Implement database backup and recovery procedures

#### 📊 Database Schema Design

- [x] **User Management Tables**

  - [x] `users` table (id, email, name, created_at, updated_at, is_active, is_admin, email_verified)
  - [x] `user_profiles` table (user_id, avatar_url, preferences, subscription_tier, oauth_provider, oauth_id)
  - [x] `teams` table (id, name, description, owner_id, created_at)
  - [x] `team_members` table (team_id, user_id, role, joined_at)
  - [x] `admin_accounts` table (user_id, permissions, created_by, created_at, last_login)

- [x] **Project & Document Tables**

  - [x] `projects` table (id, name, description, owner_id, team_id, settings, created_at)
  - [x] `documents` table (id, project_id, name, content, file_path, uploaded_by, created_at)
  - [x] `tag_sets` table (id, project_id, name, tags_json, created_by, created_at)
  - [x] `tags` table (id, tag_set_id, name, definition, examples, color)

- [x] **Annotation Tables**
  - [x] `annotations` table (id, document_id, user_id, tag_id, text, start_pos, end_pos, confidence, source, created_at)
  - [x] `annotation_history` table (annotation_id, field_changed, old_value, new_value, changed_by, changed_at)
  - [x] `validation_results` table (annotation_id, status, error_message, fixed_automatically, validated_at)

#### 🔐 Authentication & Authorization

- [x] **Supabase Auth Integration**

  - [x] Set up Supabase Auth configuration with RLS policies
  - [x] Implement JWT token validation middleware
  - [x] Create user registration and login endpoints
  - [ ] Set up OAuth providers integration:
    - [ ] Configure Google OAuth (Gmail signup)
    - [ ] Configure GitHub OAuth integration
    - [ ] Configure LinkedIn OAuth integration
    - [ ] Set up OAuth callback handlers
    - [ ] Implement OAuth profile data mapping
  - [x] Implement password reset functionality
  - [ ] Set up email verification with Supabase
  - [ ] Create admin account seeding system
  - [ ] Implement admin account creation workflow

- [x] **Permission System**
  - [x] Define role-based access control (RBAC) with admin roles
  - [x] Create permission decorators and middleware
  - [x] Implement project-level permissions
  - [x] Set up team-based access control
  - [x] Create admin-only endpoints and middleware
  - [x] Implement super admin vs regular admin permissions
  - [x] Set up user management permissions for admins

### Week 2: Core API Development

#### 🛠 Core API Endpoints

- [ ] **Authentication Endpoints**

  - [ ] `POST /auth/register` - User registration (email/password)
  - [ ] `POST /auth/login` - User login (email/password)
  - [ ] `POST /auth/logout` - User logout
  - [ ] `POST /auth/refresh` - Token refresh
  - [ ] `POST /auth/reset-password` - Password reset
  - [ ] `GET /auth/oauth/google` - Google OAuth initiation
  - [ ] `GET /auth/oauth/github` - GitHub OAuth initiation
  - [ ] `GET /auth/oauth/linkedin` - LinkedIn OAuth initiation
  - [ ] `POST /auth/oauth/callback` - OAuth callback handler
  - [ ] `POST /auth/verify-email` - Email verification
  - [ ] `POST /auth/resend-verification` - Resend verification email

- [ ] **User Management Endpoints**

  - [ ] `GET /users/me` - Get current user profile
  - [ ] `PUT /users/me` - Update user profile
  - [ ] `GET /users/{user_id}` - Get user by ID
  - [ ] `DELETE /users/me` - Delete user account
  - [ ] `POST /users/link-oauth` - Link OAuth provider to existing account
  - [ ] `DELETE /users/unlink-oauth/{provider}` - Unlink OAuth provider

- [ ] **Admin Management Endpoints**

  - [ ] `GET /admin/users` - List all users (admin only)
  - [ ] `PUT /admin/users/{user_id}` - Update any user (admin only)
  - [ ] `DELETE /admin/users/{user_id}` - Delete any user (admin only)
  - [ ] `POST /admin/users/{user_id}/promote` - Promote user to admin
  - [ ] `POST /admin/users/{user_id}/demote` - Remove admin privileges
  - [ ] `GET /admin/stats` - Get platform statistics
  - [ ] `GET /admin/logs` - Get system logs and audit trail
  - [ ] `POST /admin/announcements` - Create platform announcements

- [ ] **Project Management Endpoints**
  - [ ] `GET /projects` - List user's projects
  - [ ] `POST /projects` - Create new project
  - [ ] `GET /projects/{project_id}` - Get project details
  - [ ] `PUT /projects/{project_id}` - Update project
  - [ ] `DELETE /projects/{project_id}` - Delete project
  - [ ] `POST /projects/{project_id}/members` - Add team member
  - [ ] `DELETE /projects/{project_id}/members/{user_id}` - Remove member

#### 📄 Document Management

- [ ] **Document Endpoints**

  - [ ] `GET /projects/{project_id}/documents` - List documents
  - [ ] `POST /projects/{project_id}/documents` - Upload document
  - [ ] `GET /documents/{document_id}` - Get document content
  - [ ] `PUT /documents/{document_id}` - Update document
  - [ ] `DELETE /documents/{document_id}` - Delete document

- [ ] **File Upload & Storage**
  - [ ] Set up Supabase Storage integration
  - [ ] Implement file upload validation (size, type)
  - [ ] Create file processing pipeline for text extraction
  - [ ] Support multiple formats (TXT, PDF, DOCX)
  - [ ] Implement file versioning system

### Week 3: LLM Integration & Annotation Engine

#### 🤖 LLM Service Architecture

- [ ] **Migrate Current LLM Logic**

  - [ ] Extract and refactor `llm_clients.py` for FastAPI
  - [ ] Implement async LLM client wrapper
  - [ ] Add support for multiple LLM providers (OpenAI, Claude, Groq)
  - [ ] Implement rate limiting and retry logic
  - [ ] Add LLM response caching

- [ ] **Annotation Processing Service**
  - [ ] Migrate `helper.py` annotation functions
  - [ ] Implement text chunking service
  - [ ] Create annotation aggregation logic
  - [ ] Add position validation and fixing algorithms
  - [ ] Implement duplicate detection and removal

#### 🔄 Background Job System

- [ ] **Celery Setup**

  - [ ] Install and configure Celery with Redis
  - [ ] Create task queue for LLM processing
  - [ ] Implement progress tracking for long-running tasks
  - [ ] Add job status endpoints
  - [ ] Set up task scheduling for batch processing

- [ ] **Annotation Tasks**
  - [ ] `annotate_document_task` - Process document with LLM
  - [ ] `validate_annotations_task` - Validate annotation positions
  - [ ] `export_annotations_task` - Generate export files
  - [ ] `bulk_annotation_task` - Process multiple documents

#### 📊 Tag Set Management

- [ ] **Tag Set Endpoints**
  - [ ] `GET /projects/{project_id}/tagsets` - List tag sets
  - [ ] `POST /projects/{project_id}/tagsets` - Create tag set
  - [ ] `PUT /tagsets/{tagset_id}` - Update tag set
  - [ ] `DELETE /tagsets/{tagset_id}` - Delete tag set
  - [ ] `POST /tagsets/import` - Import tag set from CSV

---

## 🎨 Phase 2: Frontend Development (Weeks 4-6)

### Week 4: Next.js Setup & Core UI

#### 🏗 Project Setup

- [ ] **Next.js 14 Initialization**

  - [ ] Create Next.js project with TypeScript
  - [ ] Set up Tailwind CSS and configure design system
  - [ ] Install and configure shadcn/ui components
  - [ ] Set up ESLint, Prettier, and pre-commit hooks
  - [ ] Configure environment variables for different stages

- [ ] **State Management**
  - [ ] Install and configure Zustand
  - [ ] Create stores for user, projects, annotations
  - [ ] Set up API client with axios/fetch
  - [ ] Implement error handling and loading states
  - [ ] Add optimistic updates for better UX

#### 🔐 Authentication Flow

- [ ] **Auth Implementation**

  - [ ] Set up NextAuth.js with Supabase adapter
  - [ ] Create login/register pages with OAuth options
  - [ ] Implement OAuth sign-in buttons (Google, GitHub, LinkedIn)
  - [ ] Add email verification flow
  - [ ] Implement protected route HOC with admin checks
  - [ ] Add auth context and hooks
  - [ ] Create user profile management with OAuth linking
  - [ ] Implement admin dashboard and user management UI
  - [ ] Add role-based UI components and permissions

- [ ] **Core Layout & Navigation**
  - [ ] Design responsive app layout
  - [ ] Create navigation components (sidebar, header)
  - [ ] Implement breadcrumb navigation
  - [ ] Add theme switching (light/dark mode)
  - [ ] Create loading skeletons and error boundaries

### Week 5: Project & Document Management UI

#### 📁 Project Management Interface

- [ ] **Project Dashboard**

  - [ ] Create project listing page with cards/table view
  - [ ] Implement project creation modal
  - [ ] Add project settings page
  - [ ] Create team member management interface
  - [ ] Add project statistics and analytics

- [ ] **Document Management**
  - [ ] Design document upload interface with drag-and-drop
  - [ ] Create document listing with preview
  - [ ] Implement document viewer component
  - [ ] Add document metadata editing
  - [ ] Create bulk document operations

#### 🏷 Tag Set Management UI

- [ ] **Tag Set Interface**
  - [ ] Create tag set creation/editing forms
  - [ ] Implement CSV import/export functionality
  - [ ] Add tag definition management with examples
  - [ ] Create tag color customization
  - [ ] Implement tag set versioning UI

### Week 6: Annotation Editor & Core Features

#### ✏️ Annotation Editor

- [ ] **Text Annotation Interface**

  - [ ] Create text highlighting component
  - [ ] Implement text selection and annotation creation
  - [ ] Add annotation editing and deletion
  - [ ] Create annotation sidebar/panel
  - [ ] Implement keyboard shortcuts

- [ ] **LLM Annotation Runner**
  - [ ] Create annotation configuration panel
  - [ ] Implement real-time progress tracking
  - [ ] Add job cancellation functionality
  - [ ] Create results preview and acceptance flow
  - [ ] Add annotation quality metrics display

#### 🔍 Validation & Quality Control

- [ ] **Annotation Validation UI**
  - [ ] Create validation results display
  - [ ] Implement auto-fix suggestions interface
  - [ ] Add manual position correction tools
  - [ ] Create validation reports and analytics
  - [ ] Implement batch validation operations

---

## 🚀 Phase 3: Advanced Features & Polish (Weeks 7-8)

### Week 7: Admin Dashboard & Real-time Collaboration

#### 👑 Admin Dashboard & Management

- [ ] **Admin Dashboard UI**

  - [ ] Create admin-only dashboard with platform overview
  - [ ] Implement user management interface (view, edit, delete users)
  - [ ] Add user activity monitoring and analytics
  - [ ] Create admin role management (promote/demote users)
  - [ ] Implement system health monitoring dashboard
  - [ ] Add platform usage statistics and metrics
  - [ ] Create announcement management system
  - [ ] Implement audit log viewer for admin actions

- [ ] **Admin Tools & Features**
  - [ ] Add bulk user operations (import, export, bulk actions)
  - [ ] Implement project oversight and management tools
  - [ ] Create system configuration management
  - [ ] Add database backup and maintenance tools
  - [ ] Implement user support ticket system
  - [ ] Add content moderation tools for annotations
  - [ ] Create admin notification system

#### 🤝 Real-time Collaboration

- [ ] **WebSocket Integration**

  - [ ] Set up Socket.io on backend and frontend
  - [ ] Implement real-time annotation updates
  - [ ] Add user presence indicators
  - [ ] Create conflict resolution for simultaneous edits
  - [ ] Add collaborative cursor tracking

- [ ] **Advanced Annotation Features**
  - [ ] Implement nested annotation support
  - [ ] Add annotation relationships and dependencies
  - [ ] Create annotation templates and presets
  - [ ] Implement smart auto-suggestions
  - [ ] Add annotation quality scoring

#### 📊 Analytics & Reporting

- [ ] **Analytics Dashboard**
  - [ ] Create project analytics overview
  - [ ] Add annotation quality metrics
  - [ ] Implement user activity tracking
  - [ ] Create export usage statistics
  - [ ] Add LLM cost tracking and optimization

### Week 8: Export System & API Integration

#### 📤 Export System

- [ ] **Export Functionality**

  - [ ] Migrate CoNLL export from current app
  - [ ] Implement JSON export with metadata
  - [ ] Add CSV export for spreadsheet analysis
  - [ ] Create custom export format builder
  - [ ] Add scheduled export functionality

- [ ] **API Documentation & SDK**
  - [ ] Generate comprehensive OpenAPI documentation
  - [ ] Create API usage examples and tutorials
  - [ ] Build JavaScript/Python SDK for integrations
  - [ ] Add API key management interface
  - [ ] Implement rate limiting and usage tracking

---

## 🔧 Phase 4: Testing, Deployment & Launch (Weeks 9-10)

### Week 9: Testing & Quality Assurance

#### 🧪 Testing Implementation

- [ ] **Backend Testing**

  - [ ] Write unit tests for all API endpoints
  - [ ] Create integration tests for LLM workflows
  - [ ] Add database migration tests
  - [ ] Implement performance benchmarks
  - [ ] Add security vulnerability scanning

- [ ] **Frontend Testing**
  - [ ] Write component unit tests with Jest/RTL
  - [ ] Create E2E tests with Playwright
  - [ ] Add accessibility testing
  - [ ] Implement visual regression testing
  - [ ] Test responsive design across devices

#### 🔒 Security & Performance

- [ ] **Security Hardening**

  - [ ] Implement API rate limiting
  - [ ] Add CORS configuration
  - [ ] Set up SQL injection prevention
  - [ ] Add XSS protection
  - [ ] Implement proper data sanitization

- [ ] **Performance Optimization**
  - [ ] Optimize database queries and indexing
  - [ ] Implement caching strategies
  - [ ] Add CDN for static assets
  - [ ] Optimize bundle size and loading times
  - [ ] Add monitoring and alerting

### Week 10: Deployment & Launch Preparation

#### 🚀 Deployment Setup

- [ ] **Infrastructure Setup**

  - [ ] Set up production Supabase instance
  - [ ] Configure Vercel for frontend deployment
  - [ ] Set up Railway/Render for backend deployment
  - [ ] Configure environment variables for production
  - [ ] Set up domain and SSL certificates

- [ ] **CI/CD Pipeline**
  - [ ] Create GitHub Actions workflows
  - [ ] Set up automated testing on PRs
  - [ ] Configure automatic deployments
  - [ ] Add deployment health checks
  - [ ] Set up rollback procedures

#### 📊 Monitoring & Analytics

- [ ] **Production Monitoring**
  - [ ] Set up Sentry for error tracking
  - [ ] Configure application performance monitoring
  - [ ] Add user analytics with privacy compliance
  - [ ] Set up uptime monitoring
  - [ ] Create alerting for critical issues

---

## 📋 Migration Checklist

### 🔄 Data Migration

- [ ] **Export Current Data**
  - [ ] Export any existing user preferences
  - [ ] Save current tag set configurations
  - [ ] Document current workflow patterns
  - [ ] Create migration scripts for user data

### 📚 Documentation

- [ ] **User Documentation**

  - [ ] Create user onboarding guide
  - [ ] Write feature documentation
  - [ ] Create video tutorials
  - [ ] Add FAQ and troubleshooting guides

- [ ] **Developer Documentation**
  - [ ] Document API endpoints and schemas
  - [ ] Create development setup guide
  - [ ] Write deployment instructions
  - [ ] Document architecture decisions

### 🎯 Launch Preparation

- [ ] **Beta Testing**

  - [ ] Recruit beta users from current app users
  - [ ] Create feedback collection system
  - [ ] Run performance tests with real data
  - [ ] Validate migration success criteria

- [ ] **Marketing & Communication**
  - [ ] Create migration announcement
  - [ ] Prepare feature comparison documentation
  - [ ] Set up user support channels
  - [ ] Plan rollout strategy

---

## 🎨 Future Enhancements (Post-Launch)

### 🔮 Advanced Features

- [ ] **AI/ML Enhancements**

  - [ ] Implement active learning for annotation improvement
  - [ ] Add custom model fine-tuning capabilities
  - [ ] Create annotation quality prediction
  - [ ] Implement smart batch processing

- [ ] **Enterprise Features**

  - [ ] Add SSO integration (SAML, LDAP)
  - [ ] Implement audit logging and compliance
  - [ ] Create admin dashboard for organizations
  - [ ] Add usage quotas and billing integration

- [ ] **Integration & API Expansion**
  - [ ] Create webhook system for external integrations
  - [ ] Add support for more file formats
  - [ ] Implement batch API endpoints
  - [ ] Create plugin system for custom processors

---

## 📊 Success Metrics

### 🎯 Technical Metrics

- [ ] **Performance**

  - [ ] Page load time < 2 seconds
  - [ ] API response time < 500ms
  - [ ] 99.9% uptime SLA
  - [ ] Zero data loss during migration

- [ ] **Quality**
  - [ ] > 80% test coverage
  - [ ] Zero critical security vulnerabilities
  - [ ] <1% error rate in production
  - [ ] Successful handling of 10x current load

### 👥 User Experience Metrics

- [ ] **Adoption**
  - [ ] 100% of beta users successfully migrated
  - [ ] <5% user churn during transition
  - [ ] Positive user satisfaction scores (>4/5)
  - [ ] Reduced time-to-first-annotation by 50%

---

## 🛠 Tools & Resources

### 📦 Development Tools

- **Backend**: FastAPI, SQLAlchemy, Alembic, Celery, Redis
- **Frontend**: Next.js 14, TypeScript, Tailwind CSS, shadcn/ui, Zustand
- **Database**: PostgreSQL (Supabase)
- **Testing**: Jest, RTL, Playwright, pytest
- **Deployment**: Vercel, Railway/Render, GitHub Actions
- **Monitoring**: Sentry, Vercel Analytics

### 📖 Documentation References

- [ ] FastAPI documentation and best practices
- [ ] Next.js 14 documentation and migration guides
- [ ] Supabase documentation and examples
- [ ] React testing best practices
- [ ] PostgreSQL optimization guides

---

## 📝 Notes & Decisions

### 🎯 Key Architectural Decisions

- **Database**: PostgreSQL with Supabase for managed hosting and auth
- **Backend**: FastAPI for Python ecosystem compatibility
- **Frontend**: Next.js for modern React with SSR capabilities
- **State Management**: Zustand for simplicity and performance
- **Real-time**: Socket.io for collaborative features

### ⚠️ Risk Mitigation

- **Data Loss**: Comprehensive backup strategy and migration testing
- **Performance**: Load testing and gradual rollout
- **User Adoption**: Beta testing and feedback integration
- **Technical Debt**: Regular code reviews and refactoring sprints

---

**Last Updated**: [Date]  
**Next Review**: [Date]  
**Status**: Planning Phase

---

_This document serves as a living roadmap for the migration project. It should be updated regularly as progress is made and requirements evolve._
