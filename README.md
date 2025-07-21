# yt media tool

Minimalny MVP do pobierania audio z YouTube przez FastAPI.

## Opis Projektu

`yt-media-tool` to proste narzędzie webowe oparte na FastAPI, które umożliwia pobieranie metadanych z filmów YouTube oraz ekstrakcję i pobieranie ścieżek audio. Projekt został zbudowany z myślą o łatwości uruchomienia i rozbudowy, wykorzystując konteneryzację Docker.

## Funkcjonalności

-   **Pobieranie metadanych:** Umożliwia pobranie tytułu, autora, miniatury oraz dostępnych formatów audio dla danego filmu YouTube.
-   **Pobieranie ścieżki audio:** Pozwala na ekstrakcję i pobranie ścieżki audio z filmu YouTube w wybranym formacie.
-   **Prosty frontend:** Intuicyjny interfejs użytkownika do interakcji z API.
-   **Walidacja URL:** Weryfikacja poprawności linków YouTube.
-   **Wskaźniki ładowania:** Informacje zwrotne dla użytkownika podczas operacji.
-   **Limity:** Ograniczenia rozmiaru pobieranych plików i częstości zapytań (rate limiting).

## Uruchomienie Projektu

Projekt można uruchomić na dwa sposoby: lokalnie (bez Docker Compose) lub za pomocą Docker Compose.

### Uruchomienie Lokalnie (bez Docker Compose)

1.  **Upewnij się, że masz zainstalowany Python 3.11+ i `pip`.**

2.  **Sklonuj repozytorium:**
    ```bash
    git clone https://github.com/your-username/yt-media-tool.git
    cd yt-media-tool
    ```

3.  **Zainstaluj zależności:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Uruchom aplikację:**
    ```bash
    python run.py
    ```
    Aplikacja domyślnie uruchomi się na porcie `8000`. Możesz zmienić port, ustawiając zmienną środowiskową `PORT` (np. `PORT=5000 python run.py`).

### Uruchomienie za pomocą Docker Compose

Najprostszym sposobem na uruchomienie projektu wraz z usługą Redis jest użycie Docker Compose.

1.  **Upewnij się, że masz zainstalowany Docker i Docker Compose.**

2.  **Sklonuj repozytorium:**
    ```bash
    git clone https://github.com/your-username/yt-media-tool.git
    cd yt-media-tool
    ```

3.  **Zbuduj i uruchom kontenery:**
    ```bash
    docker-compose up --build -d
    ```
    Flaga `--build` zbuduje obrazy Docker (jeśli jeszcze ich nie ma lub jeśli zmieniły się zależności), a `-d` uruchomi kontenery w tle.

4.  **Dostęp do aplikacji:**
    Aplikacja będzie dostępna pod adresem: `http://localhost:8000` (lub na porcie ustawionym w `docker-compose.yml`).

## Uruchomienie Testów

Testy jednostkowe dla backendu można uruchomić wewnątrz kontenera Docker.

1.  **Upewnij się, że kontenery są uruchomione** (patrz sekcja Uruchomienie Projektu).

2.  **Wykonaj testy:**
    ```bash
    docker-compose exec -e PYTHONPATH=/app yt-media-tool pytest
    ```
    Oczekiwany wynik to pomyślne przejście wszystkich testów.

### Testy Frontendowe (JavaScript)

Ze względu na specyfikę środowiska CLI, w którym rozwijany jest ten projekt, kompleksowe testy jednostkowe JavaScript (frontendu) nie są uruchamiane automatycznie. W projekcie znajduje się plik `tests/test_script.js`, który służy jako placeholder i zawiera komentarze wyjaśniające, jak można by podejść do testowania frontendowego w bardziej rozbudowanym środowisku (np. z użyciem Jest lub Playwright).

## Struktura Projektu

