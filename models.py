from sqlalchemy import Column, Integer, String, ForeignKey, Date
from sqlalchemy.orm import relationship
from database import Base

class Usuario(Base):
    __tablename__ = "usuarios"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    senha = Column(String, nullable=False)

    habitos = relationship("Habito", back_populates="usuario")
    registros = relationship("Registro", back_populates="usuario")


class Habito(Base):
    __tablename__ = "habitos"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(String)
    user_id = Column(Integer, ForeignKey("usuarios.id"))

    usuario = relationship("Usuario", back_populates="habitos")
    registros = relationship("Registro", back_populates="habito")


class Registro(Base):
    __tablename__ = "registros"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("usuarios.id"))
    habit_id = Column(Integer, ForeignKey("habitos.id"))
    date = Column(Date)

    usuario = relationship("Usuario", back_populates="registros")
    habito = relationship("Habito", back_populates="registros")
