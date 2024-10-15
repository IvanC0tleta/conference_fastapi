# Веб приложение “Конференция”

FastAPI проект с подключением к PostgreSQL через SQLAlchemy и миграциями Alembic. Этот проект развернут с помощью Docker и Poetry.

## Требования

Перед запуском убедитесь, что на вашем компьютере установлен [Docker](https://www.docker.com/)

## Установка

1. Склонируйте репозиторий:
   ```bash
   git clone https://github.com/IvanC0tleta/conference_fastapi.git
   ```
   
2. В файле .env заполните переменные окружения.

3. Убедитесь, что Docker запущен на вашем компьютере.

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
