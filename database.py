from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import User, Base

DATABASE_URL = "sqlite:///./autocuidado.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
db = SessionLocal()

def listar_usuarios():
    usuarios = db.query(User).all()
    if not usuarios:
        print("Nenhum usuário encontrado no banco.")
    else:
        for u in usuarios:
            print(f"ID: {u.id}, Nome: {u.name}, Email: {u.email}")

# ✅ ESTA PARTE É NOVA
def init_db():
    Base.metadata.create_all(bind=engine)

if __name__ == "__main__":
    listar_usuarios()
