from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.templating import Jinja2Templates
from dependencies import get_db_session, verify_token
from schemas.schemas import PedidoSchema, ItemPedidoSchema, ResponsePedidoEspecificoSchema
from sqlalchemy import select
from sqlalchemy.orm import Session
from models.models import Pedido, Usuario, ItensPedido
from typing import List

# Adicionada a rota, a tag para a documentação e a dependencia em "dependencies"
# essa dependencia é para verificar o token do usuario, para que todas as rotas desse código só consigam ser executada
# com autenticação do usuario
pedidos_rota = APIRouter(prefix="/pedidos", tags=["Pedidos"], dependencies=[Depends(verify_token)])

# Configurando um template html para a pagina inicial de rotas, configuração com Jinja2 como template engine
templates = Jinja2Templates(directory="templates")

@pedidos_rota.get(path="/", status_code=201)
async def orders():
    return {"message": "rotas pedidos"}

@pedidos_rota.get(path="/listar-pedidos", status_code=201)
async def orders_list(session: Session = Depends(get_db_session), usuario: Usuario = Depends(verify_token)):
    """
        Lista todos os pedidos cadastrados no sistema.

        Esta rota é restrita a usuários administradores. Realiza a validação
        do token JWT e verifica se o usuário autenticado possui permissão
        de administrador antes de retornar os pedidos.

        Args:
            session (Session): Sessão ativa do SQLAlchemy para acesso ao banco de dados.
            usuario (Usuario): Usuário autenticado obtido a partir do token JWT.

        Raises:
            HTTPException:
                - 401: Caso o usuário autenticado não possua permissão de administrador.

        Returns:
            list[Pedido]: Lista contendo todos os pedidos registrados no sistema.
    """
    # Verificando se o usuario é admin
    if not usuario.admin:
        raise HTTPException(status_code=401, detail="Você não tem permissão para acessar essa funcionalidade.")

    # Pegando todos os pedidos
    pedidos = session.query(Pedido).all()

    return pedidos

# Configurando a classe de resposta da rota como HTMLResponse para renderizar um html na resposta.
@pedidos_rota.get(path="/listar-html", status_code=201)
async def orders_html(request: Request, session: Session = Depends(get_db_session), usuario: Usuario = Depends(verify_token)):
    """
        Renderiza uma página HTML com a listagem de pedidos do sistema.

        Esta rota é restrita a usuários administradores e retorna os pedidos
        organizados por status (pendentes, finalizados e cancelados),
        utilizando templates HTML para exibição visual.

        Args:
            request (Request): Objeto de requisição do FastAPI necessário
                para renderização do TemplateResponse.
            session (Session): Sessão ativa do SQLAlchemy para acesso ao banco de dados.
            usuario (Usuario): Usuário autenticado obtido a partir do token JWT.

        Raises:
            HTTPException:
                - 401: Caso o usuário autenticado não possua permissão de administrador.

        Returns:
            TemplateResponse: Página HTML renderizada contendo os pedidos
            separados por status.
    """
    # Verificando se o usuario é admin: Apenas admin podem ver TODOS OS PEDIDOS
    if not usuario.admin:
        raise HTTPException(status_code=401, detail="Você não tem permissão para acessar essa funcionalidade.")

    # Pegando todos os pedidos do banco de dados
    query_select_all = select(Pedido)

    # Executa e transforma numa lista para retorno
    pedidos = session.execute(query_select_all).scalars().all()

    # Configurando o retorno em HTM Response usando o Template Response e referenciando o arquivo .html que temos na pasta templates.
    return templates.TemplateResponse(
        "orders.html",
        {
            "request": request,
            "pendentes": [p for p in pedidos if p.status == "PENDENTE"],
            "finalizados": [pf for pf in pedidos if pf.status == "FINALIZADO"],
            "cancelados": [pc for pc in pedidos if pc.status == "CANCELADO"],
        }
    )

