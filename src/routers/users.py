from fastapi import APIRouter, Depends, HTTPException
from database import db_session
from models import User
from schemas import UserCreate, UserResponse
from sqlalchemy.orm import Session

router = APIRouter()

@router.post("/", response_model=UserResponse)
def create_user(user: UserCreate, session: Session = Depends(db_session)):

  new_user = User(name=user.name)
  session.add(new_user)
  session.commit()
  session.refresh(new_user)
  return new_user


@router.get("/", response_model=list[UserResponse])
def get_users(session: Session = Depends(db_session)):
    users_query = session.query(User)

    return users_query.all()

@router.get("/{user_id}", response_model=UserResponse)
def get_user(user_id: int, session: Session = Depends(db_session)):
    users_query = session.query(User)
    user = users_query.filter(User.id == user_id).first()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user
