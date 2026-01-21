from fastapi import APIRouter, Depends, HTTPException
from models.models import Usuario
from dependencies import get_db_session, verify_token
from core.security import (SECRET_KEY, ACCESS_TOKEN_EXPIRE_MINUTES, ALGORITHM_TOKEN, bcrypt_context)
from schemas.schemas import UsuarioSchema, LoginSchema
from sqlalchemy.orm import Session
from datetime import datetime, timedelta, timezone
from fastapi.security import OAuth2PasswordRequestForm

# Usando python-jose para autenticaçao com JWT
from jose import jwt

SUCCESSFULL_AUTH_USER_MESSAGE = "Usuario Autenticado!"
INVALID_PWD_MESSAGE = "Error: Usuario não encontrado ou senha invalida"
EMAIL_ALREADY_CREATED_MESSAGE = "E-mail do usuario ja cadastrado"
USER_SUCCESSFULLY_CREATED = "Usuario cadastrado com sucesso:"

autenticacao_rota = APIRouter(prefix="/autenticacao", tags=["Autenticação"])

# Função para criar o token de autenticação do usuario
def create_token_jwt(id_usuario, duracao_token=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)):
    """
        Cria e retorna um token JWT para autenticação de usuários.

        O token gerado contém o identificador do usuário (`sub`) e a data de expiração (`exp`),
        permitindo autenticação segura sem a necessidade de expor e-mail ou senha em cada requisição.

        Args:
            id_usuario (int | str): Identificador único do usuário que será incluído no token.
            duracao_token (timedelta, optional): Tempo de validade do token JWT.
                Por padrão, utiliza o valor definido em ACCESS_TOKEN_EXPIRE_MINUTES.

        Returns:
            str: Token JWT codificado contendo as informações do usuário e a data de expiração.

        Raises:
            JWTError: Caso ocorra algum erro durante a codificação do token.
    """
    # Criando token JWT para não usar email e senha explicitamente
    # Criando uma data de expiração do token de acordo com os minutos de expiração
    expire_date_token = datetime.now(timezone.utc) + duracao_token

    # Informações para codificar e trasnforamr em token JWT
    dict_info = {
        "sub": str(id_usuario), # Id usuario
        "exp": expire_date_token.timestamp() # Data de expiraçao do token em timestamp
    }

    # Variavel de jwt codificado
    # Passando o dicionario, a chave de codificação das senhas e o tipo de algoritimo usado no JWT
    encoded_jwt = jwt.encode(
        claims=dict_info,
        key=SECRET_KEY,
        algorithm=ALGORITHM_TOKEN
    )

    return encoded_jwt


# Função para autenticar o usuario
def authentic_user(email, senha, session):
    """
        Autentica um usuário com base no e-mail e na senha informados.

        A função realiza a busca do usuário no banco de dados utilizando o e-mail
        e valida a senha fornecida comparando com o hash armazenado.
        Caso as credenciais estejam incorretas ou o usuário não exista,
        a autenticação falha.

        Args:
            email (str): Endereço de e-mail do usuário a ser autenticado.
            senha (str): Senha em texto puro fornecida pelo usuário.
            session (Session): Sessão ativa do SQLAlchemy para acesso ao banco de dados.

        Returns:
            Usuario | bool: Retorna o objeto Usuario quando a autenticação é bem-sucedida.
            Retorna False caso o usuário não exista ou a senha esteja incorreta.
    """
    # Pegando o usuario no banco de acordo com o email
    user = session.query(Usuario).filter(Usuario.email == email).first()

    # Se o usuario nao existir, então ele retorna false
    if not user:
        return False
    # Se o usuario existir, ele verifica se a senha do usuario nao é igual a do banco.
    elif not bcrypt_context.verify(secret=senha, hash=user.senha):
        # Retorna false se a senha estiver errada
        return False

    # Retorna o usuario caso exista o email e a senha esteja certa
    return user

@autenticacao_rota.get(path="/", status_code=201)
async def autenticacao():
    """
    Rota padrão ou "home" das autenticações.
    :return:
    """
    return {"message": "rota de autenticacao"}

@autenticacao_rota.post("/criar_conta")
async def criar_conta(usuario_schema: UsuarioSchema, session: Session = Depends(get_db_session), usuario: Usuario = Depends(verify_token)):
    """
        Cria uma nova conta de usuário no sistema.

        Realiza a validação de e-mail duplicado, criptografa a senha
        e salva o usuário no banco de dados. A criação de usuários
        administradores é restrita a usuários já autenticados com
        permissão de administrador.

        Args:
            usuario_schema (UsuarioSchema): Dados do usuário validados pelo Pydantic.
            session (Session): Sessão ativa do SQLAlchemy.
            usuario (Usuario): Usuário autenticado obtido a partir do token JWT.

        Raises:
            HTTPException:
                - 400: Caso o e-mail já esteja cadastrado.
                - 401: Caso um usuário sem permissão tente criar uma conta admin.

        Returns:
            dict: Mensagem de sucesso com o e-mail do usuário criado.
    """
    # Query para buscar usuario com o email especificado.
    # Caso não haja usuarios ele cria, se nao, retorna uma mensagem.
    user = session.query(Usuario).filter(Usuario.email == usuario_schema.email).first()

    if user:
        # Retornando um HTTPException para retornar codigo 400 e nao sempre 200 na rota
        raise HTTPException(status_code=400, detail=EMAIL_ALREADY_CREATED_MESSAGE)

    # Verificação se o usuario esta tentando criar uma conta ADMIN.
    # Caso sim, entao verificar se o usuario ja é admin, se nao, criar um user como admin = false
    if usuario_schema.admin:
        if not usuario.admin:
            raise HTTPException(status_code=401, detail="Erro ao tentar criar usuario admin, você não tem permissão para isso")


    # Criando uma senha criptgrafada a partir da senha do usuario
    # usando a variavel bcrypt context do arquivo main, onde está configurada
    # toda o processo para criptografia da senha
    senha_criptografada = bcrypt_context.hash(usuario_schema.senha)

    # Criando um usuario/conta caso nao exista
    # Usando usuario_schema do Pydantic para validar o dado
    new_user = Usuario(nome=usuario_schema.nome, email=usuario_schema.email, senha=senha_criptografada, telefone=usuario_schema.telefone, sexo=usuario_schema.sexo, admin=usuario_schema.admin, ativo=usuario_schema.ativo)

    # Armazenando na sessao o novo usario criado na variavel de user.
    session.add(new_user)

    # Fazendo o commit (inserção no banco de dados)
    session.commit()

    return {"message": f"{USER_SUCCESSFULLY_CREATED} {usuario_schema.email}"}