@pedidos_rota.post(path="/pedido", status_code=201)
async def create_order(pedido_schema: PedidoSchema, session: Session = Depends(get_db_session), usuario: Usuario = Depends(verify_token)):
    """
        Cria um novo pedido no sistema.

        Recebe os dados do pedido validados pelo schema Pydantic,
        realiza a persistência no banco de dados e retorna uma
        mensagem de confirmação com o identificador do pedido criado.

        Args:
            pedido_schema (PedidoSchema): Dados do pedido validados pelo Pydantic.
            session (Session): Sessão ativa do SQLAlchemy para acesso ao banco de dados.

        Returns:
            dict: Mensagem de sucesso contendo o ID do pedido criado.
    """
    new_order = Pedido(usuario=pedido_schema.usuario, nome_usuario=pedido_schema.nome_usuario)

    if usuario.id != new_order.usuario:
        raise HTTPException(status_code=401, detail="Você não tem autorização para fazer essa modificação")

    session.add(new_order)
    session.commit()

    return {"message": f"Pedido criado com sucesso: {new_order.id}"}

# Criando rota de cancelamento de pedido
@pedidos_rota.post("/pedido/cancelar/{id_pedido}")
async def cancel_order(id_pedido: int, session: Session = Depends(get_db_session), user: Usuario = Depends(verify_token)):
    """
        Cancela um pedido existente no sistema.

        A rota permite o cancelamento de pedidos apenas para usuários
        administradores ou para o próprio usuário que realizou o pedido.
        Caso o pedido não exista ou o usuário não tenha permissão,
        a operação é interrompida.

        Args:
            id_pedido (int): Identificador único do pedido a ser cancelado.
            session (Session): Sessão ativa do SQLAlchemy para acesso ao banco de dados.
            user (Usuario): Usuário autenticado obtido a partir do token JWT.

        Raises:
            HTTPException:
                - 400: Caso o pedido não seja encontrado.
                - 401: Caso o usuário não tenha permissão para cancelar o pedido.

        Returns:
            dict: Mensagem de sucesso e dados do pedido cancelado.
    """
    # Pegando o pedido de acordo com o ID dentro do banco de dados
    pedido = session.query(Pedido).filter(Pedido.id == id_pedido).first()

    # Verificando se o pedido existe ou nao para cancelar.
    if not pedido:
        raise HTTPException(status_code=400, detail="Erro: Pedido não encontrado.")

    # Verificando se o usuario tem permissão para cancelar o pedido
    # Verificar se ele é admin ou se é DONO do pedido que irá ser cancelado.
    if not user.admin and user.id != pedido.usuario:
        raise HTTPException(status_code=401, detail="Você não tem autorização para fazer essa modificação")

    # Alterando o status do pedido para cancelado
    pedido.status = "CANCELADO"

    # Dando commit para o pedido ser salvo como cancelado no banco
    session.commit()

    return {
        "mensagem": f"Pedido Nº {pedido.id} cancelado com sucesso",
        "pedido": pedido
    }


# Criando a rota de adicionar ITENS ao PEDIDO (Uma pizza pode ter sabor mussarela, e etc)
@pedidos_rota.post("/pedido/adicionar-item/{id_pedido}")
async def add_item_order(id_pedido: int, item_schema: ItemPedidoSchema, session: Session = Depends(get_db_session), usuario: Usuario = Depends(verify_token)):
    """
        Adiciona um item a um pedido existente.

        Permite a inclusão de itens (ex.: sabores, produtos ou adicionais)
        em um pedido já criado. A ação é restrita a usuários administradores
        ou ao próprio usuário dono do pedido. Após a inclusão, o valor total
        do pedido é recalculado automaticamente.

        Args:
            id_pedido (int): Identificador único do pedido.
            item_schema (ItemPedidoSchema): Dados do item a ser adicionado ao pedido.
            session (Session): Sessão ativa do SQLAlchemy para acesso ao banco de dados.
            usuario (Usuario): Usuário autenticado obtido a partir do token JWT.

        Raises:
            HTTPException:
                - 400: Caso o pedido não seja encontrado.
                - 401: Caso o usuário não tenha permissão para modificar o pedido.

        Returns:
            dict: Mensagem de sucesso, ID do item criado e valor atualizado do pedido.
    """
    pedido = session.query(Pedido).filter(Pedido.id == id_pedido).first()
    if not pedido:
        raise HTTPException(status_code=400, detail="Pedido não encontrado.")

    if not usuario.admin and usuario.id != pedido.usuario:
        raise HTTPException(status_code=401, detail="Você não tem autorização para fazer essa modificação")

    new_item_order = ItensPedido(nome=item_schema.nome, valor=item_schema.valor, peso=item_schema.peso, quantidade=item_schema.quantidade, sabor=item_schema.sabor, pedido=id_pedido)

    session.add(new_item_order)

    # Atualizando o preço do pedido
    pedido.calculate_price()

    session.commit()

    return {
        "message": "Item adicionado com sucesso!",
        "item_id": new_item_order.id,
        "preco_pedido": pedido.valor
    }

