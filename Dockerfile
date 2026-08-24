# Image de preproduction Concorde. La base est prechargee avant la demonstration.
FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /opt/concorde

# Premiere livraison autonome : meme graphe de dependances que la CI.
COPY pyproject.toml README.md ./
COPY src ./src
COPY api ./api
COPY app ./app
RUN python -m pip install --upgrade pip && python -m pip install .

# Le code source est prioritaire sur la roue installee pour que PROJECT_ROOT
# reste /opt/concorde et que les artefacts copies soient bien resolus.
ENV PYTHONPATH=/opt/concorde:/opt/concorde/src

# Demarrage sans collecte, entrainement ni telechargement.
COPY data/samples ./data/samples
COPY data/processed ./data/processed
COPY models ./models
COPY scripts/run_demo_container.sh ./scripts/run_demo_container.sh

RUN useradd --create-home --uid 10001 concorde \
    && chown -R concorde:concorde /opt/concorde \
    && chmod 755 ./scripts/run_demo_container.sh

USER concorde
EXPOSE 8000
ENTRYPOINT ["./scripts/run_demo_container.sh"]
