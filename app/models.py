from .database import Base
from sqlalchemy import Column, Integer, String, ForeignKey, Table, DateTime, Enum, Time
from sqlalchemy.orm import relationship
import enum

presenter_presentation = Table(
    'presenter_presentation',
    Base.metadata,
    Column('presenter_id', ForeignKey('users.id', ondelete="CASCADE"), primary_key=True),
    Column('presentation_id', ForeignKey('presentations.id', ondelete="CASCADE"), primary_key=True)
)

listener_schedule = Table(
    'listener_schedule',
    Base.metadata,
    Column('listener_id', ForeignKey('users.id', ondelete="CASCADE"), primary_key=True),
    Column('schedule_id', ForeignKey('schedules.id', ondelete="CASCADE"), primary_key=True)
)


class Roles(str, enum.Enum):
    Presenter = "Presenter"
    Listener = "Listener"


class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True)
    role = Column(Enum(Roles))

    presentations = relationship('Presentation', secondary=presenter_presentation, back_populates='presenters')
    schedules = relationship('Schedule', secondary=listener_schedule, back_populates='listeners')


class Room(Base):
    __tablename__ = 'rooms'

    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True)


class Presentation(Base):
    __tablename__ = 'presentations'

    id = Column(Integer, primary_key=True)
    title = Column(String)
    description = Column(String)

    presenters = relationship('User', secondary=presenter_presentation, back_populates='presentations')


class Schedule(Base):
    __tablename__ = 'schedules'

    id = Column(Integer, primary_key=True)
    presentation_id = Column(Integer, ForeignKey('presentations.id', ondelete="CASCADE"))
    room_id = Column(Integer, ForeignKey('rooms.id', ondelete="CASCADE"))
    start_time = Column(DateTime)
    end_time = Column(DateTime)

    listeners = relationship("User", secondary='listener_schedule', back_populates='schedules')
    presentation = relationship('Presentation')
    room = relationship('Room')
