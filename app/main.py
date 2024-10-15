from typing import List
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from .models import Roles, User, Room, Presentation, Schedule
from . import schemas
from .database import engine, get_db, Base
from datetime import datetime, timedelta

Base.metadata.create_all(bind=engine)

app = FastAPI()


@app.on_event("startup")
def startup_event():
    """Событие при старте приложения"""
    db = next(get_db())
    create_initial_data(db)


@app.get("/")
def index():
    """Доступность сервера"""
    return {"ping": "pong!"}


@app.post("/register/", response_model=schemas.Schedule)
def register_user(username: str, schedule_id: int, db: Session = Depends(get_db)):
    """Регистрация пользователя в качестве слушателя"""
    db_user = db.query(User).filter(User.username == username).first()
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    if db_user.role != Roles.Listener:
        raise HTTPException(status_code=400, detail="Only listener can register")
    db_schedule = db.query(Schedule).get(schedule_id)
    if db_schedule is None:
        raise HTTPException(status_code=404, detail="Schedule not found")
    if len(db_schedule.listeners) == 0:
        db_schedule.listeners = [db_user]
    else:
        db_schedule.listeners.append(db_user)
    db.add(db_schedule)
    db.commit()
    db.refresh(db_schedule)
    return db_schedule


@app.get("/schedules/")
def get_schedule_by_room(db: Session = Depends(get_db)):
    """Получение расписания презентаций, разбитое по аудиториям"""
    schedules = db.query(Schedule).join(Schedule.room).join(Schedule.presentation).all()
    schedules_by_room = {}
    for schedule in schedules:
        tmp = schedule.listeners
        if schedules_by_room.get(schedule.room_id) is None:
            schedules_by_room[schedule.room_id] = {
                "room": schedule.room.name,
                "schedule": [schedule]
            }
        else:
            schedules_by_room[schedule.room_id]["schedule"].append(schedule)

    return schedules_by_room


@app.post("/presentations/create", response_model=schemas.Presentation)
def create_presentation(presentation: schemas.PresentationCreate,
                        db: Session = Depends(get_db)):
    """Создание новой презентации"""
    usernames = presentation.presenters.split()
    presenters = db.query(User).filter(
        User.username.in_(usernames),
        User.role == Roles.Presenter
    ).all()

    if len(presenters) != len(usernames):
        raise HTTPException(status_code=400, detail="Presenters not found or not have role 'Presenter'")
    new_presentation = Presentation(
        title=presentation.title,
        description=presentation.description,
        presenters=presenters
    )
    db.add(new_presentation)
    db.commit()
    db.refresh(new_presentation)
    return new_presentation


@app.get("/presentations/", response_model=List[schemas.Presentation])
def get_presentations(db: Session = Depends(get_db)):
    """Получение списка всех презентаций"""
    presentations = db.query(Presentation).all()
    return presentations


@app.post("/presentations/{presentation_id}/schedule", response_model=schemas.Schedule)
def schedule_presentation(presentation_id: int,
                          presenter_id: int,
                          schedule: schemas.ScheduleCreate,
                          db: Session = Depends(get_db)):
    """Добавление презентации в расписание"""
    presenter = db.query(User).join(Presentation.presenters).filter(
        User.id == presenter_id,
        Presentation.id == presentation_id
    ).first()
    if presenter is None:
        raise HTTPException(status_code=404, detail="Presenter or presentation not found")

    conflict_schedules = db.query(Schedule).filter(
        Schedule.room_id == schedule.room_id,
        Schedule.start_time < schedule.end_time,
        Schedule.end_time > schedule.start_time
    ).all()
    if conflict_schedules:
        raise HTTPException(status_code=400, detail="Time conflict")

    if db.query(Room).get(schedule.room_id) is None:
        raise HTTPException(status_code=404, detail="Room not found")

    new_schedule = Schedule(
        presentation_id=presentation_id,
        room_id=schedule.room_id,
        start_time=schedule.start_time,
        end_time=schedule.end_time
    )
    db.add(new_schedule)
    db.commit()
    db.refresh(new_schedule)
    return new_schedule


@app.get("/presentations/{presenter_id}/my_presentations", response_model=List[schemas.Presentation])
def get_presentations_by_user(presenter_id: int, db: Session = Depends(get_db)):
    """Получение всех презентаций для конкретного пользователя"""
    presenter = db.query(User).filter(User.id == presenter_id, User.role == Roles.Presenter).first()
    if not presenter:
        raise HTTPException(status_code=404, detail="Presenter not found")

    presentations = db.query(Presentation).join(Presentation.presenters).filter(User.id == presenter_id).all()
    return presentations


