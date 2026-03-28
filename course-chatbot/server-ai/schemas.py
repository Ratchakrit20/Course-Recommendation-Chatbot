from typing import List, Optional
from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    department: str
    query: str
    provider: Optional[str] = "ollama"   # ollama | hf
    top_k: Optional[int] = 3


class CourseHit(BaseModel):
    course_code: str
    course_name_en: str
    course_name_th: Optional[str] = None
    category: Optional[str] = None
    reason: str
    match_level: Optional[str] = None
    keywords: List[str] = Field(default_factory=list)
    skills: List[str] = Field(default_factory=list)


class RecommendedCourse(BaseModel):
    rank: int
    course_code: str
    course_name: str
    match_level: str
    reason: str
    skills: List[str] = Field(default_factory=list)
    recommended_before_after: str = ""


class ChatMeta(BaseModel):
    provider: Optional[str] = None
    department: Optional[str] = None
    top_k: Optional[int] = None
    model: Optional[str] = None


class ChatResponse(BaseModel):
    summary: str
    target_career: str
    recommended_courses: List[RecommendedCourse] = Field(default_factory=list)
    learning_order: List[str] = Field(default_factory=list)
    career_paths: List[str] = Field(default_factory=list)
    note: str = ""

    recommendations: List[CourseHit] = Field(default_factory=list)
    meta: Optional[ChatMeta] = None

    # เก็บข้อความดิบจาก LLM เผื่อ debug หรือ fallback
    answer_raw: Optional[str] = None