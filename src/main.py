import asyncio

from datetime import datetime, timezone
from fastapi import FastAPI, HTTPException, Path
from fastapi.responses import JSONResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles

from pathlib import Path as PathLib
from pydantic import BaseModel, ConfigDict, Field
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Annotated

# Импортируем мок HTML
from mock_html import MOCK_HTML


FRONTEND_DIR = PathLib(__file__).parent / "frontend"
STATIC_FILES_DIR = PathLib(__file__).parent / "static"


app = FastAPI(title="FastAI App", version="1.0.0")


def to_camel_case(snake_str: str) -> str:
    """Преобразование названия поля в camelCase"""
    components = snake_str.split('_')
    return components[0] + ''.join(word.capitalize() for word in components[1:])


# === PYDANTIC МОДЕЛИ ДАННЫХ ===

class UserDetailsResponse(BaseModel):
    """
    Модель ответа с детальной информацией о пользователе.

    Attributes:
        profile_id: Уникальный идентификатор профиля в системе
        username: Отображаемое имя пользователя
        email: Контактный email адрес
        is_active: Флаг активности учетной записи
        registered_at: Дата и время регистрации
        updated_at: Дата и время последнего обновления информации

    Example:
        >>> UserDetailsResponse(
        ...     profile_id="1",
        ...     username="user123",
        ...     email="test@example.com",
        ...     is_active=True
        ... )
        UserDetailsResponse(
            profile_id='1',
            username='user123',
            email='test@example.com',
            is_active=True,
            registered_at=datetime.datetime(...),
            updated_at=datetime.datetime(...)
        )
    """
    profile_id: str = Field(..., examples=["1"])
    username: str = Field(..., examples=["user123"])
    email: str = Field(..., examples=["example@example.com"])
    is_active: bool = Field(..., examples=[True])
    registered_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

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
        },
        alias_generator=to_camel_case,
        populate_by_name=True,
        use_attribute_docstrings=True
    )


class CreateSiteRequest(BaseModel):
    """
    Модель запроса для создания сайта.

    Attributes:
        title: Название сайта (необязательное, макс. 128 символов)
        prompt: Описание или промт для сайта (обязательное)
    """
    title: str | None = Field(
        default=None,
        max_length=128,
        examples=["Фан клуб игры в домино"],
        description="Название сайта, не более 128 символов"
    )
    prompt: str = Field(
        ...,
        examples=["Сайт любителей играть в домино"],
        description="Описание или промт для создания сайта"
    )

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "title": "Фан клуб игры в домино",
                    "prompt": "Сайт любителей играть в домино"
                },
                {
                    "title": None,
                    "prompt": "Сайт без названия"
                }
            ]
        }
    )


class CreateSiteResponse(BaseModel):
    id: int = Field(..., examples=[1])
    title: str | None = Field(..., examples=["Фан клуб Домино"], description="Название сайта, может быть null")
    prompt: str = Field(..., examples=["Сайт любителей играть в домино"])
    html_code_url: str = Field(..., examples=["http://example.com/media/index.html"])
    html_code_download_url: str = Field(
        ...,
        examples=["http://example.com/media/index.html?response-content-disposition=attachment"]
    )
    screenshot_url: str = Field(..., examples=["http://example.com/media/index.png"])
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    model_config = ConfigDict(
        alias_generator=to_camel_case,
        populate_by_name=True,
        json_schema_extra={
            "example": {
                "id": 1,
                "site_id": 1,
                "title": "Фан клуб Домино",
                "prompt": "Сайт любителей играть в домино",
                "html_code_url": "http://example.com/media/index.html",
                "html_code_download_url": "http://example.com/media/index.html?response-content-disposition=attachment",
                "screenshot_url": "http://example.com/media/index.png",
                "created_at": "2025-06-15T18:29:56+00:00",
                "updated_at": "2025-06-15T18:29:56+00:00",
            }
        }
    )


class SiteGenerationRequest(BaseModel):
    """
    Модель запроса для генерации HTML кода сайта.

    Attributes:
        prompt: Промт для генерации контента сайта
    """
    prompt: str = Field(
        ...,
        examples=["Сайт любителей играть в домино"],
        description="Промт для генерации HTML контента"
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "prompt": "Сайт любителей играть в домино"
            }
        }
    )


