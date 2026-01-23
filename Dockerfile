#-----------frontend stage-------------

FROM node:20-alpine AS frontend


WORKDIR /app/
RUN npm install -g npm@11.6.1
COPY frontend/package.json frontend/package-lock.json ./frontend/

RUN cd frontend && npm install

COPY frontend/src ./frontend/src
COPY frontend/public ./frontend/public

RUN cd frontend && npm run build  # produces /app/build


#------------backend stage----------

FROM python:3.13-slim AS backend

WORKDIR /app/

ENV PATH="/root/.local/bin:$PATH" \
    PYTHONUNBUFFERED=1 \
    POETRY_VIRTUALENVS_CREATE=false \
    POETRY_NO_INTERACTION=1

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libproj-dev libgdal-dev libgeos-dev proj-bin gdal-bin curl highs \
    && rm -rf /var/lib/apt/lists/*


ENV PROJ_LIB=/usr/share/proj

# Install Poetry
RUN curl -sSL https://install.python-poetry.org | python3 -


COPY backend/pyproject.toml backend/poetry.lock ./
RUN poetry install --no-root

COPY backend ./backend

COPY --from=frontend /app/frontend/build ./frontend/build

EXPOSE 5000

# Default command
CMD ["poetry", "run", "uvicorn", "backend.run:app", "--host", "0.0.0.0", "--port", "5000"]
