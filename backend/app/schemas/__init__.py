from pydantic import BaseModel, EmailStr
from typing import Optional, List, Dict, Any
from datetime import datetime

# User Schemas
class UserBase(BaseModel):
    email: EmailStr
    name: str
    is_active: bool = True

class UserCreate(UserBase):
    password: Optional[str] = None
    oauth_provider: Optional[str] = None
    oauth_id: Optional[str] = None

class UserUpdate(BaseModel):
    name: Optional[str] = None
    is_active: Optional[bool] = None

class UserProfile(BaseModel):
    avatar_url: Optional[str] = None
    preferences: Dict[str, Any] = {}
    subscription_tier: str = "free"
    oauth_provider: Optional[str] = None

class User(UserBase):
    id: int
    is_admin: bool
    email_verified: bool
    created_at: datetime
    updated_at: datetime
    profile: Optional[UserProfile] = None
    
    class Config:
        from_attributes = True

# Authentication Schemas
class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

class TokenData(BaseModel):
    email: Optional[str] = None

class Login(BaseModel):
    email: EmailStr
    password: str

class Register(BaseModel):
    email: EmailStr
    name: str
    password: str

class PasswordReset(BaseModel):
    email: EmailStr

class PasswordUpdate(BaseModel):
    token: str
    new_password: str

# Project Schemas
class ProjectBase(BaseModel):
    name: str
    description: Optional[str] = None
    settings: Dict[str, Any] = {}

class ProjectCreate(ProjectBase):
    team_id: Optional[int] = None

class ProjectUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    settings: Optional[Dict[str, Any]] = None

class Project(ProjectBase):
    id: int
    owner_id: int
    team_id: Optional[int] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

# Document Schemas
class DocumentBase(BaseModel):
    name: str
    content: str

class DocumentCreate(DocumentBase):
    project_id: int

class DocumentUpdate(BaseModel):
    name: Optional[str] = None
    content: Optional[str] = None

class Document(DocumentBase):
    id: int
    project_id: int
    file_path: Optional[str] = None
    uploaded_by: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

# Tag Set Schemas
class TagBase(BaseModel):
    name: str
    definition: Optional[str] = None
    examples: Optional[str] = None
    color: Optional[str] = None

class TagSetBase(BaseModel):
    name: str
    tags_json: Dict[str, Any]

class TagSetCreate(TagSetBase):
    project_id: int

class TagSetUpdate(BaseModel):
    name: Optional[str] = None
    tags_json: Optional[Dict[str, Any]] = None

class TagSet(TagSetBase):
    id: int
    project_id: int
    created_by: int
    created_at: datetime
    tags: List[TagBase] = []
    
    class Config:
        from_attributes = True

# Annotation Schemas
class AnnotationBase(BaseModel):
    text: str
    start_pos: int
    end_pos: int
    confidence: Optional[float] = None
    source: str = "manual"

class AnnotationCreate(AnnotationBase):
    document_id: int
    tag_id: int

class AnnotationUpdate(BaseModel):
    text: Optional[str] = None
    start_pos: Optional[int] = None
    end_pos: Optional[int] = None
    tag_id: Optional[int] = None
    confidence: Optional[float] = None

class Annotation(AnnotationBase):
    id: int
    document_id: int
    user_id: int
    tag_id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

# LLM Processing Schemas
class LLMAnnotationRequest(BaseModel):
    document_id: int
    tag_set_id: int
    provider: str = "OpenAI"
    model: str = "gpt-4"
    temperature: float = 0.1
    max_tokens: int = 1000
    chunk_size: int = 1000

class LLMAnnotationResponse(BaseModel):
    task_id: str
    status: str
    message: str

class AnnotationJobStatus(BaseModel):
    task_id: str
    status: str
    progress: int
    result: Optional[List[Annotation]] = None
    error: Optional[str] = None

# Validation Schemas
class ValidationRequest(BaseModel):
    annotation_ids: List[int]

class ValidationResult(BaseModel):
    annotation_id: int
    status: str
    error_message: Optional[str] = None
    fixed_automatically: bool = False
    suggestions: Optional[Dict[str, Any]] = None

class ValidationResponse(BaseModel):
    results: List[ValidationResult]
    summary: Dict[str, int]

# Export Schemas
class ExportRequest(BaseModel):
    document_id: int
    format: str = "conll"  # 'conll', 'json', 'csv'
    include_metadata: bool = True

class ExportResponse(BaseModel):
    download_url: str
    file_name: str
    format: str

# Team Schemas
class TeamBase(BaseModel):
    name: str
    description: Optional[str] = None

class TeamCreate(TeamBase):
    pass

class TeamUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None

class TeamMemberAdd(BaseModel):
    user_id: int
    role: str = "member"

class Team(TeamBase):
    id: int
    owner_id: int
    created_at: datetime
    
    class Config:
        from_attributes = True

# Admin Schemas
class AdminUserUpdate(BaseModel):
    is_active: Optional[bool] = None
    is_admin: Optional[bool] = None
    email_verified: Optional[bool] = None

class PlatformStats(BaseModel):
    total_users: int
    total_projects: int
    total_documents: int
    total_annotations: int
    active_users_last_30_days: int
