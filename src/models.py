"""
Database models for the High School Management System
"""

from sqlalchemy import create_engine, Column, String, Integer, Table
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.schema import ForeignKey
import os

# Create database engine
DATABASE_URL = "sqlite:///./activities.db"
engine = create_engine(DATABASE_URL)

# Create declarative base
Base = declarative_base()

# Association table for many-to-many relationship between activities and participants
activity_participants = Table('activity_participants', Base.metadata,
    Column('activity_id', Integer, ForeignKey('activities.id')),
    Column('email', String, ForeignKey('participants.email'))
)

class Activity(Base):
    """Activity model representing school activities"""
    __tablename__ = 'activities'

    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True, nullable=False)
    description = Column(String, nullable=False)
    schedule = Column(String, nullable=False)
    max_participants = Column(Integer, nullable=False)
    
    # Relationship with participants
    participants = relationship('Participant', 
                              secondary=activity_participants,
                              back_populates='activities')

class Participant(Base):
    """Participant model representing students"""
    __tablename__ = 'participants'

    email = Column(String, primary_key=True)
    
    # Relationship with activities
    activities = relationship('Activity', 
                            secondary=activity_participants,
                            back_populates='participants')

# Create all tables
Base.metadata.create_all(engine)