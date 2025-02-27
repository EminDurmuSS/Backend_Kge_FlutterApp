FROM python:3.12-slim

# Uygulama klasörünü belirtiyoruz
WORKDIR /app

# Gerekli Python paketlerini yüklüyoruz
COPY requirements.txt .
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Klasörleri ve dosyaları kopyalıyoruz
COPY core/ core/
COPY models/ models/
COPY routers/ routers/
COPY data/ data/
COPY embedding/ embedding/
COPY main.py .

# Uygulamanın dinleyeceği port
EXPOSE 8000

# Uygulama çalıştırma komutu
CMD ["gunicorn", "-k", "uvicorn.workers.UvicornWorker", "--bind", "0.0.0.0:8000", "--timeout", "1000",  "--keep-alive", "1000", "--preload", "main:app"]
