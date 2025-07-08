from pydantic import BaseModel
from typing import Optional
from datetime import date

# --------------------------
# USUÁRIO
# --------------------------
class UserBase(BaseModel):
    name: str
    email: str

class UserCreate(UserBase):
    senha: str

class User(UserBase):
    id: int

    class Config:
        orm_mode = True

# --------------------------
# HÁBITOS
# --------------------------
class HabitBase(BaseModel):
    title: str
    description: str
    user_id: int

class HabitCreate(HabitBase):
    pass

class Habit(HabitBase):
    id: int
    favorito: Optional[bool] = False

    class Config:
        orm_mode = True

# --------------------------
# LOGS
# --------------------------
class LogBase(BaseModel):
    user_id: int
    habit_id: int

class LogCreate(LogBase):
    date: Optional[date] = None  # aceita None ou uma data válida

class Log(LogBase):
    id: int
    date: date

    class Config:
        orm_mode = True

# --------------------------
# LOGIN
# --------------------------
class LoginInput(BaseModel):
    email: str
    senha: str
