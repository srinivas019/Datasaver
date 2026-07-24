from fastapi import FastAPI
from starlette.middleware.sessions import SessionMiddleware
from app.crud import router
from app.database import Base, engine
from fastapi.staticfiles import StaticFiles

Base.metadata.create_all(bind=engine)

app = FastAPI()
app.mount("/static", StaticFiles(directory="app/static"), name="static")
app.add_middleware(
    SessionMiddleware,
    secret_key="mysecretkey123"
)

app.include_router(router)