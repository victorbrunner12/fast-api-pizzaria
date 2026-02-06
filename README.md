# 🍕 Pizzaria API — FastAPI

API REST desenvolvida com **FastAPI** para gerenciamento de pedidos de uma pizzaria.

O sistema permite:
- Autenticação JWT
- Controle de usuários (admin e cliente)
- Criação e gerenciamento de pedidos
- Adição e remoção de itens em pedidos
- Finalização e cancelamento de pedidos
- Visualização de pedidos em HTML via templates Jinja2

---

## Tecnologias utilizadas

- Python 3.10+
- FastAPI
- SQLAlchemy
- Alembic
- Pydantic
- JWT (python-jose)
- Bcrypt (passlib)
- Jinja2
- Docker & Docker Compose
- Poetry (gerenciamento de dependências)

---

## Estrutura do projeto

```bash
PizzariaFastAPI2/
├─ alembic/                 # Migrations do banco de dados
├─ core/                    # Segurança, JWT, etc
├─ databases/               # Banco SQLite (ou outro, conforme configuração)
├─ Documentation/           # README.md e documentação
├─ models/                  # models.py onde ficam os modelos de banco de dados
├─ routes/                  # Rotas da API
├─ schemas/                 # Schemas para validação com Pydantic
├─ templates/               # HTML templates
├─ .env.example             # Exemplo de variáveis de ambiente
├─ alembic.ini              # Arquivo ini do alembic (Configs alembic)
├─ dependencies.py          # Arquivo com as dependencias do projeto e funções
├─ docker-compose.yml       # Docker Compose
├─ Dockerfile               # Dockerfile
├─ main.py                  # Arquivo principal que inicia a API
├─ pyproject.toml           # Poetry dependencies
├─ poetry.lock              # Poetry lock file
└─ requirements.txt         # Dependências (opcional)
```

---

## Rodando o projeto com Docker (recomendado)

### Pré-requisitos

- Docker e Docker Compose (recomendado)
- Python 3.10+ e Poetry (para rodar sem Docker)

---

1. Clone o repositório:

```bash
git clone https://github.com/SEU_USUARIO/pizzaria-fastapi.git
cd pizzaria-fastapi
```

2. Crie o arquivo .env a partir do exemplo:

```bash
cp .env.example .env   # Cria o arquivo .env a partir do exemplo
```

3. Suba o docker com o usuario padrao e banco criados:

```bash
docker-compose up --build
```

## URLs da API

- API base: http://localhost:8000
- Documentação Swagger: http://localhost:8000/docs
- Redoc: http://localhost:8000/redoc

---

## Usuário padrão

O usuário admin padrão é criado automaticamente usando as variáveis do .env.
Exemplo de .env.example:

```bash
ADMIN_EMAIL=admin@example.com
ADMIN_PASSWORD=123456
```
#### OBS: Você pode alterar essas variáveis antes de rodar o container para criar seu próprio usuário admin.

---

## Banco de dados e migrations

O projeto utiliza Alembic para versionamento do banco.

Ao subir o Docker, o banco e as migrations serão aplicadas automaticamente.

Para aplicar manualmente:

```bash
docker-compose exec api alembic upgrade head
```
---

## Parar a aplicação

```bash
docker-compose down       # Para os containers
docker-compose down -v    # Para e remove volumes (incluindo banco de dados)
```

---

## Rodar sem Docker (opcional)

### Pré-requisitos

- Python 3.10+
- Poetry
- 
```bash
git clone https://github.com/SEU_USUARIO/pizzaria-fastapi.git
cd pizzaria-fastapi
cp .env.example .env
poetry install
poetry run uvicorn main:app --reload
```
- API base: http://localhost:8000
- Documentação: http://localhost:8000/docs

---

## Observações

- As migrations do Alembic estão incluídas no repositório.

- Banco de dados não é versionado, mas é criado automaticamente.

- Usuários e senhas podem ser configurados via .env.

- Projeto totalmente portátil entre Windows, Linux e Mac.

# 🏷 Licença

## Projeto livre para uso educacional.
