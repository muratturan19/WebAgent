#!/bin/bash

# 1. Gerekli Python paketlerini yükle
pip install --upgrade pip
pip install -r WebSailor/requirements.txt

# 2. (Varsa) Model dosyalarını kontrol et/yükle
# Örnek: HuggingFace veya lokal model path ayarı
# export MODEL_PATH="D:/Mira/WebSailor-3B/"
# (model zaten indirildiyse bu adımı geçebilirsin)

# 3. (Varsa) Ortam değişkenlerini ayarla
# export SERPER_API_KEY="senin_serper_api_key"
# export GOOGLE_SEARCH_KEY="senin_google_api_key"

# 4. Kullanıcıya bilgi ver
echo "Kurulum tamamlandı! WebSailor çalışmaya hazır 🚀"
