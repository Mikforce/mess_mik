from fastapi import FastAPI, UploadFile, File, HTTPException, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlalchemy.ext.asyncio import AsyncEngine

from .config import get_settings
from .db import engine, Base
from .routers import auth as auth_router
from .routers import users as users_router
from .routers import chat as chat_router
from .routers import admin as admin_router


def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(title=settings.APP_NAME, debug=settings.DEBUG)

    # CORS (для локальной разработки фронтенда)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Routers
    app.include_router(auth_router.router)
    app.include_router(users_router.router)
    app.include_router(chat_router.router)
    app.include_router(admin_router.router)

    @app.on_event("startup")
    async def on_startup() -> None:
        # Для простоты на старте создаём таблицы (в проде — миграции)
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        # Гарантируем наличие директории для загрузок
        from pathlib import Path
        Path("uploads").mkdir(parents=True, exist_ok=True)

    @app.get("/")
    async def read_root():
        return {"message": "Welcome to Messenger Backend!"}

    # Раздача статики: простая UI-страница по адресу /ui
    app.mount("/ui", StaticFiles(directory="app/static", html=True), name="ui")
    # Убрали прямую раздачу /uploads; используем защищённую выдачу через эндпоинт

    @app.post("/media/upload")
    async def upload_media(file: UploadFile = File(...)):
        # Примитивная валидация изображений по content-type
        if not file.content_type or not file.content_type.startswith("image/"):
            raise HTTPException(status_code=400, detail="Only image uploads are allowed")
        import uuid
        from pathlib import Path
        from base64 import urlsafe_b64decode
        from cryptography.fernet import Fernet

        uploads_dir = Path("uploads")
        uploads_dir.mkdir(parents=True, exist_ok=True)
        suffix = Path(file.filename or "").suffix or ""
        name = f"{uuid.uuid4().hex}{suffix}"
        dest = uploads_dir / name

        # Читаем весь файл в память (для простоты MVP). Для больших файлов — потоковое шифрование/запись чанками
        data = await file.read()
        key = get_settings().MEDIA_ENC_KEY
        if key:
            try:
                fernet = Fernet(key.encode())
                data = fernet.encrypt(data)
            except Exception:
                raise HTTPException(status_code=500, detail="Encryption error")
        with dest.open("wb") as out:
            out.write(data)

        return {"filename": name, "url": f"/media/{name}", "content_type": file.content_type}

    @app.get("/media/{filename}")
    async def get_media(filename: str):
        from pathlib import Path
        from cryptography.fernet import Fernet
        file_path = Path("uploads") / filename
        if not file_path.exists():
            raise HTTPException(status_code=404, detail="Not found")
        data = file_path.read_bytes()
        key = get_settings().MEDIA_ENC_KEY
        if key:
            try:
                fernet = Fernet(key.encode())
                data = fernet.decrypt(data)
            except Exception:
                raise HTTPException(status_code=500, detail="Decryption error")
        return Response(content=data, media_type="application/octet-stream")

    return app


app = create_app()