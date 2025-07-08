import requests
import json
from datetime import date

BASE_URL = "http://127.0.0.1:8000"

def criar_usuario():
    nome = input("Nome: ")
    email = input("Email: ")
    senha = input("Senha: ")
    payload = {"name": nome, "email": email, "senha": senha}
    response = requests.post(f"{BASE_URL}/users/", json=payload)
    print("Status code:", response.status_code)
    print("Resposta JSON:", response.json())

def login():
    email = input("Email: ")
    senha = input("Senha: ")
    payload = {"email": email, "senha": senha}
    response = requests.post(f"{BASE_URL}/login", json=payload)
    print("Status code:", response.status_code)
    print("Resposta JSON:", response.json())

def listar_usuarios():
    response = requests.get(f"{BASE_URL}/users/")
    print("Status code:", response.status_code)
    print("Resposta JSON:", response.json())

def criar_habito():
    titulo = input("Título do hábito: ")
    descricao = input("Descrição: ")
    user_id = int(input("ID do usuário: "))
    payload = {"title": titulo, "description": descricao, "user_id": user_id}
    response = requests.post(f"{BASE_URL}/habits/", json=payload)
    print("Status code:", response.status_code)
    print("Resposta JSON:", response.json())

def registrar_log():
    user_id = int(input("ID do usuário: "))
    habit_id = int(input("ID do hábito: "))
    
    usar_data_custom = input("Deseja informar a data manualmente? (s/n): ").strip().lower()
    
    payload = {
        "user_id": user_id,
        "habit_id": habit_id
    }

    if usar_data_custom == "s":
        data = input("Informe a data (AAAA-MM-DD): ").strip()
        payload["date"] = data  # Só envia se o usuário quiser

    response = requests.post(f"{BASE_URL}/logs/", json=payload)
    print("Status code:", response.status_code)
    try:
        print("Resposta JSON:", response.json())
    except json.JSONDecodeError:
        print("Erro ao interpretar JSON: Resposta não é JSON.")
        print("Resposta raw:", response.text)

def ver_motivacao():
    response = requests.get(f"{BASE_URL}/motivacao/")
    print("Status code:", response.status_code)
    print("Mensagem motivacional:", response.json().get("mensagem"))

def ver_resumo_semanal():
    user_id = int(input("ID do usuário: "))
    response = requests.get(f"{BASE_URL}/users/{user_id}/resumo-semanal")
    print("Status code:", response.status_code)
    print("Resposta JSON:", response.json())

def ver_ranking():
    response = requests.get(f"{BASE_URL}/ranking")
    print("Status code:", response.status_code)
    print("Resposta JSON:", response.json())

def menu():
    while True:
        print("\n1 - Criar usuário")
        print("2 - Login")
        print("3 - Listar usuários")
        print("4 - Criar hábito")
        print("5 - Registrar log")
        print("6 - Ver motivação")
        print("7 - Ver resumo semanal")
        print("8 - Ver ranking semanal")
        print("0 - Sair")
        escolha = input("Escolha: ")

        if escolha == "1":
            criar_usuario()
        elif escolha == "2":
            login()
        elif escolha == "3":
            listar_usuarios()
        elif escolha == "4":
            criar_habito()
        elif escolha == "5":
            registrar_log()
        elif escolha == "6":
            ver_motivacao()
        elif escolha == "7":
            ver_resumo_semanal()
        elif escolha == "8":
            ver_ranking()
        elif escolha == "0":
            print("Saindo...")
            break
        else:
            print("Opção inválida.")

if __name__ == "__main__":
    menu()
