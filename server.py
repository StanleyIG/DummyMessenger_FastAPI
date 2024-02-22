import uvicorn
from fastapi.requests import Request
from typing import Optional, Annotated
from fastapi import FastAPI, APIRouter
from fastapi import Depends
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, declared_attr
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager


message_route = APIRouter()

# создание движка для асинхронного взаимодействия с базой, а так-же создание создание асинхронной сессии
async_db_engine = create_async_engine("sqlite+aiosqlite:///server.db")
async_session = async_sessionmaker(async_db_engine, expire_on_commit=False)


async def get_async_session():
    """функция, которая вернет async_session"""
    async with async_session() as session:
        yield session
    #  try:
    #      yield session
    #  finally:
    #      session.close()


async def create_db():
    """создание базы"""
    async with async_db_engine.begin() as conn:
        await conn.run_sync(Model.metadata.create_all)


class Model(DeclarativeBase):
    pass


class Messages(Model):
    __tablename__ = "server"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]
    text: Mapped[Optional[str]]
    date: Mapped[]


# инициализация объекта приложения сервера FastAPI


# создание схемы сериализации и валидации данных с помощью встроенной бтблиотеки
# pydantic


class UserBodyRequestToDB(BaseModel):
    name: str
    text: str


class UserBodyID(UserBodyRequestToDB):
    idx: int


# роут для добавления сообщения в базу данных

@message_route.post('/add-message')
async def add_message(user_post: Annotated[UserBodyRequestToDB, Depends()],
                      db: AsyncSession = Depends(get_async_session)):
    new_message = Messages(name=user_post.name, text=user_post.text)
    db.add(new_message)
    await db.commit()
    
    #last_ten_message = 
    return {"message": "Message added successfully"}


# функция выполняет процесс создания приложения и запуск зависимостей, в частности создание базы
def create_app():
    @asynccontextmanager
    async def lifespan(app: FastAPI):
        """При запуске сервера создаётся база, если база уже создана, то соответсвенно этот код 
        выполняться повторно уже не будет, согласно документации FastAPI"""
        await create_db()
        yield
    app = FastAPI(lifespan=lifespan)
    app.include_router(message_route)

    return app


# Запуск сервера FastAPI
app = create_app()
if __name__ == '__main__':
    uvicorn.run('server:app', host='127.0.0.1', port=5000, reload=True)
