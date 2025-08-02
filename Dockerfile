FROM nvidia/cuda:12.1.1-cudnn8-runtime-ubuntu22.04

# Çalışma dizini
WORKDIR /app

# Python ve temel bağımlılıkların kurulumu
RUN apt-get update && apt-get install -y \
    python3 python3-pip git curl build-essential \
    && rm -rf /var/lib/apt/lists/*

# Proje bağımlılıkları
COPY WebSailor/requirements.txt WebSailor/requirements.txt
RUN pip3 install --upgrade pip \
    && pip3 install --no-cache-dir -r WebSailor/requirements.txt

# Kodların kopyalanması
COPY . .

# Varsayılan model yolu
ENV MODEL_PATH=/models
RUN mkdir -p /models /app/output

# Gerekli portlar
EXPOSE 6001 6002

CMD ["bash"]
