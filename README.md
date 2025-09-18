# Cadastral Query Service

Мини‑сервис для обработки кадастровых запросов: принимает номер, координаты, сохраняет запись в БД, обращается к внешнему симулятору и возвращает результат. Готов к запуску в Docker Compose, миграции Alembic применяются автоматически.

## Состав проекта

- Query Service (FastAPI) — основной API на порту 8000
- External Simulator (FastAPI) — имитация внешнего сервиса на порту 8001
- PostgreSQL — база данных для хранения заявок

## Быстрый старт (Docker)

1) Клонируйте репозиторий
```bash
git clone https://github.com/AleksandrZaec/cadastral.git
cd cadastral
```
2) Создайте файл окружения `.env` в корне (рядом с `docker-compose.yaml`). Пример ниже.
3) Запустите
```bash
docker compose up --build
```
- Миграции применятся автоматически при старте `query_service`
- API: `http://localhost:8000`
- Симулятор: `http://localhost:8001`

Остановка:
```bash
docker compose down
```
Полная пересборка:
```bash
docker compose build --no-cache && docker compose up
```

## Пример .env

```env
# Режим (для логики/логгирования, опционально)
MODE=local

# Postgres
DB_HOST=db
DB_PORT=5432
POSTGRES_DB=app
POSTGRES_USER=app
POSTGRES_PASSWORD=app

# URL внешнего сервиса (симулятора)
EXTERNAL_SERVICE_URL=http://external_simulator:8001

# Логи (опционально)
LOG_LEVEL=INFO   # DEBUG/INFO/WARNING/ERROR
LOG_JSON=false   # true|false
LOG_NAME=app
```

Примечания:
- В контейнерах `DB_HOST` должен быть `db` (имя сервиса в docker-compose)
- `EXTERNAL_SERVICE_URL` указывает на сервис симулятора по имени контейнера

## API

Базовый URL: `http://localhost:8000`

### Документация
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

### 1) Healthcheck
- Метод: GET `/ping`
- Описание: Проверка доступности сервиса
- Ответ: `{ "status": "ok" }`

Пример:
```bash
curl -s http://localhost:8000/ping
```

### 2) Создать и обработать запрос
- Метод: POST `/query`
- Тело запроса (JSON):
```json
{
  "cadastral_number": "77:01:0004012:3456",
  "latitude": 55.751244,
  "longitude": 37.618423
}
```
- Успешный ответ: 201 Created, схема `RequestRead`
```json
{
  "id": 1,
  "cadastral_number": "77:01:0004012:3456",
  "latitude": 55.751244,
  "longitude": 37.618423,
  "payload": {"cadastral_number": "77:01:0004012:3456", "latitude": 55.751244, "longitude": 37.618423},
  "response": {"success": true},
  "success": true,
  "created_at": "2025-09-18T12:34:56.000000"
}
```
- Валидация: широта в диапазоне [-90, 90], долгота — [-180, 180]
- Возможные ошибки:
  - 504: таймаут внешнего сервиса (> 60 сек)
  - 502: ошибка внешнего сервиса (HTTP ошибка/некорректный ответ)
  - 500: прочие ошибки внешнего сервиса

Ответ ошибки:
```json
{
  "detail": {
    "message": "External service timeout (more than 60 sec)",
    "request_id": 123
  }
}
```

Пример запроса:
```bash
curl -s -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{
    "cadastral_number": "77:01:0004012:3456",
    "latitude": 55.75,
    "longitude": 37.62
  }'
```

### 3) История всех запросов
- Метод: GET `/history`
- Параметры:
  - `limit` (int, 1..1000, по умолчанию 100)
  - `offset` (int, >=0, по умолчанию 0)
- Ответ: список `RequestRead`, упорядочен по `created_at` по убыванию

Пример:
```bash
curl -s "http://localhost:8000/history?limit=10&offset=0"
```

### 4) История по кадастровому номеру
- Метод: GET `/history/{cadastral_number}`
- Параметры: `limit`, `offset` — как выше
- Ответ: список `RequestRead` для указанного номера

Пример:
```bash
curl -s "http://localhost:8000/history/77:01:0004012:3456?limit=5"
```

## Устройство сервиса (вкратце)

- `app/query_service/routers.py` — маршруты FastAPI
- `app/query_service/schemas.py` — модели запросов/ответов (Pydantic)
- `app/query_service/services.py` — бизнес‑логика: создаёт запись, вызывает внешний сервис, сохраняет результат
- `app/query_service/repositories.py` — доступ к БД (CRUD)
- `app/query_service/models.py` — модели SQLAlchemy
- `app/core/db.py` — создание async‑движка и сессии
- `app/core/logging.py` — конфигурация логирования
- `alembic/` — миграции БД

Внешний симулятор (`app/external_simulator/main.py`):
- POST `/result` — отвечает через случайную задержку (0–60 сек) полем `{ "success": true|false }`

## Частые вопросы

- Права на `entrypoint.sh` в Windows
  - В compose уже добавлена команда `chmod +x app/query_service/entrypoint.sh && app/query_service/entrypoint.sh` — права выставляются при старте.
- Контейнер использует старую версию кода
  - Пересоберите без кеша: `docker compose build --no-cache`.

## Локальный запуск без Docker (опционально)

1) Установите Python 3.12 и зависимости (poetry):
```bash
poetry install
```
2) Экспортируйте переменные окружения (см. `.env`), примените миграции:
```bash
alembic upgrade head
```
3) Запустите API:
```bash
uvicorn app.main:app --reload --port 8000
```


