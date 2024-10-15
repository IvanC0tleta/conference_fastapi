# conference_fastapi
веб приложение “Конференция”

FastAPI проект с подключением к PostgreSQL через SQLAlchemy и миграциями Alembic. Этот проект развернут с помощью Docker и Poetry.

## Требования

Перед запуском убедитесь, что на вашем компьютере установлены:

- [Docker](https://www.docker.com/)
- [Poetry](https://python-poetry.org/)

## Установка

1. Склонируйте репозиторий:
   ```bash
   git clone https://github.com/ваш-логин/conf1.git
   cd conf1
   ```
   
2. Создайте файл .env и заполните переменные окружения:

3. Убедитесь, что Docker работает на вашем компьютере.

## Запуск приложения с Docker
1. Соберите и запустите приложение через Docker Compose:
  ```bash
  docker-compose up --build
  ```
2. Приложение будет доступно по адресу http://localhost:8000

## Тестирование 
Для запуска тестов используется pytest
  ```bash
  poetry run pytest
  ```
