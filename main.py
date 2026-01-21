import os
from dependencies import init_admin
from fastapi import FastAPI, Request
from fastapi.security import OAuth2PasswordBearer
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse

# Importando a ferramenta para criptografar as senhas dos usuarios.
from passlib.context import CryptContext

# Carregando as envs e buscando a secret key com 'os'
from dotenv import load_dotenv

load_dotenv()

# Subir a API: uvicorn main:app --reload

app = FastAPI()

# Criando o admin inicial para usar aplicação em produção
@app.on_event("startup")
def startup_event():
    init_admin()

# Criando a pasta de templates do jinja
templates = Jinja2Templates(directory="templates")


# # Criando a variavel para criar a varaivel que vai verificar se a senha é igual a senha criptografada no db
# # deprecated="auto" é usado para o CryptContext sempre buscar o esquema mais atualziado para criptografia
# bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
#
# # Criando a variavel oauth2_schema como um esquema da autenticação oauth2 para
# # funcionar o refresh token, tendo em vista que oauth2 usa o esquema de
# # "Bearer token" dentro do headers, então precisamos adicionar o token como um Depends
# # da função que usa o refresh token para gerar um novo access token
# oauth2_schema = OAuth2PasswordBearer(tokenUrl="autenticacao/login-form")

# Importando e adicionando as rotas do sistema no aplicativo!
from routes.autenticacao_rotas import autenticacao_rota
from routes.pedidos_rotas import pedidos_rota

app.include_router(autenticacao_rota)
app.include_router(pedidos_rota)

# Rota principal do aplicativo com as informações da API
@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """
        Rota HOME da API.

        Renderiza a página inicial contendo a documentação geral do sistema,
        descrição das funcionalidades e informações sobre as rotas disponíveis.
    """
    return templates.TemplateResponse(
        "index.html",
        {"request": request}
    )