# 🗓️ Plan Prac nad Projektem: yt media tool

---

## 🧱 Założenia organizacyjne

- Sprint = 3–4 dni robocze
- Każdy sprint kończy się działającą wersją demo
- Podejście: MVP ➜ UX ➜ Rozszerzenia ➜ Automatyzacja

---

## ✅ Sprint 1: Inicjalizacja projektu i podstawowa architektura

**Cel:** Przygotowanie środowiska, struktury katalogów, uruchomienie FastAPI i testowy endpoint.

**Zadania:**
- Inicjalizacja repozytorium (np. GitHub)
- Utworzenie katalogów `templates/`, `static/`, `utils/`
- Konfiguracja `Dockerfile`, `docker-compose.yml`
- Endpoint `GET /ping` (test połączenia)
- Prosty frontend HTML z przyciskiem „Testuj API”

🎯 **Efekt:** Kontener działa, frontend łączy się z backendem

---

## ✅ Sprint 2: Pobieranie metadanych z YouTube (yt-dlp)

**Cel:** Wprowadzenie logiki `yt-dlp`, pobieranie tytułu, autora, miniatury i formatów.

**Zadania:**
- Endpoint `GET /metadata?url=...`
- Implementacja `ytdlp_helper.py` do ekstrakcji metadanych
- Walidacja linku (czy to YouTube?)
- Obsługa błędów (link nie działa, brak internetu itd.)
- Frontend: formularz wklejenia linku + wyświetlenie metadanych

🎯 **Efekt:** Można wkleić link i zobaczyć dostępne formaty + tytuł

---

## ✅ Sprint 3: Pobieranie ścieżki audio i wysyłka do przeglądarki

**Cel:** Zaimplementowanie faktycznego pobierania i konwersji audio.

**Zadania:**
- Endpoint `POST /download` z `url` i `format_id`
- Uruchomienie `yt-dlp` z opcjami `--format`, `--postprocessor`
- Stream pliku audio bez zapisu na dysk
- Frontend: wybór formatu i przycisk „Pobierz”

🎯 **Efekt:** Działa pobieranie ścieżki audio z filmu

---

## ✅ Sprint 4: Optymalizacja UX i walidacja danych

**Cel:** Ułatwienie obsługi użytkownikowi i eliminacja błędów użytkownika.

**Zadania:**
- Walidacja danych wejściowych na froncie i backendzie
- Obsługa błędów użytkownika (złe linki, brak formatu)
- Ulepszenie komunikatów błędów
- Poprawa responsywności UI

🎯 **Efekt:** Aplikacja jest bardziej przyjazna i odporna na błędy

---

## 🆕 Sprint 5: Testy automatyczne (backend i frontend)

**Cel:** Zapewnienie stabilności i odporności na regresje.

**Zadania:**
- Przygotowanie testów jednostkowych backendu (FastAPI, utils)
- Proste testy integracyjne endpointów
- Testy frontendowe (np. sprawdzenie walidacji formularza)

🎯 **Efekt:** Podstawowe testy przechodzą, łatwiej rozwijać projekt

---

## 🆕 Sprint 6: Dokumentacja projektu

**Cel:** Ułatwienie wdrożenia i rozwoju narzędzia.

**Zadania:**
- Opis API (README lub OpenAPI)
- Instrukcja uruchomienia (Docker, lokalnie)
- Opis architektury katalogów

🎯 **Efekt:** Każdy może szybko uruchomić i zrozumieć projekt

---

## 🆕 Sprint 7: Bezpieczeństwo i limity

**Cel:** Zabezpieczenie narzędzia przed nadużyciami i błędami.

**Zadania:**
- Walidacja wejścia (np. długość URL, poprawność formatu)
- Ochrona przed spamem/botami (np. rate limiting)
- Ograniczenie rozmiaru pobieranych plików

🎯 **Efekt:** Narzędzie jest bezpieczniejsze i bardziej odporne

---

## 🆕 Sprint 8: Deployment/publiczne demo

**Cel:** Udostępnienie narzędzia publicznie lub na demo.

**Zadania:**
- Przygotowanie deploymentu (np. na render.com, fly.io, Heroku, VPS)
- Konfiguracja zmiennych środowiskowych
- Testy działania na produkcji

🎯 **Efekt:** yt media tool dostępny publicznie lub w demo

---

## ✅ Sprint 5: Dodatki i kosmetyka

**Cel:** Uporządkowanie kodu, drobne funkcje dodatkowe.

**Zadania:**
- Zapis metadanych w `data.json` (tymczasowo, np. debug)
- Logowanie do konsoli / pliku
- Ładniejszy frontend (CSS / UI bez frameworka)
- Przygotowanie demo / screencast

🎯 **Efekt:** Gotowa prezentacja MVP

---

## 🧩 Sprint 6+ (opcjonalnie: wersja rozszerzona)

**Pomysły:**
- Kolejkowanie żądań (async, Celery, Redis)
- Wysyłanie pliku do Dropbox/Google Drive
- Historia pobrań
- Playlisty YouTube
- Obsługa zakresu czasu (start/end)
- Logowanie i ochrona API

---

## 📋 Przykładowa tablica Kanban

| To do               | In progress      | Done            |
|---------------------|------------------|-----------------|
| Konfiguracja Docker | Pobieranie audio | Endpoint /ping  |
| Frontend HTML       | Metadata parser  | Format list OK  |