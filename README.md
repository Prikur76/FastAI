# FastAI

## Репозиторий для бэкенд-разработчиков

Этот репозиторий содержит backend-часть приложения. Здесь ты найдешь инструкции по локальному запуску проекта на разных операционных системах.

---

## 📋 Требования

- Python >=3.10
- [uv](https://docs.astral.sh/uv/) (рекомендуется для управления зависимостями и версиями Python)
- Git

---

## 🚀 Установка и запуск

### 1. Клонирование репозитория

```bash
git clone https://github.com/Prikur76/FastAI.git
cd FastAI
```

---

## 📦 Дополнительные команды

| Команда                     | Описание                          |
|-----------------------------|-----------------------------------|
| `uv venv`                   | Создать новое виртуальное окружение |
| `uv add <package>`          | Добавить новую зависимость        |
| `uv remove <package>`       | Удалить зависимость               |
| `uv sync --dev`             | Установить все зависимости (включая dev) |
| `uv lock`                   | Обновить файл `uv.lock`           |

---

## 🧼 Очистка

Если нужно начать с чистого листа:

```bash
rm -rf .venv
uv venv
uv sync
```

---

## Запуск фронтенда

### Шаги:

1. **Распакуйте архив** `frontend.zip` в папку `src/frontend/`.

2. **Добавьте раздачу статики** в `src/main.py`:
   ```python
   from fastapi import FastAPI
   from fastapi.staticfiles import StaticFiles
   from pathlib import Path

   FRONTEND_DIR = Path(__file__).parent / "frontend"

   app = FastAPI()

   app.mount("/", StaticFiles(directory=FRONTEND_DIR, html=True), name="frontend")
   ```

3. **Запустите сервер:**
   ```bash
   fastapi dev src/main.py
   ```

4. Откройте браузер по адресу:
   🔗 [http://localhost:8000](http://localhost:8000)

5. Проверьте:
   - главная страница загружается
   - ошибок в консоли браузера нет

---

### Настройка (если нужно изменить URL бэкенда):

1. Создайте файл `src/static/frontend-settings.json`:

    ```json
    {
        "backendBaseUrl": "https://ваш-адрес-бекенда"
    }
    ```

2. Добавьте монтирование статики в `src/main.py`:

    ```python
    STATIC_FILES_DIR = Path(__file__).parent / "static"

    app.mount("/static", StaticFiles(directory=STATIC_FILES_DIR), name="static-files")
    ```

3. Перезагрузите страницу (Shift + F5).

---

## 🤝 Возникли проблемы?

Пиши в чат или открывай issue — мы поможем!
