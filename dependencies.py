# Este arquivo é usado para as dependencias que necessito para as rotas da minha API.
import os
from sqlalchemy.orm import sessionmaker, Session
from core.security import (SECRET_KEY, ALGORITHM_TOKEN, bcrypt_context, oauth2_schema)
from jose import jwt, JWTError
from models.models import db
from models.models import Usuario
from fastapi import Depends, HTTPException

# Variaveis de ambiente para criar o user adm
ADMIN_EMAIL = os.getenv("ADMIN_EMAIL")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD")

# Função para pegar a sessão do banco de dados, retornar com yield para retornar mas não fehcar a função e no fim
# independentemente se a funçao funcionou ou deu erro, ela fecha a sessao com o banco para não
# gerar multiplas sessões abertas e congestionar o banco de dados
def get_db_session():
    try:
        Session = sessionmaker(bind=db)
        session = Session()

        # Usando yield para a sessao retornar o valor mas nao encerrar a função
        yield session
    # Usamos try finally para tratar se houver erro e garantir que a sessao sempre seja encerrada.
    finally:
        # no fim, encerrarmos a sessao com session.close()
        session.close()

# Função para criar o admin inicial
def init_admin():
    # Criando a sessão manualmente para o codigo de init admin.
    Session = sessionmaker(bind=db)
    session = Session()
    try:
        # Pegando o primeiro usuario do banco
        existe_usuario = session.query(Usuario).first()

        # Se existir, entao nao cria um novo usuario e retorna nada
        if existe_usuario:
            return

        # Se nao existir usuario, cria o usuario padrão ADM
        senha_criptografada = bcrypt_context.hash(ADMIN_PASSWORD)

        admin = Usuario(
            nome="admin",
            email=ADMIN_EMAIL,
            senha=senha_criptografada,
            telefone="11999999999",
            sexo="admin",
            admin=True,
            ativo=True
        )

        session.add(admin)
        session.commit()

        print("✅ Usuário ADMIN criado com sucesso")
    finally:
        session.close()



# Função para verificar se o token é valido para a rota de refresh, usando a sessao como Depend para
# a conexao e verificação do banco. Usando o token como Depends para utilizar o token dentro dos headers e
# usar o Bearer.
def verify_token(token: str = Depends(oauth2_schema), session: Session = Depends(get_db_session)):
    # Tentando fazer a decodificação do token JWT enviado fazendo o processo reverso ao de codificação dos dados.
    try:
        # Pegando o dicionario de informações sobre o token JWT
        dict_info = jwt.decode(token=token, key=SECRET_KEY, algorithms=ALGORITHM_TOKEN)

        # Pegando o id do usuario para pegar o usuario
        id_usuario = int(dict_info.get("sub"))
    except JWTError as jwt_error:
        raise HTTPException(status_code=401, detail="Acesso Negado, verifique a validade do token")

    # Verificar se o token é valido
    # Se o token for valido, essa função extrai o id do usuario desse token.
    usuario = session.query(Usuario).filter(Usuario.id == id_usuario).first()
    if not usuario:
        raise HTTPException(status_code=401, detail="Acesso Invalido")

    return usuario