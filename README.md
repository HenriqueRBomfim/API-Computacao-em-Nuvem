# API Computacao em Nuvem

Autor: Henrique Rocha Bomfim

Este repositório é o local que contém a explicação da API de criação de usuários, login e consulta de dados do IBGE feito pelo Henrique Rocha em 2024.
Os endpoints foram feitos com FastAPI em Python. O banco de dados foi orquestrado com SQLAlchemy em PostgresSQL e a consulta de dados com o token JWT retorna dados atualizados de notícias do IBGE.

AWS ao final

# Executando a aplicação

Para executar a aplicação, crie uma pasta, coloque o arquivo compose.yaml e digite "docker compose up -d"

# Vídeo mostrando o funcionamento da API

Um vídeo representando rapidamente o uso das endpoints e alguns exemplos pode ser visto a seguir: https://youtu.be/w7tym0sMWu4

# Publicação no Docker Hub

Para acessar o Docker Hub do projeto, pode-se acessar o link a seguir: https://hub.docker.com/repository/docker/henriquerb1/api-computacao-em-nuvem/general

# Onde encontrar o compose.yaml

Para encontrar o arquivo compose.yaml, deve-se acessar a página inicial do repositório e baixar o arquivo compose.yaml, não é necessário acessar qualquer pasta para isso. O caminho do arquivo pode ser pego a seguir: [Compose.yaml](./compose.yaml)

# Comandos usados para publicação no Docker Hub

Para fazer uma build, compilado de informações necessárias para rodar um container da aplicação, foi usado o comando a seguir:
```
docker build -t henriquerb1/api-computacao-em-nuvem:latest .
```

Para levar o build para o dockerhub, permitindo acesso independente da máquina, usou-se o comando a seguir:
```
docker push henriquerb1/api-computacao-em-nuvem:latest
```

# Documentação dos EndPoints

**Registrar**

O endpoint Registrar gera uma requisição do tipo POST e recebe os seguintes argumentos: nome, email e senha em json, como no exemplo da imagem abaixo:

![/registrar](./img/registrar.png)

Uma resposta possível é o retorno de um token JWT, como na imagem abaixo:

![/registrar_response](./img/registrar_response.png)

Um exemplo de curl para registro, pode ser testada no Postman:

```
curl -X 'POST' \
  'http://localhost:8000/registrar' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
  "nome": "string",
  "email": "string",
  "senha": "string"
}'
```

**Login**

O endpoint Login faz uma requisitação do tipo POST e recebe os argumentos email e senha através do formato JSON. Isso pode ser visto na figura abaixo:

![/login](./img/login.png)

Uma resposta possível é o token JWT para o payload passado, como na imagem abaixo:

![/login_response](./img/login_response.png)

Um exemplo de curl para teste do login, pode ser testada no Postman:

```
curl -X 'POST' \
  'http://localhost:8000/login' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
  "email": "string",
  "senha": "string"
}'
```

**Consultar**

O endpoint /consultar é do tipo GET, recebe o token JWT no Header "Authorization Bearer "jwt" " e retorna dados de API externa, no caso do IBGE, caso o token seja válido. Um exemplo de requisitação é a seguinte:

![/consulta](./img/consulta.png)

Na imagem acima, foi usado o Postman para testar a seguinte curl:

```
curl -X 'GET' 'http://localhost:8000/consultar' -H 'accept: application/json' -H 'Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJub21lIjoic3RyaW5nZyIsImVtYWlsIjoic3RyaW5nZyIsImV4cCI6MTczMDU2NDY4OX0.oeU8rlRTwXwD9ZBJcoNzxc1G7ib2wEFXgE0C5yGVtfs'
```

Assim, o cabeçalho Authorization foi passado com um Token válido.

Caso digitassemos um token inválido, o resultado seria este:

![/consulta_invalida](./img/consulta_invalida.png)

Caso o cabeçalho não seja fornecido corretamente, o response será como na imagem a seguir:

![/consulta_sem_Authorization](./img/consulta_sem_Authorization.png)

**Consulta de usuários**

O endpoint Usuarios faz uma requisição do tipo GET sem argumentos, conforme figura abaixo:

![/usuarios](./img/usuarios.png)

E retornar todos os nomes de usuários da base de dados, conforme figura abaixo:

![/usuarios_response](./img/usuarios_response.png)

Para consultar os usuarios na API, pode ser usar o seguinte curl no Postman:

```
curl -X 'GET' \
  'http://localhost:8000/usuarios' \
  -H 'accept: application/json'
```

**AWS**
Link para acesso a URL da AWS:

http://aac214db873ef4f75bf20e178f72676f-917515047.us-east-1.elb.amazonaws.com/docs
