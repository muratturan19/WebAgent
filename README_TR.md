# WebAgent Docker Kurulumu

Bu proje, Tongyi Lab tarafından geliştirilen **WebAgent**'in Docker üzerinde GPU desteğiyle çalıştırılmasını sağlar.

## Önkoşullar

- NVIDIA GPU'lu bir makine.
- Docker ve [NVIDIA Container Toolkit](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/install-guide.html) kurulu olmalı.
- WebSailor-3B model dosyalarının bulunduğu klasör (örnek: `D:/Mira/WebSailor-3B`).

## Ortam Değişkenleri

1. `.env.example` dosyasını `.env` olarak kopyalayın.
2. Aşağıdaki anahtarları doldurun:
   - `JINA_API_KEYS`, `GOOGLE_SEARCH_KEY`, `SEARCH_API_URL` gibi API bilgileri.
   - `SUMMARY_MODEL_PATH`: Özetleme modeli için yol. Gerekirse bu modelin bulunduğu dizini de volume olarak bağlayın.

## Docker İmajını Oluşturma

```bash
docker build -t webagent:latest .
```

## Konteyneri Çalıştırma

Model dosyalarının bulunduğu dizini `/models` olarak bağlayın ve `.env` değerlerini içeri aktarın:

```bash
docker run --gpus all --rm \
  --env-file .env \
  -v D:/Mira/WebSailor-3B:/models \
  webagent:latest \
  bash WebSailor/src/run.sh sahibinden /app/output
```

- `sahibinden` yerine aşağıdaki veri setlerinden birini kullanabilirsiniz: `gaia`, `browsecomp_zh`, `browsecomp_en`, `xbench-deepsearch`, `sahibinden`.
- Çıktıları host üzerinde görmek için ayrıca `-v $(pwd)/output:/app/output` parametresi ekleyebilirsiniz.

Etkileşimli bir kabuk açmak için:

```bash
docker run --gpus all --rm \
  --env-file .env \
  -v D:/Mira/WebSailor-3B:/models \
  -it webagent:latest bash
```

## Notlar

- Varsayılan model yolu `/models` olarak tanımlıdır (`MODEL_PATH`). Farklı bir yol kullanmak isterseniz `-e MODEL_PATH=/farkli/yol` parametresi ekleyin.
- `.env` dosyasını `--env-file` yerine volume olarak bağlamak isterseniz: `-v $(pwd)/.env:/app/.env`.
