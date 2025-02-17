# Используем официальный образ Python
FROM python:3.12

# Устанавливаем рабочую директорию
WORKDIR /portfolio

# Копируем файлы проекта в контейнер
COPY . /portfolio

# Устанавливаем зависимости
RUN pip install --no-cache-dir -r requirements.txt

# Открываем порт, на котором будет работать приложение
EXPOSE 4566

# Команда для запуска приложения
CMD ["alembic upgrade head", "python", "app/main.py"]