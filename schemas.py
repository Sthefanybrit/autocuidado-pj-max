from pydantic import BaseModel
from typing import Optional

# Usuário
class UserCreate(BaseModel):
    name: str
    email: str
    senha: str

class User(UserCreate):
    id: int

# Hábito
class HabitCreate(BaseModel):
    title: str
    description: str
    user_id: int

class Habit(HabitCreate):
    id: int
    favorito: bool 

# Log de hábito diário
class LogCreate(BaseModel):
    user_id: int
    habit_id: int
    date: Optional[str] = None

class Log(LogCreate):
    id: int

# Login
class LoginInput(BaseModel):
    email: str
    senha: str
