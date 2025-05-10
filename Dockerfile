FROM python:3.12-bullseye

WORKDIR /app

RUN ["pip", "install", "poetry"]

COPY poetry.lock .
COPY pyproject.toml .
RUN ["poetry", "install"]

COPY . .

CMD ["poetry", "run", "fastapi", "run", "app.py", "--host", "0.0.0.0", "--workers", "4"]