# Imagem base com Python 3.12 slim
FROM python:3.12-slim

# Diretório de trabalho dentro do container
WORKDIR /app

# Copia primeiro os arquivos de dependência para aproveitar o cache de camadas
COPY pyproject.toml README.md ./

# Instala o projeto e suas dependências
RUN pip install --no-cache-dir -e .

# Copia o restante do código-fonte
COPY src ./src
COPY scripts ./scripts
COPY data ./data

# Porta padrão da API
EXPOSE 8000

# Comando padrão: sobe a API FastAPI
CMD ["python", "-m", "src.cli", "serve", "--port", "8000"]
