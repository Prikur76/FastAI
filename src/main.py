import asyncio

from datetime import datetime, timezone
from fastapi import FastAPI, HTTPException, Path
from fastapi.responses import JSONResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles

from pathlib import Path as PathLib
from pydantic import BaseModel, ConfigDict, Field
from typing import Annotated

# Импортируем мок HTML
from mock_html import MOCK_HTML


FRONTEND_DIR = PathLib(__file__).parent / "frontend"
STATIC_FILES_DIR = PathLib(__file__).parent / "static"


app = FastAPI(title="FastAI App", version="1.0.0")

# === PYDANTIC МОДЕЛИ ДАННЫХ ===


class UserResponse(BaseModel):
    email: str
    is_active: bool
    profile_id: str
    registered_at: str
    updated_at: str
    username: str

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "email": "example@example.com",
                "is_active": True,
                "profile_id": "1",
                "registered_at": "2025-06-15T18:29:56+00:00",
                "updated_at": "2025-06-15T18:29:56+00:00",
                "username": "user123",
            }
        }
    )


class SiteCreateRequest(BaseModel):
    title: Annotated[
        str, Field(description="Название сайта", examples=["Мой блог", "Сайт про стегозавров", "Лендинг продукта"])
    ] = "Новый сайт"
    description: str | None = Field(default=None, description="Описание сайта", examples=["Сайт о стегозаврах"])

    model_config = ConfigDict(
        json_schema_extra={"example": {"title": "Новый сайт", "description": "Сайт про стегозавров"}}
    )


class SiteCreateResponse(BaseModel):
    site_id: Annotated[int, Field(description="Уникальный идентификатор сайта", examples=[1])]
    title: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    status: str = Field(default="created", examples=["created", "generating", "ready"])


class SiteResponse(BaseModel):
    site_id: int
    title: str
    description: str | None = None
    created_at: datetime
    updated_at: datetime
    status: str
    url: str | None = None
    html_preview: str | None = Field(default=None, description="Превью HTML (первые 200 символов)")


class SiteListResponse(BaseModel):
    sites: list[SiteResponse]


# === Мок-данные ===
MOCK_SITE = SiteResponse(
    site_id=1,
    title="Сайт про стегозавров",
    description="Сгенерированный сайт о стегозаврах",
    created_at=datetime(2025, 7, 29, 12, 0, 0),
    updated_at=datetime(2025, 7, 29, 12, 0, 0),
    status="ready",
    url="/sites/1",
    html_preview=MOCK_HTML[:200] + "..." if len(MOCK_HTML) > 200 else MOCK_HTML,
)

MOCK_SITES_LIST = [MOCK_SITE, MOCK_SITE, MOCK_SITE]


# === Генератор чанков для стриминга ===
async def generate_html_chunks():
    """Асинхронный генератор, имитирующий постепенную генерацию HTML"""
    for i in range(0, len(MOCK_HTML), 100):  # разбиваем на чанки по 100 символов
        chunk = MOCK_HTML[i : i + 100]
        yield chunk
        await asyncio.sleep(0.1)  # имитация задержки генерации


# === ЭНДПОИНТЫ ===


# 1. GET: /users/me
@app.get(
    "/users/me",
    response_model=UserResponse,
    summary="Получить учетные данные пользователя",
    response_description="Содержит информацию о текущем пользователе",
    tags=["Users"],
    responses={
        200: {
            "description": "Successful Response",
            "content": {
                "application/json": {
                    "example": {
                        "email": "example@example.com",
                        "is_active": True,
                        "profile_id": "1",
                        "registered_at": "2025-06-15T18:29:56+00:00",
                        "updated_at": "2025-06-15T18:29:56+00:00",
                        "username": "user123",
                    }
                }
            },
        },
        401: {
            "description": "Unauthorized",
            "content": {"application/json": {"example": {"detail": "string"}}},
        },
    },
)
def mock_get_current_user() -> JSONResponse:
    mock_user_data = {
        "email": "example@example.com",
        "is_active": True,
        "profile_id": "1",
        "registered_at": "2025-06-15T18:29:56+00:00",
        "updated_at": "2025-06-15T18:29:56+00:00",
        "username": "user123",
    }
    return JSONResponse(content=mock_user_data, status_code=200)


# 2. POST: /sites/create
@app.post(
    "/sites/create",
    response_model=SiteCreateResponse,
    summary="Создать новый сайт",
    response_description="Возвращает информацию о созданном сайте",
    tags=["Sites"],
    responses={
        200: {
            "description": "Successful Response",
            "content": {
                "application/json": {
                    "example": {
                        "site_id": 1,
                        "title": "Новый сайт",
                        "created_at": "2025-06-15T18:29:56+00:00",
                        "status": "created",
                    }
                }
            },
        },
        422: {
            "description": "Validation Error",
            "content": {
                "application/json": {
                    "example": {
                        "detail": [{"loc": ["body", "name"], "msg": "field required", "type": "value_error.missing"}]
                    }
                }
            },
        },
    },
)
async def mock_create_site(request: SiteCreateRequest):
    return SiteCreateResponse(site_id=1, title=request.title, status="created")


# 5. GET: /sites/my
@app.get(
    "/sites/my",
    response_model=SiteListResponse,
    summary="Получить список сайтов пользователя",
    response_description="Список созданных пользователем сайтов",
    tags=["Sites"],
    responses={200: {"description": "Список сайтов пользователя"}},
)
async def mock_get_user_sites():
    return {"sites": MOCK_SITES_LIST}


# 4. GET: /sites/{site_id}
@app.get(
    "/sites/{site_id}",
    response_model=SiteResponse,
    summary="Получить информацию о сайте",
    response_description="Детальная информация о сайте",
    tags=["Sites"],
    responses={200: {"description": "Информация о сайте"}, 404: {"description": "Site not found"}},
)
async def mock_get_site(site_id: int = Path(..., description="ID сайта", example=1)):
    if site_id != 1:
        raise HTTPException(status_code=404, detail="Site not found")

    return MOCK_SITE


# 3. POST: /sites/{site_id}/generate
@app.post(
    "/sites/{site_id}/generate",
    summary="Сгенерировать HTML-контент сайта",
    description="Стриминг HTML-кода в процессе генерации",
    tags=["Sites"],
    responses={
        200: {"description": "HTML контент сайта", "content": {"text/html": {}}},
        404: {"description": "Site not found"},
    },
)
async def mock_generate_site_html(site_id: int = Path(..., description="ID сайта", example=1)):
    """
    Сгенерировать HTML-контент сайта.
    curl -X 'POST' -N http://127.0.0.1:8000/sites/1/generate
    """
    if site_id != 1:
        raise HTTPException(status_code=404, detail="Site not found")

    return StreamingResponse(generate_html_chunks(), media_type="text/html")


app.mount(
    "/static",
    StaticFiles(directory=STATIC_FILES_DIR),
    name="static-files",
)


app.mount(
    "/",
    StaticFiles(directory=FRONTEND_DIR, html=True),
    name="frontend",
)