# Criando rota de login para autenticar usuarios para liberar acessos restritos somente a usuarios autenticados
@autenticacao_rota.post("/login")
async def login(login_schema: LoginSchema, session: Session = Depends(get_db_session)):
    """
        Autentica um usuário utilizando e-mail e senha.

        Valida as credenciais informadas e, em caso de sucesso,
        gera um access token e um refresh token para autenticação
        nas rotas protegidas da API.

        Args:
            login_schema (LoginSchema): Credenciais de login do usuário.
            session (Session): Sessão ativa do SQLAlchemy.

        Raises:
            HTTPException:
                - 400: Caso o e-mail não exista ou a senha esteja incorreta.

        Returns:
            dict: Tokens de autenticação (access e refresh), tipo do token
            e mensagem de sucesso.
    """
    user = authentic_user(email=login_schema.email, senha=login_schema.senha, session=session)
    if not user:
        # Usuario nao cadastrado ou senha errada
        raise HTTPException(status_code=400, detail=INVALID_PWD_MESSAGE)


    # Usuario existe, entao criando access e refresh token para o usuario
    access_token = create_token_jwt(id_usuario=user.id)

    # Passando o parametro duracao_token para o refresh token como sendo 7 dias.
    # esse parametro por padrao é o valor padrao de ACCESS_TOKEN_EXPIRE_MINUTES na .env
    # Ou seja, a cada 7 dias é preciso logar novamente no sistema e pegar o access_token
    # Mas durante os 7 dias, voce pode usar o refresh token para pegar o access token
    refresh_token = create_token_jwt(id_usuario=user.id, duracao_token=timedelta(days=7))

    return {
        "message": SUCCESSFULL_AUTH_USER_MESSAGE,
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "Bearer"
    }

# Criando rota de login para autenticar usuarios na documentação com OAuth2 login usando o Bearer.
# Passando a variavel form_data como sendo os dados do formulario de autenticação para usar o Bearer
# dentro da documentacao da api. Transformando essa variavel em Depends vazio, porque a dependencia é preenchida
# automaticamente pelo fastapi.
@autenticacao_rota.post("/login-form")
async def login_form(form_data: OAuth2PasswordRequestForm = Depends(), session: Session = Depends(get_db_session)):
    """
        Autentica um usuário utilizando OAuth2 Password Flow.

        Endpoint utilizado principalmente pela documentação Swagger
        para autenticação via Bearer Token. Recebe os dados do formulário
        padrão do OAuth2.

        Args:
            form_data (OAuth2PasswordRequestForm): Dados do formulário OAuth2
                contendo username (e-mail) e password.
            session (Session): Sessão ativa do SQLAlchemy.

        Raises:
            HTTPException:
                - 400: Caso as credenciais estejam inválidas.

        Returns:
            dict: Access token JWT e tipo do token para autenticação Bearer.
    """
    user = authentic_user(email=form_data.username, senha=form_data.password, session=session)
    if not user:
        # Usuario nao cadastrado ou senha errada
        raise HTTPException(status_code=400, detail=INVALID_PWD_MESSAGE)


    # Usuario existe, entao criando access e refresh token para o usuario
    access_token = create_token_jwt(id_usuario=user.id)

    # Passando o parametro duracao_token para o refresh token como sendo 7 dias.
    # esse parametro por padrao é o valor padrao de ACCESS_TOKEN_EXPIRE_MINUTES na .env
    # Ou seja, a cada 7 dias é preciso logar novamente no sistema e pegar o access_token
    # Mas durante os 7 dias, voce pode usar o refresh token para pegar o access token
    refresh_token = create_token_jwt(id_usuario=user.id, duracao_token=timedelta(days=7))

    return {
        "message": SUCCESSFULL_AUTH_USER_MESSAGE,
        "access_token": access_token,
        "token_type": "Bearer"
    }

# Gerando uma nova rota para pegar um novo access token via refresh token
# Criando uma função dependente (Depends) e adicionando a função use_refresh_token
@autenticacao_rota.get("/refresh")
async def use_refresh_token(user: Usuario = Depends(verify_token)):
    """
        Gera um novo access token a partir de um token válido.

        Essa rota é utilizada para renovar o access token sem a
        necessidade de realizar login novamente, desde que o token
        atual ainda seja válido.

        Args:
            user (Usuario): Usuário autenticado obtido a partir do token JWT.

        Returns:
            dict: Novo access token JWT e tipo do token.
    """
    # Criando o token de acordo com o usuario
    access_token = create_token_jwt(id_usuario=user.id)

    return {
        "message": SUCCESSFULL_AUTH_USER_MESSAGE,
        "access_token": access_token,
        "token_type": "Bearer"
    }
