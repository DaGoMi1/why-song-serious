FROM python:3.11-slim

WORKDIR /app

COPY ./requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY ./inference/src /app/src
COPY ./inference/service_assets /app/service_assets

ENV PYTHONPATH="/app:/app/src"

EXPOSE 8001

CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8001"]