# Rota para remoção de um item de um pedido especifico.
@pedidos_rota.post("/pedido/remover-item/{id_item_pedido}")
async def remove_item_order(id_item_pedido: int, session: Session = Depends(get_db_session), usuario: Usuario = Depends(verify_token)):
    """
        Remove um item específico de um pedido.

        A operação é permitida apenas para usuários administradores
        ou para o próprio usuário dono do pedido. Após a remoção do item,
        o valor total do pedido é recalculado automaticamente.

        Args:
            id_item_pedido (int): Identificador único do item do pedido.
            session (Session): Sessão ativa do SQLAlchemy para acesso ao banco de dados.
            usuario (Usuario): Usuário autenticado obtido a partir do token JWT.

        Raises:
            HTTPException:
                - 400: Caso o item do pedido não seja encontrado.
                - 401: Caso o usuário não tenha permissão para modificar o pedido.

        Returns:
            dict: Mensagem de sucesso, ID do item removido, quantidade
            de itens restantes no pedido e resumo atualizado do pedido.
    """
    # Pegando o item do pedido de acordo com o id do item
    item_pedido = session.query(ItensPedido).filter(ItensPedido.id == id_item_pedido).first()

    # Pegando o pedido para verificar se aquele usuario é dono daquele pedido
    # e para mostrar na resposta os itens que ainda estao no pedido
    pedido = session.query(Pedido).filter(Pedido.id==item_pedido.pedido).first()

    # Se nao existir pedido, retorna erro
    if not item_pedido:
        raise HTTPException(status_code=400, detail="Item do pedido não encontrado!")

    # Se o usuario nao for admin ou o pedido nao for dele, retornar erro para o usuario
    if not usuario.admin and usuario.id != pedido.usuario:
        raise HTTPException(status_code=401, detail="Você não tem autorização para fazer essa modificação")

    # Deletando o pedido no banco
    session.delete(item_pedido)
    # Calculando o novo preço do pedido com a função de calcular o preço
    pedido.calculate_price()
    # Commitando (Executando) as alterações no banco de dados
    session.commit()

    return {
        "message": "Item removido com sucesso!",
        "item_id": item_pedido.id,
        "quantidade_itens_pedido": len(pedido.itens),
        "resumo_pedido": pedido
    }


# Rota para finalização de um pedido
@pedidos_rota.post("/pedido/finalizar/{id_pedido}")
async def finalize_order(id_pedido: int, session: Session = Depends(get_db_session), usuario: Usuario = Depends(verify_token)):
    """
        Finaliza um pedido existente no sistema.

        Altera o status do pedido para "FINALIZADO". A ação é permitida
        apenas para usuários administradores ou para o usuário dono do pedido.

        Args:
            id_pedido (int): Identificador único do pedido a ser finalizado.
            session (Session): Sessão ativa do SQLAlchemy para acesso ao banco de dados.
            usuario (Usuario): Usuário autenticado obtido a partir do token JWT.

        Raises:
            HTTPException:
                - 400: Caso o pedido não seja encontrado.
                - 401: Caso o usuário não tenha permissão para finalizar o pedido.

        Returns:
            dict: Mensagem de sucesso e resumo do pedido finalizado.
    """
    # Pega o pedido especifico
    pedido = session.query(Pedido).filter(id_pedido == Pedido.id).first()

    # Verifica se o pedido não existe
    if not pedido:
        raise HTTPException(status_code=400, detail="Pedido não encontrado.")

    # Verifica se o usuario é admin ou se o pedido é referente aquele usuario
    if not usuario.admin and usuario.id != pedido.usuario:
        raise HTTPException(status_code=401, detail="Você não tem autorização para fazer essa modificação")

    pedido.status = "FINALIZADO"
    session.commit()

    return {
        "message": f"Pedido {pedido.id} finalizado com sucesso!",
        "resumo_pedido": pedido
    }


