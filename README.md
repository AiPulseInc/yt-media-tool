# yt media tool

Minimalny MVP do pobierania audio z YouTube przez FastAPI.

## Opis Projektu

`yt-media-tool` to proste narzędzie webowe oparte na FastAPI, które umożliwia pobieranie metadanych z filmów YouTube oraz ekstrakcję i pobieranie ścieżek audio. Projekt został zbudowany z myślą o łatwości uruchomienia i rozbudowy, wykorzystując konteneryzację Docker. Aplikacja strumieniuje plik do przeglądarki (bez trwałego zapisu na serwerze) i prezentuje postęp (pobieranie/konwersja) w UI.

## Funkcjonalności

- **Pobieranie metadanych:** Umożliwia pobranie tytułu, autora, miniatury oraz dostępnych formatów audio dla danego filmu YouTube.
- **Pobieranie ścieżki audio:** Pozwala na ekstrakcję i pobranie ścieżki audio z filmu YouTube w wybranym formacie.
- **Prosty frontend:** Intuicyjny interfejs użytkownika do interakcji z API.
- **Walidacja URL:** Weryfikacja poprawności linków YouTube.
- **Wskaźniki postępu:** Modal pokazujący etapy (inicjowanie → pobieranie → konwersja → przygotowanie → zakończenie).
- **Limity:** Ograniczenia rozmiaru pobieranych plików i częstości zapytań (rate limiting).

## Uruchomienie Projektu

Projekt można uruchomić na dwa sposoby: lokalnie (bez Docker Compose) lub za pomocą Docker Compose.

### Uruchomienie Lokalnie (bez Docker Compose)

1.  **Upewnij się, że masz zainstalowany Python 3.11+ i `pip`.** Dodatkowo do konwersji MP3 wymagany jest `ffmpeg`.
    - macOS (Homebrew): `brew install ffmpeg`

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
    python3.13 run.py
    ```
    Aplikacja domyślnie uruchomi się na porcie `8000`. Możesz zmienić port, ustawiając zmienną środowiskową `PORT` (np. `PORT=5000 python run.py`). Tryb przeładowywania kodu (dev reload) można włączyć przez `RELOAD=true`.

### Uruchomienie za pomocą Docker Compose

Najprostszym sposobem na uruchomienie projektu jest użycie Docker Compose.

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
    Aplikacja będzie dostępna pod adresem: `http://localhost:8000` (port zgodny z `EXPOSE 8000` w `Dockerfile`).

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
├── Dockerfile                # Definicja obrazu Docker dla aplikacji (EXPOSE 8000)
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

- **`GET /ping`**

  - **Opis:** Prosty endpoint do sprawdzenia statusu API.
  - **Odpowiedź:** `{"status": "ok"}`

- **`GET /metadata?url=<youtube_url>`**

  - **Opis:** Pobiera metadane dla podanego URL filmu YouTube.
  - **Parametry:**
    - `url` (query): Pełny URL filmu YouTube.
  - **Odpowiedź (sukces):** JSON zawierający `title`, `author`, `thumbnail` i `formats` (lista dostępnych formatów audio).
  - **Odpowiedź (błąd):** JSON zawierający `{"error": "Komunikat błędu"}`

- **`POST /download`**
  - **Opis:** Rozpoczyna pobieranie i strumieniowanie ścieżki audio dla podanego URL i formatu. Opcjonalnie konwertuje do MP3.
  - **Ciało żądania (JSON):**
    ```json
    {
        "url": "<youtube_url>",
        "format_id": "<selected_format_id>",
        "convert_to_mp3": true/false  // Opcjonalnie, domyślnie false
    }
    ```
  - **`format_id`:** Unikalny identyfikator formatu audio, uzyskany z endpointu `/metadata`.
  - **Odpowiedź:** Strumień audio (plik w oryginalnym formacie lub MP3) z nagłówkiem `Content-Disposition` do pobrania pliku.

- **`GET /progress?task_id=<id>`**
  - **Opis:** Zwraca bieżący etap procesu dla zadania o danym `task_id` (np. `downloading`, `converting`, `completed`). Wykorzystywane w UI do wyświetlania postępu.

## Wdrażanie (Deployment)

Projekt jest skonteneryzowany za pomocą Docker, co ułatwia wdrożenie na różnych platformach. Poniżej przedstawiono ogólne kroki wdrożenia.

### Zmienne Środowiskowe

- `PORT` — port nasłuchu (ustawiany automatycznie na platformach jak Railway/Render)
- `RELOAD` — `true/false` (domyślnie `false`), włącza tryb reload w dev

### Przykładowe Platformy Wdrożeniowe

#### Railway / Render.com / Fly.io / Heroku

Te platformy oferują łatwe wdrożenie aplikacji Dockerowych. Zazwyczaj proces wygląda następująco:

1.  **Połącz swoje repozytorium Git** z wybraną platformą.
2.  **Skonfiguruj usługę:**
    - Wybierz typ usługi (np. Web Service).
    - Wskaż `Dockerfile` jako źródło kompilacji.
    - Ustaw port aplikacji na `8000` (zgodnie z `EXPOSE 8000` w `Dockerfile`), większość platform ustawia `PORT` automatycznie.
3.  **Wdróż (Deploy):** Platforma automatycznie zbuduje obraz Docker i uruchomi aplikację.

#### Własny Serwer (VPS)

Możesz wdrożyć aplikację na własnym serwerze wirtualnym (VPS) z zainstalowanym Dockerem i Docker Compose.

1.  **Sklonuj repozytorium** na swój serwer.
2.  **Uruchom Docker Compose** w katalogu projektu:
    ```bash
    docker-compose up -d
    ```
3.  **Skonfiguruj serwer proxy** (np. Nginx lub Caddy) do przekierowania ruchu z portu 80/443 na port 8000 kontenera `yt-media-tool`.

## Rollback / Recovery

W razie potrzeby szybkiego wycofania zmian masz dwie ścieżki:

1) Git – zachowanie historii liniowej (rekomendowane)

- __Cofnij pojedynczy commit__ (lokalnie):
  ```bash
  git log -n 10
  git revert <SHA>
  git push
  ```
- __Cofnij zakres commitów__ (seria revertów):
  ```bash
  git revert <SHA_PIERWSZY>^..<SHA_OSTATNI>
  git push
  ```
- __Revert PR w GitHub__ – na stronie PR kliknij „Revert”, a następnie zmerguj utworzony PR.

2) Railway – rollback bez zmian w repo

- W panelu Railway otwórz usługę → zakładka Deployments → wybierz wcześniejszy deploy → kliknij „Rollback”.

Uwaga: `git reset --hard` + `push --force` zmienia historię i jest ryzykowny – używaj tylko gdy wiesz, co robisz i branch main nie jest współdzielony.