```
your-project-root/
├── docker-compose.yml        # Konfiguracja usług Docker
├── Dockerfile                # Definicja obrazu Docker dla aplikacji
├── main.py                   # Główna aplikacja FastAPI i definicje endpointów
├── requirements.txt          # Zależności Pythona
├── static/                   # Pliki statyczne (CSS, JavaScript, favicon)
│   ├── .gitkeep
│   ├── script.js
│   ├── style.css
│   └── favicon.ico
├── templates/                # Szablony HTML (Jinja2)
│   ├── .gitkeep
│   ├── index.html
│   └── __init__.py
└── utils/                    # Pomocnicze moduły Pythona
    ├── .gitkeep
    ├── __init__.py
    └── ytdlp_helper.py       # Logika interakcji z yt-dlp
```

## Endpointy API

-   **`GET /ping`**
    -   **Opis:** Prosty endpoint do sprawdzenia statusu API.
    -   **Odpowiedź:** `{"status": "ok"}`

-   **`GET /metadata?url=<youtube_url>`**
    -   **Opis:** Pobiera metadane dla podanego URL filmu YouTube.
    -   **Parametry:**
        -   `url` (query): Pełny URL filmu YouTube.
    -   **Odpowiedź (sukces):** JSON zawierający `title`, `author`, `thumbnail` i `formats` (lista dostępnych formatów audio).
    -   **Odpowiedź (błąd):** JSON zawierający `{"error": "Komunikat błędu"}`

-   **`POST /download`**
    -   **Opis:** Rozpoczyna pobieranie i strumieniowanie ścieżki audio dla podanego URL i formatu. Opcjonalnie konwertuje do MP3.
    -   **Ciało żądania (JSON):**
        ```json
        {
            "url": "<youtube_url>",
            "format_id": "<selected_format_id>",
            "convert_to_mp3": true/false  // Opcjonalnie, domyślnie false
        }
        ```
    -   **`format_id`:** Unikalny identyfikator formatu audio, uzyskany z endpointu `/metadata`.
    -   **Odpowiedź:** Strumień audio (plik w oryginalnym formacie lub MP3) z nagłówkiem `Content-Disposition` do pobrania pliku.

## Wdrażanie (Deployment)

Projekt jest skonteneryzowany za pomocą Docker, co ułatwia wdrożenie na różnych platformach. Poniżej przedstawiono ogólne kroki wdrożenia.

### Zmienne Środowiskowe

Obecnie aplikacja nie wymaga żadnych specyficznych zmiennych środowiskowych. Adres serwera Redis jest domyślnie ustawiony na `redis` (nazwa usługi w `docker-compose.yml`). W przypadku wdrożenia, gdzie Redis jest hostowany zewnętrznie, konieczne może być skonfigurowanie zmiennej środowiskowej dla adresu Redis w `main.py`.

### Przykładowe Platformy Wdrożeniowe

#### Render.com / Fly.io / Heroku

Te platformy oferują łatwe wdrożenie aplikacji Dockerowych. Zazwyczaj proces wygląda następująco:

1.  **Połącz swoje repozytorium Git** z wybraną platformą.
2.  **Skonfiguruj usługę:**
    *   Wybierz typ usługi (np. Web Service).
    *   Wskaż `Dockerfile` jako źródło kompilacji.
    *   Ustaw port aplikacji na `8000` (zgodnie z `EXPOSE` w `Dockerfile`).
    *   Dodaj usługę Redis (jeśli platforma oferuje zarządzane usługi Redis) i zaktualizuj `main.py` o odpowiednie zmienne środowiskowe do połączenia z Redis.
3.  **Wdróż (Deploy):** Platforma automatycznie zbuduje obraz Docker i uruchomi aplikację.

#### Własny Serwer (VPS)

Możesz wdrożyć aplikację na własnym serwerze wirtualnym (VPS) z zainstalowanym Dockerem i Docker Compose.

1.  **Sklonuj repozytorium** na swój serwer.
2.  **Uruchom Docker Compose** w katalogu projektu:
    ```bash
    docker-compose up -d
    ```
3.  **Skonfiguruj serwer proxy** (np. Nginx lub Caddy) do przekierowania ruchu z portu 80/443 na port 8000 kontenera `yt-media-tool`.

