from fastapi import FastAPI, HTTPException, Depends, Header
from fastapi.security import HTTPBearer
from pydantic import BaseModel
from datetime import datetime, timedelta, timezone
import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import declarative_base, sessionmaker
import httpx
from jwt import encode, decode, ExpiredSignatureError, InvalidTokenError
from pwdlib import PasswordHash

# Carregar variáveis de ambiente
load_dotenv()

# Configurações
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES"))
pwd_context = PasswordHash.recommended()

POSTGRES_HOST = "db"
POSTGRES_PORT = 5432

# Configuração do SQLAlchemy para conectar ao PostgreSQL
#DATABASE_URL = f"postgresql+psycopg2://henrique:segredo@db:5432/superprojetao"
DATABASE_URL = f"postgresql://{os.getenv('POSTGRES_USER')}:{os.getenv('POSTGRES_PASSWORD')}@{POSTGRES_HOST}:{POSTGRES_PORT}/{os.getenv('POSTGRES_DB')}"

ENGINE = create_engine(DATABASE_URL)

SESSION = sessionmaker(autocommit=False, bind=ENGINE, autoflush=False)

BASE = declarative_base()

# Modelo de Usuário
class Usuario(BASE):
    __tablename__ = "usuarios"
    
    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String, index=True)
    email = Column(String, unique=True, index=True)
    senha_hashed = Column(String)

def get_password_hash(password: str):
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str):
    return pwd_context.verify(plain_password, hashed_password)

# Modelos de Dados
class RegistrarRequest(BaseModel):
    nome: str
    email: str
    senha: str

class LoginRequest(BaseModel):
    email: str
    senha: str

class TokenResponse(BaseModel):
    jwt: str

def create_access_token(email: str, nome: str):
    expire = datetime.now(timezone.utc) + timedelta(
        minutes=ACCESS_TOKEN_EXPIRE_MINUTES
    )
    to_encode = {
        "nome": nome,
        "email": email,
        "exp": expire
    }
    to_encode.update({'exp': expire})
    encoded_jwt = encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def test_jwt(token: str):
    try:
        payload = decode(token, SECRET_KEY, algorithms=['HS256'])
        return payload
    except ExpiredSignatureError:
        raise HTTPException(status_code=403, detail="Token expirado")
    except InvalidTokenError:
        raise HTTPException(status_code=403, detail="Token inválido")

BASE.metadata.create_all(bind = ENGINE)

app = FastAPI()
security = HTTPBearer()

# Endpoints
@app.post("/registrar", response_model=TokenResponse)
def registrar(registrar_request: RegistrarRequest):
    db = SESSION()
    usuario_existente = db.query(Usuario).filter(Usuario.email == registrar_request.email).first()
    if usuario_existente:
        raise HTTPException(status_code=409, detail="Email já cadastrado")

    usuario = Usuario(
        nome=registrar_request.nome,
        email=registrar_request.email,
        senha_hashed=get_password_hash(registrar_request.senha)
    )
    db.add(usuario)
    db.commit()
    db.refresh(usuario)

    jwt_token = create_access_token(usuario.email, usuario.nome)
    return {"jwt": jwt_token}

@app.post("/login", response_model=TokenResponse)
def login(login_request: LoginRequest):
    db = SESSION()
    usuario = db.query(Usuario).filter(Usuario.email == login_request.email).first()
    if not usuario or not verify_password(login_request.senha, usuario.senha_hashed):
        raise HTTPException(status_code=403, detail="Credenciais inválidas")

    jwt_token = create_access_token(usuario.email, usuario.nome)
    return {"jwt": jwt_token}

@app.get("/consultar")
async def consultar(authorization: str = Header(...)):
    print(authorization)
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=403, detail="Token de autorização inválido")
    
    token = authorization.split(" ")[1]
    
    test_jwt(token)

    url = "http://servicodados.ibge.gov.br/api/v3/noticias/"
    async with httpx.AsyncClient() as client:
        response = await client.get(url)
        if response.status_code != 200:
            raise HTTPException(status_code=response.status_code, detail="Erro ao consultar dados externos")

    dados_externos = response.json()
    return {"dados": dados_externos}

@app.get("/usuarios")
def listar_usuarios():
    db = SESSION()
    usuarios = db.query(Usuario).all()
    nomes = [usuario.nome for usuario in usuarios]
    return nomes