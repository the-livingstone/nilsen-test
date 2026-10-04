# LRU Cache с TTL

HTTP-сервис, реализующий in-memory кэш с политикой вытеснения **LRU** (Least Recently Used) и опциональным **TTL** (time-to-live) для каждой записи.

Тестовое задание для Nielsen.

## Возможности

- Ограничение по числу ключей (`cache_size`); при переполнении удаляется наименее недавно использованный элемент
- Чтение и запись обновляют порядок использования (LRU)
- Для каждого ключа можно задать TTL в секундах; просроченные записи удаляются при обращении к кэшу
- REST API для get / put / delete и просмотра статистики
- OpenAPI-документация: `/api/_docs`
- Логирование HTTP-запросов в `log/log.log`

## Стек

| Компонент | Технология |
|-----------|------------|
| Язык | Python 3.11 |
| API | FastAPI, Uvicorn |
| Конфигурация | pydantic-settings (`.env`) |
| Зависимости | Poetry |
| Контейнер | Docker, docker-compose |

## Структура проекта

```
.
├── api/              # HTTP-роуты (/cache/...)
├── app/
│   ├── cache.py      # LRU + TTL
│   ├── main.py       # приложение, lifespan, middleware
│   ├── schemas.py    # модели запросов
│   └── settings.py   # настройки из окружения
├── tests/            # pytest (async)
├── docker-compose.yml
├── docker-compose.test.yml
└── env.example
```

## Требования

Зависимости задаются в `pyproject.toml` и ставятся через Poetry (`poetry install`).

```
python >= 3.11
fastapi >= 0.115.12
uvicorn >= 0.34.0
pydantic-settings >= 2.8.1
black >= 25.1.0
pytest >= 8.3.5
pytest-asyncio >= 0.26.0
```


## Конфигурация

Скопируйте пример окружения и при необходимости измените значения:

```bash
cp env.example .env
```

| Переменная | По умолчанию | Описание |
|------------|--------------|----------|
| `host` | `0.0.0.0` | Адрес прослушивания |
| `port` | `8000` | Порт сервера (используется и в `docker-compose` для проброса) |
| `title` | `LRU Cache с TTL` | Заголовок в OpenAPI |
| `cache_size` | `10` | Максимальное число ключей в кэше |

Переменная `debug` задаётся в коде (`AppSettings`); при необходимости её можно вынести в `.env`.

## Запуск

### Docker

```bash
docker compose -f docker-compose.yml up --build
```

Сервис будет доступен на `http://localhost:8000` (если в `.env` указан `port=8000`).

Каталог `./log` монтируется в контейнер для файла логов.

### Локально (Poetry)

```bash
poetry install
mkdir -p log
poetry run python -m app.main
```

## API

Базовый префикс: `/cache`.

### Получить значение

```http
GET /cache/{key}
```

**200** : тело `{"value": ...}`  
**404** : ключ не найден или истёк TTL

### Записать значение

```http
PUT /cache/{key}
Content-Type: application/json

{"value": <любой JSON>, "ttl": 60}
```

- `value` : обязательное поле (любой JSON-тип)
- `ttl` : необязательное, целое **> 0**, время жизни в секундах

**201** : ключ создан  
**200**: существующий ключ обновлён

### Удалить ключ

```http
DELETE /cache/{key}
```

**204** : удалено  
**404** : ключ не найден

### Статистика

```http
GET /cache/stats
```

**200** : пример ответа:

```json
{
  "size": 2,
  "capacity": 10,
  "items": ["key_recent", "key_older"]
}
```

Поле `items` : ключи от более недавно использованных к более старым (после внутренней очистки по TTL).

### Примеры (curl)

```bash
curl -X PUT http://localhost:8000/cache/user:1 \
  -H 'Content-Type: application/json' \
  -d '{"value": {"name": "Alice"}, "ttl": 300}'

curl http://localhost:8000/cache/user:1
curl http://localhost:8000/cache/stats
curl -X DELETE http://localhost:8000/cache/user:1
```

Swagger: `http://localhost:8000/api/_docs`.

## Тесты

Через Docker:

```bash
docker compose -f docker-compose.test.yml up --build --abort-on-container-exit
```

Локально:

```bash
poetry run pytest tests
```

Тесты покрывают заполнение кэша, TTL, удаление, вытеснение LRU, обновление записей и `stats`.

## Поведение кэша (кратко)

1. **LRU**: при `GET` / успешном `PUT` ключ становится «самым свежим»; при превышении `capacity` удаляется элемент с наименьшим приоритетом использования.
2. **TTL**: проверка срока действия выполняется при операциях с кэшем (`get`, `put`, `delete`, `stats`), не фоновым воркером.
3. **Обновление**: повторный `PUT` по тому же ключу заменяет `value` и `ttl`, не увеличивая число записей (если ключ уже был в кэше).
