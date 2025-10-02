FROM python:3.11-slim
WORKDIR /app

# install deps from root context
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

# copy shared code and this service
COPY common /app/common
COPY feature-extractor /app/feature-extractor

ENV PYTHONPATH=/app
EXPOSE 8082
CMD ["uvicorn", "feature-extractor.app:app", "--host", "0.0.0.0", "--port", "8082"]
