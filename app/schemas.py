from pydantic import BaseModel
from typing import Optional, List
from .models import Roles
from datetime import datetime


class UserCreate(BaseModel):
    username: str
    role: Roles


class User(UserCreate):
    id: int


class Room(BaseModel):
    id: int
    name: str


class ScheduleCreate(BaseModel):
    presentation_id: int
    room_id: int
    start_time: datetime
    end_time: datetime


class Schedule(ScheduleCreate):
    id: int
    listeners: Optional[List[User]] = []


class ScheduleByRoom(BaseModel):
    room: Room
    schedule: Optional[List[Schedule]] = []


class PresentationCreate(BaseModel):
    title: str
    description: Optional[str] = None
    presenters: str


class Presentation(PresentationCreate):
    id: int
    presenters: List[User]


class PresentationUpdate(PresentationCreate):
    title: Optional[str] = None
    presenters: Optional[str] = None

