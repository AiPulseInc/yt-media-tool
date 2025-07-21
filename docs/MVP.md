# 🎧 yt media tool (MVP)

Aplikacja webowa pozwalająca użytkownikowi pobrać ścieżkę audio z filmu YouTube w wybranym formacie i jakości – bez przechowywania pliku na serwerze.

---

## 📌 Funkcjonalność

- Wklejenie linku YouTube
- Podgląd metadanych (tytuł, autor, miniatura)
- Dynamiczne pobieranie dostępnych formatów audio
- Wybór formatu i jakości
- Pobieranie audio bezpośrednio do przeglądarki

---

## 🛠️ Technologie i wymagania

### Backend
- Python 3.11+
- FastAPI
- yt-dlp (do pobierania treści z YouTube)
- ffmpeg (do konwersji formatów audio)
- uvicorn (serwer aplikacji)

### Frontend
- HTML + JavaScript (vanilla)
- Formularz z polem URL, podglądem metadanych i wyborem formatu

---

## ⚙️ Endpointy API

### `GET /metadata?url=<youtube_url>`

Zwraca metadane filmu i dostępne formaty audio.

**Przykładowa odpowiedź:**
```json
{
  "title": "Przykładowy film",
  "uploader": "Kanał YouTube",
  "thumbnail": "https://yt.com/miniatura.jpg",
  "formats": [
    {
      "format_id": "140",
      "ext": "m4a",
      "abr": "128",
      "format_note": "m4a 128kbps"
    }
  ]
}
```

---

### `POST /download`

Pobiera wybrany format i przesyła go do użytkownika jako plik.

**Body JSON:**
```json
{
  "url": "https://youtube.com/...",
  "format_id": "140"
}
```

---

## 🐳 Uruchomienie z Docker

### Wymagania:
- Docker zainstalowany na systemie (https://www.docker.com/)
- Opcjonalnie: Docker Compose (https://docs.docker.com/compose/)

### `Dockerfile`

```dockerfile
FROM python:3.11-slim

RUN apt-get update && apt-get install -y \
    ffmpeg \
    curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
EXPOSE 8000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

---

### `docker-compose.yml`

```yaml
---

## 🧪 Testowanie

Projekt zaleca pokrycie kluczowych funkcji testami automatycznymi:

### Backend
- Testy jednostkowe (np. pytest) dla funkcji pomocniczych i endpointów FastAPI
- Testy integracyjne dla całych ścieżek API (np. testclient FastAPI)
- Przykład uruchomienia: `pytest`

### Frontend
- Proste testy walidacji formularza (np. w przeglądarce lub narzędziem takim jak Jest + jsdom)
- Manualne testy UI (weryfikacja obsługi błędów, poprawności przepływu)

---

## 🔒 Bezpieczeństwo

Aby zapewnić bezpieczeństwo użytkowników i serwera:

- Walidacja wejścia po stronie backendu (np. poprawność i długość URL, dozwolone domeny)
- Ograniczenie rozmiaru pobieranych plików
- Obsługa wyjątków i błędów (np. brak internetu, nieprawidłowy link)
- Zabezpieczenie przed spamem/botami (np. rate limiting, captcha przy publicznym demo)
- Ukrycie wrażliwych informacji w logach

---

## 🚀 Deployment

Aplikację można wdrożyć w środowisku produkcyjnym lub testowym. Przykładowe opcje:

- **Docker**: gotowy `Dockerfile` do budowania obrazu
- **Docker Compose**: szybkie uruchomienie zależności
- **Platformy chmurowe**: Render.com, Fly.io, Heroku, własny VPS
- **Konfiguracja zmiennych środowiskowych** (np. port, debug)
- **Testy działania po wdrożeniu** (sprawdzenie endpointów, pobierania plików)

Przykład uruchomienia lokalnego:
```bash
docker build -t yt-media-tool .
docker run -p 8000:8000 yt-media-tool
```

Po wdrożeniu aplikacja powinna być dostępna pod wybranym adresem URL.

services:
  yt-audio-downloader:
    build: .
    ports:
      - "8000:8000"
    volumes:
      - .:/app
    restart: unless-stopped
```

---

## ✅ Uruchomienie lokalne z Docker

```bash
# 1. Zbuduj obraz
docker build -t yt-audio-downloader .

# 2. Uruchom aplikację
docker run -p 8000:8000 yt-audio-downloader

# lub z docker-compose
docker-compose up --build
```

---

## 📂 Struktura projektu

```
yt_audio_downloader/
├── main.py
├── templates/
│   └── index.html
├── static/
│   ├── style.css
│   └── script.js
├── utils/
│   └── ytdlp_helper.py
├── requirements.txt
├── Dockerfile
└── docker-compose.yml
```

---

## 🔄 Diagram przepływu aplikacji

```
Użytkownik → [GET /metadata] → FastAPI (yt-dlp) → Metadane
        ↓
    [POST /download] → FastAPI (yt-dlp) → strumień audio → Przeglądarka
```

---

## ⚠️ Uwagi prawne

Aplikacja przeznaczona jest wyłącznie do użytku prywatnego. Użytkownik powinien przestrzegać warunków korzystania z YouTube i praw autorskich.

---

## 📧 Kontakt

Twórca: [Twoje Imię lub alias]  
Wersja MVP: lipiec 2025