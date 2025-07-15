import requests
import json
import pandas as pd
from datetime import date

BASE_URL = "http://127.0.0.1:8000"

def criar_usuario():
    nome = input("Nome: ")
    email = input("Email: ")
    senha = input("Senha: ")
    payload = {"name": nome, "email": email, "senha": senha}
    response = requests.post(f"{BASE_URL}/usuarios/", json=payload)
    print(response.json())

def login():
    email = input("Email: ")
    senha = input("Senha: ")
    payload = {"email": email, "senha": senha}
    response = requests.post(f"{BASE_URL}/login", json=payload)
    print(response.json())

def listar_usuarios():
    response = requests.get(f"{BASE_URL}/usuarios/")
    usuarios = response.json()
    if usuarios:
        df = pd.DataFrame(usuarios)
        print("\nUsuários cadastrados:")
        print(df[["id", "name", "email"]])
    else:
        print("Nenhum usuário encontrado.")

def criar_habito():
    titulo = input("Título do hábito: ")
    descricao = input("Descrição: ")
    user_id = int(input("ID do usuário: "))
    payload = {"title": titulo, "description": descricao, "user_id": user_id}
    response = requests.post(f"{BASE_URL}/habitos/", json=payload)
    print(response.json())

def listar_habitos():
    response = requests.get(f"{BASE_URL}/habitos/")
    habitos = response.json()
    if habitos:
        df = pd.DataFrame(habitos)
        if "favorito" in df.columns:
            df = df.drop(columns=["favorito"])  # Remove coluna desnecessária
        print("\nHábitos cadastrados:")
        print(df[["id", "title", "description", "user_id"]])
    else:
        print("Nenhum hábito encontrado.")

def registrar_registro():
    user_id = int(input("ID do usuário: "))
    habit_id = int(input("ID do hábito: "))
    usar_data_custom = input("Deseja informar a data? (s/n): ").strip().lower()

    payload = {
        "user_id": user_id,
        "habit_id": habit_id,
    }

    if usar_data_custom == "s":
        data = input("Data (AAAA-MM-DD): ").strip()
        payload["date"] = data

    response = requests.post(f"{BASE_URL}/registros/", json=payload)
    try:
        print(response.json())
    except json.JSONDecodeError:
        print("Erro ao interpretar JSON:", response.text)

def ver_motivacao():
    response = requests.get(f"{BASE_URL}/motivacao/")
    print("Mensagem motivacional:", response.json().get("mensagem"))

def ver_resumo_semanal():
    user_id = int(input("ID do usuário: "))
    response = requests.get(f"{BASE_URL}/usuarios/{user_id}/resumo-semanal")
    print(response.json())

def ver_ranking():
    response = requests.get(f"{BASE_URL}/ranking")
    dados = response.json().get("ranking_semanal", [])
    if dados:
        df = pd.DataFrame(dados)
        print("\nRanking da semana:")
        print(df)
    else:
        print("Nenhum dado encontrado para ranking.")


def menu():
    while True:
        print("\n=== Menu Principal ===")
        print("1 - Criar usuário")
        print("2 - Login")
        print("3 - Listar usuários")
        print("4 - Criar hábito")
        print("5 - Listar hábitos")
        print("6 - Registrar hábito realizado")
        print("7 - Ver motivação")
        print("8 - Ver resumo semanal")
        print("9 - Ver ranking semanal")
        print("0 - Sair")
        escolha = input("Escolha uma opção: ")

        if escolha == "0":
            print("Saindo...")
            break
        elif escolha == "1":
            criar_usuario()
        elif escolha == "2":
            login()
        elif escolha == "3":
            listar_usuarios()
        elif escolha == "4":
            criar_habito()
        elif escolha == "5":
            listar_habitos()
        elif escolha == "6":
            registrar_registro()
        elif escolha == "7":
            ver_motivacao()
        elif escolha == "8":
            ver_resumo_semanal()
        elif escolha == "9":
            ver_ranking()
        else:
            print("Opção inválida. Tente novamente.")

if __name__ == "__main__":
    menu()