# Rota para visualizar UM pedido especifico
@pedidos_rota.get("/pedido/{id_pedido}")
async def get_order(id_pedido: int, session: Session = Depends(get_db_session), usuario: Usuario = Depends(verify_token)):
    """
        Retorna os dados de um pedido específico.

        Permite a visualização de um pedido individual apenas para
        usuários administradores ou para o próprio usuário dono do pedido.
        Todos os itens relacionados ao pedido são carregados para compor o resumo.

        Args:
            id_pedido (int): Identificador único do pedido.
            session (Session): Sessão ativa do SQLAlchemy para acesso ao banco de dados.
            usuario (Usuario): Usuário autenticado obtido a partir do token JWT.

        Raises:
            HTTPException:
                - 400: Caso o pedido não seja encontrado.
                - 401: Caso o usuário não tenha permissão para acessar o pedido.

        Returns:
            dict: Informações do pedido, incluindo total de itens e resumo completo.
    """
    # Pega o pedido especificado
    pedido = session.query(Pedido).filter(Pedido.id == id_pedido).first()

    # Verificando se o pedido nao existe
    if not pedido:
        raise HTTPException(status_code=400, detail="O pedido especificado não existe.")

    # Verificando se o usuario não tem permissao para acessar esse pedido
    # admin ou dono do pedido
    if not usuario.admin and usuario.id != pedido.usuario:
        raise HTTPException(status_code=401, detail="Você não tem autorização para fazer essa requisição")

    return {
        "message": "Pedido resgatado",
        "pedido_id": pedido.id,
        "total_itens_pedido": len(pedido.itens), # Fazendo isso para o lazyloaded carregar todos os itens do pedido
        "resumo_pedido": pedido,
    }

# visualizar todos os pedidos de 1 usuario especifico e retornando o schema de response pedidos
# Utilizando o response_model para passar o schema do pedido que deve ser retornado
@pedidos_rota.get(path="pedido/listar-pedidos-usuario/{id_usuario}", response_model=List[ResponsePedidoEspecificoSchema])
async def orders_list_user(id_usuario: int, session: Session = Depends(get_db_session), usuario: Usuario = Depends(verify_token)):
    """
        Lista todos os pedidos de um usuário específico.

        A rota retorna os pedidos vinculados a um usuário informado.
        O acesso é restrito ao próprio usuário ou a administradores.
        O retorno segue o schema definido no response_model.

        Args:
            id_usuario (int): Identificador único do usuário.
            session (Session): Sessão ativa do SQLAlchemy para acesso ao banco de dados.
            usuario (Usuario): Usuário autenticado obtido a partir do token JWT.

        Raises:
            HTTPException:
                - 401: Caso o usuário não tenha permissão para acessar os pedidos.

        Returns:
            List[ResponsePedidoEspecificoSchema]: Lista de pedidos do usuário.
    """
    # Pega todos os pedidos de um usuario especifico
    pedidos = session.query(Pedido).filter(Pedido.usuario == id_usuario).all()

    # Fazendo a verificação se o usuario tem permissão para acessar os pedidos desse ID
    if not usuario.admin and usuario.id != id_usuario:
        raise HTTPException(status_code=401, detail="Você não tem autorização para fazer essa requisição")

    return pedidos

    # Não é possivel utilizar a resposta abaixo porque o Pydantic esta validando com o Schema de pedidos especificos
    # return {
    #     "message": "Pedidos resgatados",
    #     "quantidade_pedidos": len(pedidos),
    #     "pedidos": pedidos
    # }
