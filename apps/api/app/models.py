"""SQLAlchemy models for the database."""
from sqlalchemy import Column, String, Text, Integer, Numeric, ForeignKey, DateTime, JSON
from sqlalchemy.dialects.postgresql import UUID, JSONB, TIMESTAMP
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid
from app.database import Base
from app import omc_fields


class Production(Base):
    __tablename__ = "productions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    code = Column(String(50), unique=True, nullable=False)
    title = Column(String(255), nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    updated_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now())


class Shot(Base):
    __tablename__ = "shots"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    production_id = Column(UUID(as_uuid=True), ForeignKey("productions.id"), nullable=False)
    shot_code = Column(String(50), nullable=False)
    scene = Column(String(50))
    description = Column(Text)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    updated_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now())

    production = relationship("Production", backref="shots")


class Asset(Base):
    __tablename__ = "assets"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    shot_id = Column(UUID(as_uuid=True), ForeignKey("shots.id"), nullable=False)
    production_id = Column(UUID(as_uuid=True), ForeignKey("productions.id"), nullable=False)
    asset_type = Column(String(50), nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    updated_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now())

    shot = relationship("Shot", backref="assets")
    production = relationship("Production", backref="assets")


class Version(Base):
    __tablename__ = "versions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    asset_id = Column(UUID(as_uuid=True), ForeignKey("assets.id"), nullable=False)
    version_type = Column(String(50), nullable=False)
    derived_from_version_id = Column(UUID(as_uuid=True), ForeignKey("versions.id"))
    storage_uri = Column(Text, nullable=False)
    omc_json = Column(JSONB)
    creative_context = Column(JSONB)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    updated_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now())

    asset = relationship("Asset", backref="versions")
    derived_from = relationship("Version", remote_side=[id], backref="derived_versions")

    # Media attributes live only in omc_json (Phase B); these read-only views keep the API shape unchanged.
    codec = property(lambda self: omc_fields.codec(self.omc_json))
    container = property(lambda self: omc_fields.container(self.omc_json))
    fps = property(lambda self: omc_fields.fps(self.omc_json))
    timecode_in = property(lambda self: omc_fields.timecode_in(self.omc_json))
    timecode_out = property(lambda self: omc_fields.timecode_out(self.omc_json))


class VersionLineage(Base):
    __tablename__ = "version_lineage"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    derived_version_id = Column(UUID(as_uuid=True), ForeignKey("versions.id"), nullable=False)
    source_version_id = Column(UUID(as_uuid=True), ForeignKey("versions.id"), nullable=False)
    transform_type = Column(String(50))
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())


class Package(Base):
    __tablename__ = "packages"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    production_id = Column(UUID(as_uuid=True), ForeignKey("productions.id"), nullable=False)
    package_type = Column(String(50), nullable=False)
    label = Column(String(255), nullable=False)
    vendor = Column(String(255))
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    updated_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now())

    production = relationship("Production", backref="packages")


class PackageMember(Base):
    __tablename__ = "package_members"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    package_id = Column(UUID(as_uuid=True), ForeignKey("packages.id"), nullable=False)
    version_id = Column(UUID(as_uuid=True), ForeignKey("versions.id"), nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())

    package = relationship("Package", backref="members")
    version = relationship("Version", backref="package_memberships")


class Event(Base):
    __tablename__ = "events"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    shot_id = Column(UUID(as_uuid=True), ForeignKey("shots.id"), nullable=False)
    event_type = Column(String(50), nullable=False)
    version_id = Column(UUID(as_uuid=True), ForeignKey("versions.id"))
    package_id = Column(UUID(as_uuid=True), ForeignKey("packages.id"))
    actor = Column(String(255))
    tool = Column(String(255))
    details = Column(JSONB)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())

    shot = relationship("Shot", backref="events")
    version = relationship("Version", backref="events")
    package = relationship("Package", backref="events")

