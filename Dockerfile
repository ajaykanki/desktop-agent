# Use a Python 3.13 base image with slim
FROM python:3.13-slim

# Set work directory
WORKDIR /app

# Install uv package manager
RUN pip install uv

COPY . .

# Install dependencies using uv
RUN uv sync

# Expose port for API service
EXPOSE 8000

# Default command - can be overridden by docker-compose
CMD ["uv", "run", "fastapi", "run", "app/main.py", "--host", "0.0.0.0", "--port", "8000"]
