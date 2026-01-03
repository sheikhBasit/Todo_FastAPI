from sqlalchemy import (
    Column, Integer, String, Boolean, ForeignKey, 
    DateTime, Text, UniqueConstraint, event
)
from sqlalchemy.orm import relationship, Query, Session
from sqlalchemy.sql import func, expression
from ..config.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, nullable=False, index=True)
    email = Column(String, unique=True, nullable=False, index=True)
    password_hash = Column(String, nullable=False)

    # Cascade ensures that deleting a user deletes their groups/tasks
    groups = relationship("Group", back_populates="owner", cascade="all, delete-orphan")
    tasks = relationship("Task", back_populates="owner", cascade="all, delete-orphan")


class Group(Base):
    __tablename__ = "groups"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    deleted_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # CONFLICT REMOVED: Name is only unique FOR THE OWNER.
    __table_args__ = (
        UniqueConstraint('name', 'user_id', name='_user_group_uc'),
    )

    owner = relationship("User", back_populates="groups")
    tasks = relationship("Task", back_populates="group")

    @staticmethod
    def not_deleted(session: Session):
        return session.query(Group).filter(Group.deleted_at.is_(None))


class Task(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False, index=True) 
    description = Column(Text, nullable=True)
    is_completed = Column(Boolean, default=False, server_default=expression.false(), index=True)

    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # STRATEGY CHANGE: nullable=False because every task must have a group (even 'Inbox')
    group_id = Column(Integer, ForeignKey("groups.id"), nullable=False)
    
    deleted_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Proper Indexing: Title is unique only within a specific group for that user
    __table_args__ = (
        UniqueConstraint('title', 'group_id', 'user_id', name='_user_task_group_uc'),
    )

    owner = relationship("User", back_populates="tasks")
    group = relationship("Group", back_populates="tasks")

    @staticmethod
    def not_deleted(session: Session):
        return session.query(Task).filter(Task.deleted_at.is_(None))


# --- AUTOMATION: Ensuring Every User has an 'Inbox' ---

@event.listens_for(User, 'after_insert')
def create_default_group(mapper, connection, target):
    connection.execute(
        Group.__table__.insert().values(
            name="Inbox",
            user_id=target.id
        )
    )