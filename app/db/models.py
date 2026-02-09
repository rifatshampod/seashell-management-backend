from sqlalchemy import Column, String, Boolean, DateTime, Text, Integer, Date, ForeignKey, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid
from datetime import datetime
from app.db.base import Base


class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relationship: User can add many seashells
    seashells = relationship("Seashell", back_populates="added_by", lazy="dynamic")

    def __repr__(self):
        return f"<User(id={self.id}, email={self.email})>"


class Seashell(Base):
    __tablename__ = "seashells"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(120), nullable=False)
    species = Column(String(120), nullable=False)
    description = Column(Text, nullable=True)
    color = Column(String(60), nullable=True)
    size_mm = Column(Integer, nullable=True)
    found_on = Column(Date, nullable=True)
    found_at = Column(String(200), nullable=True)
    storage_location = Column(String(150), nullable=True)
    condition = Column(String(50), nullable=True)
    notes = Column(Text, nullable=True)
    image_url = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Foreign key: Reference to the user who added this seashell
    added_by_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    added_by = relationship("User", back_populates="seashells")

    def __repr__(self):
        return f"<Seashell(id={self.id}, name={self.name}, species={self.species})>"
