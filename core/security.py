import os
from fastapi.security import OAuth2PasswordBearer
# Importando a ferramenta para criptografar as senhas dos usuarios.
from passlib.context import CryptContext

# Carregando as envs e buscando a secret key com 'os'
from dotenv import load_dotenv

load_dotenv()

# Pegando a chave privado para criptografar as senhas
SECRET_KEY = os.getenv("SECRET_KEY")

# Algoritimo do jwt token
ALGORITHM_TOKEN = os.getenv("JWT_ALGORITHM")

# Minutos de expiração do token e transformando em inteiro para usar na função de criação do jwt token
# de expiração de data
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES"))

# Criando a variavel para criar a varaivel que vai verificar se a senha é igual a senha criptografada no db
# deprecated="auto" é usado para o CryptContext sempre buscar o esquema mais atualziado para criptografia
bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Criando a variavel oauth2_schema como um esquema da autenticação oauth2 para
# funcionar o refresh token, tendo em vista que oauth2 usa o esquema de
# "Bearer token" dentro do headers, então precisamos adicionar o token como um Depends
# da função que usa o refresh token para gerar um novo access token
oauth2_schema = OAuth2PasswordBearer(tokenUrl="autenticacao/login-form")