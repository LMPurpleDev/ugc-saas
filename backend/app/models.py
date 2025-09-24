
from pydantic import BaseModel, EmailStr, Field, ConfigDict
from typing import Optional, List, Dict, Any, Type
from datetime import datetime
from bson import ObjectId
from enum import Enum
from pydantic_core import core_schema

# Comentário: A classe PyObjectId foi recriada para ser compatível com Pydantic v2.
# O método __get_pydantic_core_schema__ foi implementado para instruir o Pydantic sobre como validar e serializar o tipo ObjectId.
# A função validate_object_id é usada como validador, e a função to_str é usada como serializador.
class PyObjectId(ObjectId):
    @classmethod
    def __get_pydantic_core_schema__(
        cls,
        source_type: Any,
        handler: Any,
    ) -> core_schema.CoreSchema:
        def validate_object_id(v: Any) -> ObjectId:
            if isinstance(v, ObjectId):
                return v
            if isinstance(v, str) and ObjectId.is_valid(v):
                return ObjectId(v)
            raise ValueError("Invalid ObjectId")

        return core_schema.json_or_python_schema(
            json_schema=core_schema.str_schema(),
            python_schema=core_schema.union_schema([
                core_schema.is_instance_schema(ObjectId),
                core_schema.chain_schema([
                    core_schema.str_schema(),
                    core_schema.no_info_plain_validator_function(validate_object_id)
                ])
            ]),
            serialization=core_schema.plain_serializer_function_ser_schema(lambda x: str(x)),
        )

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

    model_config = ConfigDict(populate_by_name=True, arbitrary_types_allowed=True)

class User(UserBase):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(populate_by_name=True, arbitrary_types_allowed=True)

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

    model_config = ConfigDict(populate_by_name=True, arbitrary_types_allowed=True)

class Profile(ProfileBase):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    user_id: PyObjectId
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(populate_by_name=True, arbitrary_types_allowed=True)

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

    model_config = ConfigDict(populate_by_name=True, arbitrary_types_allowed=True)

class Metrics(MetricsBase):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    post_metrics: List[Dict[str, Any]] = []
    created_at: datetime

    model_config = ConfigDict(populate_by_name=True, arbitrary_types_allowed=True)

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

    model_config = ConfigDict(populate_by_name=True, arbitrary_types_allowed=True)

class Report(ReportBase):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    file_path: Optional[str] = None
    is_ready: bool = False
    created_at: datetime

    model_config = ConfigDict(populate_by_name=True, arbitrary_types_allowed=True)

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

    model_config = ConfigDict(populate_by_name=True, arbitrary_types_allowed=True)

class PostFeedback(PostFeedbackBase):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    created_at: datetime

    model_config = ConfigDict(populate_by_name=True, arbitrary_types_allowed=True)

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


