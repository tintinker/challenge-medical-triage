FROM python:3.12-slim

WORKDIR /app

RUN pip install uv

COPY pyproject.toml .
RUN uv sync --no-dev

CMD ["uv", "run", "python", "medical_triage.py"]
