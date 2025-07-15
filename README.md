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

## 🔧 Настройка окружения

> 💡 Используем [`uv`](https://docs.astral.sh/uv/) — быстрый менеджер пакетов и виртуальных окружений для Python.

### Установка `uv` (если не установлен)

```bash
curl -LsSf https://astral.github.io/uv/guides/installation.html | sh
```

Или через `pip`:

```bash
pip install uv
```

---

## 🐧 Linux (Ubuntu 24.04 / 22.04)

### Установите зависимости:

```bash
uv sync
```

### Активируйте виртуальное окружение:

```bash
source .venv/bin/activate
```

### Запустите сервер:

```bash
fastapi dev src/main.py
```

ты должен увидеть вывод похожий на:

```
server   Server started at http://127.0.0.1:8000
server   Documentation at http://127.0.0.1:8000/docs
```

⚠️ Если у тебя нет `.venv`, создай его:

```bash
uv venv
```

---

## 🍏 macOS

### Установите зависимости:

```bash
uv sync
```

### Активируйте виртуальное окружение:

```bash
source .venv/bin/activate
```

### Запустите сервер:

```bash
uv run python main.py
```

---

## 🪟 Windows (PowerShell)

> 💡 Работаем в PowerShell

### Установите зависимости:

```powershell
uv sync
```

### Активируйте виртуальное окружение:

```powershell
.venv\Scripts\Activate.ps1
```

### Запустите сервер:

```powershell
uv run python main.py
```

---

## 🧪 Проверка установленной версии Python

```bash
python --version
```

Версия указана в `pyproject.toml`:

```toml
requires-python = ">=3.10,<3.11"
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
