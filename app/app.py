from fastapi import FastAPI, HTTPException, Depends, Header
from fastapi.security import HTTPBearer
from pydantic import BaseModel
from datetime import datetime, timedelta
import jwt
import bcrypt
import os
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

# Configurações
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
EXPIRES_IN_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES"))

app = FastAPI()
security = HTTPBearer()

# Funções de auxílio para o JWT e hash da senha
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

# Funções de auxílio para o JWT
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
    # Simulação de lógica para registro do usuário
    jwt_token = criar_token_jwt(registrar_request.email, registrar_request.nome)
    return {"jwt": jwt_token}

@app.post("/login", response_model=TokenResponse)
def login(login_request: LoginRequest):
    # Simulação de lógica de autenticação
    if login_request.email == "cloud@insper.edu.br" and login_request.senha == "cloud0":
        jwt_token = criar_token_jwt(login_request.email, "Disciplina Cloud")
        return {"jwt": jwt_token}
    else:
        raise HTTPException(status_code=403, detail="Credenciais inválidas")

@app.get("/consultar")
def consultar(authorization: str = Header(None)):
    if authorization is None:
        raise HTTPException(status_code=403, detail="Token de autorização não encontrado")

    token = authorization.split(" ")[1]
    verificar_token_jwt(token)  # Verifica se o token é válido

    # Dados de exemplo simulando uma consulta de dados externos, como índice Bovespa
    dados_externos = [
        {"Date": "2024-09-05", "Open": 136112.0, "High": 136656.0, "Low": 135959.0, "Close": 136502.0, "Volume": 7528700},
        # Adicione outros dias simulados
    ]
    
    return {"dados": dados_externos}