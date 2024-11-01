# Usar uma imagem base que tenha Python
FROM python:3.10-slim

# Atualizar e instalar dependências
RUN apt-get update && \
    apt-get install -y net-tools && \
    rm -rf /var/lib/apt/lists/*

RUN pip install --upgrade pip

# Definir diretório de trabalho dentro do contêiner
WORKDIR /app

# Copiar o arquivo de requisitos
COPY requirements.txt .

# Instalar pacotes Python necessários
RUN pip install --no-cache-dir -r requirements.txt

# Copiar o restante do código da aplicação
COPY . .

# Definir a porta em que o FastAPI será exposto (a porta interna do container)
EXPOSE 8000

# Comando para iniciar o aplicativo com a variável de ambiente PORT
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]