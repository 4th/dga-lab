FROM python:3.11-slim
WORKDIR /app

# install deps from root context
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

# copy shared code and this service
COPY common /app/common
COPY gateway /app/gateway

ENV PYTHONPATH=/app
EXPOSE 8080
CMD ["uvicorn", "gateway.app:app", "--host", "0.0.0.0", "--port", "8080"]
