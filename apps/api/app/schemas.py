"""Pydantic schemas for API request/response models."""
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime
from uuid import UUID


# Production schemas
class ProductionResponse(BaseModel):
    code: str
    title: str

    class Config:
        from_attributes = True


class ProductionsResponse(BaseModel):
    productions: List[ProductionResponse]


# Shot schemas
class ShotSummary(BaseModel):
    shot_code: str
    scene: Optional[str]
    description: Optional[str]
    stage: str

    class Config:
        from_attributes = True


class ShotDetail(BaseModel):
    shot_code: str
    scene: Optional[str]
    description: Optional[str]

    class Config:
        from_attributes = True


class ShotsResponse(BaseModel):
    shots: List[ShotSummary]


class ShotDetailResponse(BaseModel):
    shot: ShotDetail


# Version schemas
class VersionResponse(BaseModel):
    id: UUID
    version_type: str
    storage_uri: str
    codec: Optional[str]
    container: Optional[str]
    fps: Optional[float]
    timecode_in: Optional[str]
    timecode_out: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


class LineageNode(BaseModel):
    version_id: UUID
    version_type: str
    derived_from: Optional[UUID]

    class Config:
        from_attributes = True


class LineageResponse(BaseModel):
    shot_code: str
    chain: List[LineageNode]


# Event schemas
class EventResponse(BaseModel):
    id: UUID
    event_type: str
    version_id: Optional[UUID]
    package_id: Optional[UUID]
    actor: Optional[str]
    tool: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


class EventsResponse(BaseModel):
    events: List[EventResponse]


# Package schemas
class PackageResponse(BaseModel):
    id: UUID
    package_type: str
    label: str
    vendor: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


class PackagesResponse(BaseModel):
    packages: List[PackageResponse]


class PackageMemberResponse(BaseModel):
    version_id: UUID
    version_type: str
    storage_uri: str

    class Config:
        from_attributes = True


class PackageDetailResponse(BaseModel):
    package: PackageResponse
    members: List[PackageMemberResponse]


# Ask schemas
class AskRequest(BaseModel):
    production_code: str
    question: str


class AskResponse(BaseModel):
    template: str
    params: Dict[str, Any]
    answer: str
    evidence: Dict[str, List[Any]]
    explanation: str


# Import/Seed schemas
class SeedRequest(BaseModel):
    mode: Optional[str] = None


class SeedResponse(BaseModel):
    ok: bool
    production_code: str
    shots_loaded: int


# Error schemas
class ErrorDetail(BaseModel):
    code: str
    message: str
    details: Optional[Dict[str, Any]] = None


class ErrorResponse(BaseModel):
    error: ErrorDetail


# Advance operation schemas
class AdvanceRequest(BaseModel):
    operation: str  # publish_dailies, create_edit_export, deliver_turnover, archive


class AdvanceResponse(BaseModel):
    ok: bool
    version_id: Optional[UUID] = None
    event_id: UUID
    message: str