class SiteResponse(BaseModel):
    """
    Модель ответа с информацией о сайте.

    Attributes:
        id: Уникальный идентификатор сайта
        title: Название сайта
        prompt: Промт использованный для генерации
        html_code_url: URL HTML кода (может быть null)
        html_code_download_url: URL для скачивания HTML (может быть null)
        screenshot_url: URL скриншота (может быть null)
        created_at: Дата создания
        updated_at: Дата обновления
    """
    id: int = Field(..., examples=[1])
    title: str = Field(..., examples=["Фан клуб Домино"])
    prompt: str = Field(..., examples=["Сайт любителей играть в домино"])
    html_code_url: str | None = Field(
        default=None,
        examples=["http://example.com/media/index.html"],
        description="URL HTML кода сайта"
    )
    html_code_download_url: str | None = Field(
        default=None,
        examples=["http://example.com/media/index.html?response-content-disposition=attachment"],
        description="URL для скачивания HTML кода"
    )
    screenshot_url: str | None = Field(
        default=None,
        examples=["http://example.com/media/index.png"],
        description="URL скриншота сайта"
    )
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    model_config = ConfigDict(
        alias_generator=to_camel_case,
        populate_by_name=True,
        json_schema_extra={
            "example": {
                "id": 1,
                "title": "Фан клуб Домино",
                "prompt": "Сайт любителей играть в домино",
                "html_code_url": "http://example.com/media/index.html",
                "html_code_download_url": "http://example.com/media/index.html?response-content-disposition=attachment",
                "screenshot_url": "http://example.com/media/index.png",
                "created_at": "2025-06-15T18:29:56+00:00",
                "updated_at": "2025-06-15T18:29:56+00:00",
            }
        }
    )


class GeneratedSitesResponse(BaseModel):
    sites: list[SiteResponse]


# === Мок-данные ===

MOCK_SITE = SiteResponse(
    id=1,
    title="Фан клуб Домино",
    prompt="Сайт любителей играть в домино",
    html_code_url="http://example.com/media/index.html",
    html_code_download_url="http://example.com/media/index.html?response-content-disposition=attachment",
    screenshot_url="http://example.com/media/index.png",
    created_at=datetime(2025, 6, 15, 18, 29, 56, tzinfo=timezone.utc),
    updated_at=datetime(2025, 6, 15, 18, 29, 56, tzinfo=timezone.utc),
)


MOCK_SITES_LIST = [MOCK_SITE, ]


# === Генератор чанков для стриминга ===

