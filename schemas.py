from pydantic import BaseModel
from typing import Optional
from datetime import date

# --------------------------
# USUÁRIO
# --------------------------
class UsuarioBase(BaseModel):
    name: str
    email: str

class UsuarioCriar(UsuarioBase):
    senha: str

class Usuario(UsuarioBase):
    id: int

    class Config:
        orm_mode = True

# --------------------------
# HÁBITOS
# --------------------------
class HabitoBase(BaseModel):
    title: str
    description: Optional[str]
    user_id: int

class HabitoCriar(HabitoBase):
    pass

class Habito(HabitoBase):
    id: int

    class Config:
        orm_mode = True

# --------------------------
# REGISTROS
# --------------------------
class RegistroBase(BaseModel):  # Corrigido nome
    user_id: int
    habit_id: int

class RegistroCriar(RegistroBase):
    date: Optional[date] = None

class Registro(RegistroBase):
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
