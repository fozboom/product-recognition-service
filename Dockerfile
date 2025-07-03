FROM python:3.12-slim

WORKDIR /app

COPY pyproject.toml ./

RUN pip install --no-cache-dir .

COPY src/ /app/src/
COPY models/ /app/models/
COPY logging_config.yaml /app/

EXPOSE 8000

CMD ["uvicorn", "src.product_recognition_service.main:app", "--host", "0.0.0.0", "--port", "8000"] 