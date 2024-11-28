# API Computacao em Nuvem

Autor: Henrique Rocha Bomfim

Este repositório é o local que contém a explicação da API de criação de usuários, login e consulta de dados do IBGE feito pelo Henrique Rocha em 2024.
Os endpoints foram feitos com FastAPI em Python. O banco de dados foi orquestrado com SQLAlchemy em PostgresSQL e a consulta de dados com o token JWT retorna dados atualizados de notícias do IBGE.

**AWS**

Nesta parte do projeto, foi realizado o deploy da aplicação nos serviços da AWS. De forma resumida, foi gerado um deploy do banco de dados Postgres e da API através do Serviço EKS da AWS.

# Executando a aplicação

Para executar a aplicação, acesse este link gerado com os serviços da AWS: [link da aplicação na AWS](http://aac214db873ef4f75bf20e178f72676f-917515047.us-east-1.elb.amazonaws.com/docs)

# Vídeo mostrando o funcionamento da API

Foi realizado um vídeo explicando brevemente os serviços AWS que estão fazendo com que a aplicação seja acessível pela internet, além de mostrar comandos de uso através do Postman: https://youtu.be/CTqpEHfANo4 

# Onde encontrar o deployment.yaml

Para encontrar o arquivo deployment.yaml, deve-se acessar a página inicial do repositório, clicar na pasta k8s e entrar no arquivo deployment.yaml. O caminho do arquivo pode ser pego a seguir: [deployment.yaml](k8s/deployment.yaml)

Obs: Tanto os deployments da API e da DataBase quanto os seus respectivos serviços foram gerados no mesmo arquivo acima.

# Passo a passo para publicação na AWS

## 1. Instalação do AWS CLI:

Para realizar os comandos de manutenção dos PODs e cnfiguração do Kubernets, foi necessário criar uma sessão da AWS na minha máquina local. Para isso, instalei o AWS CLI, que é o terminal da AWS, através do seguinte tutorial oficial: [Tutorial](https://docs.aws.amazon.com/pt_br/cli/latest/userguide/getting-started-install.html)

O comando utilizado para instalação foi:
```
msiexec.exe /i https://awscli.amazonaws.com/AWSCLIV2.msi
```

Após isso, foi necessário configurar a sessão local. Para isso, segui o tutorial presente neste link: [Tutorial](https://docs.aws.amazon.com/pt_br/cli/latest/userguide/getting-started-quickstart.html) na sessão a seguir:

![AWS Configure](./img/aws_configure.png)

Para conseguir as informações para o AWS Configure, foi necessário possuir uma chave de acesso. Para conseguir ela, fiz o seguinte:

- Fiz login na minha conta
- Fui até a sessão Access Management
- Selecionei a opção users e cliquei no meu usuário
- Fui em Create access key na caixa Summary
- Marquei a opção CLI
- Baixei o arquivo .csv contendo a Access Key e a Secret Access Key
- Peguei minha região ao abrir o CLI dentro da AWS, mas acredito ter outras formas mais práticas de pegar essa informação

Com essas informações, digitei "aws configure" no terminal do Windows como administrador e preenchi os dados:
- Access Key
- Secret Access Key
- Região
- Selecionei o formato json para outputs

## 2. Configuração do kubectl:

Nesta etapa, instalei o kubectl para poder controlar o kubernetes pelo terminal e fazer deploy da minha aplicação posteriormente.

Para instalar o kubectl:
```
curl.exe -LO "https://dl.k8s.io/release/v1.31.0/bin/windows/amd64/kubectl.exe"
```

## 3. Criação das roles:

Aqui, foram definidas as roles que seriam usadas:

![/roles](./img/roles.png)

## 4. Criação da nuvem:

Foi utilizado o serviço CloudFormation para criar um esquema de nuvem a partir do link fornecido na referência: [Arquivo padrão para criação da VPC](https://www.youtube.com/redirect?event=comments&redir_token=QUFFLUhqblhiVUxkeGg3SUdaSWdSRXliQ2JSTHVOS3VTQXxBQ3Jtc0ttdkhldzFLWmJjeGhPS3NqVVIxUnR4M0dFQ2QtREQxbWk0Q21HYWJwQjY2OENkUDB4dVNxclhlQ0VPUjdaRzE4MXZNTEkwUmhZQ3lDeGNpMDZnVmc4OEFQVFYzWDdGNmdfYmJTYXcyb3FvVWNURk5ibw&q=https%3A%2F%2Fs3.us-west-2.amazonaws.com%2Famazon-eks%2Fcloudformation%2F2020-10-29%2Famazon-eks-vpc-private-subnets.yaml)

Nesse esquema, foram geradas as subnets, VPC, rotas, security group e outros recursos necessários para fazer o deploy.

## 5. Criação do Cluster:

Com a role CloudAWSClusterRole e a nuvem criadas, pude fazer o Cluster do EKS: 

Seleção da role e de um nome
![cluster1](./img/cluster1.png)

Seleção da configuração de rede feita pelo CloudFormation
![network](./img/network.png)

Após isso, só fui clicando em next. 

## 6. Criação do Node Group:

Foi criado um grupo de nós para que houvesse sempre um nó para o banco de dados e outro para a API. Foi usada uma instância do tipo t3.medium.

## 7. Uso do kubectl:

Para poder usar o kubectl, foi necessário indicar para ele qual o Cluster EKS da sessão ele iria controlar:

```
aws eks update-kubeconfig --name eks-live
```

Após isso, criei uma pasta chamada k8s e um arquivo chamado deployment.yaml dentro dela. Nesse arquivo, coloquei todas as instruções necessárias para que o kubectl conseguisse fazer deploy da minha aplicação no Cluster.

```
kubectl apply -f k8s/
```

Após fazer isso, foram adicionados dois novos PODs ao Cluster EKS: app-deployment e db. Esses PODs são refeitos quando algo de errado acontece ou eles são deletados, garantindo consistência na aplicação.

Para ver os PODs ativos da aplicação, pode-se usar este comando:

```
kubectl get pods
```

Para ver todos os recursos e informações do Cluster, foi utilizado o comando:
```
kubectl get all
```

Para obter o link da aplicação, foi utilizado o comando:
```
kubectl get svc app-service
```

# Documentação dos EndPoints

**Registrar**

O endpoint Registrar gera uma requisição do tipo POST e recebe os seguintes argumentos: nome, email e senha em json, como no exemplo da imagem abaixo:

![/registrar](./img/registrarAWS.png)

Um exemplo de curl para registro, pode ser testada no Postman:

```
curl -X 'POST' \
  'http://aac214db873ef4f75bf20e178f72676f-917515047.us-east-1.elb.amazonaws.com/registrar' \
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

![/login](./img/loginAWS.png)

Um exemplo de curl para teste do login, pode ser testada no Postman:

```
curl -X 'POST' \
  'http://aac214db873ef4f75bf20e178f72676f-917515047.us-east-1.elb.amazonaws.com/login' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
  "email": "string",
  "senha": "string"
}'
```

**Consultar**

O endpoint /consultar é do tipo GET, recebe o token JWT no Header "Authorization Bearer "jwt" " e retorna dados de API externa, no caso do IBGE, caso o token seja válido. Um exemplo de requisitação é a seguinte:

![/consultaAWS](./img/consultaAWS.png)

Na imagem acima, foi usado o Postman para testar a seguinte curl:

```
curl -X 'GET' 'http://aac214db873ef4f75bf20e178f72676f-917515047.us-east-1.elb.amazonaws.com/consultar' -H 'accept: application/json' -H 'Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJub21lIjoic3RyaW5nIiwiZW1haWwiOiJzdHJpbmciLCJleHAiOjE3MzI3NjczMjB9.GDKRf7eC-IZYfr6EJWWjajNw_uuEEaHvzx1OQHhYt6U'
```

Assim, o cabeçalho Authorization foi passado com um Token válido.

Caso digitassemos um token inválido, o resultado seria este:

![/consulta_invalidaAWS](./img/consulta_invalidaAWS.png)

Caso o cabeçalho não seja fornecido corretamente, o response será como na imagem a seguir:

![/consulta_sem_AuthorizationAWS](./img/consulta_sem_AuthorizationAWS.png)

**Consulta de usuários**

O endpoint Usuarios faz uma requisição do tipo GET sem argumentos, conforme figura abaixo:

![/usuariosAWS](./img/usuariosAWS.png)

Para consultar os usuarios na API, pode-se usar o seguinte curl no Postman:

```
curl -X 'GET' \
  'http://aac214db873ef4f75bf20e178f72676f-917515047.us-east-1.elb.amazonaws.com/usuarios' \
  -H 'accept: application/json'
```
