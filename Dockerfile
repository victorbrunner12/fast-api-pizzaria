FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Dependências do sistema
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Instala Poetry
RUN pip install poetry

# Copia arquivos de dependência
COPY pyproject.toml poetry.lock ./

# Configura Poetry para NÃO criar venv dentro do container
RUN poetry config virtualenvs.create false

# Instala dependências
RUN poetry install --no-interaction --no-ansi --no-root

# Copia o restante do código
COPY . .

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
