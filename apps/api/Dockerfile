# Build context is the repository root (see Railway service settings), because
# the seed endpoint reads db/seed.sql from outside apps/api.
# Keep this in step with the Python used for local development (3.11.x).
FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

# app/seed.py resolves the repo root as four levels above itself,
# so keep the layout /srv/apps/api/app/seed.py and /srv/db/seed.sql.
WORKDIR /srv/apps/api

COPY apps/api/requirements.txt ./
RUN pip install -r requirements.txt

COPY apps/api/ ./
COPY db/ /srv/db/

EXPOSE 8080
CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8080}"]