async def generate_html_chunks(prompt: str, site_id: int):
    """Генерирует HTML контент чанками на основе промта."""
    # Примерная реализация - замените на реальную логику
    html_template = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Сайт #{site_id}</title>
    </head>
    <body>
        <h1>Сгенерировано на основе: {prompt}</h1>
        <p>Контент сайта...</p>
    </body>
    </html>
    """

    # Эмуляция streaming - отдаем чанками
    chunk_size = 100
    for i in range(0, len(html_template), chunk_size):
        yield html_template[i:i + chunk_size]
        await asyncio.sleep(0.1)


# === ЭНДПОИНТЫ ===

# 1. GET: /users/me
@app.get(
    "/users/me",
    response_model=UserDetailsResponse,
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
        "profile_id": "1",
        "username": "user123",
        "email": "example@example.com",
        "is_active": True,
        "registered_at": "2025-06-15T18:29:56+00:00",
        "updated_at": "2025-06-15T18:29:56+00:00",
    }
    return JSONResponse(content=mock_user_data, status_code=200)


# 2. GET: /sites/my
@app.get(
    "/sites/my",
    response_model=GeneratedSitesResponse,
    summary="Получить список сгенерированных сайтов текущего пользователя",
    response_description="Список созданных пользователем сайтов",
    tags=["Sites"],
    responses={200: {"description": "Successful Response"}},
)
async def mock_get_user_sites():
    return {"sites": MOCK_SITES_LIST}


# 3. POST: /sites/create
@app.post(
    "/sites/create",
    response_model=CreateSiteResponse,
    summary="Создать сайт",
    response_description="Возвращает информацию о созданном сайте",
    tags=["Sites"],
    responses={
        200: {
            "description": "Successful Response",
            "content": {
                "application/json": {
                    "example": {
                        "id": 1,
                        "title": "Фан клуб Домино",
                        "prompt": "Сайт любителей играть в домино",
                        "created_at": "2025-06-15T18:29:56+00:00",
                        "updated_at": "2025-06-15T18:29:56+00:00",
                        "html_code_url": "http://example.com/media/index.html",
                        "html_code_download_url": "http://example.com/media/index.html?response-content-disposition=attachment",
                        "screenshot_url": "http://example.com/media/index.png"
                    }
                }
            },
        },
        422: {
            "description": "Validation Error",
            "content": {
                "application/json": {
                    "examples": {
                        "missing_prompt": {
                            "summary": "Missing required field",
                            "value": {
                                "detail": [
                                    {
                                        "loc": ["body", "prompt"],
                                        "msg": "Field required",
                                        "type": "missing"
                                    }
                                ]
                            }
                        },
                        "title_too_long": {
                            "summary": "Title too long",
                            "value": {
                                "detail": [
                                    {
                                        "loc": ["body", "title"],
                                        "msg": "ensure this value has at most 128 characters",
                                        "type": "value_error.any_str.max_length",
                                        "ctx": {"limit_value": 128}
                                    }
                                ]
                            }
                        }
                    }
                }
            },
        },
    },
)
async def mock_create_site(request: CreateSiteRequest):
    current_time = datetime.now(timezone.utc)

    return CreateSiteResponse(
        id=1,
        title=request.title,
        prompt=request.prompt,
        created_at=current_time,
        updated_at=current_time,
        html_code_url="http://example.com/media/index.html",
        html_code_download_url="http://example.com/media/index.html?response-content-disposition=attachment",
        screenshot_url="http://example.com/media/index.png"
    )


# 4. POST: /sites/{site_id}/generate
@app.post(
    "/sites/{site_id}/generate",
    summary="Сгенерировать HTML код сайта",
    description="Код сайта будет транслироваться стримом по мере генерации.",
    tags=["Sites"],
    responses={
        200: {
            "description": "Successful Response",
            "content": {
                "text/html": {
                    "example": """<!DOCTYPE html>
            <html>
            <head>
                <title>Сайт #1</title>
            </head>
            <body>
                <h1>Сгенерировано на основе: Сайт любителей играть в домино</h1>
                <p>Контент сайта...</p>
            </body>
            </html>"""
                }
            }
        },
        404: {
            "description": "Site not found",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "Site not found"
                    }
                }
            }
        },
        422: {
            "description": "Validation Error",
            "content": {
                "application/json": {
                    "example": {
                        "detail": [
                            {
                                "loc": ["body", "prompt"],
                                "msg": "field required",
                                "type": "missing"
                            }
                        ]
                    }
                }
            }
        },
    },
)
async def mock_generate_site_html(
    request: SiteGenerationRequest,
    site_id: int = Path(..., description="ID сайта", examples=[1])
):
    """
    Сгенерировать HTML-контент сайта.

    Проверка:
    ```bash
    curl -X 'POST' -N http://127.0.0.1:8000/sites/1/generate \
      -H "Content-Type: application/json" \
      -d '{"prompt": "Сайт любителей играть в домино"}'
    ```
    """
    if id != 1:
        raise HTTPException(status_code=404, detail="Site not found")

    return StreamingResponse(
        generate_html_chunks(request.prompt, site_id),
        media_type="text/html",
        headers={"Content-Disposition": f"attachment; filename=site_{site_id}.html"}
    )


# 5. GET: /sites/{site_id}
@app.get(
    "/sites/{site_id}",
    response_model=SiteResponse,
    summary="Получить сайт",
    description="Возвращает полную информацию о сайте по его ID",
    tags=["Sites"],
    responses={
        200: {
            "description": "Информация о сайте",
            "content": {
                "application/json": {
                    "example": {
                        "id": 1,
                        "title": "Фан клуб Домино",
                        "prompt": "Сайт любителей играть в домино",
                        "html_code_url": "http://example.com/media/index.html",
                        "html_code_download_url": "http://example.com/media/index.html?response-content-disposition=attachment",
                        "screenshot_url": "http://example.com/media/index.png",
                        "created_at": "2025-06-15T18:29:56+00:00",
                        "updated_at": "2025-06-15T18:29:56+00:00",
                    }
                }
            }
        },
        404: {
            "description": "Site not found",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "Site not found"
                    }
                }
            }
        },
        422: {
            "description": "Validation Error",
            "content": {
                "application/json": {
                    "example": {
                        "detail": [
                            {
                                "loc": ["path", "site_id"],
                                "msg": "ensure this value is greater than 0",
                                "type": "value_error.number.not_gt",
                                "ctx": {"limit_value": 0}
                            }
                        ]
                    }
                }
            }
        },
    },
)
async def mock_get_site(site_id: int = Path(..., description="ID сайта", examples=[1])):
    """
    Получить информацию о сайте по ID.

    Args:
        site_id: ID сайта для получения информации
    """
    if site_id != 1:
        raise HTTPException(status_code=404, detail="Site not found")

    return MOCK_SITE


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
