# API-Computacao-em-Nuvem

Henrique Rocha Bomfim

Eu fiz os endpoints com FastAPI em Python, orquestrei o banco de dados com SQLAlchemy no PostgresSQL e retorno dados de notícias do IBGE.

Para executar a aplicação, crie uma pasta, coloque o arquivo compose.yaml e digite docker-compose up --build

Link de um vídeo mostrando a API: https://youtu.be/w7tym0sMWu4

Comandos usados para publicação no Docker Hub:
docker build -t henriquerb1/api-computacao-em-nuvem:latest .
docker push henriquerb1/api-computacao-em-nuvem:latest