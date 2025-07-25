from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles


FRONTEND_DIR = Path(__file__).parent / "frontend"
STATIC_FILES_DIR = Path(__file__).parent / "static"


app = FastAPI(title="FastAI App", version="1.0.0")


@app.get(
    "/users/me",
    summary="Получить учетные данные пользователя",
    response_description="Содержит информацию о текущем пользователе",
    tags=["Users"],
    responses = {
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
                        "username": "user123"
                    }
                }
            },
        },
        401: {
            "description": "Unauthorized",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "string"
                    }
                }
            },
        },
    }
)
def mock_get_current_user():
    mock_user_data = {
        "email": "example@example.com",
        "is_active": True,
        "profile_id": "1",
        "registered_at": "2025-06-15T18:29:56+00:00",
        "updated_at": "2025-06-15T18:29:56+00:00",
        "username": "user123"
    }
    return JSONResponse(content=mock_user_data, status_code=200)


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