@app.put("/presentations/{presentation_id}/update", response_model=schemas.Presentation)
def update_presentation(presentation_id: int,
                        updated_data: schemas.PresentationUpdate,
                        db: Session = Depends(get_db)):
    """Обновление информации о презентации"""
    presentation = db.query(Presentation).filter(Presentation.id == presentation_id).first()
    if not presentation:
        raise HTTPException(status_code=404, detail="Presentation not found")

    if updated_data.title:
        presentation.title = updated_data.title
    if updated_data.description:
        presentation.description = updated_data.description
    if updated_data.presenters:
        usernames = updated_data.presenters.split()
        presenters = db.query(User).filter(
            User.username.in_(usernames),
            User.role == Roles.Presenter
        ).all()
        if len(presenters) != len(usernames):
            raise HTTPException(status_code=400, detail="Presenters not found or not have role 'Presenter'")
        presentation.presenters = presenters

    db.commit()
    db.refresh(presentation)
    return presentation


@app.delete("/presentations/{presentation_id}/delete", response_model=schemas.Presentation)
def delete_presentation(presentation_id: int, db: Session = Depends(get_db)):
    """Удаление презентации"""
    presentation = db.query(Presentation).filter(Presentation.id == presentation_id).first()
    if not presentation:
        raise HTTPException(status_code=404, detail="Presentation not found")

    db.delete(presentation)
    db.commit()
    return presentation


@app.post("/rooms/new")
def create_room(name: str, db: Session = Depends(get_db)):
    """Добавление новой аудитории"""
    db_room = db.query(Room).filter_by(name=name).first()
    if db_room:
        raise HTTPException(status_code=400, detail="Room already registered")
    new_room = Room(name=name)
    db.add(new_room)
    db.commit()
    db.refresh(new_room)
    return new_room

@app.post("/create_user/", response_model=schemas.User)
def create_user(user: schemas.UserCreate = Depends(schemas.UserCreate), db: Session = Depends(get_db)):
    """Регистрация нового пользователя с выбором роли"""
    db_user = db.query(User).filter(User.username == user.username).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    new_user = User(username=user.username, role=user.role)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user



def create_initial_data(db: Session = Depends(get_db)):
    """Создание данных при старте приложения"""

    if db.query(User).count() == 0:
        users = [
            User(username="user1", role=Roles.Presenter),
            User(username="user2", role=Roles.Listener),
            User(username="user3", role=Roles.Presenter),
            User(username="user4", role=Roles.Listener),
        ]
        db.add_all(users)
        db.commit()
        print("Пользователи добавлены")

    if db.query(Room).count() == 0:
        rooms = [
            Room(name="room1"),
            Room(name="room2"),
            Room(name="room3"),
            Room(name="room4"),
        ]
        db.add_all(rooms)
        db.commit()
        print("Аудитории добавлены")

    if db.query(Presentation).count() == 0:
        presenter1 = db.query(User).filter(User.username == "user1", User.role == Roles.Presenter).first()
        presenter2 = db.query(User).filter(User.username == "user3", User.role == Roles.Presenter).first()

        presentations = [
            Presentation(title="Доклад 1", description="Описание доклада 1", presenters=[presenter1]),
            Presentation(title="Доклад 2", description="Описание доклада 2", presenters=[presenter2]),
            Presentation(title="Доклад 3", description="Описание доклада 3", presenters=[presenter1, presenter2]),
        ]
        db.add_all(presentations)
        db.commit()
        print("Презентации добавлены")

    if db.query(Schedule).count() == 0:
        room1 = db.query(Room).filter(Room.name == "room1").first()
        room2 = db.query(Room).filter(Room.name == "room2").first()

        presentation1 = db.query(Presentation).filter(Presentation.title == "Доклад 1").first()
        presentation2 = db.query(Presentation).filter(Presentation.title == "Доклад 2").first()

        schedules = [
            Schedule(
                presentation_id=presentation1.id,
                room_id=room1.id,
                start_time=datetime.now() + timedelta(hours=1),
                end_time=datetime.now() + timedelta(hours=2)
            ),
            Schedule(
                presentation_id=presentation2.id,
                room_id=room2.id,
                start_time=datetime.now() + timedelta(hours=3),
                end_time=datetime.now() + timedelta(hours=4)
            ),
        ]
        db.add_all(schedules)
        db.commit()
        print("Расписание добавлено")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
