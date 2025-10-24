"""
High School Management System API

A FastAPI application that allows students to view and sign up
for extracurricular activities at Mergington High School.
Data is now persisted in SQLite database.
"""

from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session, sessionmaker
import os
from pathlib import Path
from models import engine, Activity, Participant
from typing import Dict, Any

app = FastAPI(title="Mergington High School API",
             description="API for viewing and signing up for extracurricular activities")

# Configure database session
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Mount the static files directory
current_dir = Path(__file__).parent
app.mount("/static", StaticFiles(directory=os.path.join(current_dir, "static")), name="static")

def get_db():
    """Get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_sample_data():
    """Initialize sample data in the database"""
    db = next(get_db())
    
    # Check if we already have data
    if db.query(Activity).first() is not None:
        return
    
    # Sample activities data
    sample_activities = {
        "Chess Club": {
            "description": "Learn strategies and compete in chess tournaments",
            "schedule": "Fridays, 3:30 PM - 5:00 PM",
            "max_participants": 12,
            "participants": ["michael@mergington.edu", "daniel@mergington.edu"]
        },
        "Programming Class": {
            "description": "Learn programming fundamentals and build software projects",
            "schedule": "Tuesdays and Thursdays, 3:30 PM - 4:30 PM",
            "max_participants": 20,
            "participants": ["emma@mergington.edu", "sophia@mergington.edu"]
        },
        "Gym Class": {
            "description": "Physical education and sports activities",
            "schedule": "Mondays, Wednesdays, Fridays, 2:00 PM - 3:00 PM",
            "max_participants": 30,
            "participants": ["john@mergington.edu", "olivia@mergington.edu"]
        }
    }
    
    # Insert data
    for name, details in sample_activities.items():
        # Create activity
        activity = Activity(
            name=name,
            description=details["description"],
            schedule=details["schedule"],
            max_participants=details["max_participants"]
        )
        db.add(activity)
        
        # Create participants and link them to activity
        for email in details["participants"]:
            participant = db.query(Participant).filter_by(email=email).first()
            if participant is None:
                participant = Participant(email=email)
                db.add(participant)
            activity.participants.append(participant)
    
    db.commit()

# Initialize sample data
init_sample_data()

@app.get("/")
def root():
    """Redirect to static index page"""
    return RedirectResponse(url="/static/index.html")


@app.get("/activities")
def get_activities():
    """Get all activities with their details"""
    db = next(get_db())
    activities_dict = {}
    
    activities = db.query(Activity).all()
    for activity in activities:
        activities_dict[activity.name] = {
            "description": activity.description,
            "schedule": activity.schedule,
            "max_participants": activity.max_participants,
            "participants": [p.email for p in activity.participants]
        }
    
    return activities_dict

@app.post("/activities/{activity_name}/signup")
def signup_for_activity(activity_name: str, email: str):
    """Sign up a student for an activity"""
    db = next(get_db())
    
    # Get activity
    activity = db.query(Activity).filter(Activity.name == activity_name).first()
    if not activity:
        raise HTTPException(status_code=404, detail="Activity not found")
    
    # Check if student is already signed up
    participant = db.query(Participant).filter(Participant.email == email).first()
    if participant and activity in participant.activities:
        raise HTTPException(
            status_code=400,
            detail="Student is already signed up"
        )
    
    # Create participant if doesn't exist
    if participant is None:
        participant = Participant(email=email)
        db.add(participant)
    
    # Add student to activity
    activity.participants.append(participant)
    db.commit()
    
    return {"message": f"Signed up {email} for {activity_name}"}

@app.delete("/activities/{activity_name}/unregister")
def unregister_from_activity(activity_name: str, email: str):
    """Unregister a student from an activity"""
    db = next(get_db())
    
    # Get activity and participant
    activity = db.query(Activity).filter(Activity.name == activity_name).first()
    if not activity:
        raise HTTPException(status_code=404, detail="Activity not found")
    
    participant = db.query(Participant).filter(Participant.email == email).first()
    if not participant or activity not in participant.activities:
        raise HTTPException(
            status_code=400,
            detail="Student is not signed up for this activity"
        )
    
    # Remove student from activity
    activity.participants.remove(participant)
    db.commit()
    
    return {"message": f"Unregistered {email} from {activity_name}"}
