from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from database import read_users, write_users, read_habits, write_habits, read_logs, write_logs
from schemas import UserCreate, User, HabitCreate, Habit, LogCreate, Log, LoginInput
from datetime import date, datetime, timedelta
import random
import hashlib
import json
import os

app = FastAPI(title= "Plano de Autocuidado")


@app.get("/")
def root():
    return {"message": "Planner de Autocuidado"}

# Criptografia de senha
def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

#Usuário

@app.get("/users/", response_model=list[User])
def get_users():
    return read_users()

@app.post("/users/", response_model=User)
def create_user(user: UserCreate):
    users = read_users()
    for existing_user in users:
        if existing_user["email"] == user.email:
            raise HTTPException(status_code=400, detail="E-mail já cadastrado.")
    new_id = max([u["id"] for u in users], default=0) + 1
    new_user = {"id": new_id, **user.dict()}
    users.append(new_user)
    write_users(users)
    return new_user

@app.put("/users/{user_id}", response_model=User)
def update_user(user_id: int, user_update: UserCreate):
    users = read_users()
    for u in users:
        if u["id"] == user_id:
            u["name"] = user_update.name
            u["email"] = user_update.email
            u["senha"] = user_update.senha
            write_users(users)
            return u
    raise HTTPException(status_code=404, detail="Usuário não encontrado.")


@app.delete("/users/{user_id}")
def delete_user(user_id: int):
    users = read_users()
    updated_users = [u for u in users if u["id"] != user_id]
    if len(users) == len(updated_users):
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    write_users(updated_users)
    return {"message": f"Usuário {user_id} deletado com sucesso."}


#login

@app.post("/login")
def login(login_data: LoginInput):
    users = read_users()
    for user in users:
        if user["email"] == login_data.email and user["senha"] == login_data.senha:
            return {"mensagem": "Login bem-sucedido!", "user_id": user["id"]}
    raise HTTPException(status_code=401, detail="E-mail ou senha incorretos.")

# Exportar dados de um usuário
@app.get("/exportar/{user_id}")
def exportar_dados(user_id: int):
    users = read_users()
    habits = read_habits()
    logs = read_logs()

    user = next((u for u in users if u["id"] == user_id), None)
    if not user:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")

    dados = {
        "usuario": user,
        "habitos": [h for h in habits if h["user_id"] == user_id],
        "registros": [l for l in logs if l["user_id"] == user_id]
    }

    path = f"data/usuario_{user_id}_exportado.json"
    with open(path, "w") as f:
        json.dump(dados, f, indent=4)

    return FileResponse(path, media_type="application/json", filename=f"usuario_{user_id}.json")


#habitos

@app.get("/habits/", response_model=list[Habit])
def get_habits():
    return read_habits()

@app.post("/habits/", response_model=Habit)
def create_habit(habit: HabitCreate):
    habits = read_habits()
    new_id = max([h["id"] for h in habits], default=0) + 1
    new_habit = {"id": new_id, **habit.dict()}
    habits.append(new_habit)
    write_habits(habits)
    return new_habit

@app.put("/habits/{habit_id}", response_model=Habit)
def update_habit(habit_id: int, habit_update: HabitCreate):
    habits = read_habits()
    for h in habits:
        if h["id"] == habit_id:
            h["title"] = habit_update.title
            h["description"] = habit_update.description
            h["user_id"] = habit_update.user_id
            write_habits(habits)
            return h
    raise HTTPException(status_code=404, detail="Hábito não encontrado.")


@app.delete("/habits/{habit_id}")
def delete_habit(habit_id: int):
    habits = read_habits()
    updated_habits = [h for h in habits if h["id"] != habit_id]
    if len(habits) == len(updated_habits):
        raise HTTPException(status_code=404, detail="Hábito não encontrado")
    write_habits(updated_habits)
    return {"message": f"Hábito {habit_id} deletado com sucesso."}

# Marcar/desmarcar hábito como favorito
@app.put("/habits/{habit_id}/favorito")
def toggle_favorito(habit_id: int):
    habits = read_habits()
    for h in habits:
        if h["id"] == habit_id:
            h["favorito"] = not h.get("favorito", False)
            write_habits(habits)
            return {"id": h["id"], "favorito": h["favorito"]}
    raise HTTPException(status_code=404, detail="Hábito não encontrado.")

# Registro 

daily_messages = [
    "Você está indo muito bem! Continue assim!",
    "Cada hábito realizado é uma flor no seu jardim interior!",
    "A constância é mais importante que a perfeição."
]

@app.post("/logs/", response_model=Log)
def create_log(log: LogCreate):
    logs = read_logs()
    new_id = max([l["id"] for l in logs], default=0) + 1
    log_data = {"id": new_id, "date": log.date or str(date.today()), **log.dict()}
    logs.append(log_data)
    write_logs(logs)
    return log_data

@app.get("/logs/", response_model=list[Log])
def get_logs():
    return read_logs()

@app.get("/motivacao/")
def motivacao():
    return {"mensagem": random.choice(daily_messages)}


# Resumo semanal de progresso
@app.get("/usuarios/{user_id}/resumo-semanal")
def resumo_semanal(user_id: int):
    logs = read_logs()
    hoje = datetime.now().date()
    semana_passada = hoje - timedelta(days=7)

    habitos_realizados = [
        log for log in logs
        if log["user_id"] == user_id and datetime.strptime(log["date"], "%Y-%m-%d").date() >= semana_passada
    ]

    total = len(habitos_realizados)
    return {
        "user_id": user_id,
        "habitos_realizados_na_ultima_semana": total,
        "mensagem": "Continue assim! Cada dia importa."
    }


# Ranking semanal
@app.get("/ranking")
def ranking_usuarios():
    logs = read_logs()
    hoje = datetime.now().date()
    semana_passada = hoje - timedelta(days=7)
    contagem = {}

    for log in logs:
        log_date = datetime.strptime(log["date"], "%Y-%m-%d").date()
        if log_date >= semana_passada:
            uid = log["user_id"]
            contagem[uid] = contagem.get(uid, 0) + 1

    ranking = sorted([
        {"user_id": uid, "total": total} for uid, total in contagem.items()
    ], key=lambda x: x["total"], reverse=True)

    return {"ranking_semanal": ranking}