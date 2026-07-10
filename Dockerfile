FROM rhysd/actionlint:1.7.7 AS actionlint

FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /workspace

COPY --from=actionlint /usr/local/bin/actionlint /usr/local/bin/actionlint

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        bash \
        ca-certificates \
        git \
        rsync \
    && rm -rf /var/lib/apt/lists/*

COPY pyproject.toml README.md LICENSE ./
COPY tbot223_base ./tbot223_base
COPY tests ./tests

RUN python -m pip install --upgrade pip \
    && python -m pip install -e ".[test,type,release]" \
    && git config --global --add safe.directory /workspace

COPY . .

ENTRYPOINT ["bash", "scripts/check-release-readiness.sh"]
CMD ["v1.0.0rc2"]
