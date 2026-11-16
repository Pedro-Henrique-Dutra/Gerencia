FROM python:3.12-slim-bookworm

# Configurações do Python
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PIP_NO_CACHE_DIR=1

# Criação de usuário sem privilégios
RUN groupadd --gid 1000 appuser && \
    useradd \
      --uid 1000 \
      --gid 1000 \
      --create-home \
      --shell /usr/sbin/nologin \
      appuser && \
    mkdir -p /app && \
    chown -R appuser:appuser /app

WORKDIR /app

# Instala dependências
COPY requirements.txt /tmp/requirements.txt

RUN pip install --no-cache-dir \
    -r /tmp/requirements.txt

# Usuário padrão
USER appuser

WORKDIR /app

EXPOSE 5000

CMD ["flask", "--app", "main", "run", "--host=0.0.0.0", "--port=5000", "--debug"]