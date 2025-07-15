from fastapi import FastAPI, HTTPException, Depends, Request
from fastapi.responses import FileResponse, JSONResponse
from sqlalchemy.orm import Session
from sqlalchemy import event
from sqlalchemy.engine import Engine
import sqlite3
from models import Usuario as UsuarioDB, Habito as HabitoDB, Registro as RegistroDB
from database import SessionLocal, init_db
from schemas import UsuarioCriar, Usuario, HabitoCriar, Habito, RegistroCriar, Registro, LoginInput
from typing import List
from datetime import date, timedelta
import random
import hashlib
import json
import os

app = FastAPI(title="Plano de Autocuidado")

init_db()  # inicializa o banco na primeira execução

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

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

# ==== Usuário ====

@app.get("/usuarios/", response_model=List[Usuario])
def listar_usuarios(db: Session = Depends(get_db)):
    return db.query(UsuarioDB).all()

@app.post("/usuarios/")
def criar_usuario(usuario: UsuarioCriar, db: Session = Depends(get_db)):
    existente = db.query(UsuarioDB).filter(UsuarioDB.email == usuario.email).first()
    if existente:
        raise HTTPException(status_code=400, detail="E-mail já cadastrado.")

    hashed = hash_password(usuario.senha)
    novo = UsuarioDB(name=usuario.name, email=usuario.email, senha=hashed)
    db.add(novo)
    db.commit()
    db.refresh(novo)

    return {
        "mensagem": "Usuário criado com sucesso!",
        "usuario": {
            "id": novo.id,
            "name": novo.name,
            "email": novo.email
        }
    }

@app.put("/usuarios/{usuario_id}", response_model=Usuario)
def atualizar_usuario(usuario_id: int, dados: UsuarioCriar, db: Session = Depends(get_db)):
    usuario = db.query(UsuarioDB).filter(UsuarioDB.id == usuario_id).first()
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuário não encontrado.")
    usuario.name = dados.name
    usuario.email = dados.email
    usuario.senha = hash_password(dados.senha)
    db.commit()
    return usuario

@app.delete("/usuarios/{usuario_id}")
def excluir_usuario(usuario_id: int, db: Session = Depends(get_db)):
    usuario = db.query(UsuarioDB).filter(UsuarioDB.id == usuario_id).first()
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")

    try:
        habito_ids = [h.id for h in db.query(HabitoDB).filter(HabitoDB.user_id == usuario_id).all()]
        if habito_ids:
            db.query(RegistroDB).filter(RegistroDB.habit_id.in_(habito_ids)).delete(synchronize_session=False)
        db.query(HabitoDB).filter(HabitoDB.user_id == usuario_id).delete(synchronize_session=False)
        db.query(RegistroDB).filter(RegistroDB.user_id == usuario_id).delete(synchronize_session=False)
        db.delete(usuario)
        db.commit()
        return {"mensagem": f"Usuário {usuario_id} deletado com sucesso."}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Erro ao deletar usuário: {str(e)}")

# ==== Login ====

@app.post("/login")
def login(dados: LoginInput, db: Session = Depends(get_db)):
    usuario = db.query(UsuarioDB).filter(UsuarioDB.email == dados.email).first()
    if not usuario or usuario.senha != hash_password(dados.senha):
        raise HTTPException(status_code=401, detail="E-mail ou senha incorretos.")
    return {"mensagem": "Login bem-sucedido!", "usuario_id": usuario.id}


# ==== Hábitos ====

@app.get("/habitos/", response_model=List[Habito])
def listar_habitos(db: Session = Depends(get_db)):
    return db.query(HabitoDB).all()

@app.post("/habitos/", response_model=Habito)
def criar_habito(habito: HabitoCriar, db: Session = Depends(get_db)):
    novo = HabitoDB(**habito.dict())
    db.add(novo)
    db.commit()
    db.refresh(novo)
    return novo

@app.put("/habitos/{habito_id}", response_model=Habito)
def atualizar_habito(habito_id: int, dados: HabitoCriar, db: Session = Depends(get_db)):
    habito = db.query(HabitoDB).filter(HabitoDB.id == habito_id).first()
    if not habito:
        raise HTTPException(status_code=404, detail="Hábito não encontrado.")
    habito.title = dados.title
    habito.description = dados.description
    habito.user_id = dados.user_id
    db.commit()
    return habito

@app.delete("/habitos/{habito_id}")
def excluir_habito(habito_id: int, db: Session = Depends(get_db)):
    habito = db.query(HabitoDB).filter(HabitoDB.id == habito_id).first()
    if not habito:
        raise HTTPException(status_code=404, detail="Hábito não encontrado")

    try:
        db.query(RegistroDB).filter(RegistroDB.habit_id == habito_id).delete(synchronize_session=False)
        db.delete(habito)
        db.commit()
        return {"mensagem": f"Hábito {habito_id} deletado com sucesso."}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Erro ao deletar hábito: {str(e)}")

# ==== Registros ====

@app.post("/registros/", response_model=Registro)
def criar_registro(registro: RegistroCriar, db: Session = Depends(get_db)):
    data_registro = registro.date or date.today()
    novo = RegistroDB(user_id=registro.user_id, habit_id=registro.habit_id, date=data_registro)
    db.add(novo)
    db.commit()
    db.refresh(novo)
    return novo

@app.get("/registros/", response_model=List[Registro])
def listar_registros(db: Session = Depends(get_db)):
    return db.query(RegistroDB).all()

# ==== Motivação ====

@app.get("/motivacao/")
def motivacao():
    mensagens = [
        "Você está indo muito bem! Continue assim!",
        "Cada hábito realizado é uma flor no seu jardim interior!",
        "A constância é mais importante que a perfeição."
    ]
    return {"mensagem": random.choice(mensagens)}

# ==== Resumo Semanal ====

@app.get("/usuarios/{usuario_id}/resumo-semanal")
def resumo(usuario_id: int, db: Session = Depends(get_db)):
    usuario = db.query(UsuarioDB).filter(UsuarioDB.id == usuario_id).first()
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    hoje = date.today()
    semana_passada = hoje - timedelta(days=7)
    registros = db.query(RegistroDB).filter(RegistroDB.user_id == usuario_id, RegistroDB.date >= semana_passada).all()
    return {
        "usuario_id": usuario_id,
        "habitos_realizados_na_ultima_semana": len(registros),
        "mensagem": "Continue assim! Cada dia importa."
    }

# ==== Ranking Semanal ====

@app.get("/ranking")
def ranking(db: Session = Depends(get_db)):
    hoje = date.today()
    semana_passada = hoje - timedelta(days=7)
    registros = db.query(RegistroDB).filter(RegistroDB.date >= semana_passada).all()
    contagem = {}
    for reg in registros:
        contagem[reg.user_id] = contagem.get(reg.user_id, 0) + 1
    resultado = sorted([
        {"usuario_id": uid, "total": total} for uid, total in contagem.items()
    ], key=lambda x: x["total"], reverse=True)
    return {"ranking_semanal": resultado}
