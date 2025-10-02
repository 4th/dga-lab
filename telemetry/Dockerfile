FROM python:3.11-slim
WORKDIR /app

# install deps from root context
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

# copy shared code and this service
COPY common /app/common
COPY telemetry /app/telemetry

ENV PYTHONPATH=/app
EXPOSE 8085
CMD ["uvicorn", "telemetry.app:app", "--host", "0.0.0.0", "--port", "8085"]
