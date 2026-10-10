# Python 3.12 khớp venv local (3.12.3). Image slim để nhẹ.
FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    # Airflow chạy all-in-one bằng lệnh `airflow standalone`
    AIRFLOW_HOME=/opt/airflow \
    AIRFLOW__CORE__DAGS_FOLDER=/app/dags \
    AIRFLOW__CORE__LOAD_EXAMPLES=False \
    # Để DAGs `from strategies import ...` và `import config` chạy được
    PYTHONPATH=/app

WORKDIR /app

# Cài deps trước để tận dụng layer cache (chỉ build lại khi requirements đổi)
# vnstock/vnai/vnstock_ezchart nằm ở index riêng của Vnstock, không có trên PyPI
COPY requirements.txt .
RUN pip install --upgrade pip && \
    pip install -r requirements.txt \
        --extra-index-url https://vnstocks.com/api/simple

COPY . .

EXPOSE 7860 8080

# Mặc định chạy UI; service airflow trong compose sẽ override command
CMD ["python", "ui/app.py"]
