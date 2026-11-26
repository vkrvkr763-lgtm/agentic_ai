from datetime import datetime

from sqlalchemy import (
    String, Text, Boolean, Integer, Float,
    ForeignKey, DateTime, func
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.database.base import Base


class IssueCategory(Base):
    __tablename__ = "issue_categories"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), unique=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    routes = relationship("CategoryRouting", back_populates="category")


class Department(Base):
    __tablename__ = "departments"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(150), unique=True)
    email: Mapped[str] = mapped_column(String(255))
    jurisdiction: Mapped[str] = mapped_column(String(150))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    routes = relationship("CategoryRouting", back_populates="department")


class CategoryRouting(Base):
    __tablename__ = "category_routing"

    id: Mapped[int] = mapped_column(primary_key=True)

    category_id: Mapped[int] = mapped_column(
        ForeignKey("issue_categories.id")
    )
    department_id: Mapped[int] = mapped_column(
        ForeignKey("departments.id")
    )

    priority: Mapped[int] = mapped_column(Integer, default=1)

    category = relationship("IssueCategory", back_populates="routes")
    department = relationship("Department", back_populates="routes")


class Complaint(Base):
    __tablename__ = "complaints"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)

    category_id: Mapped[int | None] = mapped_column(
        ForeignKey("issue_categories.id"), nullable=True
    )
    department_id: Mapped[int | None] = mapped_column(
        ForeignKey("departments.id"), nullable=True
    )

    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    image_path: Mapped[str | None] = mapped_column(String(500), nullable=True)

    severity: Mapped[str | None] = mapped_column(String(30), nullable=True)

    latitude: Mapped[float | None] = mapped_column(Float, nullable=True)
    longitude: Mapped[float | None] = mapped_column(Float, nullable=True)
    address: Mapped[str | None] = mapped_column(Text, nullable=True)

    status: Mapped[str] = mapped_column(String(50), default="submitted")
    email_status: Mapped[str] = mapped_column(String(50), default="pending")

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    ai_status: Mapped[str] = mapped_column(
        String(30),
        default="pending"
    )

    ai_error: Mapped[str | None] = mapped_column(
        Text,
        nullable=True
    )

    ai_analyzed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True
    )