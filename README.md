# nilsen-test
## Тестовое задание для Нильсен
## Least Recent Used cache with TTL

### Запуск приложения
- скопировать env.example в .env
- указать в .env желаемую ёмкость кэша (переменная cache_size)
- запустить ```docker compose -f docker-compose.yml up``` для запуска приложения
- запустить ```docker compose -f docker-compose.test.yml up``` для запуска тестов