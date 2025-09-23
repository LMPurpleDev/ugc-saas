from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from bson import ObjectId
from enum import Enum

class PyObjectId(ObjectId):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid objectid")
        return ObjectId(v)

    @classmethod
    def __modify_schema__(cls, field_schema):
        field_schema.update(type="string")

class UserRole(str, Enum):
    CREATOR = "creator"
    ADMIN = "admin"

class SubscriptionStatus(str, Enum):
    FREE = "free"
    BASIC = "basic"
    PREMIUM = "premium"

class NicheCategory(str, Enum):
    FASHION = "fashion"
    BEAUTY = "beauty"
    FITNESS = "fitness"
    FOOD = "food"
    TRAVEL = "travel"
    LIFESTYLE = "lifestyle"
    TECH = "tech"
    GAMING = "gaming"
    PARENTING = "parenting"
    BUSINESS = "business"
    OTHER = "other"

# User Models
class UserBase(BaseModel):
    email: EmailStr
    full_name: str
    role: UserRole = UserRole.CREATOR
    is_active: bool = True

class UserCreate(UserBase):
    password: str

class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    is_active: Optional[bool] = None

class UserInDB(UserBase):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    hashed_password: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}

class User(UserBase):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    created_at: datetime
    updated_at: datetime

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}

# Profile Models
class SocialMediaLinks(BaseModel):
    instagram: Optional[str] = None
    tiktok: Optional[str] = None
    youtube: Optional[str] = None

class InstagramTokens(BaseModel):
    access_token: str
    user_id: str
    expires_at: Optional[datetime] = None

class ProfileBase(BaseModel):
    display_name: str
    bio: Optional[str] = None
    niche: NicheCategory
    social_links: SocialMediaLinks = SocialMediaLinks()
    subscription_status: SubscriptionStatus = SubscriptionStatus.FREE

class ProfileCreate(ProfileBase):
    pass

class ProfileUpdate(BaseModel):
    display_name: Optional[str] = None
    bio: Optional[str] = None
    niche: Optional[NicheCategory] = None
    social_links: Optional[SocialMediaLinks] = None

class ProfileInDB(ProfileBase):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    user_id: PyObjectId
    instagram_tokens: Optional[InstagramTokens] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}

class Profile(ProfileBase):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    user_id: PyObjectId
    created_at: datetime
    updated_at: datetime

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}

# Metrics Models
class PostMetrics(BaseModel):
    likes: int = 0
    comments: int = 0
    shares: int = 0
    saves: int = 0
    reach: int = 0
    impressions: int = 0

class MetricsBase(BaseModel):
    profile_id: PyObjectId
    date: datetime
    followers_count: int = 0
    following_count: int = 0
    posts_count: int = 0
    avg_engagement_rate: float = 0.0
    total_likes: int = 0
    total_comments: int = 0
    total_reach: int = 0

class MetricsCreate(MetricsBase):
    pass

class MetricsInDB(MetricsBase):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    post_metrics: List[Dict[str, Any]] = []
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}

class Metrics(MetricsBase):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    post_metrics: List[Dict[str, Any]] = []
    created_at: datetime

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}

# Report Models
class ReportType(str, Enum):
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    CUSTOM = "custom"

class ReportBase(BaseModel):
    profile_id: PyObjectId
    report_type: ReportType
    period_start: datetime
    period_end: datetime
    title: str
    summary: str

class ReportCreate(ReportBase):
    pass

class ReportInDB(ReportBase):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    file_path: Optional[str] = None
    is_ready: bool = False
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}

class Report(ReportBase):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    file_path: Optional[str] = None
    is_ready: bool = False
    created_at: datetime

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}

# Post Feedback Models
class FeedbackScore(BaseModel):
    overall: float = 0.0
    content_quality: float = 0.0
    engagement_potential: float = 0.0
    visual_appeal: float = 0.0

class PostFeedbackBase(BaseModel):
    profile_id: PyObjectId
    post_id: str
    post_url: str
    post_caption: Optional[str] = None
    post_type: str  # "image", "video", "carousel"
    scores: FeedbackScore
    feedback_text: str
    suggestions: List[str] = []

class PostFeedbackCreate(PostFeedbackBase):
    pass

class PostFeedbackInDB(PostFeedbackBase):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}

class PostFeedback(PostFeedbackBase):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    created_at: datetime

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}

# Authentication Models
class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"

class TokenData(BaseModel):
    email: Optional[str] = None

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

# Dashboard Models
class DashboardStats(BaseModel):
    followers_count: int
    following_count: int
    posts_count: int
    avg_engagement_rate: float
    total_likes: int
    total_comments: int
    followers_growth: float  # percentage
    engagement_growth: float  # percentage

class ChartDataPoint(BaseModel):
    date: str
    value: float

class DashboardCharts(BaseModel):
    followers_evolution: List[ChartDataPoint]
    engagement_evolution: List[ChartDataPoint]
    reach_evolution: List[ChartDataPoint]

