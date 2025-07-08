from sqlalchemy import Column, Integer, String, Boolean, Date, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    senha = Column(String, nullable=False)

    habits = relationship("Habit", back_populates="user", cascade="all, delete", passive_deletes=True)
    logs = relationship("Log", back_populates="user", cascade="all, delete", passive_deletes=True)

class Habit(Base):
    __tablename__ = "habits"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(String)
    favorito = Column(Boolean, default=False)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)

    user = relationship("User", back_populates="habits")
    logs = relationship("Log", back_populates="habit", cascade="all, delete", passive_deletes=True)

class Log(Base):
    __tablename__ = "logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    habit_id = Column(Integer, ForeignKey("habits.id", ondelete="CASCADE"), nullable=False)
    date = Column(Date)

    user = relationship("User", back_populates="logs")
    habit = relationship("Habit", back_populates="logs")