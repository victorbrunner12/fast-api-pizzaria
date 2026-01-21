# Arquivo de schemas é usado com o Pydantic para definir oque cada item e classe necessita para criação de usuario e outras adições
from pydantic import BaseModel
from typing import Optional, List

# Esquema do Pydantic para o Usuario, qualquer interação tem que seguir esse esquema, principalmente adição de novos.
class UsuarioSchema(BaseModel):
    nome: str
    email: str
    senha: str
    telefone: str
    sexo: Optional[str]
    admin: Optional[bool]
    ativo : Optional[bool]

    # Criando a classe Config para dizer que essa classe de Schema sera uma classe ORM e nao um dicionario PY
    class Config:
        from_attributes = True

# Esquema para pedidos
class PedidoSchema(BaseModel):
    usuario: int
    nome_usuario: str
    valor: Optional[float]
    status: Optional[str]

    class Config:
        from_attributes = True


# Esquema para login na API
class LoginSchema(BaseModel):
    email: str
    senha: str

    class Config:
        from_attributes = True


class ItemPedidoSchema(BaseModel):
    nome: str
    valor: float
    peso: float
    quantidade: int
    sabor: str

    class Config:
        from_attributes = True


# Schema para resposta da requisiçaõ para a rota de orders_list_user.
class ResponsePedidoEspecificoSchema(BaseModel):
    id: int
    status: str
    nome_usuario: str
    valor: float
    itens: List[ItemPedidoSchema]

    class Config:
        from_attributes = True
