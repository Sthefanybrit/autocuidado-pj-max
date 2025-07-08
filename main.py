from fastapi import FastAPI, HTTPException, Depends, Request
from fastapi.responses import FileResponse, JSONResponse
from sqlalchemy.orm import Session
from sqlalchemy import event
from sqlalchemy.engine import Engine
import sqlite3
from models import User as DBUser, Habit as DBHabit, Log as DBLog
from database import SessionLocal
from schemas import UserCreate, User, HabitCreate, Habit, LogCreate, Log, LoginInput
from typing import List
from datetime import date, timedelta
import random
import hashlib
import json
import os

app = FastAPI(title="Plano de Autocuidado")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Hash de senha
def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

# Middleware para capturar erro 422 (validação)
@app.exception_handler(422)
async def validation_exception_handler(request: Request, exc):
    return JSONResponse(
        status_code=422,
        content={"mensagem": "Erro de validação de dados. Verifique os campos enviados."}
    )
@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    if isinstance(dbapi_connection, sqlite3.Connection):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON;")
        cursor.close()
# Usuário
@app.get("/users/", response_model=List[User])
def get_users(db: Session = Depends(get_db)):
    return db.query(DBUser).all()

@app.post("/users/")
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    try:
        existing = db.query(DBUser).filter(DBUser.email == user.email).first()
        if existing:
            raise HTTPException(status_code=400, detail="E-mail já cadastrado.")

        hashed = hash_password(user.senha)
        new_user = DBUser(name=user.name, email=user.email, senha=hashed)
        db.add(new_user)
        db.commit()
        db.refresh(new_user)

        return {
            "mensagem": "Usuário criado com sucesso!",
            "user": {
                "id": new_user.id,
                "name": new_user.name,
                "email": new_user.email
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro interno ao criar usuário: {str(e)}")

@app.put("/users/{user_id}", response_model=User)
def update_user(user_id: int, user_update: UserCreate, db: Session = Depends(get_db)):
    user = db.query(DBUser).filter(DBUser.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuário não encontrado.")
    user.name = user_update.name
    user.email = user_update.email
    user.senha = hash_password(user_update.senha)
    db.commit()
    return user

@app.delete("/users/{user_id}")
def delete_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(DBUser).filter(DBUser.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")

    try:
        # Buscar IDs dos hábitos do usuário
        habit_ids = [habit.id for habit in db.query(DBHabit).filter(DBHabit.user_id == user_id).all()]

        # Deleta os logs associados a esses hábitos
        if habit_ids:
            db.query(DBLog).filter(DBLog.habit_id.in_(habit_ids)).delete(synchronize_session=False)

        # Deleta os hábitos do usuário
        db.query(DBHabit).filter(DBHabit.user_id == user_id).delete(synchronize_session=False)

        # Deleta os logs diretamente associados ao usuário (caso existam)
        db.query(DBLog).filter(DBLog.user_id == user_id).delete(synchronize_session=False)

        # Deleta o usuário
        db.delete(user)

        db.commit()
        return {"message": f"Usuário {user_id} deletado com sucesso."}
    except Exception as e:
        db.rollback()
        print(f"Erro ao deletar usuário: {e}")
        raise HTTPException(status_code=500, detail=f"Erro ao deletar usuário: {str(e)}")


# Login
@app.post("/login")
def login(login_data: LoginInput, db: Session = Depends(get_db)):
    user = db.query(DBUser).filter(DBUser.email == login_data.email).first()
    if not user or user.senha != hash_password(login_data.senha):
        raise HTTPException(status_code=401, detail="E-mail ou senha incorretos.")
    return {"mensagem": "Login bem-sucedido!", "user_id": user.id}

# Exportar dados
@app.get("/exportar/{user_id}")
def exportar_dados(user_id: int, db: Session = Depends(get_db)):
    user = db.query(DBUser).filter(DBUser.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    habits = db.query(DBHabit).filter(DBHabit.user_id == user_id).all()
    logs = db.query(DBLog).filter(DBLog.user_id == user_id).all()

    dados = {
        "usuario": {"id": user.id, "name": user.name, "email": user.email},
        "habitos": [habit.__dict__ for habit in habits],
        "registros": [log.__dict__ for log in logs]
    }

    for item in dados["habitos"] + dados["registros"]:
        item.pop("_sa_instance_state", None)

    path = f"data/usuario_{user_id}_exportado.json"
    os.makedirs("data", exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(dados, f, indent=4, ensure_ascii=False)

    return FileResponse(path, media_type="application/json", filename=f"usuario_{user_id}.json")

# Hábitos
@app.get("/habits/", response_model=List[Habit])
def get_habits(db: Session = Depends(get_db)):
    return db.query(DBHabit).all()

@app.post("/habits/", response_model=Habit)
def create_habit(habit: HabitCreate, db: Session = Depends(get_db)):
    new_habit = DBHabit(**habit.dict())
    db.add(new_habit)
    db.commit()
    db.refresh(new_habit)
    return new_habit

@app.put("/habits/{habit_id}", response_model=Habit)
def update_habit(habit_id: int, habit_update: HabitCreate, db: Session = Depends(get_db)):
    habit = db.query(DBHabit).filter(DBHabit.id == habit_id).first()
    if not habit:
        raise HTTPException(status_code=404, detail="Hábito não encontrado.")
    habit.title = habit_update.title
    habit.description = habit_update.description
    habit.user_id = habit_update.user_id
    db.commit()
    return habit

@app.delete("/habits/{habit_id}")
def delete_habit(habit_id: int, db: Session = Depends(get_db)):
    habit = db.query(DBHabit).filter(DBHabit.id == habit_id).first()
    if not habit:
        raise HTTPException(status_code=404, detail="Hábito não encontrado")

    try:
        # Deleta os logs associados a esse hábito
        db.query(DBLog).filter(DBLog.habit_id == habit_id).delete(synchronize_session=False)

        # Deleta o hábito
        db.delete(habit)
        db.commit()

        return {"message": f"Hábito {habit_id} deletado com sucesso."}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Erro ao deletar hábito: {str(e)}")

@app.put("/habits/{habit_id}/favorito")
def toggle_favorito(habit_id: int, db: Session = Depends(get_db)):
    habit = db.query(DBHabit).filter(DBHabit.id == habit_id).first()
    if not habit:
        raise HTTPException(status_code=404, detail="Hábito não encontrado.")
    habit.favorito = not habit.favorito
    db.commit()
    return {"id": habit.id, "favorito": habit.favorito}

# Registro de Logs
@app.post("/logs/", response_model=Log)
def create_log(log: LogCreate, db: Session = Depends(get_db)):
    log_date = log.date or date.today()
    new_log = DBLog(user_id=log.user_id, habit_id=log.habit_id, date=log_date)
    db.add(new_log)
    db.commit()
    db.refresh(new_log)
    return new_log

@app.get("/logs/", response_model=List[Log])
def get_logs(db: Session = Depends(get_db)):
    return db.query(DBLog).all()

# Motivação
@app.get("/motivacao/")
def motivacao():
    mensagens = [
        "Você está indo muito bem! Continue assim!",
        "Cada hábito realizado é uma flor no seu jardim interior!",
        "A constância é mais importante que a perfeição."
    ]
    return {"mensagem": random.choice(mensagens)}

# Resumo semanal (com verificação de existência do usuário)
@app.get("/users/{user_id}/resumo-semanal")
def resumo_semanal(user_id: int, db: Session = Depends(get_db)):
    user = db.query(DBUser).filter(DBUser.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    hoje = date.today()
    semana_passada = hoje - timedelta(days=7)
    logs = db.query(DBLog).filter(DBLog.user_id == user_id, DBLog.date >= semana_passada).all()
    return {
        "user_id": user_id,
        "habitos_realizados_na_ultima_semana": len(logs),
        "mensagem": "Continue assim! Cada dia importa."
    }

# Ranking semanal
@app.get("/ranking")
def ranking_usuarios(db: Session = Depends(get_db)):
    hoje = date.today()
    semana_passada = hoje - timedelta(days=7)
    logs = db.query(DBLog).filter(DBLog.date >= semana_passada).all()
    contagem = {}
    for log in logs:
        contagem[log.user_id] = contagem.get(log.user_id, 0) + 1
    ranking = sorted([
        {"user_id": uid, "total": total} for uid, total in contagem.items()
    ], key=lambda x: x["total"], reverse=True)
    return {"ranking_semanal": ranking}


