from sqlalchemy import create_engine, Column, String, Boolean, Integer, ForeignKey, Float
from sqlalchemy.orm import declarative_base, relationship

# Criando a engine do banco para se comunicar
db = create_engine("sqlite:///databases/banco.db", connect_args={"check_same_thread": False})

# Criando uma base do banco para que as classes e suas funções consigam executar SQL no banco informado.
Base = declarative_base()

# Criando uma classe com o parametro "Base" que é para indicar que essa classe PODE executar comandos SQL no banco. (Usuari é uma sub classe do Base agora)
class Usuario(Base):
    # Definindo o nome da tabela dessa classe no banco de dados
    __tablename__ = "users"

    # Definindo as configurações dos campos como: nomes, tipos de dados, se podem ser nulos ou nao, se sao chave primaria, se são autoincrementaveis
    id = Column(name="id", type_=Integer, nullable=False, primary_key=True, autoincrement=True)
    nome = Column(name="nome", type_=String, nullable=False)
    email = Column(name="email", type_=String, nullable=False)
    senha = Column(name="senha", type_=String, nullable=False)
    ativo = Column(name="ativo", type_=Boolean, nullable=False)
    admin = Column(name="admin", type_=Boolean, default=False)
    telefone = Column(name="telefone", type_=String)
    sexo = Column(name="sexo", type_=String, default="Não informado")

    # Criando uma função de inicialização passando os parametros que sua API espera receber.
    def __init__(self, nome, email, senha, telefone, sexo, admin=False, ativo=True):
        self.nome = nome
        self.email = email
        self.senha = senha
        self.telefone = telefone
        self.sexo = sexo
        self.admin = admin
        self.ativo = ativo


class Pedido(Base):
    __tablename__="orders"

    id = Column(name="id", type_=Integer, primary_key=True, autoincrement=True, nullable=False)
    status = Column(type_=String, name="status")
    usuario = Column(ForeignKey("users.id"), name="usuario", type_=Integer, nullable=False)
    nome_usuario = Column(type_=String, name="nome_usuario", nullable=False)
    valor = Column(name="valor", type_=Float, nullable=False)

    # Criando um campo de Relationship para relação dessa tabela com a tabela de itens,
    # tendo em vista que temos que adicionar os itens do pedido a esse e seu devido valor
    # O argument é o nome da classe que vc quer ter a relação.
    # O cascade é uma query para quando um item for excluido do banco, automaticamente ele é excluido do pedido referente
    itens = relationship(argument="ItensPedido", cascade="all, delete")

    def __init__(self, usuario, nome_usuario, valor=0, status="PENDENTE"):
        self.status = status
        self.usuario = usuario
        self.nome_usuario = nome_usuario
        self.valor = valor

    # Criando a função que vai calcular o preço do pedido de acordo com os itens dele
    def calculate_price(self):
        # Percorre todos os itens do pedido
        # Soma todos os precos de todos os pedidos
        # adiciona no campo VALOR o preço final
        self.valor = sum(item.valor * item.quantidade for item in self.itens)

class ItensPedido(Base):
    __tablename__="order_items"

    id = Column(name="id", type_=Integer, nullable=False, autoincrement=True, primary_key=True)
    nome = Column(name="nome", type_=String, nullable=False)
    valor = Column(name="valor", type_=Float, nullable=False)
    peso = Column(name="peso", type_=Float, nullable=False)
    quantidade = Column(name="quantidade", type_=Integer, nullable=False)
    sabor = Column(name="sabor", type_=String, nullable=False)
    pedido = Column(ForeignKey("orders.id"), name="pedido", type_=Integer)

    def __init__(self, nome, valor, peso, quantidade, sabor, pedido):
        self.nome = nome
        self.valor = valor
        self.peso = peso
        self.quantidade = quantidade
        self.sabor = sabor
        self.pedido = pedido



# Processo de MIGRAÇÃO DO BANCO EM CLASSES PARA BANCO DE DADOS.

# Criando a pasta alembic e arquivo alembic.ini
# alembic init alembic

# Dentro do alembic.ini, voce tem que definir a url do banco de dados que está usando na variavel sqlalchemy.url.
#sqlalchemy.url = sqlite:///banco.db

# Arquivo env.py dentro da pasta alembic.
# Esse arquivo env.py precisa da chamada da variavel Base dentro dele
# mas ele esta dentro de uma pasta e a variavel Base está fora,
# entao pra chamar é necessario o comando abaixo:
# sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# Para realizar uma migração para criar o banco de dados e atualiza-lo é necessario rodar:
# alembic revision --autogenerate -m "Initial Migration"

# Caso o processo de migração de erro no meio do caminho:
# Excluir o arquivo de migração criado para nao ser executado de novo.
# Corrigir o erro e executar o processo de migração novamente.
    # Criar o arquivo de migração que será executado: alembic revision --autogenerate -m "msg"
    # Executar o comando que roda o arquivo de migração para ser executado:
        # alembic upgrade head
