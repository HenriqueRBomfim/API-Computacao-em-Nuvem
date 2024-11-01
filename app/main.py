from fastapi import FastAPI, HTTPException, Depends, Header
from fastapi.security import HTTPBearer
from pydantic import BaseModel
from datetime import datetime, timedelta
import jwt
import bcrypt
import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import declarative_base, scoped_session, sessionmaker
import httpx

# Carregar variáveis de ambiente
load_dotenv()

# Configurações
SECRET_KEY = os.getenv("SECRET_KEY") #hidsa53sdadshDADBJSKsd1d2as1d3
ALGORITHM = os.getenv("ALGORITHM") #HS256
EXPIRES_IN_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES")) # 30 minutos

# Configuração do SQLAlchemy para conectar ao PostgreSQL
DATABASE_URL = f"postgresql+psycopg2://{os.getenv('POSTGRES_USER')}:{os.getenv('POSTGRES_PASSWORD')}@{os.getenv('POSTGRES_HOST')}:{os.getenv('POSTGRES_PORT')}/{os.getenv('POSTGRES_NAME')}"
ENGINE = create_engine(DATABASE_URL)
BASE = declarative_base()
BASE.metadata.bind = ENGINE

# Modelo de Usuário
class Usuario(BASE):
    __tablename__ = "usuarios"
    
    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String, index=True)
    email = Column(String, unique=True, index=True)
    senha_hashed = Column(String)

# Criar todas as tabelas no banco de dados
BASE.metadata.create_all(ENGINE)

SESSION = scoped_session(sessionmaker(bind=ENGINE, autoflush=False))

app = FastAPI()
security = HTTPBearer()

# Funções de auxílio para o jwt e hash da senha
def hash_senha(senha: str) -> str:
    return bcrypt.hashpw(senha.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def verificar_senha(senha: str, senha_hashed: str) -> bool:
    return bcrypt.checkpw(senha.encode('utf-8'), senha_hashed.encode('utf-8'))

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

# Funções de auxílio para o jwt
def criar_token_jwt(email: str, nome: str):
    expire = datetime.utcnow() + timedelta(minutes=EXPIRES_IN_MINUTES)
    payload = {
        "nome": nome,
        "email": email,
        "exp": expire
    }
    token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
    return token

def verificar_token_jwt(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=403, detail="Token expirado")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=403, detail="Token inválido")

# Endpoints
@app.post("/registrar", response_model=TokenResponse)
def registrar(registrar_request: RegistrarRequest):
    db = SESSION()
    # Verificar se o email já está cadastrado
    usuario_existente = db.query(Usuario).filter(Usuario.email == registrar_request.email).first()
    if usuario_existente:
        raise HTTPException(status_code=409, detail="Email já cadastrado")

    # Criar novo usuário
    usuario = Usuario(
        nome=registrar_request.nome,
        email=registrar_request.email,
        senha_hashed=hash_senha(registrar_request.senha)
    )
    db.add(usuario)
    db.commit()
    db.refresh(usuario)

    jwt_token = criar_token_jwt(usuario.email, usuario.nome)
    return {"jwt": jwt_token}

@app.post("/login", response_model=TokenResponse)
def login(login_request: LoginRequest):
    db = SESSION()
    # Buscar usuário pelo nome
    usuario = db.query(Usuario).filter(Usuario.email == login_request.email).first()
    if not usuario or not verificar_senha(login_request.senha, usuario.senha_hashed):
        raise HTTPException(status_code=403, detail="Credenciais inválidas")

    jwt_token = criar_token_jwt(usuario.email, usuario.nome)
    return {"jwt": jwt_token}

@app.get("/consultar")
async def consultar(token: str):
    if token is None:
        raise HTTPException(status_code=403, detail="Token de autorização não encontrado")

    verificar_token_jwt(token)

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